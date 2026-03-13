import streamlit as st
import cv2
import numpy as np
import json
import os
from datetime import datetime
import pandas as pd
import hashlib
import plotly.express as px
import plotly.graph_objects as go
import page_styling
import pickle
try:
    import mediapipe as mp
    mp_face = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
except (ImportError, AttributeError):
    mp_face = None
    mp_drawing = None
from scipy.spatial.distance import cosine
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions

# =========================
# SETUP & CONFIG
# =========================
st.set_page_config(page_title="Smart AI Attendance", layout="wide", page_icon="🎓")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.csv")

def init_data_file(file_path, cols):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        pd.DataFrame(columns=cols).to_csv(file_path, index=False)

init_data_file(USERS_FILE, ["email", "name", "student_id", "section", "password_hash"])
init_data_file(ATTENDANCE_FILE, ["email", "session_id", "subject", "timestamp", "similarity_score", "status"])

def safe_read_csv(file_path, default_cols):
    try:
        return pd.read_csv(file_path)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return pd.DataFrame(columns=default_cols)

# =========================
# GLOBAL CSS — BASE44 REPLICATION
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Full page background */
.stApp { background: #F9FAFB !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }

/* Max-width content area */
.block-container {
    max-width: 1000px !important;
    padding-top: 0rem !important;
    padding-bottom: 3rem !important;
}

/* ===== STICKY NAV BAR ===== */
.top-nav {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: white;
    border-bottom: 1px solid #E5E7EB;
    padding: 0.75rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 -100% 1.5rem;
    padding: 0.75rem calc(100% - 500px + 2rem);
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
/* Adjusting navbar for wider screen */
@media (max-width: 1000px) {
    .top-nav { padding: 0.75rem 1rem; margin: 0 0 1.5rem; }
}

.nav-logo {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.1rem;
    font-weight: 700;
    color: #111827;
}
.nav-logo-icon {
    background: #2563EB;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}
.nav-links { display: flex; align-items: center; gap: 1.5rem; }
.nav-link {
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    color: #4B5563;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 0.6rem;
    border-radius: 6px;
    transition: all 0.2s;
}
.nav-link:hover { background: #F3F4F6; }
.nav-link.active { color: #2563EB; font-weight: 600; }
.nav-logout { color: #EF4444 !important; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 0.3rem; }

/* ===== HERO PROFILE CARD ===== */
.hero-card {
    background: #2563EB;
    border-radius: 24px;
    padding: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
    color: white;
    position: relative;
    overflow: hidden;
}
.profile-section { display: flex; align-items: center; gap: 1.5rem; }
.profile-img {
    width: 80px; height: 80px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem; border: 3px solid rgba(255,255,255,0.3);
}
.profile-text h2 { font-size: 2rem; font-weight: 800; margin: 0; color: white; }
.profile-text p { color: rgba(255,255,255,0.8); font-size: 0.95rem; margin: 0.2rem 0 0; }
.trend-widget {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 16px;
    padding: 1rem 1.5rem;
    text-align: center;
}
.trend-widget small { font-size: 0.8rem; color: rgba(255,255,255,0.8); display: block; margin-bottom: 0.2rem; }
.trend-widget strong { font-size: 1.8rem; font-weight: 800; }

/* ===== STATS GRID ===== */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.25rem;
    margin-bottom: 2.5rem;
}
.stat-item {
    background: white;
    border-radius: 18px;
    padding: 1.5rem;
    border: 1px solid #F3F4F6;
    display: flex;
    flex-direction: column;
}
.stat-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
.stat-header span { color: #6B7280; font-size: 0.85rem; font-weight: 500; }
.stat-icon {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.stat-val { font-size: 1.8rem; font-weight: 800; color: #111827; }
.stat-sub { color: #9CA3AF; font-size: 0.75rem; margin-top: 0.4rem; }

/* Colors */
.bg-blue { background: #EFF6FF; color: #3B82F6; }
.bg-green { background: #ECFDF5; color: #10B981; }
.bg-purple { background: #F5F3FF; color: #8B5CF6; }
.bg-orange { background: #FFF7ED; color: #F97316; }

/* ===== QUICK ACTIONS ===== */
.actions-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
    margin-bottom: 2.5rem;
}
.action-item {
    background: white;
    border-radius: 18px;
    padding: 1.5rem;
    border: 1px solid #E5E7EB;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    transition: all 0.2s;
    cursor: pointer;
}
.action-item:hover { border-color: #2563EB; box-shadow: 0 10px 15px -3px rgba(37,99,235,0.1); }
.action-ico {
    width: 54px; height: 54px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
}
.act-blue { background: #2563EB; color: white; }
.act-green { background: #10B981; color: white; }
.action-info h4 { font-size: 1rem; font-weight: 700; color: #111827; margin: 0 0 0.2rem; }
.action-info p { font-size: 0.85rem; color: #6B7280; margin: 0; }
.action-item i { margin-left: auto; color: #D1D5DB; font-size: 1.2rem; }

/* ===== RECENT ATTENDANCE ===== */
.section-head { font-size: 1.1rem; font-weight: 700; color: #111827; margin-bottom: 1rem; }
.list-container { background: transparent; display: flex; flex-direction: column; gap: 0.75rem; }
.list-row {
    background: white;
    padding: 1rem 1.5rem;
    border-radius: 16px;
    border: 1px solid #F3F4F6;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.list-ico {
    width: 40px; height: 40px;
    background: #ECFDF5;
    color: #10B981;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
}
.list-details { flex: 1; }
.list-details h5 { font-size: 0.95rem; font-weight: 600; color: #111827; margin: 0; }
.list-details small { color: #6B7280; font-size: 0.8rem; }
.list-right { text-align: right; }
.badge-p {
    background: #ECFDF5; color: #059669;
    padding: 0.25rem 0.75rem; border-radius: 20px;
    font-size: 0.75rem; font-weight: 700;
}
.match-p { color: #9CA3AF; font-size: 0.75rem; margin-top: 0.25rem; }

/* ===== SCANNER UI ===== */
.scanner-frame {
    width: 100%; max-width: 500px;
    aspect-ratio: 1;
    background: #0F172A;
    border-radius: 32px;
    margin: 2rem auto;
    position: relative;
    overflow: hidden;
    display: flex; align-items: center; justify-content: center;
}
.scan-line {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 3px;
    background: #3B82F6;
    box-shadow: 0 0 15px #3B82F6;
    animation: scan 2s linear infinite;
    z-index: 10;
}
@keyframes scan {
    0% { top: 0; }
    100% { top: 100%; }
}
.corner {
    position: absolute; width: 40px; height: 40px;
    border: 4px solid #3B82F6;
}
.tl { top: 40px; left: 40px; border-right: 0; border-bottom: 0; border-top-left-radius: 12px; }
.tr { top: 40px; right: 40px; border-left: 0; border-bottom: 0; border-top-right-radius: 12px; }
.bl { bottom: 40px; left: 40px; border-right: 0; border-top: 0; border-bottom-left-radius: 12px; }
.br { bottom: 40px; right: 40px; border-left: 0; border-top: 0; border-bottom-right-radius: 12px; }

/* ===== BUTTONS ===== */
.stButton > button {
    background: #2563EB !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.6rem 1.25rem !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37,99,235,0.2); }
</style>
""", unsafe_allow_html=True)

# =========================
# UTILITIES
# =========================
# AI UTILITIES
# =========================
@st.cache_resource
def load_face_model():
    # Lazy load for performance
    try:
        from tensorflow.keras.models import load_model
        model_path = os.path.join("models", "facenet_keras.h5")
        if os.path.exists(model_path):
            model = load_model(model_path)
            # Dummy predict to initialize
            model.predict(np.zeros((1, 160, 160, 3)))
            return model
    except Exception as e:
        print(f"Error loading AI model: {e}")
    return None

# mp_face and mp_drawing are now imported at the top level

def get_face_embedding(image_np, model):
    if model is None: return None
    try:
        # Preprocess: resize to 160x160, normalize
        face_img = cv2.resize(image_np, (160, 160))
        face_img = face_img.astype('float32')
        mean, std = face_img.mean(), face_img.std()
        face_img = (face_img - mean) / std
        samples = np.expand_dims(face_img, axis=0)
        yhat = model.predict(samples)
        return yhat[0]
    except:
        return None

@st.cache_resource
def load_object_model():
    try:
        return MobileNetV2(weights='imagenet')
    except Exception as e:
        st.error(f"Error loading Object Detection model: {e}")
    return None

def verify_liveness(image_np):
    # Basic check for person presence and movement (simulated)
    return True 

def detect_classroom_objects(image_np):
    model = load_object_model()
    if model is None: return ["unknown"]
    
    try:
        # Preprocess for MobileNetV2
        img = cv2.resize(image_np, (224, 224))
        x = np.expand_dims(img, axis=0)
        x = preprocess_input(x)
        
        preds = model.predict(x)
        decoded = decode_predictions(preds, top=10)[0]
        
        # Classroom keywords in ImageNet
        keywords = ["desk", "computer", "keyboard", "monitor", "notebook", "projector", "chair", "table", "screen", "person"]
        detected = []
        for _, label, score in decoded:
            if score > 0.1: # Confidence threshold
                # Check if label contains any keyword
                if any(kw in label.lower() for kw in keywords):
                    detected.append(label.replace("_", " "))
        
        return list(set(detected)) if detected else ["background"]
    except Exception as e:
        return [f"Error: {str(e)}"]

# =========================
# DATA UTILITIES
# =========================
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "embeddings.pkl")

def save_embedding(email, embedding):
    data = {}
    if os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, "rb") as f:
            data = pickle.load(f)
    data[email] = embedding
    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump(data, f)

def get_embedding(email):
    if os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, "rb") as f:
            data = pickle.load(f)
            return data.get(email)
    return None

# =========================
def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_users():
    return safe_read_csv(USERS_FILE, ["email", "name", "student_id", "section", "password_hash"])

def save_user(name, sid, email, section, pwd):
    df = load_users()
    if email in df["email"].values:
        return False
    df.loc[len(df)] = {"email": email, "name": name, "student_id": sid, "section": section, "password_hash": hash_pwd(pwd)}
    df.to_csv(USERS_FILE, index=False)
    return True

def get_stats(email):
    df = safe_read_csv(ATTENDANCE_FILE, ["email", "session_id", "subject", "timestamp", "similarity_score", "status"])
    df_user = df[df["email"] == email]
    if df_user.empty:
        return {"total": 0, "month": 0, "rate": 0, "monthly_rate": 0}
    
    now = datetime.now()
    df_user["timestamp"] = pd.to_datetime(df_user["timestamp"])
    this_month = df_user[(df_user["timestamp"].dt.month == now.month) & (df_user["timestamp"].dt.year == now.year)]
    
    total = len(df_user)
    present = len(df_user[df_user["status"] == "Present"])
    month_total = len(this_month)
    month_present = len(this_month[this_month["status"] == "Present"])
    
    return {
        "total": total,
        "month": month_total,
        "rate": round(present / total * 100) if total > 0 else 0,
        "monthly_rate": round(month_present / month_total * 100) if month_total > 0 else 0
    }

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# =========================
# COMPONENTS
# =========================
def render_nav(active="dashboard"):
    # Apply custom style for the navbar buttons to make them look like links
    st.markdown("""
        <style>
        .nav-btn button {
            background: transparent !important;
            color: #4B5563 !important;
            border: none !important;
            padding: 0.4rem 0.6rem !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            box-shadow: none !important;
            width: auto !important;
        }
        .nav-btn-active button {
            color: #2563EB !important;
            font-weight: 700 !important;
        }
        .nav-btn-logout button {
            color: #EF4444 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Outer container for sticky look
    st.markdown('<div class="top-nav-placeholder"></div>', unsafe_allow_html=True)
    
    # Navbar using Columns
    nc1, nc2, nc3, nc4, nc5, nc6 = st.columns([3, 1, 1.2, 1, 1, 1])
    
    with nc1:
        st.markdown("""
            <div class="nav-logo">
                <div class="nav-logo-icon">👤</div>
                Smart AI Attendance
            </div>
        """, unsafe_allow_html=True)
    
    with nc3:
        if st.button("🏠 Dashboard", key="nav_dash", help="Go to Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
    with nc4:
        if st.button("🔲 Attendance", key="nav_mark", help="Mark Attendance", use_container_width=True):
            st.session_state.current_page = "scan"
            st.rerun()
    with nc5:
        if st.button("📊 History", key="nav_hist", help="View History", use_container_width=True):
            st.session_state.current_page = "history"
            st.rerun()
    with nc6:
        if st.button("Enroll", key="nav_enroll", help="Face Enrollment", use_container_width=True):
            st.session_state.current_page = "enroll"
            st.rerun()
    
    st.markdown('<hr style="margin: 0.5rem 0 2rem; border-color: #E5E7EB;">', unsafe_allow_html=True)

def render_hero(name, sid, section, month_val):
    initial = name[0].upper() if name else "S"
    st.markdown(f"""
    <div class="hero-card">
        <div class="profile-section">
            <div class="profile-img">{initial}</div>
            <div class="profile-text">
                <p>Welcome back,</p>
                <h2>{name}</h2>
                <p>{sid} • {section}</p>
            </div>
        </div>
        <div class="trend-widget">
            <small>📈 This Month</small>
            <strong>{month_val}%</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_stats(stats):
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-item">
            <div class="stat-header"><span>Total Classes</span> <div class="stat-icon bg-blue">📅</div></div>
            <div class="stat-val">{stats['total']}</div>
            <div class="stat-sub">All time</div>
        </div>
        <div class="stat-item">
            <div class="stat-header"><span>This Month</span> <div class="stat-icon bg-green">📅</div></div>
            <div class="stat-val">{stats['month']}</div>
            <div class="stat-sub">Classes attended</div>
        </div>
        <div class="stat-item">
            <div class="stat-header"><span>Overall Rate</span> <div class="stat-icon bg-purple">↗</div></div>
            <div class="stat-val">{stats['rate']}%</div>
            <div class="stat-sub">Attendance</div>
        </div>
        <div class="stat-item">
            <div class="stat-header"><span>Monthly Rate</span> <div class="stat-icon bg-orange">↗</div></div>
            <div class="stat-val">{stats['monthly_rate']}%</div>
            <div class="stat-sub">This month</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recent(email):
    df = safe_read_csv(ATTENDANCE_FILE, ["email", "session_id", "subject", "timestamp", "similarity_score", "status"])
    df_user = df[df["email"] == email].copy()
    st.markdown('<div class="section-head">Recent Attendance</div>', unsafe_allow_html=True)
    if df_user.empty:
        st.info("No attendance records found.")
        return
    
    df_user["timestamp"] = pd.to_datetime(df_user["timestamp"])
    df_user = df_user.sort_values("timestamp", ascending=False).head(5)
    
    rows = ""
    for _, r in df_user.iterrows():
        date = r["timestamp"].strftime("%a, %b %d")
        match = f"{r['similarity_score']*100:.0f}% match"
        rows += f"""
        <div class="list-row">
            <div class="list-ico">📅</div>
            <div class="list-details">
                <h5>{r['subject']}</h5>
                <small>{date}</small>
            </div>
            <div class="list-right">
                <span class="badge-p">Present</span>
                <div class="match-p">{match}</div>
            </div>
        </div>
        """
    st.markdown(f'<div class="list-container">{rows}</div>', unsafe_allow_html=True)

# =========================
# PAGES
# =========================
if "current_page" not in st.session_state: st.session_state.current_page = "login"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# Global Styling for all pages
page_styling.set_page_background(st.session_state.current_page)

# LOGIN PAGE REPLICATION
if not st.session_state.logged_in:
    st.markdown("""
    <div style="max-width:450px; margin: 4rem auto; background:white; padding:3rem; border-radius:24px; border:1px solid #E5E7EB; box-shadow:0 10px 15px -3px rgba(0,0,0,0.05); text-align:center;">
        <div style="width:64px; height:64px; background:#EFF6FF; border-radius:16px; margin:0 auto 1.5rem; display:flex; align-items:center; justify-content:center; font-size:1.8rem;">🎓</div>
        <h1 style="font-size:1.75rem; font-weight:800; color:#111827; margin-bottom:0.5rem;">Welcome to ePortal</h1>
        <p style="color:#6B7280; margin-bottom:2rem;">Sign in to continue</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        _, col, _ = st.columns([1, 2, 1])
        with col:
            email_val = st.text_input("Email", placeholder="you@university.edu", key="login_email")
            pwd_val = st.text_input("Password", type="password", placeholder="••••••••", key="login_pwd")
            if st.button("Sign in", use_container_width=True, key="login_btn_submit"):
                if email_val and pwd_val:
                    users = load_users()
                    user = users[users["email"] == email_val]
                    if not user.empty and hash_pwd(pwd_val) == user.iloc[0]["password_hash"]:
                        st.session_state.logged_in = True
                        st.session_state.email = email_val
                        st.session_state.name = user.iloc[0]["name"]
                        st.session_state.sid = user.iloc[0]["student_id"]
                        st.session_state.section = user.iloc[0]["section"]
                        st.session_state.current_page = "dashboard" # REDIRECT
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.error("Please enter email and password")
            
            st.markdown('<div style="text-align:center; color:#6B7280; font-size:0.9rem; margin-top:0.5rem;">Need an account?</div>', unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True, key="go_reg"):
                st.session_state.current_page = "register"
                st.rerun()

# REGISTER PAGE
elif st.session_state.current_page == "register":
    st.markdown("""
    <div style="max-width:450px; margin: 2rem auto; background:white; padding:2.5rem; border-radius:24px; border:1px solid #E5E7EB; box-shadow:0 10px 15px -3px rgba(0,0,0,0.05); text-align:center;">
        <div style="width:56px; height:56px; background:#EFF6FF; border-radius:14px; margin:0 auto 1.25rem; display:flex; align-items:center; justify-content:center; font-size:1.5rem;">👤</div>
        <h1 style="font-size:1.5rem; font-weight:800; color:#111827; margin-bottom:0.4rem;">Create Account</h1>
        <p style="color:#6B7280; margin-bottom:1.5rem;">Join ePortal today</p>
    </div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        reg_name = st.text_input("Full Name", placeholder="Sashidhar Reddy")
        reg_sid = st.text_input("Student ID", placeholder="201")
        reg_email = st.text_input("Email", placeholder="sashi@college.edu")
        reg_section = st.text_input("Class / Section", placeholder="AIML/SEC-B")
        reg_pwd = st.text_input("Password", type="password", placeholder="••••••••")
        reg_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
        
        if st.button("Create Account", use_container_width=True, key="reg_submit"):
            if all([reg_name, reg_sid, reg_email, reg_section, reg_pwd, reg_confirm]):
                if reg_pwd == reg_confirm:
                    if save_user(reg_name, reg_sid, reg_email, reg_section, reg_pwd):
                        st.success("✅ Account created! Please sign in.")
                        st.session_state.current_page = "login"
                        st.rerun()
                    else:
                        st.error("❌ Email already registered.")
                else:
                    st.error("❌ Passwords do not match.")
            else:
                st.error("❌ Please fill in all fields.")
        
        if st.button("Back to Login", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()

# DASHBOARD
elif st.session_state.current_page == "dashboard":
    render_nav("dashboard")
    stats = get_stats(st.session_state.email)
    render_hero(st.session_state.name, st.session_state.sid, st.session_state.section, stats["monthly_rate"])
    render_stats(stats)
    
    st.markdown('<div class="section-head">Quick Actions</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="action-item">
            <div class="action-ico act-blue">🔲</div>
            <div class="action-info">
                <h4>Mark Attendance</h4>
                <p>Scan session QR code</p>
            </div>
            <i>›</i>
        </div>""", unsafe_allow_html=True)
        if st.button("Open Scanner →", key="btn_scan", use_container_width=True):
            st.session_state.current_page = "scan"
            st.rerun()
    with c2:
        st.markdown("""
        <div class="action-item">
            <div class="action-ico act-green">📊</div>
            <div class="action-info">
                <h4>Attendance History</h4>
                <p>View complete history</p>
            </div>
            <i>›</i>
        </div>""", unsafe_allow_html=True)
        if st.button("View Records →", key="btn_hist", use_container_width=True):
            st.session_state.current_page = "history"
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    render_recent(st.session_state.email)
    
    if st.button("Logout", key="main_logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_page = "login"
        st.rerun()

# FACE ENROLLMENT PAGE
elif st.session_state.current_page == "enroll":
    render_nav("enroll")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"): navigate_to("dashboard")
    
    st.markdown("""
    <div style="text-align:center; margin-bottom:2rem;">
        <div style="width:64px; height:64px; background:#EEF2FF; border-radius:50%; margin:0 auto 1.5rem; display:flex; align-items:center; justify-content:center; font-size:1.8rem;">🎭</div>
        <h1 style="font-size:1.8rem; font-weight:800; color:#111827;">Face Enrollment</h1>
        <p style="color:#6B7280;">Capture your face to enable biometric verification</p>
    </div>
    """, unsafe_allow_html=True)
    
    model = load_face_model()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.info("💡 Position your face clearly in the frame with good lighting.")
        img_file = st.camera_input("Capture Enrollment Photo")
        
        if img_file:
            # Verify if embedding already exists
            existing = get_embedding(st.session_state.email)
            if existing is not None:
                st.warning("⚠️ You already have a face enrolled. Capturing again will update your biometrics.")
            
            if st.button("Save Biometrics", use_container_width=True, type="primary"):
                # Process image
                file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                with st.spinner("Extracting features..."):
                    embedding = get_face_embedding(img_rgb, model)
                    if embedding is not None:
                        save_embedding(st.session_state.email, embedding)
                        st.success("✅ Face Enrollment Successful!")
                        st.balloons()
                    else:
                        st.error("❌ Could not detect face clearly. Please try again.")

    with col2:
        st.markdown("""
        <div style="background:white; padding:2rem; border-radius:16px; border:1px solid #E5E7EB;">
            <h4 style="margin-top:0;">Why enroll?</h4>
            <ul style="color:#4B5563; padding-left:1.5rem;">
                <li>Prevents proxy attendance (marking for friends)</li>
                <li>Ensures liveness and physical presence</li>
                <li>Secure encrypted feature storage</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# SCANNER PAGE (3-STEP FLOW)
elif st.session_state.current_page == "scan":
    render_nav("mark")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"): 
        st.session_state.pop("scan_step", None)
        navigate_to("dashboard")
    
    if "scan_step" not in st.session_state:
        st.session_state.scan_step = 1 # 1: QR, 2: Selfie, 3: Classroom
    
    # Progress Bar
    step = st.session_state.scan_step
    cols = st.columns(3)
    steps_info = ["1. QR Scan", "2. Selfie", "3. Classroom"]
    for i, s in enumerate(steps_info):
        with cols[i]:
            active = i + 1 == step
            done = i + 1 < step
            color = "#2563EB" if active else ("#10B981" if done else "#9CA3AF")
            st.markdown(f'<div style="text-align:center; border-bottom: 3px solid {color}; padding-bottom: 5px; color:{color}; font-weight:600;">{s}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # STEP 1: QR CODE
    if step == 1:
        st.markdown("""
        <div style="text-align:center; margin-bottom:2rem;">
            <h1 style="font-size:1.8rem; font-weight:800; color:#111827;">Scan Session QR</h1>
            <p style="color:#6B7280;">Scan the QR code displayed in your classroom</p>
        </div>
        """, unsafe_allow_html=True)
        
        qr_img = st.camera_input("Scan QR Code", key="cam_qr")
        if qr_img:
            # Mock success for QR
            st.success("✅ QR Scanned: Advanced Mathematics (SESS_102)")
            if st.button("Proceed to Face Verification"):
                st.session_state.scan_step = 2
                st.rerun()

    # STEP 2: FACE VERIFICATION
    elif step == 2:
        st.markdown("""
        <div style="text-align:center; margin-bottom:2rem;">
            <h1 style="font-size:1.8rem; font-weight:800; color:#111827;">Verify Identity</h1>
            <p style="color:#6B7280;">Take a selfie to verify your identity</p>
        </div>
        """, unsafe_allow_html=True)
        
        enrolled_embedding = get_embedding(st.session_state.email)
        if enrolled_embedding is None:
            st.error("❌ No face enrolled! Please go to the Enrollment page first.")
            if st.button("Go to Enrollment"): navigate_to("enroll")
        else:
            selfie = st.camera_input("Take Selfie", key="cam_face")
            if selfie:
                model = load_face_model()
                file_bytes = np.asarray(bytearray(selfie.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                with st.spinner("Verifying identity..."):
                    live_embedding = get_face_embedding(img_rgb, model)
                    if live_embedding is not None:
                        dist = cosine(enrolled_embedding, live_embedding)
                        similarity = 1 - dist
                        if similarity > 0.7: # Threshold
                            st.success(f"✅ Identity Verified! (Score: {similarity:.2f})")
                            st.session_state.face_score = similarity
                            if st.button("Proceed to Classroom Verification"):
                                st.session_state.scan_step = 3
                                st.rerun()
                        else:
                            st.error(f"❌ Verification Failed. Match score too low: {similarity:.2f}")
                    else:
                        st.error("❌ Could not detect face in selfie.")

    # STEP 3: CLASSROOM CONTEXT
    elif step == 3:
        st.markdown("""
        <div style="text-align:center; margin-bottom:2rem;">
            <h1 style="font-size:1.8rem; font-weight:800; color:#111827;">Verify Location</h1>
            <p style="color:#6B7280;">Capture classroom surroundings (PCs, desks, projectors)</p>
        </div>
        """, unsafe_allow_html=True)
        
        context_img = st.camera_input("Capture Classroom Photo", key="cam_context")
        if context_img:
            with st.spinner("Analyzing surroundings..."):
                file_bytes = np.asarray(bytearray(context_img.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, 1)
                objects = detect_classroom_objects(img)
                
                if any(obj in ["chair", "table", "laptop", "monitor", "person"] for obj in objects):
                    st.success(f"✅ Classroom Verified! Detected: {', '.join(objects)}")
                    if st.button("Finalize Attendance", type="primary"):
                        # Save Attendance
                        df = safe_read_csv(ATTENDANCE_FILE, ["email", "session_id", "subject", "timestamp", "similarity_score", "status"])
                        score = st.session_state.get("face_score", 0.0)
                        df.loc[len(df)] = [st.session_state.email, "SESS_102", "Advanced Mathematics", datetime.now(), score, "Present"]
                        df.to_csv(ATTENDANCE_FILE, index=False)
                        
                        st.session_state.pop("scan_step", None)
                        page_styling.show_success_page("Advanced Mathematics", score)
                        navigate_to("dashboard")
                else:
                    st.error("❌ Could not verify classroom context. Please capture classroom objects.")

# HISTORY PAGE
elif st.session_state.current_page == "history":
    render_nav("history")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"): navigate_to("dashboard")
    
    st.markdown('<h1 style="font-weight:800;">Attendance History</h1>', unsafe_allow_html=True)
    df = pd.read_csv(ATTENDANCE_FILE)
    df_user = df[df["email"] == st.session_state.email].copy()
    
    if df_user.empty:
        st.info("No records yet.")
    else:
        st.dataframe(df_user.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
        
        # Simple Chart
        df_user["timestamp"] = pd.to_datetime(df_user["timestamp"])
        fig = px.line(df_user.sort_values("timestamp"), x="timestamp", y="similarity_score", title="Match Score Trend",
                     color_discrete_sequence=["#2563EB"])
        st.plotly_chart(fig, use_container_width=True)