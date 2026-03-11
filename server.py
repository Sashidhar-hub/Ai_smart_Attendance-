from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import uvicorn
import cv2
import numpy as np
import json
import hashlib
from datetime import datetime
from contextlib import asynccontextmanager

# Import AI logic from utils (ignoring CSV/Streamlit parts)
try:
    from utils import extract_embedding, verify_face, verify_liveness, verify_classroom, preprocess_face
except ImportError:
    pass

app = FastAPI()

# Add CORS middleware for React Web App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development (e.g., localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

DB_FILE = "attendance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Helper: Hash Password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Pydantic Models
class UserRegister(BaseModel):
    name: str
    student_id: str
    email: str
    password: str
    section: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AttendanceRequest(BaseModel):
    user_id: int
    session_code: str # QR Code content 
    # Image will be uploaded separately or base64? 
    # For file uploads, it's better to use Form data or separate endpoints.
    # We'll use File Upload endpoint that takes session_code as Form parameter.

@app.get("/")
def read_root():
    return {"message": "Smart Attendance API is running"}

@app.post("/register")
def register(user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hashed_pw = hash_password(user.password)
        cursor.execute(
            "INSERT INTO users (name, student_id, email, password_hash, section) VALUES (?, ?, ?, ?, ?)",
            (user.name, user.student_id, user.email, hashed_pw, user.section)
        )
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        conn.close()

@app.post("/login")
def login(request: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_pw = hash_password(request.password)
    cursor.execute("SELECT * FROM users WHERE email = ? AND password_hash = ?", (request.email, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "token": "demo-token-123", 
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/enroll-face")
async def enroll_face(user_id: int = Body(...), file: UploadFile = File(...)):
    # Read image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Extract Embedding
    embedding = extract_embedding(image)
    if embedding is None:
        raise HTTPException(status_code=400, detail="No face detected")
    
    # Store in DB
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Serialize embedding (JSON)
    emb_json = json.dumps(embedding.tolist())
    
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO embeddings (user_id, embedding_vector) VALUES (?, ?)",
            (user_id, emb_json)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    
    conn.close()
    return {"message": "Face enrolled successfully"}

@app.post("/mark-attendance")
async def mark_attendance(
    user_id: int = Body(...), 
    session_code: str = Body(...),
    file: UploadFile = File(...)
):
    # 1. Verify Session
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, subject FROM sessions WHERE code = ?", (session_code,))
    session = cursor.fetchone()
    if not session:
        conn.close()
        raise HTTPException(status_code=404, detail="Invalid Session Code")
    session_id = session["id"]

    # 2. Process Image (Selfie)
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 3. Liveness Check
    if not verify_liveness(image):
        conn.close()
        raise HTTPException(status_code=400, detail="Liveness check failed")

    # 4. Face Verification
    # Fetch stored embedding
    cursor.execute("SELECT embedding_vector FROM embeddings WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="Face not enrolled")
    
    stored_embedding = np.array(json.loads(row["embedding_vector"]))
    new_embedding = extract_embedding(image)
    
    if new_embedding is None:
        conn.close()
        raise HTTPException(status_code=400, detail="No face detected in selfie")

    match, score = verify_face(stored_embedding, new_embedding)
    if not match:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Face mismatch (Score: {score:.2f})")

    # 5. Mark Attendance
    try:
        cursor.execute(
            "INSERT INTO attendance (user_id, session_id, status, similarity_score) VALUES (?, ?, ?, ?)",
            (user_id, session_id, "Present", float(score))
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
        
    conn.close()
    return {"message": "Attendance marked", "score": float(score)}

@app.get("/sessions")
def get_sessions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions")
    sessions = cursor.fetchall()
    conn.close()
    return [dict(s) for s in sessions]

# Mock Session Creation for Testing
@app.post("/create-test-session")
def create_test_session(subject: str, code: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO sessions (subject, code, start_time, end_time) VALUES (?, ?, ?, ?)",
            (subject, code, datetime.now(), datetime.now())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Session code exists")
    finally:
        conn.close()
    return {"message": "Session created"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
