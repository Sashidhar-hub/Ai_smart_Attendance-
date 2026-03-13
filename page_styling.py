"""
Page Background Manager for ePortal
Clean, professional look for all pages
"""

import streamlit as st

def set_page_background(page_name):
    """
    Set clean professional background for all pages.
    All pages share the same clean white/gray bg to match
    the reference design.
    """
    st.markdown("""
        <style>
            /* Clean white background for ALL pages */
            .stApp {
                background: #F9FAFB !important;
                min-height: 100vh;
            }
            .stApp::before {
                display: none !important;
            }
            
            /* Global Font and Styles */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }
        </style>
    """, unsafe_allow_html=True)


def show_success_page(subject, similarity=0.0):
    """
    Display success page after attendance is marked
    Matching the Base44 design vibes
    """
    from datetime import datetime
    import time
    
    set_page_background('success')
    st.balloons()
    
    # Success page HTML matching Base44 design
    st.markdown(f"""
        <div style='text-align: center; padding: 3rem; background: white; border-radius: 24px; margin: 3rem auto; max-width: 550px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); border: 1px solid #E5E7EB;'>
            <div style='width: 80px; height: 80px; background: #ECFDF5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem;'>
                <span style='font-size: 3rem;'>✅</span>
            </div>
            <h1 style='color: #059669; font-size: 1.875rem; margin-bottom: 0.5rem; font-weight: 700;'>Attendance Marked!</h1>
            <p style='color: #6B7280; font-size: 1rem; margin-bottom: 2rem;'>Your attendance has been successfully recorded</p>
            
            <div style='background: #F9FAFB; padding: 1.5rem; border-radius: 16px; margin: 2rem 0; text-align: left; border: 1px solid #F3F4F6;'>
                <div style='display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #F3F4F6;'>
                    <span style='color: #6B7280; font-weight: 500;'>Subject:</span>
                    <span style='color: #111827; font-weight: 600;'>{subject}</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #F3F4F6;'>
                    <span style='color: #6B7280; font-weight: 500;'>Status:</span>
                    <span style='color: #10B981; font-weight: 600;'>✓ Present</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #F3F4F6;'>
                    <span style='color: #6B7280; font-weight: 500;'>Match Score:</span>
                    <span style='color: #111827; font-weight: 600;'>{similarity:.1%}</span>
                </div>
                <div style='display: flex; justify-content: space-between; padding: 0.75rem 0;'>
                    <span style='color: #6B7280; font-weight: 500;'>Time:</span>
                    <span style='color: #111827; font-weight: 600;'>{datetime.now().strftime("%I:%M %p")}</span>
                </div>
            </div>
            
            <p style='color: #9CA3AF; font-size: 0.875rem; margin-top: 2rem;'>Redirecting to dashboard in <span id="countdown">3</span> seconds...</p>
        </div>
        
        <script>
            let countdown = 3;
            const countdownElement = document.getElementById('countdown');
            const interval = setInterval(() => {{
                countdown--;
                if (countdownElement) {{
                    countdownElement.textContent = countdown;
                }}
                if (countdown <= 0) {{
                    clearInterval(interval);
                }}
            }}, 1000);
        </script>
    """, unsafe_allow_html=True)
    
    time.sleep(3)
    return True
