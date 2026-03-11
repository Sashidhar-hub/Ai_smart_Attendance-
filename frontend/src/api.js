import axios from 'axios';

// In development, Vite proxies /api -> localhost:8000
// In production (Netlify), use the Render backend URL set during build
const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;
