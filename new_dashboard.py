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


