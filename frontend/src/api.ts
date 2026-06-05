import axios, { InternalAxiosRequestConfig } from 'axios';

const api = axios.create({
    baseURL: (import.meta.env.VITE_API_URL as string) || 'http://localhost:5000',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});

const getCookie = (name: string): string | null => {
    if (typeof document === 'undefined') return null;
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        const partsPop = parts.pop();
        if (partsPop) return partsPop.split(';').shift() || null;
    }
    return null;
};

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const csrfToken = getCookie('XSRF-TOKEN');
    if (csrfToken && config.headers) {
        config.headers['X-XSRF-TOKEN'] = csrfToken;
    }

    if (config.url && config.url.startsWith('/') && !config.url.startsWith('/api/')) {
        config.url = `/api/v1${config.url}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

export default api;
