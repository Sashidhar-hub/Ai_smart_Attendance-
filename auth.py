# auth.py
import pandas as pd
import hashlib
import os

USERS_FILE = "data/users.csv"

def init_users_db():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=["email", "name", "student_id", "section", "password_hash"])
        df.to_csv(USERS_FILE, index=False)

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def register_user(email, name, student_id, section, password):
    init_users_db()
    df = pd.read_csv(USERS_FILE)
    if email in df["email"].values:
        return False, "Email already registered"
    
    new_row = {
        "email": email,
        "name": name,
        "student_id": student_id,
        "section": section,
        "password_hash": hash_password(password)
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)
    return True, "Registration successful"

def verify_login(email, password):
    init_users_db()
    df = pd.read_csv(USERS_FILE)
    user = df[df["email"] == email]
    if user.empty:
        return False, None
    stored_hash = user.iloc[0]["password_hash"]
    if hash_password(password) == stored_hash:
        return True, user.iloc[0].to_dict()
    return False, None