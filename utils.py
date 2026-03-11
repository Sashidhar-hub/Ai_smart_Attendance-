import os
import sqlite3
import pickle
import hashlib
import numpy as np
import cv2
import json
from datetime import datetime
import streamlit as st

# Suppress TensorFlow/OneDNN warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# AI Libraries
try:
    from keras.models import load_model
    import mediapipe as mp
    from ultralytics import YOLO
except ImportError as e:
    st.error(f"Missing AI dependencies: {e}")

# Constants
DB_FILE = "attendance.db"
MODELS_DIR = "models"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# ==============================
# 🗄 DATABASE CONNECTION
# ==============================
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ==============================
# 🔐 PASSWORD HASHING
# ==============================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==============================
# 👤 USER REGISTRATION
# ==============================
def register_user(name, student_id, email, section, password):
    hashed_pw = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, student_id, email, section, password_hash) VALUES (?, ?, ?, ?, ?)",
            (name, student_id, email, section, hashed_pw)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("Email already registered!")
    finally:
        conn.close()

# ==============================
# 🔑 AUTHENTICATION
# ==============================
def authenticate_user(email, password):
    hashed_pw = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ? AND password_hash = ?", (email, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True, user["name"]
    return False, None

# ==============================
# 👑 ADMIN FUNCTIONS
# ==============================
def get_all_users():
    """Return all registered users as a list of dictionaries"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, student_id, email, section, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return [dict(u) for u in users]

def get_all_attendance():
    """Return all attendance records as a pandas DataFrame"""
    import pandas as pd
    conn = get_db_connection()
    
    query = """
    SELECT a.timestamp, u.name, u.email, s.subject, a.status, a.similarity_score
    FROM attendance a
    JOIN users u ON a.user_id = u.id
    JOIN sessions s ON a.session_id = s.id
    ORDER BY a.timestamp DESC
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

# ==============================
# 🧠 AI MODEL LOADING
# ==============================
@st.cache_resource
def load_models():
    """Load FaceNet, MediaPipe FaceDetection, and YOLO models once"""
    try:
        print("🔄 Loading models...")
        
        # Check FaceNet file
        facenet_path = os.path.join(MODELS_DIR, "facenet_keras.h5")
        if not os.path.exists(facenet_path):
             st.error(f"❌ File not found: {facenet_path}. Please ensure the model file is in the 'models' folder.")
             return None, None, None

        facenet_model = load_model(facenet_path)
        
        # Initialize MediaPipe Face Detection
        mp_face_detection = mp.solutions.face_detection
        detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
        
        yolo_model = YOLO("yolov8n.pt")  # Auto-downloads if missing
        
        print("✅ All models loaded successfully!")
        return facenet_model, detector, yolo_model
    except Exception as e:
        st.error(f"❌ Model loading failed: {e}")
        return None, None, None

# Load models globally for this module
# Note: In Streamlit, this runs once per process/reload
FACENET_MODEL, DETECTOR, YOLO_MODEL = load_models()

# ==============================
# 📸 IMAGE PREPROCESSING
# ==============================
def preprocess_face(face_img):
    """Resize and normalize face for FaceNet (160x160)"""
    face_img = cv2.resize(face_img, (160, 160))
    face_img = face_img.astype('float32')
    mean, std = face_img.mean(), face_img.std()
    face_img = (face_img - mean) / std
    face_img = np.expand_dims(face_img, axis=0)
    return face_img

# ==============================
# 🧬 EMBEDDING EXTRACTION
# ==============================
def extract_embedding(image_array):
    """Extract 128-d embedding from an image containing a face"""
    if FACENET_MODEL is None or DETECTOR is None:
        return None

    try:
        rgb_img = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        
        # Optionally resize if image is too large for faster detection
        if rgb_img.shape[1] > 640:
            scale = 640 / rgb_img.shape[1]
            rgb_img = cv2.resize(rgb_img, (0,0), fx=scale, fy=scale)
            
        h, w, _ = rgb_img.shape

        results = DETECTOR.process(rgb_img)
        if not results.detections:
            return None
            
        # Get the first/most prominent face
        best_face = results.detections[0]
        bboxC = best_face.location_data.relative_bounding_box
        
        # Convert relative coords to absolute
        xmin = int(bboxC.xmin * w)
        ymin = int(bboxC.ymin * h)
        width = int(bboxC.width * w)
        height = int(bboxC.height * h)
        
        margin = 10
        x = max(0, xmin - margin)
        y = max(0, ymin - margin)
        w_box = min(w - x, width + 2*margin)
        h_box = min(h - y, height + 2*margin)
        
        face_roi = rgb_img[y:y+h_box, x:x+w_box]
        
        # If the ROI is somehow empty
        if face_roi.size == 0:
            return None
            
        face_input = preprocess_face(face_roi)
        # Assuming FaceNet outputs a single embedding vector in a batch of 1
        embedding = FACENET_MODEL.predict(face_input, verbose=0)[0]
        return embedding
    except Exception as e:
        print(f"Error extracting embedding: {e}")
        return None

# ==============================
# 💾 EMBEDDING STORAGE (SQL)
# ==============================
def save_embedding(email, embedding):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get User ID
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if user:
        user_id = user["id"]
        emb_json = json.dumps(embedding.tolist())
        cursor.execute(
            "INSERT OR REPLACE INTO embeddings (user_id, embedding_vector) VALUES (?, ?)",
            (user_id, emb_json)
        )
        conn.commit()
    
    conn.close()

def load_embedding(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT e.embedding_vector FROM embeddings e JOIN users u ON e.user_id = u.id WHERE u.email = ?", 
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return np.array(json.loads(row["embedding_vector"]))
    return None

# ==============================
# 📏 FACE VERIFICATION
# ==============================
def verify_face(stored_embedding, new_embedding, threshold=0.6):
    dot_product = np.dot(stored_embedding, new_embedding)
    norm_stored = np.linalg.norm(stored_embedding)
    norm_new = np.linalg.norm(new_embedding)
    similarity = dot_product / (norm_stored * norm_new)
    
    return similarity >= threshold, similarity

# ==============================
# 👁 LIVENESS CHECK
# ==============================
def verify_liveness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    texture = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    if brightness > 30 and texture > 100:
        return True
    return False

# ==============================
# 🏫 CLASSROOM VERIFICATION
# ==============================
def verify_classroom(image):
    if YOLO_MODEL is None:
        return False, "YOLO model missing"
        
    results = YOLO_MODEL(image)
    class_counts = {0: 0} # Person
    
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls == 0:
                class_counts[0] += 1
                
    if class_counts[0] > 0:
        return True
    return False

# ==============================
# 📝 MARK ATTENDANCE (SQL)
# ==============================
def mark_attendance(email, session_code, subject, similarity):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get User ID
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return

    # Get Session ID (Create if not exists for demo, or assume pre-created)
    # For compatibility with QR code which gives session ID string:
    cursor.execute("SELECT id FROM sessions WHERE code = ?", (session_code,))
    session = cursor.fetchone()
    
    if not session:
        # Auto-create session if it doesn't exist (for demo continuity)
        cursor.execute(
            "INSERT INTO sessions (subject, code, start_time, end_time) VALUES (?, ?, ?, ?)",
            (subject, session_code, datetime.now(), datetime.now())
        )
        conn.commit()
        session_id = cursor.lastrowid
    else:
        session_id = session["id"]

    cursor.execute(
        "INSERT INTO attendance (user_id, session_id, status, similarity_score) VALUES (?, ?, ?, ?)",
        (user["id"], session_id, "Present", float(similarity))
    )
    conn.commit()
    conn.close()
