"""
Script to update app.py with new dashboard and history page
"""

# Read files
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

with open('new_dashboard.py', 'r', encoding='utf-8') as f:
    new_dashboard = f.read()

with open('history_page.py', 'r', encoding='utf-8') as f:
    history_page = f.read()

# Find dashboard section
dashboard_start = app_content.find('# =========================\n# DASHBOARD\n# =========================\nelif st.session_state.current_page == "dashboard" and st.session_state.logged_in:')
dashboard_end = app_content.find('# =========================\n# MARK ATTENDANCE\n# =========================', dashboard_start)

if dashboard_start == -1 or dashboard_end == -1:
    print("❌ Could not find dashboard section")
    exit(1)

# Replace dashboard section
new_content = app_content[:dashboard_start] + new_dashboard + '\n' + app_content[dashboard_end:]

# Find enroll_face section to insert history page before it
enroll_start = new_content.find('# =========================\n# FACE ENROLLMENT (FOR LOGGED-IN USERS)\n# =========================\nelif st.session_state.current_page == "enroll_face"')

if enroll_start == -1:
    print("❌ Could not find enroll_face section")
    exit(1)

# Insert history page before enroll_face
final_content = new_content[:enroll_start] + history_page + '\n\n' + new_content[enroll_start:]

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("✅ Dashboard updated successfully!")
print("✅ History page inserted successfully!")
print("\n📝 Changes made:")
print("  - Replaced old dashboard with new design")
print("  - Added navigation bar")
print("  - Added welcome banner")
print("  - Added statistics cards")
print("  - Added quick actions")
print("  - Added recent attendance list")
print("  - Inserted history page with analytics")
print("\n🔄 Restart Streamlit to see changes!")
