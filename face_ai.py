# face_ai.py
import numpy as np
import cv2
import pickle
import os
from typing import Optional, Tuple

# Optional: Use MTCNN for better face detection (recommended)
try:
    from mtcnn import MTCNN
    HAS_MTCNN = True
except ImportError:
    HAS_MTCNN = False
    print("⚠️ Warning: mtcnn not installed. Falling back to face_recognition (less robust).")

try:
    from face_recognition import face_locations
    HAS_FACE_RECOG = True
except ImportError:
    HAS_FACE_RECOG = False
    print("⚠️ Warning: face_recognition not installed. Face detection will be disabled.")

try:
    from keras.models import load_model
    HAS_KERAS = True
except ImportError:
    HAS_KERAS = False
    print("❌ Critical: keras not installed. FaceNet embedding cannot work.")

# --- Configuration ---
EMBEDDINGS_FILE = "data/embeddings.pkl"
FACENET_MODEL_PATH = "models/facenet_keras.h5"

# Global model holder (thread-safe lazy init)
_facenet_model = None
_mtcnn_detector = None

def _load_facenet():
    global _facenet_model
    if _facenet_model is None:
        if not os.path.exists(FACENET_MODEL_PATH):
            raise FileNotFoundError(
                f"FaceNet model not found at: {FACENET_MODEL_PATH}\n"
                "Please download facenet_keras.h5 and place it in 'models/' folder."
            )
        if not HAS_KERAS:
            raise RuntimeError("Keras required for FaceNet. Install with: pip install keras tensorflow")
        _facenet_model = load_model(FACENET_MODEL_PATH)
    return _facenet_model

def _load_mtcnn():
    global _mtcnn_detector
    if _mtcnn_detector is None and HAS_MTCNN:
        _mtcnn_detector = MTCNN()
    return _mtcnn_detector

def preprocess_face(img_array: np.ndarray, target_size: Tuple[int, int] = (160, 160)) -> np.ndarray:
    """
    Preprocess face image for FaceNet: resize → normalize
    Input: BGR or RGB (will convert to RGB internally if needed)
    Output: (1, 160, 160, 3) float32 tensor
    """
    if img_array.dtype != np.uint8:
        img_array = (img_array * 255).astype(np.uint8)
    
    # Ensure 3 channels
    if img_array.shape[-1] == 1:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
    elif img_array.shape[-1] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
    
    # Resize
    img = cv2.resize(img_array, target_size)
    img = img.astype('float32')
    
    # Standardize (zero-center & unit-variance)
    mean, std = img.mean(), img.std()
    img = (img - mean) / (std + 1e-7)  # avoid div-by-zero
    return np.expand_dims(img, axis=0)

def detect_face_with_mtcnn(rgb_img: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Returns (x, y, w, h) of largest face, or None"""
    if not HAS_MTCNN:
        return None
    try:
        detector = _load_mtcnn()
        faces = detector.detect_faces(rgb_img)
        if not faces:
            return None
        # Pick largest face by area
        best = max(faces, key=lambda f: f['box'][2] * f['box'][3])
        x, y, w, h = best['box']
        return int(x), int(y), int(w), int(h)
    except Exception as e:
        print("MTCNN error:", e)
        return None

def detect_face_with_facerect(rgb_img: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Fallback using face_recognition"""
    if not HAS_FACE_RECOG:
        return None
    try:
        locs = face_locations(rgb_img)
        if not locs:
            return None
        top, right, bottom, left = locs[0]
        return left, top, right - left, bottom - top
    except Exception as e:
        print("face_recognition error:", e)
        return None

def extract_embedding(face_img: np.ndarray) -> Optional[np.ndarray]:
    """
    Extract 128-dim face embedding using FaceNet.
    Returns: np.ndarray of shape (128,) or None on failure.
    """
    try:
        if face_img is None or face_img.size == 0:
            return None

        # Convert to RGB if BGR
        if face_img.shape[-1] == 3 and face_img.dtype == np.uint8:
            if len(face_img.shape) == 3 and face_img.shape[2] == 3:
                # Assume BGR (OpenCV default)
                rgb_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            else:
                rgb_img = face_img
        else:
            rgb_img = face_img

        # Detect face region (if input is full frame)
        if rgb_img.shape[0] > 200 or rgb_img.shape[1] > 200:
            # Full image → detect face first
            box = detect_face_with_mtcnn(rgb_img) or detect_face_with_facerect(rgb_img)
            if box is None:
                print("❌ No face detected in image")
                return None
            x, y, w, h = box
            # Add margin (10%)
            pad_w, pad_h = int(w * 0.1), int(h * 0.1)
            x = max(0, x - pad_w)
            y = max(0, y - pad_h)
            w = min(rgb_img.shape[1] - x, w + 2 * pad_w)
            h = min(rgb_img.shape[0] - y, h + 2 * pad_h)
            face_roi = rgb_img[y:y+h, x:x+w]
        else:
            # Already cropped face
            face_roi = rgb_img

        # Preprocess & embed
        face_input = preprocess_face(face_roi)
        model = _load_facenet()
        embedding = model.predict(face_input, verbose=0)[0]
        
        # Ensure float32 & 1D
        embedding = np.asarray(embedding, dtype=np.float32).flatten()
        return embedding

    except Exception as e:
        print("Embedding extraction failed:", str(e))
        return None

def save_embedding(email: str, embedding: np.ndarray) -> bool:
    """Save embedding to disk"""
    try:
        if not os.path.exists(EMBEDDINGS_FILE):
            embeddings = {}
        else:
            with open(EMBEDDINGS_FILE, 'rb') as f:
                embeddings = pickle.load(f)
        
        embeddings[email] = embedding.astype(np.float32)
        
        with open(EMBEDDINGS_FILE, 'wb') as f:
            pickle.dump(embeddings, f)
        return True
    except Exception as e:
        print("Failed to save embedding:", e)
        return False

def load_embeddings() -> dict:
    """Load all embeddings"""
    if not os.path.exists(EMBEDDINGS_FILE):
        return {}
    try:
        with open(EMBEDDINGS_FILE, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print("Failed to load embeddings:", e)
        return {}

def compare_embeddings(embed1: Optional[np.ndarray], embed2: Optional[np.ndarray], threshold: float = 0.6) -> float:
    """Cosine similarity between two embeddings (0–1)"""
    if embed1 is None or embed2 is None:
        return 0.0
    try:
        embed1 = np.asarray(embed1, dtype=np.float32).flatten()
        embed2 = np.asarray(embed2, dtype=np.float32).flatten()
        if embed1.size != 128 or embed2.size != 128:
            print(f"⚠️ Embedding size mismatch: {embed1.size} vs {embed2.size}")
            return 0.0
        dot = np.dot(embed1, embed2)
        norm = np.linalg.norm(embed1) * np.linalg.norm(embed2)
        sim = dot / norm if norm > 1e-8 else 0.0
        return float(sim)
    except Exception as e:
        print("Similarity calc error:", e)
        return 0.0