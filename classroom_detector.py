# classroom_detector.py
from ultralytics import YOLO
import cv2
import numpy as np

# Load YOLOv8n (nano) — fast & suitable for edge devices
MODEL_PATH = "yolov8n.pt"  # or download custom fine-tuned model later
model = YOLO(MODEL_PATH)

# Required classroom objects (COCO class IDs)
CLASS_NAMES = model.names  # {0:'person', 1:'bicycle', ..., 56:'chair', 59:'table', 63:'computer', 64:'tvmonitor'}
REQUIRED_OBJECTS = {
    'chair': 56,
    'table': 59,
    'tvmonitor': 64,      # projector/screen often detected as TV
    'laptop': 67,         # optional
    'book': 73            # optional
}

def detect_classroom_objects(image_array):
    """
    Returns dict: {object_name: count}
    """
    results = model(image_array, verbose=False)
    detections = results[0].boxes
    
    obj_counts = {obj: 0 for obj in REQUIRED_OBJECTS}
    
    for box in detections:
        cls_id = int(box.cls.item())
        conf = float(box.conf.item())
        
        # Map class ID to name
        for name, id_ in REQUIRED_OBJECTS.items():
            if cls_id == id_ and conf > 0.4:  # min confidence
                obj_counts[name] += 1
    
    return obj_counts

def is_valid_classroom(obj_counts, min_chairs=2, min_tables=1):
    """
    Rule-based validation:
    - At least 2 chairs
    - At least 1 table
    - OR at least 1 tvmonitor/projector
    """
    chairs = obj_counts.get('chair', 0)
    tables = obj_counts.get('table', 0)
    screens = obj_counts.get('tvmonitor', 0)
    
    return (chairs >= min_chairs and tables >= min_tables) or (screens >= 1)