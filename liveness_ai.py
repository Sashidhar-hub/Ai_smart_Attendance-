# liveness_ai.py
import cv2
import numpy as np
from scipy.spatial.distance import pdist, squareform

def detect_blink(landmarks, eye_indices):
    """Simple blink detection using eye aspect ratio (EAR)"""
    left_eye = landmarks[eye_indices[0]:eye_indices[1]]
    right_eye = landmarks[eye_indices[2]:eye_indices[3]]
    
    def eye_aspect_ratio(eye):
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        return (A + B) / (2.0 * C)
    
    ear_left = eye_aspect_ratio(left_eye)
    ear_right = eye_aspect_ratio(right_eye)
    ear_avg = (ear_left + ear_right) / 2.0
    return ear_avg < 0.25  # blink threshold

def is_live_image(image_array, min_brightness=40, min_texture=80):
    """Basic liveness via brightness + texture variance"""
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return brightness > min_brightness and laplacian_var > min_texture

def check_head_pose(landmarks):
    """Rough head pose estimation using nose/mouth/eye geometry"""
    # Simplified: check if face is frontal (not profile)
    nose = landmarks[30]
    left_eye = landmarks[36]
    right_eye = landmarks[45]
    mouth_left = landmarks[48]
    mouth_right = landmarks[54]
    
    # Horizontal symmetry check
    eye_center_x = (left_eye[0] + right_eye[0]) / 2
    nose_diff = abs(nose[0] - eye_center_x)
    mouth_center_x = (mouth_left[0] + mouth_right[0]) / 2
    mouth_nose_diff = abs(nose[0] - mouth_center_x)
    
    return nose_diff < 20 and mouth_nose_diff < 25  # tolerant thresholds