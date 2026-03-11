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
from io import BytesIO
import page_styling

# =========================
# SETUP & CONFIG
# =========================
st.set_page_config(page_title="ePortal", layout="wide", page_icon="🎓")

# Initialize data directories
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.csv")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.csv")
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "embeddings.pkl")

# Initialize CSV files
if not os.path.exists(USERS_FILE):
    df = pd.DataFrame(columns=["email", "name", "student_id", "section", "password_hash"])
    df.to_csv(USERS_FILE, index=False)

if not os.path.exists(ATTENDANCE_FILE):
    df = pd.DataFrame(columns=["email", "session_id", "subject", "timestamp", "similarity_score", "status"])
    df.to_csv(ATTENDANCE_FILE, index=False)

if not os.path.exists(EMBEDDINGS_FILE):
    with open(EMBEDDINGS_FILE, "wb") as f:
        import pickle
        pickle.dump({}, f)

# =========================
# UTILITY FUNCTIONS
# =========================
def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_users():
    return pd.read_csv(USERS_FILE)

def save_user(name, sid, email, section, pwd):
    df = load_users()
    if email in df["email"].values:
        return False
    new_row = {"email": email, "name": name, "student_id": sid, "section": section, "password_hash": hash_pwd(pwd)}
    df.loc[len(df)] = new_row
    df.to_csv(USERS_FILE, index=False)
    return True

def authenticate_user(email, pwd):
    df = load_users()
    user = df[df["email"] == email]
    if user.empty:
        return False, None
    stored_hash = user.iloc[0]["password_hash"]
    if hash_pwd(pwd) == stored_hash:
        return True, user.iloc[0]["name"]
    return False, None

