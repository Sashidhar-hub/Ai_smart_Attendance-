import os
import csv
import pickle
import hashlib
import numpy as np
import cv2
from datetime import datetime
import streamlit as st

# Suppress TensorFlow/OneDNN warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# AI Libraries (Import inside functions to avoid startup crashes if possible, 
# but for caching we need them at module level or handled gracefully)
try:
    from keras.models import load_model
    from ultralytics import YOLO
except ImportError as e:
    print(f"⚠️ Missing AI dependencies: {e}")

# Using OpenCV Haar Cascade for face detection (no extra dependencies needed)
# Constants
USERS_FILE = "data/users.csv"
EMBEDDINGS_FILE = "data/embeddings.pkl"
ATTENDANCE_FILE = "data/attendance.csv"
MODELS_DIR = "models"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

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
    file_exists = os.path.isfile(USERS_FILE)
    
    with open(USERS_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["name", "student_id", "email", "section", "password"])
        writer.writerow([name, student_id, email, section, hashed_pw])

# ==============================
# 🔑 AUTHENTICATION
# ==============================
def authenticate_user(email, password):
    hashed_pw = hash_password(password)
    if not os.path.exists(USERS_FILE):
        return False, None
        
    with open(USERS_FILE, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["email"] == email and row["password"] == hashed_pw:
                return True, row["name"]
    return False, None

# ==============================
# 🧠 AI MODEL LOADING
# ==============================
@st.cache_resource
def load_models():
    """Load FaceNet and YOLO models, plus OpenCV face detector"""
    try:
        print("🔄 Loading models...")
        
        # Check FaceNet file
        facenet_path = os.path.join(MODELS_DIR, "facenet_keras.h5")
        if not os.path.exists(facenet_path):
             print(f"❌ File not found: {facenet_path}. Please ensure the model file is in the 'models' folder.")
             return None, None, None

        facenet_model = load_model(facenet_path)
        
        # Load OpenCV Haar Cascade face detector (built into OpenCV)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        yolo_model = YOLO("yolov8n.pt")  # Auto-downloads if missing
        
        print("✅ All models loaded successfully!")
        print("   - FaceNet: Loaded")
        print("   - Face Detector: OpenCV Haar Cascade")
        print("   - YOLO: Loaded")
        return facenet_model, face_cascade, yolo_model
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

# Initialize model variables as None - they will be loaded on first use
FACENET_MODEL, DETECTOR, YOLO_MODEL = None, None, None

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
    """Extract 128-d embedding from an image containing a face using FaceNet"""
    global FACENET_MODEL, DETECTOR, YOLO_MODEL
    
    # Load models on first use
    if FACENET_MODEL is None or DETECTOR is None:
        FACENET_MODEL, DETECTOR, YOLO_MODEL = load_models()
    
    if FACENET_MODEL is None:
        print("❌ FaceNet model not loaded")
        return None

    try:
        # Convert BGR -> RGB (OpenCV loads BGR, FaceNet needs RGB)
        rgb_img = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        
        face_roi = None
        
        # Try to detect face with Haar Cascade
        if DETECTOR is not None:
            try:
                gray_img = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
                faces = DETECTOR.detectMultiScale(
                    gray_img,
                    scaleFactor=1.05,  # More sensitive
                    minNeighbors=3,     # Less strict
                    minSize=(20, 20),   # Smaller minimum size
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                if len(faces) > 0:
                    # Select largest face
                    largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                    x, y, w, h = largest_face
                    
                    # Add margin
                    margin = 20
                    x = max(0, x - margin)
                    y = max(0, y - margin)
                    w = min(rgb_img.shape[1] - x, w + 2*margin)
                    h = min(rgb_img.shape[0] - y, h + 2*margin)
                    
                    face_roi = rgb_img[y:y+h, x:x+w]
                    print(f"✅ Face detected at ({x},{y}) size {w}x{h}")
                else:
                    print("⚠️ Haar Cascade didn't detect face, using center crop")
            except Exception as det_error:
                print(f"⚠️ Face detection error: {det_error}, using center crop")
        
        # Fallback: If no face detected, use center crop of image
        if face_roi is None:
            h, w = rgb_img.shape[:2]
            # Take center 70% of image
            crop_size = min(h, w)
            start_y = (h - crop_size) // 2
            start_x = (w - crop_size) // 2
            face_roi = rgb_img[start_y:start_y+crop_size, start_x:start_x+crop_size]
            print(f"📸 Using center crop: {crop_size}x{crop_size}")
        
        # Get embedding from face ROI
        try:
            face_input = preprocess_face(face_roi)
            if face_input is None:
                print("❌ Face preprocessing failed")
                return None
            
            embedding = FACENET_MODEL.predict(face_input, verbose=0)[0]
            print(f"✅ Embedding extracted successfully! Shape: {embedding.shape}, Mean: {embedding.mean():.4f}")
            return embedding
            
        except Exception as pred_error:
            print(f"❌ FaceNet prediction error: {str(pred_error)}")
            import traceback
            traceback.print_exc()
            return None
            
    except Exception as e:
        print(f"❌ Error in extract_embedding: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# ==============================
# 💾 EMBEDDING STORAGE
# ==============================
def save_embedding(email, embedding):
    if os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, "rb") as f:
            try:
                data = pickle.load(f)
            except EOFError:
                data = {}
    else:
        data = {}

    data[email] = embedding

    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump(data, f)

def load_embedding(email):
    if not os.path.exists(EMBEDDINGS_FILE):
        return None
    with open(EMBEDDINGS_FILE, "rb") as f:
        try:
            data = pickle.load(f)
            return data.get(email)
        except:
            return None

# ==============================
# 📏 FACE VERIFICATION
# ==============================
def verify_face(stored_embedding, new_embedding, threshold=0.6):
    """Cosine similarity: 1.0 = exact match, -1.0 = opposite"""
    # Cosine similarity formula: dot(A, B) / (norm(A) * norm(B))
    # FaceNet embeddings are usually normalized, so dot product works.
    dot_product = np.dot(stored_embedding, new_embedding)
    norm_stored = np.linalg.norm(stored_embedding)
    norm_new = np.linalg.norm(new_embedding)
    similarity = dot_product / (norm_stored * norm_new)
    
    return similarity >= threshold, similarity

# ==============================
# 👁 LIVENESS CHECK
# ==============================
def verify_liveness(image):
    """Simple brightness/texture check"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    texture = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Thresholds
    if brightness > 30 and texture > 100:
        return True
    return False

# ==============================
# 🏫 CLASSROOM VERIFICATION
# ==============================
def verify_classroom(image):
    """Detect people/chairs/tables using YOLO"""
    global FACENET_MODEL, DETECTOR, YOLO_MODEL
    
    # Load models on first use
    if YOLO_MODEL is None:
        FACENET_MODEL, DETECTOR, YOLO_MODEL = load_models()
    
    if YOLO_MODEL is None:
        return False, "YOLO model missing"
        
    results = YOLO_MODEL(image)
    
    # COCO Class IDs: 0=person, 56=chair, 67=dining table (desk)
    # We want to see people and furniture
    class_counts = {0: 0, 56: 0, 67: 0}
    
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls in class_counts:
                class_counts[cls] += 1
                
    # Logic: Need at least 1 person AND (chair OR table)
    # Or just stricter: 1 person for now as fallback
    has_person = class_counts[0] > 0
    # has_furniture = (class_counts[56] + class_counts[67]) > 0
    
    if has_person:
        return True
    return False

# ==============================
# 📝 MARK ATTENDANCE
# ==============================
def mark_attendance(email, session_id, subject, similarity):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(ATTENDANCE_FILE)
    
    with open(ATTENDANCE_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["email", "session_id", "subject", "timestamp", "similarity_score", "status"])
        writer.writerow([email, session_id, subject, timestamp, f"{similarity:.3f}", "Present"])

# ==============================
# 👑 ADMIN FUNCTIONS
# ==============================
def get_all_users():
    """Return all registered users as a list of dictionaries"""
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)

def get_all_attendance():
    """Return all attendance records as a pandas DataFrame"""
    import pandas as pd
    if not os.path.exists(ATTENDANCE_FILE):
        return pd.DataFrame(columns=["email", "session_id", "subject", "timestamp", "similarity_score", "status"])
    return pd.read_csv(ATTENDANCE_FILE)
