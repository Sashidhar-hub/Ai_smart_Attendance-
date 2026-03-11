"""
Script to add file upload options for mobile camera access
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add file upload for selfie (Step 2)
old_selfie = '''        selfie = st.camera_input("📷 Capture Your Face")
        
        if selfie:
            file_bytes = np.asarray(bytearray(selfie.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)'''

new_selfie = '''        # Camera input (may not work on mobile HTTP)
        selfie = st.camera_input("📷 Capture Your Face")
        
        # File upload (works on mobile)
        st.markdown("**OR Upload Photo** (Use this if camera doesn't work on mobile)")
        uploaded_selfie = st.file_uploader("📤 Upload Selfie", type=['jpg', 'jpeg', 'png'], key="selfie_upload")
        
        # Use whichever is provided
        image_source = selfie if selfie else uploaded_selfie
        
        if image_source:
            file_bytes = np.asarray(bytearray(image_source.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)'''

content = content.replace(old_selfie, new_selfie)

# Add file upload for classroom (Step 3)
old_classroom = '''        classroom_img = st.camera_input("📷 Capture Classroom View")
        
        if classroom_img:
            cb = np.asarray(bytearray(classroom_img.read()), dtype=np.uint8)
            c_img = cv2.imdecode(cb, 1)'''

new_classroom = '''        # Camera input (may not work on mobile HTTP)
        classroom_img = st.camera_input("📷 Capture Classroom View")
        
        # File upload (works on mobile)
        st.markdown("**OR Upload Photo** (Use this if camera doesn't work on mobile)")
        uploaded_classroom = st.file_uploader("📤 Upload Classroom Photo", type=['jpg', 'jpeg', 'png'], key="classroom_upload")
        
        # Use whichever is provided
        image_source = classroom_img if classroom_img else uploaded_classroom
        
        if image_source:
            cb = np.asarray(bytearray(image_source.read()), dtype=np.uint8)
            c_img = cv2.imdecode(cb, 1)'''

content = content.replace(old_classroom, new_classroom)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added file upload options for mobile!")
print("\n📱 Now students can:")
print("  1. Use camera (if HTTPS or localhost)")
print("  2. Upload photo from gallery (works on mobile HTTP)")
print("\n🔄 App will auto-reload with changes!")