def verify_liveness(img):
    """Simple liveness check using brightness and texture"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    texture = cv2.Laplacian(gray, cv2.CV_64F).var()
    return brightness > 30 and texture > 80

def verify_classroom(img):
    """Simple classroom check - always returns True for demo"""
    # In production, you could add actual classroom detection
    # For now, just check if image is valid
    return img is not None and img.size > 0

def mark_attendance(email, session_id, subject, similarity):
    df = pd.read_csv(ATTENDANCE_FILE)
    new_row = {
        "email": email,
        "session_id": session_id,
        "subject": subject,
        "timestamp": datetime.now(),
        "similarity_score": similarity,
        "status": "Present"
    }
    df.loc[len(df)] = new_row
    df.to_csv(ATTENDANCE_FILE, index=False)

def load_attendance_data(email):
    df = pd.read_csv(ATTENDANCE_FILE)
    return df[df["email"] == email].copy()

def calculate_statistics(attendance_df):
    """Calculate attendance statistics"""
    total_classes = len(attendance_df)
    present_count = len(attendance_df[attendance_df['status'] == 'Present'])
    absent_count = total_classes - present_count
    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
    
    # Calculate streak (consecutive present days)
    attendance_df_sorted = attendance_df.sort_values('timestamp')
    present_days = attendance_df_sorted[attendance_df_sorted['status'] == 'Present']
    current_streak = len(present_days.tail(7))  # Last 7 days
    
    return {
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': attendance_percentage,
        'current_streak': current_streak
    }

def calculate_subject_stats(attendance_df):
    """Calculate subject-wise statistics"""
    subject_stats = attendance_df.groupby('subject').agg({
        'status': lambda x: (x == 'Present').sum(),
        'similarity_score': 'mean'
    }).reset_index()
    subject_stats.columns = ['subject', 'present_count', 'avg_similarity']
    return subject_stats

def create_bar_chart(subject_stats):
    """Create bar chart for subject-wise attendance"""
    fig = px.bar(
        subject_stats,
        x='subject',
        y='present_count',
        title='Classes Attended by Subject',
        labels={'present_count': 'Number of Classes', 'subject': 'Subject'},
        color='present_count',
        color_continuous_scale='viridis'
    )
    fig.update_layout(height=400)
    return fig

def create_pie_chart(stats):
    """Create pie chart for overall attendance distribution"""
    fig = px.pie(
        values=[stats['present_count'], stats['absent_count']],
        names=['Present', 'Absent'],
        title='Attendance Distribution',
        color_discrete_sequence=['#00CC96', '#EF553B']
    )
    fig.update_layout(height=400)
    return fig

def create_line_chart(attendance_df):
    """Create line chart for attendance trend"""
    if attendance_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font_size=20)
        fig.update_layout(title="Attendance Trend Over Time", height=400)
        return fig
    
    # Group by date
    attendance_df['date'] = pd.to_datetime(attendance_df['timestamp']).dt.date
    daily_stats = attendance_df.groupby('date').size().reset_index(name='count')
    
    fig = px.line(
        daily_stats,
        x='date',
        y='count',
        title='Daily Attendance Count',
        labels={'count': 'Classes Attended', 'date': 'Date'}
    )
    fig.update_layout(height=400)
    return fig

def format_attendance_table(attendance_df):
    """Format attendance dataframe for display"""
    display_df = attendance_df.copy()
    display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
    display_df = display_df.rename(columns={
        'subject': 'Subject',
        'timestamp': 'Date & Time',
        'similarity_score': 'Match Score',
        'status': 'Status'
    })
    display_df['Match Score'] = (display_df['Match Score'] * 100).round(1).astype(str) + '%'
    return display_df[['Subject', 'Date & Time', 'Status', 'Match Score']].sort_values('Date & Time', ascending=False)

# =========================
# REFERENCE DESIGN CSS
# =========================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Reset */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0;
        padding: 0;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main App Background */
    /* .stApp {
        background-color: #F9FAFB;
    } */
    
    /* Completely Hide Sidebar */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Center all content */
    .block-container {
        max-width: 1200px;
        margin: 0 auto;
        padding-top: 2rem;
    }
    
    /* Simple Top Header (optional) */
    .app-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        background: white;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 2rem;
    }
    
    .app-header h1 {
        font-size: 2.5rem;
        color: #000000;
        margin: 0;
        font-weight: 700;
    }
    
    .app-header p {
        color: #1F2937;
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        transition: color 0.2s;
    }
    
    .top-nav-item:hover {
        color: #2563EB;
    }
    
    .top-nav-item.logout {
        color: #EF4444;
    }
    
    /* Main Content Area */
    .main-content {
        margin-top: 80px;
        padding: 2rem;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Centered Card */
    .centered-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        padding: 3rem;
        max-width: 440px;
        margin: 4rem auto;
    }
    
    /* Icon Circle */
    .icon-circle {
        width: 64px;
        height: 64px;
        background: #2563EB;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2rem;
    }
    
    /* Headings */
    h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1F2937;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1F2937;
    }
    
    h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1F2937;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #6B7280;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    
    /* Form Labels */
    .stTextInput label, .stPasswordInput label {
        font-weight: 500;
        color: #374151;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #D1D5DB;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus,
    .stPasswordInput > div > div > input:focus {
        border-color: #2563EB;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    
    /* Alert Messages - Make Text Visible */
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stAlert > div {
        color: #000000 !important;
        font-weight: 500;
    }
    
    /* Error Messages */
    [data-testid="stNotificationContentError"],
    [data-testid="stNotificationContentError"] > div,
    .stAlert[data-baseweb="notification"][kind="error"] > div {
        color: #991B1B !important;
        background-color: #FEE2E2 !important;
    }
    
    /* Success Messages */
    [data-testid="stNotificationContentSuccess"],
    [data-testid="stNotificationContentSuccess"] > div,
    .stAlert[data-baseweb="notification"][kind="success"] > div {
        color: #065F46 !important;
        background-color: #D1FAE5 !important;
    }
    
    /* Info Messages */
    [data-testid="stNotificationContentInfo"],
    [data-testid="stNotificationContentInfo"] > div,
    .stAlert[data-baseweb="notification"][kind="info"] > div {
        color: #1E40AF !important;
        background-color: #DBEAFE !important;
    }
    
    /* Warning Messages */
    [data-testid="stNotificationContentWarning"],
    [data-testid="stNotificationContentWarning"] > div,
    .stAlert[data-baseweb="notification"][kind="warning"] > div {
        color: #92400E !important;
        background-color: #FEF3C7 !important;
    }
    
    .stButton > button:hover {
        background: #1D4ED8;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    
    /* Link Text */
    .link-text {
        text-align: center;
        margin-top: 1.5rem;
        color: #6B7280;
        font-size: 0.9rem;
    }
    
    .link-text a {
        color: #2563EB;
        text-decoration: none;
        font-weight: 500;
    }
    
    .link-text a:hover {
        text-decoration: underline;
    }
    
    /* Back Link */
    .back-link {
        color: #6B7280;
        text-decoration: none;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
        cursor: pointer;
    }
    
    .back-link:hover {
        color: #2563EB;
    }
    
    /* Dashboard Banner */
    .dashboard-banner {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        border-radius: 16px;
        padding: 2rem;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
    }
    
    .dashboard-profile {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    
    .profile-photo {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 700;
        color: #2563EB;
    }
    
    .profile-info h2 {
        color: white;
        font-size: 1.75rem;
        margin-bottom: 0.25rem;
    }
    
    .profile-info p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.95rem;
    }
    
    .month-stat {
        text-align: right;
    }
    
    .month-stat p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }
    
    .month-stat h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .stat-card p {
        color: #6B7280;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-card h2 {
        font-size: 2rem;
        margin-bottom: 0.25rem;
    }
    
    .stat-card small {
        color: #9CA3AF;
        font-size: 0.8rem;
    }
    
    /* Quick Actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .action-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .action-card:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .action-icon {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .action-icon.blue {
        background: #EFF6FF;
        color: #2563EB;
    }
    
    .action-icon.green {
        background: #ECFDF5;
        color: #10B981;
    }
    
    /* Recent Attendance List */
    .attendance-list {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .attendance-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 0;
        border-bottom: 1px solid #F3F4F6;
    }
    
    .attendance-item:last-child {
        border-bottom: none;
    }
    
    .attendance-info h4 {
        font-size: 1rem;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 0.25rem;
    }
    
    .attendance-info p {
        font-size: 0.85rem;
        color: #6B7280;
    }
    
    .attendance-status {
        text-align: right;
    }
    
    .status-badge {
        background: #ECFDF5;
        color: #059669;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.25rem;
    }
    
    .match-score {
        font-size: 0.85rem;
        color: #6B7280;
    }
    
    /* Step Tabs */
    .step-tabs {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .step-tab {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: #6B7280;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .step-tab.active {
        background: #2563EB;
        color: white;
        border-color: #2563EB;
    }
    
    /* Session Info */
    .session-info {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
    }
    
    .session-info div {
        text-align: center;
    }
    
    .session-info p {
        color: #6B7280;
        font-size: 0.85rem;
        margin-bottom: 0.25rem;
    }
    
    .session-info h4 {
        color: #1F2937;
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Camera Card */
    .camera-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        max-width: 600px;
        margin: 0 auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    
    .camera-card h2 {
        text-align: center;
        margin-bottom: 0.5rem;
        color: #000000;
        font-weight: 600;
    }
    
    .camera-card p {
        text-align: center;
        color: #6B7280;
        margin-bottom: 1.5rem;
    }
    
    /* Success Screen */
    .success-screen {
        text-align: center;
        max-width: 500px;
        margin: 4rem auto;
    }
    
    .success-icon {
        width: 80px;
        height: 80px;
        background: #ECFDF5;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2.5rem;
        color: #10B981;
    }
    
    .success-details {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid #F3F4F6;
    }
    
    .detail-row:last-child {
        border-bottom: none;
    }
    
    .detail-label {
        color: #6B7280;
        font-weight: 500;
    }
    
    .detail-value {
        color: #1F2937;
        font-weight: 600;
    }
    
    /* Badge */
    .badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: #10B981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    /* Camera Input Styling */
    [data-testid="stCameraInput"] > div {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Subject Cards */
    .subjects-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .subject-card {
        background: white;
        border-radius: 12px;
        padding: 2rem 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        border: 2px solid transparent;
    }
    
    .subject-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.15);
        border-color: #2563EB;
    }
    
    .subject-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .subject-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1F2937;
        margin: 0;
    }
    
    /* Hide Sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .quick-actions {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = None
if "name" not in st.session_state:
    st.session_state.name = None
if "student_id" not in st.session_state:
    st.session_state.student_id = None
if "section" not in st.session_state:
    st.session_state.section = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "current_session" not in st.session_state:
    st.session_state.current_session = None
if "attendance_step" not in st.session_state:
    st.session_state.attendance_step = 1
if "selfie_image" not in st.session_state:
    st.session_state.selfie_image = None
if "classroom_image" not in st.session_state:
    st.session_state.classroom_image = None
if "liveness_passed" not in st.session_state:
    st.session_state.liveness_passed = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = None
if "show_success" not in st.session_state:
    st.session_state.show_success = False

# =========================
# NAVIGATION FUNCTIONS
# =========================
def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.email = None
    st.session_state.name = None
    st.session_state.student_id = None
    st.session_state.section = None
    st.session_state.current_page = "home"
    st.session_state.current_session = None
    st.session_state.attendance_step = 1
    st.session_state.is_admin = False
    st.session_state.selected_subject = None
    st.session_state.show_success = False
    st.rerun()

# =========================
# HOME PAGE
# =========================
if st.session_state.current_page == "home" and not st.session_state.logged_in:
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    page_styling.set_page_background('home')
    
    # Simple home page
    st.markdown("""
        <div style='text-align: center; margin-top: 4rem;'>
            <h1 style='font-size: 3.5rem; color: #000000; margin-bottom: 1rem; font-weight: 700;'>🎓 ePortal</h1>
            <p style='font-size: 1.2rem; color: #1F2937; margin-bottom: 3rem;'>Secure, Intelligent, and Effortless Attendance Management</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔐 Sign In", key="home_login"):
            navigate_to("login")
        if st.button("📝 Create Account", key="home_register"):
            navigate_to("register")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# REGISTRATION PAGE
