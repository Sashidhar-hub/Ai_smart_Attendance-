import React, { useRef, useState, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import api from '../api';
import {
    Camera, CheckCircle, XCircle, LogOut, ScanLine,
    ChevronRight, ArrowLeft, Upload, LayoutDashboard,
    QrCode, History, TrendingUp, CalendarDays
} from 'lucide-react';
import jsQR from 'jsqr';

const StudentDashboard = ({ user, setAuth }) => {
    const [mode, setMode] = useState('dashboard');
    const [selectedSubject, setSelectedSubject] = useState(null);
    const [attendance, setAttendance] = useState([]);
    const [stats, setStats] = useState({ total: 0, thisMonth: 0, overall: 0, monthly: 0 });

    // Scanner State
    const webcamRef = useRef(null);
    const canvasRef = useRef(null);
    const fileInputRef = useRef(null);
    const [sessionCode, setSessionCode] = useState('');
    const [status, setStatus] = useState('Looking for QR code...');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [hasScanned, setHasScanned] = useState(false);

    // Fetch attendance records from the API
    useEffect(() => {
        const fetchAttendance = async () => {
            try {
                const res = await api.get(`/attendance?user_id=${user.id}`);
                const records = res.data || [];
                setAttendance(records);

                const now = new Date();
                const thisMonthRecords = records.filter(r => {
                    const d = new Date(r.timestamp);
                    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
                });

                const total = records.length;
                const thisMonth = thisMonthRecords.length;
                const overall = total > 0 ? Math.round((records.filter(r => r.status === 'Present').length / total) * 100) : 0;
                const monthly = thisMonth > 0 ? Math.round((thisMonthRecords.filter(r => r.status === 'Present').length / thisMonth) * 100) : 0;
                setStats({ total, thisMonth, overall, monthly });
            } catch {
                // No attendance yet
            }
        };
        fetchAttendance();
    }, [user.id, success]);

    const scanQR = useCallback(() => {
        if (loading || hasScanned) return;
        if (webcamRef.current?.video?.readyState === webcamRef.current.video.HAVE_ENOUGH_DATA) {
            const video = webcamRef.current.video;
            const canvas = canvasRef.current;
            const context = canvas.getContext('2d', { willReadFrequently: true });
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: 'dontInvert' });
            if (code?.data) {
                setSessionCode(code.data);
                setHasScanned(true);
                captureAndMark(code.data);
            }
        }
    }, [loading, hasScanned]);

    useEffect(() => {
        let interval;
        if (!hasScanned && !loading && mode === 'scanner') {
            interval = setInterval(scanQR, 250);
        }
        return () => clearInterval(interval);
    }, [scanQR, hasScanned, loading, mode]);

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
                canvas.getContext('2d').drawImage(img, 0, 0);
                const imageData = canvas.getContext('2d').getImageData(0, 0, img.width, img.height);
                const code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: 'dontInvert' });
                if (code?.data) {
                    setSessionCode(code.data);
                    setHasScanned(true);
                    captureAndMark(code.data);
                } else {
                    setStatus('No QR Code found in the uploaded image. Please try again.');
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
        setStatus(`QR detected. Verifying your face...`);
        try {
            const blob = await (await fetch(imageSrc)).blob();
            const formData = new FormData();
            formData.append('user_id', user.id);
            formData.append('session_code', scannedCode);
            formData.append('file', new File([blob], 'selfie.jpg', { type: 'image/jpeg' }));
            await api.post('/mark-attendance', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
            setSuccess(true);
            setStatus('✅ Attendance Marked Successfully!');
        } catch (err) {
            setSuccess(false);
            setStatus(err.response?.data?.detail || 'Face verification failed');
            setTimeout(() => setHasScanned(false), 3000);
        }
        setLoading(false);
    }

    const handleLogout = () => { localStorage.clear(); setAuth(null); };
    const resetScanner = () => { setHasScanned(false); setSessionCode(''); setSuccess(false); setStatus('Looking for QR code...'); };

    const formatDate = (ts) => {
        if (!ts) return '';
        const d = new Date(ts);
        return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <canvas ref={canvasRef} style={{ display: 'none' }} />

            {/* ===== TOP NAV BAR ===== */}
            <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-50 shadow-sm">
                <div className="flex items-center gap-2 font-bold text-gray-800 text-lg">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">A</div>
                    Smart AI Attendance
                </div>
                {mode === 'dashboard' && (
                    <div className="hidden md:flex items-center gap-1">
                        <button className="flex items-center gap-1.5 px-3 py-2 text-blue-600 bg-blue-50 rounded-lg text-sm font-medium">
                            <LayoutDashboard size={16} /> Dashboard
                        </button>
                        <button onClick={() => setMode('scanner')} className="flex items-center gap-1.5 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium">
                            <QrCode size={16} /> Mark Attendance
                        </button>
                        <button className="flex items-center gap-1.5 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium">
                            <History size={16} /> History
                        </button>
                    </div>
                )}
                <button onClick={handleLogout} className="flex items-center gap-1.5 text-red-500 hover:text-red-600 text-sm font-semibold transition-colors">
                    <LogOut size={16} /> Logout
                </button>
            </nav>

            {/* ===== DASHBOARD VIEW ===== */}
            {mode === 'dashboard' && (
                <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">

                    {/* Welcome Banner */}
                    <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-6 flex items-center justify-between text-white shadow-lg">
                        <div className="flex items-center gap-4">
                            <div className="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center text-2xl font-bold border-2 border-white/30">
                                {(user?.name || 'U').charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <p className="text-blue-100 text-sm font-medium">Welcome back,</p>
                                <h1 className="text-2xl font-bold">{user?.name || 'Student'}</h1>
                                <p className="text-blue-200 text-sm mt-0.5">{user?.student_id || 'N/A'} • {user?.section || 'N/A'}</p>
                            </div>
                        </div>
                        <div className="bg-white/20 rounded-xl p-4 text-center min-w-[110px] backdrop-blur-sm border border-white/20">
                            <div className="flex items-center justify-center gap-1 text-blue-100 text-xs mb-1">
                                <TrendingUp size={12} /> This Month
                            </div>
                            <p className="text-3xl font-extrabold">{stats.monthly}%</p>
                        </div>
                    </div>

                    {/* Stats Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { label: 'Total Classes', value: stats.total, sub: 'All time', icon: <CalendarDays size={20} className="text-blue-500" />, iconBg: 'bg-blue-50' },
                            { label: 'This Month', value: stats.thisMonth, sub: 'Classes attended', icon: <CalendarDays size={20} className="text-green-500" />, iconBg: 'bg-green-50' },
                            { label: 'Overall Rate', value: `${stats.overall}%`, sub: 'Attendance', icon: <TrendingUp size={20} className="text-purple-500" />, iconBg: 'bg-purple-50' },
                            { label: 'Monthly Rate', value: `${stats.monthly}%`, sub: 'This month', icon: <TrendingUp size={20} className="text-orange-500" />, iconBg: 'bg-orange-50' },
                        ].map((s) => (
                            <div key={s.label} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex flex-col gap-2">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm text-gray-500 font-medium">{s.label}</p>
                                    <div className={`w-8 h-8 ${s.iconBg} rounded-lg flex items-center justify-center`}>{s.icon}</div>
                                </div>
                                <p className="text-3xl font-bold text-gray-900">{s.value}</p>
                                <p className="text-xs text-gray-400">{s.sub}</p>
                            </div>
                        ))}
                    </div>

                    {/* Quick Actions */}
                    <div>
                        <h2 className="text-base font-bold text-gray-800 mb-3">Quick Actions</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <button
                                onClick={() => setMode('scanner')}
                                className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center gap-4 hover:border-blue-300 hover:shadow-md transition-all text-left group"
                            >
                                <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform">
                                    <QrCode size={22} className="text-white" />
                                </div>
                                <div className="flex-1">
                                    <p className="font-bold text-gray-900">Mark Attendance</p>
                                    <p className="text-sm text-gray-500">Scan QR code to mark your attendance</p>
                                </div>
                                <ChevronRight size={18} className="text-gray-400" />
                            </button>

                            <button className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center gap-4 hover:border-green-300 hover:shadow-md transition-all text-left group">
                                <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform">
                                    <History size={22} className="text-white" />
                                </div>
                                <div className="flex-1">
                                    <p className="font-bold text-gray-900">Attendance History</p>
                                    <p className="text-sm text-gray-500">View your complete attendance record</p>
                                </div>
                                <ChevronRight size={18} className="text-gray-400" />
                            </button>
                        </div>
                    </div>

                    {/* Recent Attendance */}
                    <div>
                        <h2 className="text-base font-bold text-gray-800 mb-3">Recent Attendance</h2>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 divide-y divide-gray-50">
                            {attendance.length === 0 ? (
                                <div className="p-8 text-center text-gray-400">
                                    <CalendarDays size={36} className="mx-auto mb-2 opacity-30" />
                                    <p>No attendance records yet.</p>
                                </div>
                            ) : (
                                attendance.slice(0, 6).map((rec, i) => (
                                    <div key={i} className="flex items-center gap-4 px-5 py-3.5 hover:bg-gray-50 transition">
                                        <div className="w-9 h-9 bg-green-50 rounded-lg flex items-center justify-center flex-shrink-0">
                                            <CalendarDays size={18} className="text-green-500" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-semibold text-gray-900 text-sm truncate">{rec.subject}</p>
                                            <p className="text-xs text-blue-500">{formatDate(rec.timestamp)}</p>
                                        </div>
                                        <div className="text-right flex-shrink-0">
                                            <span className="inline-block bg-green-100 text-green-700 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                                                {rec.status || 'Present'}
                                            </span>
                                            <p className="text-xs text-gray-400 mt-0.5">
                                                {rec.similarity_score ? `${Math.round(rec.similarity_score * 100)}% match` : ''}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* ===== SCANNER VIEW ===== */}
            {mode === 'scanner' && (
                <div className="max-w-2xl mx-auto px-4 py-6">
                    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                        <div className="bg-blue-600 p-4 text-white flex items-center gap-3">
                            <button onClick={() => { setMode('dashboard'); resetScanner(); }} className="p-2 hover:bg-blue-700 rounded-lg transition-colors">
                                <ArrowLeft size={20} />
                            </button>
                            <div>
                                <h2 className="text-lg font-bold">Mark Attendance</h2>
                                <p className="text-blue-100 text-sm">Show the QR Code to your camera</p>
                            </div>
                        </div>

                        <div className="p-6 space-y-5">
                            <div className={`p-4 rounded-xl flex items-center gap-3 border text-sm font-semibold
                                ${success ? 'bg-green-50 text-green-700 border-green-200' :
                                    loading ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                        hasScanned ? 'bg-red-50 text-red-700 border-red-200' :
                                            'bg-gray-50 text-gray-700 border-gray-200'}`}
                            >
                                {success ? <CheckCircle className="flex-shrink-0" /> :
                                    hasScanned && !loading ? <XCircle className="flex-shrink-0" /> :
                                        <ScanLine className={`flex-shrink-0 ${loading ? 'animate-pulse' : 'animate-pulse'}`} />}
                                <span>{status}</span>
                            </div>

                            <div className="relative rounded-2xl overflow-hidden bg-black aspect-video shadow-inner border-2 border-gray-800">
                                <Webcam audio={false} ref={webcamRef} screenshotFormat="image/jpeg"
                                    videoConstraints={{ facingMode: 'user' }} className="w-full object-cover" />
                                {!hasScanned && (
                                    <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                                        <div className="w-48 h-48 border-2 border-white/60 rounded-xl relative overflow-hidden">
                                            <div className="w-full h-0.5 bg-green-400 absolute animate-[scan_2s_ease-in-out_infinite]" />
                                        </div>
                                    </div>
                                )}
                                {loading && <div className="absolute inset-0 bg-white/30 backdrop-blur-sm animate-pulse pointer-events-none" />}
                            </div>

                            {!hasScanned && !loading && (
                                <>
                                    <input type="file" accept="image/*" className="hidden" ref={fileInputRef} onChange={handleFileUpload} />
                                    <button onClick={() => fileInputRef.current.click()}
                                        className="w-full py-3 bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold rounded-xl flex items-center justify-center gap-2 transition">
                                        <Upload size={18} /> Upload QR Image
                                    </button>
                                </>
                            )}

                            {hasScanned && !loading && (
                                <button onClick={resetScanner}
                                    className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition">
                                    <Camera size={18} /> Scan Again
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <style>{`
                @keyframes scan {
                    0%, 100% { top: 0%; opacity: 0; }
                    10% { opacity: 1; }
                    50% { top: 100%; }
                    90% { opacity: 1; }
                }
            `}</style>
        </div>
    );
};

export default StudentDashboard;
