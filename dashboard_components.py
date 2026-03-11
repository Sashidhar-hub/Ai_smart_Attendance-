"""
Dashboard Components for ePortal
Provides functions for rendering the new dashboard layout
"""

import streamlit as st
from datetime import datetime
import pandas as pd
from attendance_analytics import load_attendance_data

def calculate_dashboard_stats(email):
    """
    Calculate statistics for dashboard cards
    
    Returns:
        dict with total_classes, this_month, overall_rate, monthly_rate
    """
    df = load_attendance_data(email)
    
    # Total classes (all time)
    total_classes = len(df)
    
    # This month's attendance
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    if len(df) > 0:
        this_month_df = df[
            (df['timestamp'].dt.month == current_month) & 
            (df['timestamp'].dt.year == current_year)
        ]
        this_month_count = len(this_month_df)
    else:
        this_month_count = 0
    
    # For now, assume 100% for attended classes (we only mark when present)
    # In production, you'd track total expected classes
    overall_rate = 100.0 if total_classes > 0 else 0.0
    monthly_rate = 100.0 if this_month_count > 0 else 0.0
    
    return {
        'total_classes': total_classes,
        'this_month': this_month_count,
        'overall_rate': overall_rate,
        'monthly_rate': monthly_rate
    }


def render_top_navigation(current_page, navigate_func):
    """
    Render top navigation bar
    """
    st.markdown("""
        <style>
            .top-nav {
                background: white;
                padding: 1rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 2rem;
            }
            .nav-logo {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 1.2rem;
                font-weight: 700;
                color: #1F2937;
            }
            .nav-links {
                display: flex;
                gap: 2rem;
                align-items: center;
            }
            .nav-link {
                color: #6B7280;
                text-decoration: none;
                font-weight: 500;
                cursor: pointer;
                transition: color 0.2s;
            }
            .nav-link:hover {
                color: #4F7CFF;
            }
            .nav-link.active {
                color: #4F7CFF;
                font-weight: 700;
            }
        </style>
        
        <div class='top-nav'>
            <div class='nav-logo'>
                🎓 Smart AI Attendance
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1.5, 1, 1])
    
    with col2:
        if st.button("🏠 Dashboard", use_container_width=True):
            navigate_func("dashboard")
    
    with col3:
        if st.button("📱 Mark Attendance", use_container_width=True):
            navigate_func("mark_attendance")
    
    with col4:
        if st.button("📊 History", use_container_width=True):
            navigate_func("history")
    
    with col5:
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.session_state.email = None
            navigate_func("home")


def render_welcome_banner(name, email, monthly_percentage):
    """
    Render welcome banner with profile and monthly stats
    """
    # Extract roll number from email or use default
    roll_no = email.split('@')[0].upper() if email else "STUDENT"
    
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #4F7CFF 0%, #6B8FFF 100%);
            padding: 2.5rem;
            border-radius: 20px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(79, 124, 255, 0.3);
        '>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='display: flex; gap: 1.5rem; align-items: center;'>
                    <div style='
                        width: 80px;
                        height: 80px;
                        border-radius: 50%;
                        background: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 2.5rem;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    '>
                        👤
                    </div>
                    <div>
                        <p style='margin: 0; font-size: 0.9rem; opacity: 0.9;'>Welcome back,</p>
                        <h1 style='margin: 0.5rem 0; font-size: 2rem; font-weight: 800;'>{name}</h1>
                        <p style='margin: 0; font-size: 0.95rem; opacity: 0.85;'>{roll_no}</p>
                    </div>
                </div>
                <div style='
                    background: rgba(255,255,255,0.2);
                    padding: 1.5rem 2rem;
                    border-radius: 16px;
                    text-align: center;
                    backdrop-filter: blur(10px);
                '>
                    <p style='margin: 0; font-size: 0.85rem; opacity: 0.9;'>📈 This Month</p>
                    <h1 style='margin: 0.5rem 0; font-size: 2.5rem; font-weight: 800;'>{monthly_percentage:.0f}%</h1>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_statistics_cards(stats):
    """
    Render 4 statistics cards
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <p style='margin: 0; color: #6B7280; font-size: 0.9rem;'>Total Classes</p>
                        <h2 style='margin: 0.5rem 0; color: #1F2937; font-size: 2rem; font-weight: 800;'>{stats['total_classes']}</h2>
                        <p style='margin: 0; color: #9CA3AF; font-size: 0.85rem;'>All time</p>
                    </div>
                    <div style='font-size: 2rem;'>📚</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <p style='margin: 0; color: #6B7280; font-size: 0.9rem;'>This Month</p>
                        <h2 style='margin: 0.5rem 0; color: #1F2937; font-size: 2rem; font-weight: 800;'>{stats['this_month']}</h2>
                        <p style='margin: 0; color: #9CA3AF; font-size: 0.85rem;'>Classes attended</p>
                    </div>
                    <div style='font-size: 2rem;'>📅</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <p style='margin: 0; color: #6B7280; font-size: 0.9rem;'>Overall Rate</p>
                        <h2 style='margin: 0.5rem 0; color: #1F2937; font-size: 2rem; font-weight: 800;'>{stats['overall_rate']:.0f}%</h2>
                        <p style='margin: 0; color: #9CA3AF; font-size: 0.85rem;'>Attendance</p>
                    </div>
                    <div style='font-size: 2rem;'>📊</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <p style='margin: 0; color: #6B7280; font-size: 0.9rem;'>Monthly Rate</p>
                        <h2 style='margin: 0.5rem 0; color: #1F2937; font-size: 2rem; font-weight: 800;'>{stats['monthly_rate']:.0f}%</h2>
                        <p style='margin: 0; color: #9CA3AF; font-size: 0.85rem;'>This month</p>
                    </div>
                    <div style='font-size: 2rem;'>📈</div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_quick_actions(navigate_func):
    """
    Render quick action buttons
    """
    st.markdown("### Quick Actions")
    st.markdown("<br/>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); cursor: pointer;' onclick='markAttendance()'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div style='display: flex; gap: 1.5rem; align-items: center;'>
                        <div style='
                            width: 60px;
                            height: 60px;
                            border-radius: 12px;
                            background: linear-gradient(135deg, #4F7CFF, #6B8FFF);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 1.8rem;
                        '>
                            📱
                        </div>
                        <div>
                            <h3 style='margin: 0; color: #1F2937; font-size: 1.2rem;'>Mark Attendance</h3>
                            <p style='margin: 0.5rem 0 0 0; color: #6B7280; font-size: 0.9rem;'>Scan QR code to mark your attendance</p>
                        </div>
                    </div>
                    <div style='font-size: 1.5rem; color: #9CA3AF;'>→</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📱 Mark Attendance", key="quick_mark", use_container_width=True):
            navigate_func("mark_attendance")
    
    with col2:
        st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div style='display: flex; gap: 1.5rem; align-items: center;'>
                        <div style='
                            width: 60px;
                            height: 60px;
                            border-radius: 12px;
                            background: linear-gradient(135deg, #34C759, #30D158);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 1.8rem;
                        '>
                            📊
                        </div>
                        <div>
                            <h3 style='margin: 0; color: #1F2937; font-size: 1.2rem;'>Attendance History</h3>
                            <p style='margin: 0.5rem 0 0 0; color: #6B7280; font-size: 0.9rem;'>View your complete attendance record</p>
                        </div>
                    </div>
                    <div style='font-size: 1.5rem; color: #9CA3AF;'>→</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Attendance History", key="quick_history", use_container_width=True):
            navigate_func("history")


def render_recent_attendance(email):
    """
    Render recent attendance list
    """
    st.markdown("### Recent Attendance")
    st.markdown("<br/>", unsafe_allow_html=True)
    
    df = load_attendance_data(email)
    
    if len(df) == 0:
        st.info("📭 No attendance records yet. Start marking attendance!")
        return
    
    # Get last 5 records
    recent_df = df.head(5)
    
    for idx, row in recent_df.iterrows():
        date_str = row['timestamp'].strftime('%a, %b %d')
        match_pct = int(row['match_score'] * 100)
        
        st.markdown(f"""
            <div style='
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 0.75rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                display: flex;
                justify-content: space-between;
                align-items: center;
            '>
                <div style='display: flex; gap: 1rem; align-items: center;'>
                    <div style='
                        width: 40px;
                        height: 40px;
                        border-radius: 8px;
                        background: #E8F5E9;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.2rem;
                    '>
                        📅
                    </div>
                    <div>
                        <h4 style='margin: 0; color: #1F2937; font-size: 1rem; font-weight: 600;'>{row['subject']}</h4>
                        <p style='margin: 0.25rem 0 0 0; color: #6B7280; font-size: 0.85rem;'>{date_str}</p>
                    </div>
                </div>
                <div style='text-align: right;'>
                    <span style='
                        background: #D1FAE5;
                        color: #065F46;
                        padding: 0.4rem 0.8rem;
                        border-radius: 6px;
                        font-size: 0.85rem;
                        font-weight: 600;
                    '>
                        ✅ Present
                    </span>
                    <p style='margin: 0.5rem 0 0 0; color: #6B7280; font-size: 0.85rem;'>{match_pct}% match</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