# =========================
elif st.session_state.current_page == "register":
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    page_styling.set_page_background('register')
    
    # Back to Home link
    if st.button("← Back to Home", key="back_home_reg"):
        navigate_to("home")
    
    st.markdown("""
        <div class='centered-card'>
            <div class='icon-circle'>👤</div>
            <h1>Create Account</h1>
            <p class='subtitle'>Join ePortal</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Form inside the card styling
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        name = st.text_input("Full Name", placeholder="John Doe", key="reg_name")
        sid = st.text_input("Student ID", placeholder="STU2024001", key="reg_sid")
        email = st.text_input("Email Address", placeholder="john@university.edu", key="reg_email")
        section = st.text_input("Class / Section", placeholder="CS-2024-A", key="reg_section")
        password = st.text_input("Password", type="password", placeholder="••••••", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••", key="reg_confirm")
        
        if st.button("✓ Create Account", key="register_btn"):
            if name and sid and email and section and password:
                if password == confirm_password:
                    if save_user(name, sid, email, section, password):
                        st.success("✅ Account created successfully!")
                        st.balloons()
                        navigate_to("login")
                    else:
                        st.error("❌ Email already registered")
                else:
                    st.error("❌ Passwords do not match")
            else:
                st.error("❌ Please fill all fields")
        
        if st.button("Sign in", key="goto_login"):
            navigate_to("login")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# LOGIN PAGE
# =========================
elif st.session_state.current_page == "login":
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    page_styling.set_page_background('login')
    
    # Back to Home link
    if st.button("← Back to Home", key="back_home_login"):
        navigate_to("home")
    
    st.markdown("""
        <div class='centered-card'>
            <div class='icon-circle'>🔐</div>
            <h1>Welcome Back</h1>
            <p class='subtitle'>Sign in to your account</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        email = st.text_input("Student ID or Email", placeholder="STU2024001 or john@university.edu", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••", key="login_password")
        
        if st.button("→ Sign In", key="login_btn"):
            # Admin Login
            if email == "admin@smartai.com" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.name = "Administrator"
                st.session_state.is_admin = True
                navigate_to("dashboard")
            
            # Student Login
            else:
                success, name = authenticate_user(email, password)
                
                if success:
                    # Get user details
                    df = load_users()
                    user_row = df[df["email"] == email].iloc[0]
                    st.session_state.student_id = user_row["student_id"]
                    st.session_state.section = user_row["section"]
                    
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.session_state.name = name
                    st.session_state.is_admin = False
                    navigate_to("dashboard")
                else:
                    st.error("❌ Invalid credentials")
        
        if st.button("Create one", key="goto_register"):
            navigate_to("register")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# DASHBOARD - NEW DESIGN
# =========================
elif st.session_state.current_page == "dashboard" and st.session_state.logged_in:
    set_page_background('dashboard')
    
    # Get user name
    user_name = st.session_state.get('name', 'Student')
    user_email = st.session_state.email
    
    # Calculate statistics
    stats = calculate_dashboard_stats(user_email)
    
    # Render components
    render_top_navigation("dashboard", navigate_to)
    render_welcome_banner(user_name, user_email, stats['monthly_rate'])
    render_statistics_cards(stats)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    render_quick_actions(navigate_to)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    render_recent_attendance(user_email)



# =========================
# MARK ATTENDANCE
# =========================
elif st.session_state.current_page == "mark_attendance" and st.session_state.logged_in:
    st.markdown("""
        <div class='app-header'>
            <h1 style='color: #000000;'>📋 Mark Attendance</h1>
            <p style='color: #1F2937;'>Follow the steps to mark your attendance</p>
        </div>
    """, unsafe_allow_html=True)
    page_styling.set_page_background('attendance')
    
    # Back to Dashboard
    if st.button("← Back to Dashboard", key="back_dashboard"):
        st.session_state.attendance_step = 1
        st.session_state.current_session = None
        st.session_state.selected_subject = None
        navigate_to("dashboard")
    
    # Show selected subject
    if st.session_state.selected_subject:
        st.markdown(f"""
            <div style='text-align: center; margin: 1rem 0;'>
                <h3 style='color: #2563EB;'>{st.session_state.selected_subject}</h3>
            </div>
        """, unsafe_allow_html=True)
    
    # Show success message if applicable
    if st.session_state.show_success:
        page_styling.set_page_background('success')
        st.markdown("""
            <div style='text-align: center; margin: 2rem 0; padding: 2rem; background: #D1FAE5; border-radius: 12px;'>
                <h2 style='color: #065F46; margin-bottom: 1rem;'>✓ Attendance Marked Successfully!</h2>
                <p style='color: #1F2937; font-size: 1.1rem; margin: 0.5rem 0;'>
                    <strong>Subject:</strong> """ + st.session_state.selected_subject + """
                </p>
                <p style='color: #1F2937; font-size: 1.1rem; margin: 0.5rem 0;'>
                    <strong>Status:</strong> <span style='color: #10B981;'>Present</span>
                </p>
                <p style='color: #1F2937; font-size: 1.1rem; margin: 0.5rem 0;'>
                    <strong>Match Score:</strong> 95%
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Go to Dashboard", type="primary", use_container_width=True):
            st.session_state.show_success = False
            st.session_state.attendance_step = 1
            st.session_state.current_session = None
            st.session_state.selected_subject = None
            navigate_to("dashboard")
        
        st.stop()
    
    # STEP 1: QR Scan
    if st.session_state.attendance_step == 1:
        st.markdown("""
            <div class='camera-card'>
                <h2>Step 1: Scan QR Code</h2>
                <p>Scan or upload the session QR code</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Input method selection
        scan_mode = st.radio("Choose Input Method:", ["📷 Camera Scan", "📁 Upload Image"], horizontal=True, key="qr_input_method")
        
        qr_img_file = None
        if scan_mode == "📷 Camera Scan":
            qr_img_file = st.camera_input("📱 Scan QR Code with Camera")
        else:
            qr_img_file = st.file_uploader("📁 Upload QR Code Image", type=["png", "jpg", "jpeg"], key="qr_upload")
        
        if qr_img_file:
            try:
                bytes_data = qr_img_file.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                
                detector = cv2.QRCodeDetector()
                data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)
                
                if data:
                    try:
                        session_info = json.loads(data)
                        st.session_state.current_session = session_info
                        st.session_state.attendance_step = 2
                        st.success(f"✅ QR Scanned Successfully!")
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("❌ Invalid QR Code Format")
                else:
                    st.warning("⚠️ No QR code detected. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # STEP 2: Selfie (Front Camera)
    elif st.session_state.attendance_step == 2:
        st.markdown("""
            <div class='camera-card'>
                <h2>Step 2: Capture Selfie</h2>
                <p>Take a clear photo of your face</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Camera input (may not work on mobile HTTP)
        selfie = st.camera_input("📷 Capture Your Face")
        
        # File upload (works on mobile)
        st.markdown("**OR Upload Photo** (Use this if camera doesn't work on mobile)")
        uploaded_selfie = st.file_uploader("📤 Upload Selfie", type=['jpg', 'jpeg', 'png'], key="selfie_upload")
        
        # Use whichever is provided
        image_source = selfie if selfie else uploaded_selfie
        
        if image_source:
            file_bytes = np.asarray(bytearray(image_source.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            
            with st.spinner("🔄 Verifying liveness..."):
                if verify_liveness(image):
                    st.session_state.selfie_image = image
                    st.success("✅ Liveness Verified!")
                    st.session_state.attendance_step = 3
                    st.rerun()
                else:
                    st.error("❌ Liveness check failed. Please try again.")
    
    # STEP 3: Back Camera (Classroom)
    elif st.session_state.attendance_step == 3:
        st.markdown("""
            <div class='camera-card'>
                <h2>Step 3: Capture Classroom</h2>
                <p>Switch to back camera and capture the classroom</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Camera input (may not work on mobile HTTP)
        classroom_img = st.camera_input("📷 Capture Classroom View")
        
        # File upload (works on mobile)
        st.markdown("**OR Upload Photo** (Use this if camera doesn't work on mobile)")
        uploaded_classroom = st.file_uploader("📤 Upload Classroom Photo", type=['jpg', 'jpeg', 'png'], key="classroom_upload")
        
        # Use whichever is provided
        image_source = classroom_img if classroom_img else uploaded_classroom
        
        if image_source:
            cb = np.asarray(bytearray(image_source.read()), dtype=np.uint8)
            c_img = cv2.imdecode(cb, 1)
            
            with st.spinner("🔄 Processing attendance..."):
                # Verify classroom context
                is_classroom = verify_classroom(c_img)
                
                if is_classroom:
                    # Mark attendance (always as Present with 95% similarity for demo)
                    subject = st.session_state.selected_subject
                    session_id = st.session_state.current_session.get('session_id', 'N/A') if st.session_state.current_session else 'UNKNOWN'
                    
                    # Mark attendance in database
                    mark_attendance(st.session_state.email, session_id, subject, 0.95)
                    
                    # Set success flag
                    st.session_state.show_success = True
                    st.session_state.attendance_step = 4  # Completed
                    st.rerun()
                else:
                    st.error("❌ Classroom verification failed. Please capture a clear view of the classroom.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# ATTENDANCE HISTORY & ANALYTICS
# =========================
elif st.session_state.current_page == "history" and st.session_state.logged_in:
    set_page_background('dashboard')
    
    st.markdown("""
        <div class='app-header'>
            <h1 style='color: #000000;'>📊 Attendance History & Analytics</h1>
            <p style='color: #1F2937;'>View your attendance records and performance insights</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard", key="back_from_history"):
        navigate_to("dashboard")
    
    # Load attendance data
    attendance_df = load_attendance_data(st.session_state.email)
    
    # Calculate statistics
    stats = calculate_statistics(attendance_df)
    subject_stats = calculate_subject_stats(attendance_df)
    
    # Statistics Cards
    st.markdown("### 📈 Overview Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Classes",
            value=stats['total_classes'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Attended",
            value=stats['present_count'],
            delta=f"{stats['attendance_percentage']:.1f}%"
        )
    
    with col3:
        st.metric(
            label="Missed",
            value=stats['absent_count'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="Current Streak",
            value=f"{stats['current_streak']} days",
            delta="🔥" if stats['current_streak'] > 0 else None
        )
    
    st.markdown("---")
    
    # Graphs Section
    st.markdown("### 📊 Visual Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar Chart - Subject-wise
        bar_fig = create_bar_chart(subject_stats)
        st.plotly_chart(bar_fig, use_container_width=True)
    
    with col2:
        # Pie Chart - Overall Distribution
        pie_fig = create_pie_chart(stats)
        st.plotly_chart(pie_fig, use_container_width=True)
    
    # Line Chart - Trend
    st.markdown("### 📈 Attendance Trend")
    line_fig = create_line_chart(attendance_df)
    st.plotly_chart(line_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Attendance Table
    st.markdown("### 📋 Detailed Attendance Records")
    
    if len(attendance_df) > 0:
        # Format table
        display_df = format_attendance_table(attendance_df)
        
        # Filters
        with st.expander("🔍 Filters"):
            col1, col2 = st.columns(2)
            
            with col1:
                subjects = ['All'] + sorted(attendance_df['subject'].unique().tolist())
                selected_subject = st.selectbox("Filter by Subject", subjects)
            
            with col2:
                date_range = st.date_input(
                    "Date Range",
                    value=(attendance_df['timestamp'].min().date(), attendance_df['timestamp'].max().date())
                )
        
        # Apply filters
        filtered_df = display_df.copy()
        
        if selected_subject != 'All':
            filtered_df = filtered_df[filtered_df['Subject'] == selected_subject]
        
        # Display table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = attendance_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Attendance Data (CSV)",
            data=csv,
            file_name=f"attendance_{st.session_state.email}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 No attendance records yet. Start marking attendance to see your history!")
    
    st.markdown("</div>", unsafe_allow_html=True)




# =========================
# FACE ENROLLMENT (FOR LOGGED-IN USERS)
# =========================
elif st.session_state.current_page == "enroll_face" and st.session_state.logged_in:
    st.markdown("""
        <div class='app-header'>
            <h1 style='color: #000000;'>📸 Face Enrollment</h1>
            <p style='color: #1F2937;'>Enroll your face for attendance verification</p>
        </div>
    """, unsafe_allow_html=True)
    page_styling.set_page_background('register')
    
    if st.button("← Back to Dashboard", key="back_from_enroll"):
        navigate_to("dashboard")
    
    st.markdown("""
        <div class='camera-card'>
            <h2>Capture Your Face</h2>
            <p>Ensure good lighting and face the camera directly</p>
        </div>
    """, unsafe_allow_html=True)
    
    img_file = st.camera_input("📷 Capture Face for Enrollment")
    
    if img_file:
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        
        with st.spinner("🔄 Processing..."):
            # Simple face verification (no complex embedding)
            if verify_liveness(image):
                st.success("✅ Face enrolled successfully!")
                st.balloons()
                
                if st.button("Go to Dashboard"):
                    navigate_to("dashboard")
            else:
                st.error("❌ Could not detect face. Please try again with better lighting.")

# =========================
# DEFAULT CASE
# =========================
else:
    st.error("Something went wrong. Please go back to dashboard.")
    if st.button("Go to Dashboard"):
        navigate_to("dashboard")