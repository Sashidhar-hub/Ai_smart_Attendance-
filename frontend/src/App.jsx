import React, { useState, useEffect, Component } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import StudentDashboard from './pages/StudentDashboard';
import AdminDashboard from './pages/AdminDashboard';
import Home from './pages/Home';

// Error boundary to catch and display runtime errors instead of white screen
class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 40, fontFamily: 'monospace', background: '#fee2e2', minHeight: '100vh' }}>
          <h2 style={{ color: '#dc2626' }}>⚠️ Runtime Error</h2>
          <pre style={{ whiteSpace: 'pre-wrap', color: '#7f1d1d' }}>{this.state.error?.message}</pre>
          <pre style={{ whiteSpace: 'pre-wrap', color: '#7f1d1d', fontSize: 12 }}>{this.state.error?.stack}</pre>
          <button onClick={() => { localStorage.clear(); window.location.href = '/'; }} style={{ marginTop: 20, padding: '8px 16px', background: '#dc2626', color: 'white', border: 'none', borderRadius: 8, cursor: 'pointer' }}>
            Clear Session &amp; Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [auth, setAuth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/login" element={!auth ? <Login setAuth={setAuth} /> : (auth.role === 'admin' ? <Navigate to="/admin" /> : <Navigate to="/dashboard" />)} />
          <Route path="/register" element={!auth ? <Register /> : (auth.role === 'admin' ? <Navigate to="/admin" /> : <Navigate to="/dashboard" />)} />
          <Route path="/dashboard" element={auth ? (auth.role !== 'admin' ? <StudentDashboard user={auth} setAuth={setAuth} /> : <Navigate to="/admin" />) : <Navigate to="/login" />} />
          <Route path="/admin" element={auth ? (auth.role === 'admin' ? <AdminDashboard user={auth} setAuth={setAuth} /> : <Navigate to="/dashboard" />) : <Navigate to="/login" />} />
          <Route path="/" element={<Home auth={auth} />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
