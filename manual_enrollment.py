"""
Manual Face Enrollment Script
Run this script to manually enroll faces and extract embeddings
"""

import cv2
import numpy as np
import os
import pickle
from datetime import datetime

# Import from utils
from utils import extract_embedding, save_embedding, load_embedding

def capture_and_enroll():
    """Capture photos from webcam and create embeddings"""
    
    print("\n" + "="*60)
    print("🎓 ePortal - Manual Face Enrollment")
    print("="*60)
    
    # Get user email
    email = input("\n📧 Enter your email (used in registration): ").strip()
    
    if not email:
        print("❌ Email is required!")
        return
    
    print(f"\n✅ Enrolling face for: {email}")
    print("\n📸 We'll capture 3 photos of your face")
    print("   Press SPACE to capture each photo")
    print("   Press ESC to cancel\n")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Could not open webcam!")
        return
    
    print("🎥 Webcam opened successfully!")
    print("\nInstructions:")
    print("  - Face the camera directly")
    print("  - Ensure good lighting")
    print("  - Remove glasses if possible")
    print("  - Keep a neutral expression\n")
    
    captured_photos = []
    embeddings = []
    
    while len(captured_photos) < 3:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Failed to grab frame")
            break
        
        # Display the frame
        display_frame = frame.copy()
        
        # Add text overlay
        cv2.putText(display_frame, f"Photo {len(captured_photos) + 1}/3", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(display_frame, "Press SPACE to capture", 
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, "Press ESC to cancel", 
                    (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Face Enrollment', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # SPACE key to capture
        if key == 32:
            print(f"\n📸 Capturing photo {len(captured_photos) + 1}...")
            
            # Extract embedding
            embedding = extract_embedding(frame)
            
            if embedding is not None:
                captured_photos.append(frame)
                embeddings.append(embedding)
                print(f"✅ Photo {len(captured_photos)}/3 captured successfully!")
                
                # Save the photo for reference
                photo_path = f"enrollment_photo_{len(captured_photos)}.jpg"
                cv2.imwrite(photo_path, frame)
                print(f"   Saved to: {photo_path}")
            else:
                print("❌ Could not detect face. Please try again.")
                print("   Tips: Ensure good lighting and face the camera directly")
        
        # ESC key to cancel
        elif key == 27:
            print("\n❌ Enrollment cancelled")
            cap.release()
            cv2.destroyAllWindows()
            return
    
    cap.release()
    cv2.destroyAllWindows()
    
    if len(embeddings) == 3:
        print("\n" + "="*60)
        print("✅ All 3 photos captured successfully!")
        print("="*60)
        
        # Average the embeddings
        print("\n🔄 Processing embeddings...")
        avg_embedding = np.mean(embeddings, axis=0)
        
        # Save the embedding
        print(f"💾 Saving embedding for {email}...")
        save_embedding(email, avg_embedding)
        
        print("\n✅ Face enrollment completed successfully!")
        print(f"📁 Embedding saved for: {email}")
        
        # Verify it was saved
        loaded_emb = load_embedding(email)
        if loaded_emb is not None:
            print("✅ Verification: Embedding loaded successfully from database")
        else:
            print("⚠️  Warning: Could not verify saved embedding")
        
        print("\n🎉 You can now login and mark attendance!")
        print("="*60 + "\n")
    else:
        print("\n❌ Enrollment failed - not enough photos captured")

def list_enrolled_users():
    """List all enrolled users"""
    embeddings_file = "face_embeddings.pkl"
    
    if not os.path.exists(embeddings_file):
        print("\n📭 No enrolled users found")
        return
    
    try:
        with open(embeddings_file, "rb") as f:
            data = pickle.load(f)
        
        print("\n" + "="*60)
        print("👥 Enrolled Users")
        print("="*60)
        
        for idx, email in enumerate(data.keys(), 1):
            print(f"{idx}. {email}")
        
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Error reading enrollments: {e}")

def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("🎓 ePortal - Manual Face Enrollment Tool")
        print("="*60)
        print("\n1. Enroll New Face")
        print("2. List Enrolled Users")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            capture_and_enroll()
        elif choice == "2":
            list_enrolled_users()
        elif choice == "3":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Enrollment cancelled by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
