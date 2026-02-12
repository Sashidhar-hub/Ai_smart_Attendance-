import qrcode
import json
import os

def generate_qr(session_id, subject):
    data = {
        "session_id": session_id,
        "subject": subject,
        "date": "2026-02-11" # Current date for validation
    }
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(data))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    filename = f"qr_{session_id}.png"
    img.save(filename)
    print(f"Generated QR code: {filename}")
    print(f"Data: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    # Install qrcode if missing: pip install qrcode[pil]
    try:
        import qrcode
    except ImportError:
        os.system("pip install qrcode[pil]")
        import qrcode
    
    from datetime import datetime
    
    # Create qr_codes directory if it doesn't exist
    if not os.path.exists("qr_codes"):
        os.makedirs("qr_codes")
        print("Created qr_codes directory")
    
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # List of all 7 subjects
    subjects = [
        "Compiler Design",
        "Agile Development",
        "Parallel Distribution",
        "Aptitude",
        "Soft Skills",
        "Verbal Ability",
        "Deep Learning"
    ]
    
    print(f"\n🎓 Generating QR Codes for ePortal Subjects")
    print(f"📅 Date: {current_date}\n")
    print("=" * 60)
    
    # Generate QR code for each subject
    for idx, subject in enumerate(subjects, 1):
        # Create session ID
        subject_code = subject.upper().replace(" ", "-")
        session_id = f"SESSION-{subject_code}-{idx:03d}"
        
        # Generate QR code data
        data = {
            "session_id": session_id,
            "subject": subject,
            "date": current_date
        }
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to qr_codes folder
        filename = f"qr_codes/qr_{subject.lower().replace(' ', '_')}.png"
        img.save(filename)
        
        print(f"✅ {idx}. {subject}")
        print(f"   📄 File: {filename}")
        print(f"   🔑 Session ID: {session_id}")
        print()
    
    print("=" * 60)
    print(f"\n✨ Successfully generated {len(subjects)} QR codes!")
    print(f"📁 Location: qr_codes/ folder\n")
