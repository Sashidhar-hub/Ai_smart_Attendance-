# qr_py.py
import base64
import json
import datetime

def parse_qr_data(qr_text):
    """
    Expected format: 
    {"session_id": "SESSION-XYZ", "subject": "Advanced Math", "timestamp": "2026-02-09T10:00:00Z", "faculty": "Dr. Smith"}
    OR base64-encoded JSON
    """
    try:
        # Try direct JSON
        data = json.loads(qr_text)
    except json.JSONDecodeError:
        try:
            # Try base64
            decoded = base64.b64decode(qr_text).decode()
            data = json.loads(decoded)
        except:
            return None
    
    # Validate required fields
    required = ["session_id", "subject", "timestamp"]
    if not all(k in data for k in required):
        return None
    
    # Check timestamp validity (within ±15 mins of now)
    qr_time = datetime.datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    now = datetime.datetime.utcnow()
    if abs((now - qr_time).total_seconds()) > 900:  # 15 mins
        return None
    
    return {
        "session_id": data["session_id"],
        "subject": data["subject"],
        "timestamp": qr_time,
        "faculty": data.get("faculty", "Unknown")
    }