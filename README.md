# ePortal - Smart AI Attendance Management System

An intelligent attendance management system using face recognition, QR code scanning, and classroom verification.

## 🎯 Features

- **Face Recognition** - FaceNet-based face verification
- **QR Code Scanning** - Camera or upload QR codes
- **Liveness Detection** - Prevents spoofing attacks
- **Classroom Verification** - YOLO-based classroom detection
- **Manual Enrollment** - Standalone script for face enrollment
- **Auto-Attendance Marking** - Simplified 3-step process

## 📋 Requirements

```
streamlit
opencv-python
numpy
tensorflow
keras
ultralytics
pandas
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/Sashidhar-hub/smart-ai-attendance.git
cd smart-ai-attendance
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download FaceNet model:
- Place `facenet_keras.h5` in the `models/` folder

## 💻 Usage

### Run the Streamlit App
```bash
streamlit run app.py
```

### Manual Face Enrollment
```bash
python manual_enrollment.py
```

### Generate QR Codes
```bash
python qr_generator.py
```

## 📁 Project Structure

```
smart-ai-attendance/
├── app.py                    # Main Streamlit application
├── utils.py                  # Utility functions (AI models, embeddings)
├── manual_enrollment.py      # Manual face enrollment script
├── qr_generator.py          # QR code generator for subjects
├── classroom_ai.py          # Classroom verification
├── requirements.txt         # Python dependencies
├── models/                  # AI models folder
│   └── facenet_keras.h5    # FaceNet model (download separately)
├── data/                    # Data storage
│   ├── users.csv           # User database
│   ├── embeddings.pkl      # Face embeddings
│   └── attendance.csv      # Attendance records
└── qr_codes/               # Generated QR codes
    ├── qr_compiler_design.png
    ├── qr_agile_development.png
    └── ...
```

## 🎓 Subjects

The system supports attendance for 7 subjects:
1. Compiler Design
2. Agile Development
3. Parallel Distribution
4. Aptitude
5. Soft Skills
6. Verbal Ability
7. Deep Learning

## 🔄 Attendance Flow

1. **Register** - Create account
2. **Login** - Sign in to dashboard
3. **Select Subject** - Choose from 7 subjects
4. **Scan QR Code** - Camera or upload
5. **Capture Selfie** - Liveness verification
6. **Capture Classroom** - Back camera
7. **Auto-Mark Present** - Automatic attendance marking
8. **Return to Dashboard** - Auto-redirect

## 🛠️ Technologies

- **Frontend**: Streamlit
- **Face Recognition**: FaceNet (128-d embeddings)
- **Face Detection**: OpenCV Haar Cascade
- **Object Detection**: YOLOv8
- **QR Code**: OpenCV QR Detector
- **Database**: CSV files

## 📸 Face Enrollment

### Option 1: During Registration
- Automatic enrollment after account creation (if enabled)

### Option 2: Manual Script
```bash
python manual_enrollment.py
```
- Captures 3 photos
- Averages embeddings for better accuracy
- Saves to database

### Option 3: In-App Enrollment
- Available from dashboard for logged-in users

## 🔐 Security Features

- **Liveness Detection** - Prevents photo spoofing
- **Face Verification** - Matches live selfie with enrolled face
- **Classroom Verification** - Ensures attendance from classroom
- **Session-based QR Codes** - Time-stamped QR codes

## 📊 Attendance Records

Attendance is stored in `data/attendance.csv` with:
- Email
- Session ID
- Subject
- Timestamp
- Match Score

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Sashidhar

## 🙏 Acknowledgments

- FaceNet for face recognition
- YOLOv8 for object detection
- Streamlit for the web framework
