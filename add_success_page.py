"""
Script to add professional success page to attendance flow
Run this script to replace the current success display with the new animated success page
"""

import re

# Read the current app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the success display section
old_success_pattern = r'''                # Mark attendance in database
                mark_attendance\(st\.session_state\.email, session_id, subject, similarity\)
                
                # Show success message
                st\.success\("✅ Attendance Marked Successfully!"\)
                st\.balloons\(\)
                
                st\.markdown\(f"""
                    <div style='text-align: center; margin: 2rem 0; padding: 2rem; background: #D1FAE5; border-radius: 12px;'>
                        <h2 style='color: #065F46; margin-bottom: 1rem;'>✓ Attendance Recorded!</h2>
                        <p style='color: #1F2937; font-size: 1\.1rem; margin: 0\.5rem 0;'>
                            <strong>Subject:</strong> \{subject\}
                        </p>
                        <p style='color: #1F2937; font-size: 1\.1rem; margin: 0\.5rem 0;'>
                            <strong>Status:</strong> <span style='color: #10B981;'>Present</span>
                        </p>
                        <p style='color: #1F2937; font-size: 1\.1rem; margin: 0\.5rem 0;'>
                            <strong>Match Score:</strong> \{int\(similarity \* 100\)\}%
                        </p>
                    </div>
                """, unsafe_allow_html=True\)
                
                # Auto-redirect to dashboard
                st\.info\("Returning to dashboard\.\.\."\)
                import time
                time\.sleep\(1\)
                
                # Reset state
                st\.session_state\.attendance_step = 1
                st\.session_state\.current_session = None
                st\.session_state\.selfie_image = None
                
                # Navigate to dashboard
                navigate_to\("dashboard"\)
                st\.rerun\(\)'''

new_success_code = '''                # Mark attendance in database
                mark_attendance(st.session_state.email, session_id, subject, similarity)
                
                # Show professional success page
                if show_success_page(subject, similarity):
                    # Reset state
                    st.session_state.attendance_step = 1
                    st.session_state.current_session = None
                    st.session_state.selfie_image = None
                    
                    # Navigate to dashboard
                    navigate_to("dashboard")
                    st.rerun()'''

# Replace the section
if 'show_success_page' not in content:
    content = re.sub(old_success_pattern, new_success_code, content, flags=re.DOTALL)
    print("✅ Added professional success page")
else:
    print("⚠️ Success page already added")

# Write the modified content back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 Success page implementation complete!")
print("📝 Restart your Streamlit app to see the changes:")
print("   1. Press Ctrl+C in the terminal")
print("   2. Run: streamlit run app.py")
