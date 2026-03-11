"""
Script to add professional gradient backgrounds to ePortal app.py
Run this script to automatically inject background styling into each page
"""

import re

# Read the current app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import at the top (after existing imports)
if 'from page_styling import' not in content:
    content = content.replace(
        'from utils import *',
        'from utils import *\nfrom page_styling import set_page_background, show_success_page'
    )
    print("✅ Added page_styling import")

# Add background call to home page
if 'if st.session_state.current_page == "home"' in content and 'set_page_background(\'home\')' not in content:
    content = content.replace(
        'if st.session_state.current_page == "home" and not st.session_state.logged_in:',
        'if st.session_state.current_page == "home" and not st.session_state.logged_in:\n    set_page_background(\'home\')'
    )
    print("✅ Added home page background")

# Add background call to login page  
if '"login"' in content and 'set_page_background(\'login\')' not in content:
    # Find login page section
    login_pattern = r'(elif st\.session_state\.current_page == "login":)'
    content = re.sub(login_pattern, r'\1\n    set_page_background(\'login\')', content, count=1)
    print("✅ Added login page background")

# Add background call to register page
if '"register"' in content and 'set_page_background(\'register\')' not in content:
    register_pattern = r'(elif st\.session_state\.current_page == "register":)'
    content = re.sub(register_pattern, r'\1\n    set_page_background(\'register\')', content, count=1)
    print("✅ Added register page background")

# Add background call to dashboard
if '"dashboard"' in content and 'set_page_background(\'dashboard\')' not in content:
    dashboard_pattern = r'(elif st\.session_state\.current_page == "dashboard" and st\.session_state\.logged_in:)'
    content = re.sub(dashboard_pattern, r'\1\n    set_page_background(\'dashboard\')', content, count=1)
    print("✅ Added dashboard background")

# Add background call to mark_attendance page
if '"mark_attendance"' in content and 'set_page_background(\'attendance\')' not in content:
    attendance_pattern = r'(elif st\.session_state\.current_page == "mark_attendance" and st\.session_state\.logged_in:)'
    content = re.sub(attendance_pattern, r'\1\n    set_page_background(\'attendance\')', content, count=1)
    print("✅ Added attendance page background")

# Write the modified content back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎨 Professional backgrounds added successfully!")
print("📝 Restart your Streamlit app to see the changes:")
print("   1. Press Ctrl+C in the terminal")
print("   2. Run: streamlit run app.py")
