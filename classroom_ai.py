# classroom_ai.py
import cv2
import numpy as np

def is_classroom_scene(image_array):
    """
    Heuristic-based classroom detection:
    - Presence of whiteboard/blackboard (large vertical rectangle, light/dark uniform)
    - Desks/chairs (horizontal lines, repeating patterns)
    - Windows (rectangular shapes with high contrast)
    """
    height, width = image_array.shape[:2]
    if width < 640 or height < 480:
        return False

    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    
    # Edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Hough Line Transform for desks/windows
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
    
    horizontal_lines = 0
    vertical_lines = 0
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y2 - y1) < 10:  # horizontal
                horizontal_lines += 1
            if abs(x2 - x1) < 10:  # vertical
                vertical_lines += 1
    
    # Classroom heuristic: many horizontal + vertical lines
    return horizontal_lines > 5 and vertical_lines > 3