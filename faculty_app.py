import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# ================= Configuration =================
st.set_page_config(page_title="Faculty Dashboard | Smart AI", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

# ================= Custom CSS (Base44 Premium Aesthetic) =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: #F9FAFB !important;
    }
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Form & Input Reset */
    .stTextInput input, .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 1px solid #D1D5DB !important;
        padding: 0.5rem 1rem !important;
        font-size: 1rem !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Login Card */
    .login-container {
        background: white;
        border-radius: 24px;
        padding: 3rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 1px solid #F3F4F6;
        text-align: center;
        max-width: 450px;
        margin: 4rem auto;
    }
    
    /* Custom Navbar Button Style Override */
    .nav-btn button {
        background: transparent !important;
        color: #6B7280 !important;
        border: none !important;
        box-shadow: none !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
    }
    .nav-btn button:hover { color: #4F46E5 !important; background: #EEF2FF !important; }
    
    /* Hero Card */
    .hero-card {
        background: linear-gradient(135deg, #1E1B4B 0%, #4338CA 100%);
        border-radius: 24px; padding: 2.5rem; color: white;
        display: flex; align-items: center; justify-content: space-between;
        margin-top: 1rem; margin-bottom: 2rem; box-shadow: 0 20px 25px -5px rgba(67, 56, 202, 0.25);
        position: relative; overflow: hidden;
    }
    .hero-card::after {
        content: ''; position: absolute; top: 0; right: 0; bottom: 0; left: 0;
        background: url('data:image/svg+xml;utf8,<svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="1.5" fill="rgba(255,255,255,0.05)"/></svg>');
        opacity: 0.5; pointer-events: none;
    }
    .hero-profile { display: flex; align-items: center; gap: 1.5rem; position: relative; z-index: 10; }
    .hero-avatar {
        width: 80px; height: 80px; background: rgba(255,255,255,0.15);
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-size: 2rem; border: 2px solid rgba(255,255,255,0.2); backdrop-filter: blur(4px);
    }
    .hero-text h2 { font-size: 2.25rem; font-weight: 800; margin: 0; color: white; line-height: 1.2;}
    .hero-text p { color: #A5B4FC; font-size: 1.1rem; margin: 0.2rem 0 0; font-weight: 500;}
    
    .hero-widget {
        background: rgba(255,255,255,0.1); backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.15); border-radius: 16px;
        padding: 1.25rem 2rem; text-align: center; position: relative; z-index: 10;
    }
    .hero-widget small { color: #E0E7FF; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; display: block;}
    .hero-widget strong { font-size: 2.25rem; font-weight: 800; }
    
    /* Stats Grid */
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 3rem; }
    .stat-item {
        background: white; border-radius: 20px; padding: 1.5rem;
        border: 1px solid #F3F4F6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-item:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
    .stat-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
    .stat-header span { color: #6B7280; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .stat-val { font-size: 2.25rem; font-weight: 800; color: #111827; }
    .stat-sub { margin-top: 0.5rem; display: flex; align-items: center; gap: 0.35rem; font-size: 0.85rem; font-weight: 500; color: #9CA3AF;}
    
    .stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }
    .bg-blue { background: #EEF2FF; color: #4F46E5; }
    .bg-green { background: #ECFDF5; color: #10B981; }
    .bg-red { background: #FEF2F2; color: #EF4444; }
    .bg-purple { background: #F5F3FF; color: #8B5CF6; }
    .bg-gray { background: #F3F4F6; color: #6B7280; }
    
    .text-green { color: #10B981; }
    .text-red { color: #EF4444; }
    
    /* Lists & Content Boxes */
    .section-title { font-size: 1.25rem; font-weight: 800; color: #111827; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.5rem; }
    .content-box {
        background: white; border-radius: 24px; padding: 2rem;
        border: 1px solid #E5E7EB; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 2rem;
    }
    
    .list-row {
        background: white; padding: 1.25rem 1.5rem; border-radius: 16px;
        border: 1px solid #F3F4F6; display: flex; align-items: center; gap: 1.25rem;
        margin-bottom: 0.75rem; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.02);
        transition: border-color 0.2s;
    }
    .list-row:hover { border-color: #D1D5DB; }
    .list-ico {
        width: 48px; height: 48px; background: #F3F4F6; color: #4B5563;
        border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; font-weight: 700;
    }
    .list-details { flex: 1; }
    .list-details h5 { font-size: 1rem; font-weight: 700; color: #111827; margin: 0; }
    .list-details small { color: #6B7280; font-size: 0.85rem; display: block; margin-top: 0.2rem;}
    .badge-p { background: #ECFDF5; color: #059669; padding: 0.35rem 0.85rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700; border: 1px solid #A7F3D0; }
    .badge-a { background: #FEF2F2; color: #DC2626; padding: 0.35rem 0.85rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700; border: 1px solid #FECACA; }
    .list-action { display: flex; align-items: center; gap: 1rem; }
    
    /* Image Verify Badges */
    .img-badge {
        font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 6px;
        display: inline-flex; align-items: center; gap: 0.3rem; margin-top: 0.5rem;
    }
    .img-ok { background: #ECFDF5; color: #059669; border: 1px solid #D1FAE5; }
    .img-none { background: #F3F4F6; color: #6B7280; border: 1px solid #E5E7EB; }
    
    /* Photo Verification Column */
    .verify-img-container {
        width: 120px; height: 120px; border-radius: 16px; overflow: hidden;
        border: 1px solid #E5E7EB; background: #F9FAFB; display: flex; align-items: center; justify-content: center;
        position: relative;
    }
    .verify-img-label {
        position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.6);
        color: white; font-size: 0.65rem; text-align: center; padding: 0.2rem 0; font-weight: 600; backdrop-filter: blur(2px);
    }
</style>
""", unsafe_allow_html=True)

# ================= Paths & Helpers =================
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.csv")

def safe_read_csv(file_path, cols):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(file_path)
        if df.columns.tolist() != cols and not df.empty:
             for col in cols:
                 if col not in df.columns: df[col] = None
        return df
    except:
        return pd.DataFrame(columns=cols)

def check_login(username, password):
    return username == "admin" and password == "admin123"

# ================= Authentication =================
if "faculty_authenticated" not in st.session_state:
    st.session_state.faculty_authenticated = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "dashboard"

# ================= LOGIN PAGE =================
if not st.session_state.faculty_authenticated:
    st.markdown("""
        <div class="login-container">
            <div style="font-size: 3.5rem; margin-bottom: 1rem; color: #4F46E5;">🏫</div>
            <h1 style="font-size: 1.8rem; font-weight: 800; color: #111827; margin-bottom: 0.5rem;">Faculty Portal</h1>
            <p style="color: #6B7280; font-size: 0.95rem; margin-bottom: 2.5rem;">Sign in to access analytics</p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user = st.text_input("Username", placeholder="e.g. admin", label_visibility="collapsed")
        pw = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Using a custom div for button spacing
        st.markdown('<div class="stButton" style="width: 100%;">', unsafe_allow_html=True)
        if st.button("Secure Login", use_container_width=True, type="primary"):
            if check_login(user, pw):
                st.session_state.faculty_authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials. Try admin / admin123")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<p style='color:#9CA3AF; font-size:0.8rem; text-align:center; margin-top:1.5rem;'>Demo: admin / admin123</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ================= TOP NAVIGATION (No Sidebar) =================
# Creating a custom top navigation bar
col_logo, col_nav1, col_nav2, col_nav3, col_nav4, col_logout = st.columns([2, 1, 1, 1, 1, 1])

with col_logo:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.75rem; padding-top: 0.4rem;">
            <div style="background: #4F46E5; color: white; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">🏫</div>
            <h2 style="font-size: 1.25rem; font-weight: 800; color: #111827; margin: 0;">Smart AI Faculty</h2>
        </div>
    """, unsafe_allow_html=True)

# Custom wrapper to style Streamlit buttons as nav links
st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
with col_nav1:
    if st.button("📊 Overview", use_container_width=True): st.session_state.current_view = "dashboard"; st.rerun()
with col_nav2:
    if st.button("📸 Live Feed", use_container_width=True): st.session_state.current_view = "today"; st.rerun()
with col_nav3:
    if st.button("❌ Absentees", use_container_width=True): st.session_state.current_view = "absentees"; st.rerun()
with col_nav4:
    if st.button("📈 Analytics", use_container_width=True): st.session_state.current_view = "performance"; st.rerun()
with col_logout:
    st.markdown("</div>", unsafe_allow_html=True) # close nav-btn formatting
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.faculty_authenticated = False
        st.rerun()

st.markdown('<hr style="margin: 1rem 0 2rem; border-color: #E5E7EB;">', unsafe_allow_html=True)


# ================= DATA LOADING =================
attendance_df = safe_read_csv(ATTENDANCE_FILE, ["email", "session_id", "subject", "timestamp", "similarity_score", "status", "selfie_path", "classroom_path"])
users_df = safe_read_csv(USERS_FILE, ["email","name","student_id","section","password_hash"])

students_df = users_df[users_df['email'] != 'admin@smartai.com'] if not users_df.empty else pd.DataFrame(columns=["email","name","student_id","section"])

if not attendance_df.empty and 'timestamp' in attendance_df.columns:
    try:
        attendance_df['date'] = pd.to_datetime(attendance_df['timestamp'], errors='coerce').dt.date
    except:
        attendance_df['date'] = None
else:
    attendance_df['date'] = []


# ================= DASHBOARD OVERVIEW =================
if st.session_state.current_view == "dashboard":
    
    # 1. Hero Welcome Card
    total_students = len(students_df)
    today = datetime.now().date()
    if not attendance_df.empty:
        today_records = attendance_df[attendance_df['date'] == today]
        present_today = len(today_records['email'].unique())
    else:
        present_today = 0
    absent_today = max(0, total_students - present_today)
    attendance_rate = int((present_today / total_students * 100)) if total_students > 0 else 0
    
    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-profile">
            <div class="hero-avatar">👨‍🏫</div>
            <div class="hero-text">
                <h2>Welcome, Professor</h2>
                <p>System Operating Online • {today.strftime("%B %d, %Y")}</p>
            </div>
        </div>
        <div class="hero-widget">
            <small>Today's Turnout</small>
            <strong>{attendance_rate}%</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Stats Grid
    trend_color = "text-green" if attendance_rate >= 75 else "text-red"
    trend_arrow = "↑" if attendance_rate >= 75 else "↓"
    
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-item">
            <div class="stat-header"><span>All Students</span> <div class="stat-icon bg-blue">👥</div></div>
            <div class="stat-val">{total_students}</div>
            <div class="stat-sub"><span style="color: #6B7280;">Enrolled across all sections</span></div>
        </div>
        <div class="stat-item">
            <div class="stat-header"><span>Verified Present</span> <div class="stat-icon bg-green">✅</div></div>
            <div class="stat-val">{present_today}</div>
            <div class="stat-sub"><span class="text-green">↑ {present_today}</span>  &nbsp;checked in today</div>
        </div>
        <div class="stat-item">
            <div class="stat-header"><span>Absent</span> <div class="stat-icon bg-red">❌</div></div>
            <div class="stat-val">{absent_today}</div>
            <div class="stat-sub"><span class="text-red">↓ {absent_today}</span>  &nbsp;missing today</div>
        </div>
        <div class="stat-item">
            <div class="stat-header"><span>System Status</span> <div class="stat-icon bg-purple">⚙️</div></div>
            <div class="stat-val">Active</div>
            <div class="stat-sub"><span class="text-green">●</span> &nbsp;All scanners operational</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. Recent Activity List
    st.markdown('<div class="section-title">⏱️ Real-time Activity Logs</div>', unsafe_allow_html=True)
    
    if attendance_df.empty:
        st.info("No activity recorded yet.")
    else:
        recent_df = attendance_df.sort_values(by="timestamp", ascending=False).head(5)
        recent_df = recent_df.merge(students_df[['email', 'name', 'student_id']], on='email', how='left')
        
        for index, row in recent_df.iterrows():
            name = row.get('name', 'Unknown Student')
            initial = name[0].upper() if pd.notnull(name) and name else 'S'
            sid = row.get('student_id', 'N/A')
            subj = row.get('subject', 'Session')
            time_str = str(row.get('timestamp', '')).split('.')[0]
            
            st.markdown(f"""
            <div class="list-row">
                <div class="list-ico">{initial}</div>
                <div class="list-details">
                    <h5>{name}</h5>
                    <small>{sid} • {subj}</small>
                </div>
                <div class="list-action">
                    <span style="color: #9CA3AF; font-size: 0.85rem; font-weight: 500;">{time_str}</span>
                    <span class="badge-p">Verified</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ================= TODAY'S ATTENDANCE (LIVE FEED) =================
elif st.session_state.current_view == "today":
    st.markdown('<div class="section-title">📸 Live Verification Feed</div>', unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280; margin-top:-1rem; margin-bottom: 2rem;'>Audit real-time photo verifications.</p>", unsafe_allow_html=True)
    
    today = datetime.now().date()
    if attendance_df.empty:
        st.info("No data available.")
    else:
        today_df = attendance_df[attendance_df['date'] == today].merge(students_df[['email', 'name', 'student_id']], on='email', how='left')
        
        if today_df.empty:
            st.warning("No students have marked attendance today.")
        else:
            for index, row in today_df.iterrows():
                with st.container(border=True):
                    col_info, col_img1, col_img2 = st.columns([1.5, 1, 1])
                    
                    with col_info:
                        st.markdown(f"**{row.get('name', 'Unknown')}**")
                        st.caption(f"ID: `{row.get('student_id', 'N/A')}`")
                        st.caption(f"Subject: **{row.get('subject', 'N/A')}**")
                        st.caption(f"Time: {str(row.get('timestamp', '')).split('.')[0]}")
                        
                        score = row.get('similarity_score', 0)
                        try: score = float(score)
                        except: score = 0.0
                        
                        if score >= 0.7:
                            st.markdown(f'<span class="badge-p">Face Match: {score:.2f}</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<span class="badge-a">Bypass Match: {score:.2f}</span>', unsafe_allow_html=True)

                    with col_img1:
                        if 'selfie_path' in row and pd.notnull(row['selfie_path']) and os.path.exists(row['selfie_path']):
                            st.image(row['selfie_path'], width=120, caption="Identity")
                        else:
                            st.markdown('<div class="verify-img-container"><span style="color:#9CA3AF;font-size:3rem;">👤</span><div class="verify-img-label">No Selfie</div></div>', unsafe_allow_html=True)

                    with col_img2:
                         if 'classroom_path' in row and pd.notnull(row['classroom_path']) and os.path.exists(row['classroom_path']):
                            st.image(row['classroom_path'], width=120, caption="Context")
                         else:
                            st.markdown('<div class="verify-img-container"><span style="color:#9CA3AF;font-size:3rem;">🏫</span><div class="verify-img-label">No Context</div></div>', unsafe_allow_html=True)

# ================= VIEW ABSENTEES =================
elif st.session_state.current_view == "absentees":
    st.markdown('<div class="section-title">❌ Absentee Register</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        subjects = attendance_df['subject'].unique().tolist() if 'subject' in attendance_df.columns else []
        sel_subject = st.selectbox("Select Target Subject", subjects if subjects else ["All Classes"])
    with col2:
        sel_date = st.date_input("Select Date", datetime.now().date())
    st.markdown('</div>', unsafe_allow_html=True)
        
    if not attendance_df.empty:
        if sel_subject and sel_subject != "All Classes":
            present_emails = attendance_df[(attendance_df['date'] == sel_date) & (attendance_df['subject'] == sel_subject)]['email'].unique()
        else:
            present_emails = attendance_df[attendance_df['date'] == sel_date]['email'].unique()
    else:
        present_emails = []
        
    if not students_df.empty:
        absent_df = students_df[~students_df['email'].isin(present_emails)]
        
        if absent_df.empty:
            st.success("Perfect attendance today! 🎉")
        else:
            st.error(f"Alert: {len(absent_df)} students missing their mandatory check-in.")
            
            for index, row in absent_df.iterrows():
                name = row.get('name', 'Unknown')
                initial = name[0].upper() if name else '?'
                st.markdown(f"""
                <div class="list-row" style="border-left: 4px solid #EF4444;">
                    <div class="list-ico" style="background:#FEF2F2; color:#DC2626;">{initial}</div>
                    <div class="list-details">
                        <h5>{name}</h5>
                        <small>ID: {row.get('student_id', 'N/A')} • {row.get('section', 'N/A')}</small>
                    </div>
                    <div class="list-action">
                        <span class="badge-a">Absent</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No registered students found.")


# ================= PERFORMANCE ANALYTICS =================
elif st.session_state.current_view == "performance":
    st.markdown('<div class="section-title">📈 Actionable Analytics</div>', unsafe_allow_html=True)
    
    if attendance_df.empty or students_df.empty:
        st.info("Insufficient data to generate performance models.")
    else:
        # Calculate performance
        perf_data = []
        total_days = len(attendance_df['date'].dropna().unique())
        if total_days == 0: total_days = 1
        
        for index, student in students_df.iterrows():
            std_attendance = attendance_df[attendance_df['email'] == student['email']]
            present_count = len(std_attendance['date'].unique())
            absent_count = max(0, total_days - present_count)
            rate = (present_count / total_days * 100)
            
            perf_data.append({
                "Student": student['name'],
                "ID": student['student_id'],
                "Present (Days)": present_count,
                "Absent (Days)": absent_count,
                "Attendance %": round(rate, 1)
            })
        
        perf_df = pd.DataFrame(perf_data)
        
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            fig_bar = px.bar(
                perf_df, x="Student", y=["Present (Days)", "Absent (Days)"], 
                title="Cohort Attendance Distribution", 
                barmode="group",
                color_discrete_sequence=["#10B981", "#EF4444"]
            )
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'family': 'Inter'})
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with c2:
            risk_df = perf_df.sort_values("Attendance %").head(5)
            fig_pie = px.bar(
                risk_df, x="Attendance %", y="Student", 
                orientation='h',
                title="At-Risk Register (Lowest %)",
                color="Attendance %",
                color_continuous_scale="Reds_r"
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'family': 'Inter'})
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Detailed Performance Matrix</div>', unsafe_allow_html=True)
        st.dataframe(perf_df, use_container_width=True, hide_index=True)