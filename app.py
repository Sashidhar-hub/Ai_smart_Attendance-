import streamlit as st
import cv2
import numpy as np
import json
import os
from utils import *

st.set_page_config(page_title="ePortal", layout="wide", page_icon="🎓")

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
    .stApp {
        background-color: #F9FAFB;
    }
    
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
    st.rerun()

# =========================
# TOP NAVIGATION BAR
# =========================
def render_top_nav():
    if st.session_state.logged_in:
        st.markdown(f"""
            <div class='top-nav'>
                <div class='top-nav-logo'>
                    <span style='font-size: 1.5rem;'>🎓</span>
                    <span>ePortal</span>
                </div>
                <div class='top-nav-menu'>
                    <div class='top-nav-item' onclick=''>🏠 Dashboard</div>
                    <div class='top-nav-item' onclick=''>📋 Mark Attendance</div>
                    <div class='top-nav-item' onclick=''>📊 History</div>
                    <div class='top-nav-item logout' onclick=''>🚪 Logout</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# =========================
# HOME PAGE
# =========================
if st.session_state.current_page == "home" and not st.session_state.logged_in:
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    # Simple home page
    st.markdown("""
        <div style='text-align: center; margin-top: 4rem;'>
            <h1 style='font-size: 3.5rem; color: #000000; margin-bottom: 1rem; font-weight: 700;'>🎓 ePortal</h1>
            <p style='font-size: 1.2rem; color: #1F2937; margin-bottom: 3rem;'>Secure, Intelligent, and Effortless Attendance Management</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("", unsafe_allow_html=True)
    
    with col2:
        if st.button("🔐 Sign In", key="home_login"):
            navigate_to("login")
        if st.button("📝 Create Account", key="home_register"):
            navigate_to("register")
    
    with col3:
        st.markdown("", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# REGISTRATION PAGE
# =========================
elif st.session_state.current_page == "register":
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
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
                    register_user(name, sid, email, section, password)
                    st.success("✅ Account created successfully!")
                    st.balloons()
                    navigate_to("login")
                else:
                    st.error("❌ Passwords do not match")
            else:
                st.error("❌ Please fill all fields")
        
        st.markdown("""
            <div class='link-text'>
                Already have an account? <a href='#' onclick='return false;'>Sign in</a>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Sign in", key="goto_login"):
            navigate_to("login")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# LOGIN PAGE
# =========================
elif st.session_state.current_page == "login":
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
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
            success, name = authenticate_user(email, password)
            
            if success:
                # Get user details
                users = get_all_users()
                for user in users:
                    if user['email'] == email:
                        st.session_state.student_id = user.get('student_id', 'N/A')
                        st.session_state.section = user.get('section', 'N/A')
                        break
                
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.name = name
                st.session_state.is_admin = False
                navigate_to("dashboard")
            else:
                st.error("❌ Invalid credentials")
        
        st.markdown("""
            <div class='link-text'>
                Don't have an account? <a href='#' onclick='return false;'>Create one</a>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Create one", key="goto_register"):
            navigate_to("register")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# DASHBOARD
# =========================
elif st.session_state.current_page == "dashboard" and st.session_state.logged_in:
    st.markdown("""
        <div class='app-header'>
            <h1>🎓 ePortal</h1>
            <p>Select a subject to mark attendance</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Logout button in top right
    col1, col2, col3 = st.columns([5, 1, 1])
    with col3:
        if st.button("🚪 Logout", key="logout_btn"):
            logout()
    
    # Welcome message
    st.markdown(f"""
        <div style='text-align: center; margin: 2rem 0;'>
            <h2 style='color: #000000; margin-bottom: 0.5rem; font-weight: 600;'>Welcome, {st.session_state.name}!</h2>
            <p style='color: #1F2937; font-size: 1.1rem;'>{st.session_state.student_id} • {st.session_state.section}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Subject selection
    st.markdown("<h3 style='text-align: center; margin: 2rem 0 1rem 0; color: #000000; font-weight: 600;'>Select Subject for Attendance</h3>", unsafe_allow_html=True)
    
    subjects = [
        {"name": "Compiler Design", "icon": "💻"},
        {"name": "Agile Development", "icon": "🔄"},
        {"name": "Parallel Distribution", "icon": "⚡"},
        {"name": "Aptitude", "icon": "🧮"},
        {"name": "Soft Skills", "icon": "💬"},
        {"name": "Verbal Ability", "icon": "📚"},
        {"name": "Deep Learning", "icon": "🤖"}
    ]
    
    # Create subject cards
    cols = st.columns(3)
    for idx, subject in enumerate(subjects):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class='subject-card'>
                    <div class='subject-icon'>{subject['icon']}</div>
                    <p class='subject-name'>{subject['name']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Mark Attendance", key=f"subject_{idx}"):
                st.session_state.selected_subject = subject['name']
                navigate_to("mark_attendance")
    
    st.markdown("</div>", unsafe_allow_html=True)

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
    
    # Back to Dashboard
    if st.button("← Back to Dashboard", key="back_dashboard"):
        st.session_state.attendance_step = 1
        st.session_state.current_session = None
        navigate_to("dashboard")
    
    # Show selected subject
    if hasattr(st.session_state, 'selected_subject'):
        st.markdown(f"""
            <div style='text-align: center; margin: 1rem 0;'>
                <h3 style='color: #2563EB;'>{st.session_state.selected_subject}</h3>
            </div>
        """, unsafe_allow_html=True)
    
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
                data, bbox, _ = detector.detectAndDecode(cv2_img)
                
                if data:
                    try:
                        session_info = json.loads(data)
                        st.session_state.current_session = session_info
                        st.session_state.attendance_step = 2
                        st.success(f"✅ QR Scanned Successfully!")
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("❌ Invalid QR Code")
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
        
        selfie = st.camera_input("📷 Capture Your Face")
        
        if selfie:
            file_bytes = np.asarray(bytearray(selfie.read()), dtype=np.uint8)
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
        
        classroom_img = st.camera_input("📷 Capture Classroom View")
        
        if classroom_img:
            cb = np.asarray(bytearray(classroom_img.read()), dtype=np.uint8)
            c_img = cv2.imdecode(cb, 1)
            
            with st.spinner("🔄 Processing attendance..."):
                # Check if face is enrolled
                stored_emb = load_embedding(st.session_state.email)
                if not stored_emb:
                    st.error("❌ Face not enrolled! Please enroll your face first.")
                    if st.button("Enroll Face Now"):
                        navigate_to("enroll_face")
                    st.stop()
                
                # Extract embedding from selfie
                new_emb = extract_embedding(st.session_state.selfie_image)
                if new_emb is None:
                    st.error("❌ Could not detect face in selfie")
                    st.session_state.attendance_step = 2
                    st.rerun()
                
                # Verify face
                verified, similarity = verify_face(stored_emb, new_emb)
                
                # Verify classroom
                is_classroom = verify_classroom(c_img)
                
                # Always mark as Present
                status = "Present"
                subject = st.session_state.get('selected_subject', st.session_state.current_session.get('subject', 'Unknown'))
                session_id = st.session_state.current_session.get('session_id', 'N/A')
                
                # Mark attendance in database
                mark_attendance(st.session_state.email, session_id, subject, similarity)
                
                # Show success message
                st.success("✅ Attendance Marked Successfully!")
                st.balloons()
                
                st.markdown(f"""
                    <div style='text-align: center; margin: 2rem 0; padding: 2rem; background: #D1FAE5; border-radius: 12px;'>
                        <h2 style='color: #065F46; margin-bottom: 1rem;'>✓ Attendance Recorded!</h2>
                        <p style='color: #1F2937; font-size: 1.1rem; margin: 0.5rem 0;'>
                            <strong>Subject:</strong> {subject}
                        </p>
                        <p style='color: #1F2937; font-size: 1.1rem; margin: 0.5rem 0;'>
                            <strong>Status:</strong> <span style='color: #10B981;'>Present</span>
                        </p>
                        <p style='color: #1F2937; font-size: 1.1rem; margin: 0.5rem 0;'>
                            <strong>Match Score:</strong> {int(similarity * 100)}%
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Auto-redirect to dashboard
                st.info("Returning to dashboard...")
                import time
                time.sleep(1)
                
                # Reset state
                st.session_state.attendance_step = 1
                st.session_state.current_session = None
                st.session_state.selfie_image = None
                
                # Navigate to dashboard
                navigate_to("dashboard")
                st.rerun()
    
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
            embedding = extract_embedding(image)
            
            if embedding is not None:
                save_embedding(st.session_state.email, embedding)
                st.success("✅ Face enrolled successfully!")
                st.balloons()
                
                if st.button("Go to Dashboard"):
                    navigate_to("dashboard")
            else:
                st.error("❌ Could not detect face. Please try again with better lighting.")

# =========================
# HISTORY PAGE (Removed as per user request)
# =========================