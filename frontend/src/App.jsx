import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import StudentDashboard from './pages/StudentDashboard';
import AdminDashboard from './pages/AdminDashboard';

function App() {
  const [auth, setAuth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check local storage for existing session
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setAuth(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={!auth ? <Login setAuth={setAuth} /> : (auth.role === 'admin' ? <Navigate to="/admin" /> : <Navigate to="/dashboard" />)} />
        <Route path="/register" element={!auth ? <Register /> : (auth.role === 'admin' ? <Navigate to="/admin" /> : <Navigate to="/dashboard" />)} />

        <Route path="/dashboard" element={auth ? (auth.role !== 'admin' ? <StudentDashboard user={auth} setAuth={setAuth} /> : <Navigate to="/admin" />) : <Navigate to="/login" />} />
        <Route path="/admin" element={auth ? (auth.role === 'admin' ? <AdminDashboard user={auth} setAuth={setAuth} /> : <Navigate to="/dashboard" />) : <Navigate to="/login" />} />

        <Route path="/" element={<Navigate to={auth ? (auth.role === 'admin' ? "/admin" : "/dashboard") : "/login"} />} />
      </Routes>
    </Router>
  );
}

export default App;
