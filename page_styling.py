"""
Page Background Manager for ePortal
Adds professional gradient backgrounds to each page
"""

import streamlit as st

def set_page_background(page_name):
    """
    Set professional gradient background for specific page
    
    Args:
        page_name: 'home', 'login', 'register', 'dashboard', 'attendance', or 'success'
    """
    
    backgrounds = {
        'home': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'login': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'register': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'dashboard': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'attendance': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        'success': 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    }
    
    gradient = backgrounds.get(page_name, backgrounds['home'])
    
    st.markdown(f"""
        <style>
            .stApp {{
                background: {gradient} !important;
                min-height: 100vh;
            }}
            
            /* Overlay pattern */
            .stApp::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    radial-gradient(circle at 20% 50%, rgba(255,255,255,.05) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(255,255,255,.05) 0%, transparent 50%);
                pointer-events: none;
                z-index: 0;
            }}
        </style>
    """, unsafe_allow_html=True)


def show_success_page(subject, similarity=0.0):
    """
    Display success page after attendance is marked
    
    Args:
        subject: Subject name
        similarity: Face match similarity score
    """
    from datetime import datetime
    import time
    
    # Set success page background
    set_page_background('success')
    
    # 🎈 BALLOONS ANIMATION!
    st.balloons()
    
    # Success message
    st.success("🎉 Attendance Marked Successfully!")
    
    # Success page HTML with enhanced animation
    st.markdown(f"""
        <div style='text-align: center; padding: 3rem; background: rgba(255,255,255,0.95); border-radius: 20px; margin: 2rem auto; max-width: 600px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); animation: fadeIn 0.5s ease-out;'>
            <div style='font-size: 5rem; margin-bottom: 1rem; animation: bounce 1s ease-in-out infinite;'>✅</div>
            <h1 style='color: #10B981; font-size: 2.5rem; margin-bottom: 1rem; font-weight: 800;'>Attendance Marked!</h1>
            <p style='color: #1F2937; font-size: 1.3rem; margin-bottom: 2rem;'>Your attendance has been successfully recorded</p>
            
            <div style='background: #F3F4F6; padding: 1.5rem; border-radius: 12px; margin: 2rem 0;'>
                <div style='display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem 0;'>
                    <span style='color: #6B7280; font-weight: 600;'>Subject:</span>
                    <span style='color: #111827; font-weight: 700;'>{subject}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem 0;'>
                    <span style='color: #6B7280; font-weight: 600;'>Status:</span>
                    <span style='color: #10B981; font-weight: 700;'>✓ Present</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem 0;'>
                    <span style='color: #6B7280; font-weight: 600;'>Match Score:</span>
                    <span style='color: #111827; font-weight: 700;'>{similarity:.1%}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem 0;'>
                    <span style='color: #6B7280; font-weight: 600;'>Time:</span>
                    <span style='color: #111827; font-weight: 700;'>{datetime.now().strftime("%I:%M %p")}</span>
                </div>
            </div>
            
            <p style='color: #6B7280; font-size: 0.9rem; margin-top: 2rem;'>🏠 Redirecting to dashboard in <span id="countdown">3</span> seconds...</p>
        </div>
        
        <style>
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-20px); }}
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: scale(0.9); }}
                to {{ opacity: 1; transform: scale(1); }}
            }}
        </style>
        
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
    
    # Wait 3 seconds
    time.sleep(3)
    
    return True  # Signal to redirect
