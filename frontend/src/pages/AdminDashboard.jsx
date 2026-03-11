import React, { useState, useEffect } from 'react';
import { Users, CheckCircle, Clock, AlertTriangle, LogOut, RefreshCw } from 'lucide-react';
import api from '../api';

const AdminDashboard = ({ user, setAuth }) => {
    const [stats, setStats] = useState({
        total_users: 0,
        total_sessions: 0,
        attendance_records: 0
    });
    const [loading, setLoading] = useState(true);

    const fetchStats = async () => {
        setLoading(true);
        try {
            // In a real app we'd fetch this from a /api/admin/stats endpoint
            // For now, since we only wrote /sessions in FastAPI, let's fetch sessions
            const res = await api.get('/sessions');
            setStats({
                ...stats,
                total_sessions: res.data.length,
                // Mock data for UI demonstration
                total_users: 24,
                attendance_records: 156
            });
        } catch (err) {
            console.error(err);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchStats();
    }, []);

    const handleLogout = () => {
        localStorage.clear();
        setAuth(null);
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
            {/* Header */}
            <div className="w-full max-w-6xl flex justify-between items-center mb-8 bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center font-bold text-xl">
                        A
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-gray-800">Admin Portal</h2>
                        <p className="text-sm text-gray-500">System Overview</p>
                    </div>
                </div>
                <div className="flex gap-4">
                    <button
                        onClick={fetchStats}
                        className="flex items-center gap-2 px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors font-medium"
                    >
                        <RefreshCw size={18} className={loading ? "animate-spin" : ""} /> Refresh
                    </button>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
                    >
                        <LogOut size={18} /> Logout
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
                    <div className="p-4 bg-blue-100 text-blue-600 rounded-xl">
                        <Users size={32} />
                    </div>
                    <div>
                        <p className="text-gray-500 font-medium">Total Students</p>
                        <h3 className="text-3xl font-bold text-gray-900">{stats.total_users}</h3>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
                    <div className="p-4 bg-purple-100 text-purple-600 rounded-xl">
                        <Clock size={32} />
                    </div>
                    <div>
                        <p className="text-gray-500 font-medium">Active Sessions</p>
                        <h3 className="text-3xl font-bold text-gray-900">{stats.total_sessions}</h3>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
                    <div className="p-4 bg-green-100 text-green-600 rounded-xl">
                        <CheckCircle size={32} />
                    </div>
                    <div>
                        <p className="text-gray-500 font-medium">Total Logs</p>
                        <h3 className="text-3xl font-bold text-gray-900">{stats.attendance_records}</h3>
                    </div>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Recent Attendance */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                        <h3 className="text-lg font-bold text-gray-900">Recent Attendance Logs</h3>
                        <span className="text-sm text-indigo-600 font-medium cursor-pointer hover:underline">View All</span>
                    </div>
                    <div className="p-6">
                        <div className="space-y-4">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center font-bold text-gray-500">
                                            S{i}
                                        </div>
                                        <div>
                                            <p className="font-semibold text-gray-900">Student Name {i}</p>
                                            <p className="text-xs text-gray-500">SESSION-CS-101 • 10:4{i} AM</p>
                                        </div>
                                    </div>
                                    <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                                        <CheckCircle size={12} /> Present
                                    </div>
                                </div>
                            ))}
                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center font-bold text-gray-500">
                                        M
                                    </div>
                                    <div>
                                        <p className="font-semibold text-gray-900">Missing Student</p>
                                        <p className="text-xs text-gray-500">SESSION-CS-101 • No Scan</p>
                                    </div>
                                </div>
                                <div className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                                    <AlertTriangle size={12} /> Absent
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* System Actions */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-6 border-b border-gray-100">
                        <h3 className="text-lg font-bold text-gray-900">System Analytics</h3>
                    </div>
                    <div className="p-6 flex flex-col items-center justify-center min-h-[300px] text-gray-400">
                        <div className="w-32 h-32 border-4 border-dashed border-gray-200 rounded-full flex items-center justify-center mb-4">
                            📊
                        </div>
                        <p>Admin Charts & Reports will be displayed here</p>
                        <button className="mt-4 px-6 py-2 bg-indigo-50 text-indigo-600 rounded-lg font-medium hover:bg-indigo-100 transition-colors">
                            Export CSV Report
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default AdminDashboard;
