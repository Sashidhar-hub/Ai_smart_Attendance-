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


