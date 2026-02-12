# face_register.py
import streamlit as st
from face_ai import extract_embedding, save_embedding
from liveness_ai import is_live_image
import cv2

def run_face_registration(email):
    st.subheader("📸 Capture 3–5 clear face images")
    st.write("Ensure good lighting, no glasses/hats, and look directly at camera.")
    
    images = []
    for i in range(1, 6):
        st.write(f"**Image {i}**")
        img_file = st.camera_input(f"Take photo {i}", key=f"cam_{i}")
        if img_file:
            img_array = np.frombuffer(img_file.getvalue(), np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if is_live_image(frame):
                emb = extract_embedding(frame)
                if emb is not None:
                    images.append(emb)
                    st.success("✅ Face detected and encoded!")
                else:
                    st.warning("⚠️ Could not extract face. Try again.")
            else:
                st.error("❌ Not a live image — please retake.")
        else:
            break
    
    if len(images) >= 3:
        avg_emb = np.mean(images, axis=0)
        save_embedding(email, avg_emb)
        st.success(f"🎉 Registration complete! {len(images)} embeddings saved.")
        st.session_state.registered = True
        st.button("Go to Dashboard", on_click=lambda: st.session_state.update(current_page="dashboard"))