import React from 'react';
import { Link, Navigate } from 'react-router-dom';

function Home({ auth }) {
  // If user is logged in, they can still go to dashboard from the header or we can redirect them, 
  // but let's keep the landing page visible per user request "opened from starting".

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white p-6">
      <div className="text-center max-w-2xl bg-white/10 backdrop-blur-md p-10 rounded-3xl shadow-2xl border border-white/20">
        <h1 className="text-6xl font-extrabold mb-4 drop-shadow-md">🎓 ePortal</h1>
        <p className="text-xl mb-10 text-indigo-100 drop-shadow-sm font-medium">
          Secure, Intelligent, and Effortless Attendance Management
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {auth ? (
            <Link 
              to={auth.role === 'admin' ? "/admin" : "/dashboard"}
              className="bg-white text-indigo-600 hover:bg-gray-50 font-bold py-3 px-8 rounded-xl transition duration-300 shadow-lg transform hover:-translate-y-1"
            >
              Go to Dashboard 🚀
            </Link>
          ) : (
            <>
              <Link 
                to="/login"
                className="bg-white text-indigo-600 hover:bg-gray-50 font-bold py-3 px-8 rounded-xl transition duration-300 shadow-lg transform hover:-translate-y-1 flex items-center justify-center gap-2"
              >
                <span>🔐</span> Sign In
              </Link>
              <Link 
                to="/register"
                className="bg-indigo-600 border-2 border-white text-white hover:bg-indigo-700 font-bold py-3 px-8 rounded-xl transition duration-300 shadow-lg transform hover:-translate-y-1 flex items-center justify-center gap-2"
              >
                <span>📝</span> Create Account
              </Link>
            </>
          )}
        </div>
      </div>
      
      <div className="mt-16 text-indigo-200 text-sm">
        &copy; {new Date().getFullYear()} ePortal - Smart AI Attendance System
      </div>
    </div>
  );
}

export default Home;
