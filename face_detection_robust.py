"""
Robust Face Detection and Embedding Extraction
This module provides reliable face detection using multiple methods
"""

import cv2
import numpy as np

def detect_face_robust(image):
    """
    Detect face using multiple methods for maximum reliability
    Returns: (x, y, w, h) or None
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = image.shape[:2]
    
    # Method 1: Haar Cascade (fast, good for frontal faces)
    try:
        haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = haar_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20))
        
        if len(faces) > 0:
            # Get largest face
            largest = max(faces, key=lambda f: f[2] * f[3])
            x, y, fw, fh = largest
            
            # Add margin
            margin = 20
            x = max(0, x - margin)
            y = max(0, y - margin)
            fw = min(w - x, fw + 2*margin)
            fh = min(h - y, fh + 2*margin)
            
            print(f"✅ Haar detected face at ({x},{y}) size {fw}x{fh}")
            return (x, y, fw, fh)
    except Exception as e:
        print(f"⚠️ Haar failed: {e}")
    
    # Method 2: LBP Cascade (better for varied lighting)
    try:
        lbp_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
        faces = lbp_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
        
        if len(faces) > 0:
            largest = max(faces, key=lambda f: f[2] * f[3])
            x, y, fw, fh = largest
            
            margin = 20
            x = max(0, x - margin)
            y = max(0, y - margin)
            fw = min(w - x, fw + 2*margin)
            fh = min(h - y, fh + 2*margin)
            
            print(f"✅ LBP detected face at ({x},{y}) size {fw}x{fh}")
            return (x, y, fw, fh)
    except Exception as e:
        print(f"⚠️ LBP failed: {e}")
    
    # Method 3: Profile face detector (for side angles)
    try:
        profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        faces = profile_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
        
        if len(faces) > 0:
            largest = max(faces, key=lambda f: f[2] * f[3])
            x, y, fw, fh = largest
            
            margin = 20
            x = max(0, x - margin)
            y = max(0, y - margin)
            fw = min(w - x, fw + 2*margin)
            fh = min(h - y, fh + 2*margin)
            
            print(f"✅ Profile detector found face at ({x},{y}) size {fw}x{fh}")
            return (x, y, fw, fh)
    except Exception as e:
        print(f"⚠️ Profile detector failed: {e}")
    
    # Fallback: Return center crop coordinates
    print("⚠️ All detectors failed, using center crop")
    crop_size = min(h, w)
    start_y = (h - crop_size) // 2
    start_x = (w - crop_size) // 2
    return (start_x, start_y, crop_size, crop_size)


def extract_face_roi(image):
    """
    Extract face region from image using robust detection
    Returns: face_roi (RGB image) or None
    """
    try:
        # Convert to RGB
        rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect face
        face_coords = detect_face_robust(image)
        
        if face_coords:
            x, y, w, h = face_coords
            face_roi = rgb_img[y:y+h, x:x+w]
            
            # Validate face ROI
            if face_roi.size == 0:
                print("❌ Face ROI is empty")
                return None
            
            print(f"✅ Extracted face ROI: {w}x{h}")
            return face_roi
        
        return None
        
    except Exception as e:
        print(f"❌ Error extracting face ROI: {e}")
        import traceback
        traceback.print_exc()
        return None
