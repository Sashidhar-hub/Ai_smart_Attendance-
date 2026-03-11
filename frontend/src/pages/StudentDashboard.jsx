import React, { useRef, useState, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import api from '../api';
import { Camera, CheckCircle, XCircle, LogOut, ScanLine, Book, ChevronRight, ArrowLeft, Upload } from 'lucide-react';
import jsQR from 'jsqr';

const StudentDashboard = ({ user, setAuth }) => {
    // Mode Logic: 'dashboard' -> 'scanner'
    const [mode, setMode] = useState('dashboard');
    const [selectedSubject, setSelectedSubject] = useState(null);

    // Scanner Refs and States
    const webcamRef = useRef(null);
    const canvasRef = useRef(null);
    const fileInputRef = useRef(null);
    const [sessionCode, setSessionCode] = useState('');
    const [status, setStatus] = useState('Looking for QR code...');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [hasScanned, setHasScanned] = useState(false);

    // The main scanning loop function
    const scanQR = useCallback(() => {
        // If we're already loading or have successfully scanned, stop scanning for a moment
        if (loading || hasScanned) return;

        if (
            webcamRef.current &&
            webcamRef.current.video &&
            webcamRef.current.video.readyState === webcamRef.current.video.HAVE_ENOUGH_DATA
        ) {
            const video = webcamRef.current.video;
            const canvas = canvasRef.current;
            const context = canvas.getContext('2d', { willReadFrequently: true });

            // Match canvas dimensions to video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height, {
                inversionAttempts: "dontInvert",
            });

            if (code && code.data) {
                // QR Code Found! Stop scanning immediately and lock in the code
                setSessionCode(code.data);
                setHasScanned(true);
                captureAndMark(code.data); // trigger capture automatically
            }
        }
    }, [loading, hasScanned]);

    // Set up the scanning loop (runs 4 times a second)
    useEffect(() => {
        let interval;
        if (!hasScanned && !loading) {
            interval = setInterval(scanQR, 250);
        }
        return () => clearInterval(interval);
    }, [scanQR, hasScanned, loading]);

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const context = canvas.getContext('2d');
                context.drawImage(img, 0, 0, img.width, img.height);
                
                const imageData = context.getImageData(0, 0, img.width, img.height);
                const code = jsQR(imageData.data, imageData.width, imageData.height, {
                    inversionAttempts: "dontInvert",
                });

                if (code && code.data) {
                    setSessionCode(code.data);
                    setHasScanned(true);
                    captureAndMark(code.data);
                } else {
                    setStatus("No QR Code found in the uploaded image. Please try again.");
                }
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    };

    async function captureAndMark(scannedCode) {
        const imageSrc = webcamRef.current?.getScreenshot();
        if (!imageSrc) {
            setStatus('QR Found, but could not capture selfie. Please try again.');
            setHasScanned(false);
            return;
        }

        setLoading(true);
        setStatus(`QR Code detected: ${scannedCode}. Analyzing Face in real-time...`);

        try {
            const fetchResponse = await fetch(imageSrc);
            const blob = await fetchResponse.blob();
            const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });

            const formData = new FormData();
            formData.append('user_id', user.id);
            formData.append('session_code', scannedCode);
            formData.append('file', file);

            await api.post('/mark-attendance', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            setSuccess(true);
            setStatus('Verification Complete! Attendance Marked.');
        } catch (err) {
            setSuccess(false);
            setStatus(err.response?.data?.detail || 'Face verification failed');
            // Briefly pause, then let them try scanning again
            setTimeout(() => setHasScanned(false), 3000);
        }
        setLoading(false);
    }

    const handleLogout = () => {
        localStorage.clear();
        setAuth(null);
    };

    const resetScanner = () => {
        setHasScanned(false);
        setSessionCode('');
        setSuccess(false);
        setStatus('Looking for QR code...');
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
            {/* Hidden canvas for jsQR processing */}
            <canvas ref={canvasRef} style={{ display: 'none' }} />

            {/* Common Header */}
            <div className="w-full max-w-2xl flex justify-between items-center mb-8 bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-xl">
                        {user.name.charAt(0)}
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-gray-800">{user.name}</h2>
                        <p className="text-sm text-gray-500">Student ID: {user.student_id || 'N/A'}</p>
                    </div>
                </div>
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 text-red-600 font-medium"
                >
                    <LogOut size={18} /> Logout
                </button>
            </div>

            {/* DASHBOARD MODE: Choose Subject */}
            {mode === 'dashboard' && (
                <div className="w-full max-w-2xl bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                    <div className="p-6 border-b border-gray-100">
                        <h3 className="text-xl font-bold text-gray-900">Your Classes</h3>
                        <p className="text-gray-500">Select a subject to mark attendance</p>
                    </div>
                    <div className="p-6 space-y-4">
                        {/* Mock Subjects */}
                        {['Computer Science 101', 'Advanced Mathematics', 'Physics I'].map((subj, i) => (
                            <div 
                                key={subj}
                                onClick={() => {
                                    setSelectedSubject(subj);
                                    setMode('scanner');
                                }}
                                className="flex items-center justify-between p-4 bg-gray-50 hover:bg-blue-50 border border-transparent hover:border-blue-200 cursor-pointer rounded-xl transition-all"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-white shadow-sm rounded-lg text-blue-600">
                                        <Book size={24} />
                                    </div>
                                    <h4 className="font-bold text-lg text-gray-800">{subj}</h4>
                                </div>
                                <ChevronRight className="text-gray-400" />
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* SCANNER MODE: Live Feed */}
            {mode === 'scanner' && (
                <div className="w-full max-w-2xl bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                    <div className="bg-blue-600 p-4 text-white flex items-center gap-4">
                        <button 
                            onClick={() => { setMode('dashboard'); resetScanner(); }}
                            className="p-2 hover:bg-blue-700 rounded-lg transition-colors"
                        >
                            <ArrowLeft />
                        </button>
                        <div>
                            <h1 className="text-xl font-bold">{selectedSubject} Attendance</h1>
                            <p className="text-blue-100 text-sm mt-0.5">Show the QR Code to the camera</p>
                        </div>
                    </div>

                    <div className="p-8 space-y-6">
                        {/* Status Message */}
                        <div className={`p-4 rounded-xl flex items-center justify-center gap-3 transition-colors ${success ? 'bg-green-50 text-green-700 border border-green-200' :
                                loading ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                                    hasScanned ? 'bg-red-50 text-red-700 border border-red-200' :
                                        'bg-gray-50 text-gray-700 border border-gray-200'
                            }`}>
                            {success ? <CheckCircle className="flex-shrink-0" /> :
                                hasScanned && !loading ? <XCircle className="flex-shrink-0" /> :
                                    <ScanLine className={`flex-shrink-0 ${!hasScanned ? "animate-pulse delay-100" : ""} ${loading ? "animate-pulse" : ""}`} />}
                            <span className="font-semibold text-center w-full">{status}</span>
                        </div>

                        <div className="relative rounded-2xl overflow-hidden bg-black aspect-video flex items-center justify-center shadow-inner border-4 border-gray-800" style={{ '--tw-border-opacity': hasScanned ? 0.3 : 1 }}>
                            <Webcam
                                audio={false}
                                ref={webcamRef}
                                screenshotFormat="image/jpeg"
                                videoConstraints={{ facingMode: "user" }}
                                className="w-full object-cover opacity-90"
                            />
                            {!hasScanned && (
                                <div className="absolute inset-0 pointer-events-none">
                                    <div className="w-full h-full relative">
                                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 border-2 border-white/50 rounded-xl flex items-center justify-center">
                                            <div className="w-full h-0.5 bg-green-400 absolute animate-[scan_2s_ease-in-out_infinite]" style={{ top: '0%', left: 0 }} />
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            {loading && (
                                <div className="absolute inset-0 bg-white animate-pulse opacity-50 pointer-events-none"></div>
                            )}
                        </div>

                        {!hasScanned && !loading && (
                            <div className="flex flex-col gap-3">
                                <input 
                                    type="file" 
                                    accept="image/*" 
                                    className="hidden" 
                                    ref={fileInputRef} 
                                    onChange={handleFileUpload}
                                />
                                <button
                                    onClick={() => fileInputRef.current.click()}
                                    className="w-full py-4 bg-gray-100 hover:bg-gray-200 text-gray-800 text-lg font-bold rounded-xl shadow transition-colors flex items-center justify-center gap-2"
                                >
                                    <Upload /> Upload QR Image manually
                                </button>
                            </div>
                        )}

                        {hasScanned && !loading && (
                            <button
                                onClick={resetScanner}
                                className="w-full py-4 bg-gray-100 hover:bg-gray-200 text-gray-800 text-lg font-bold rounded-xl shadow transition-colors flex items-center justify-center gap-2"
                            >
                                <Camera /> Scan Again
                            </button>
                        )}
                    </div>
                </div>
            )}

            <style dangerouslySetInnerHTML={{
                __html: `
                @keyframes scan {
                  0%, 100% { top: 0%; opacity: 0; }
                  10% { opacity: 1; }
                  50% { top: 100%; }
                  90% { opacity: 1; }
                }
              `}} />
        </div>
    );
};

export default StudentDashboard;
