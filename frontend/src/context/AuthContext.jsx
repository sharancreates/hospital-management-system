import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(() => {
        try {
            const cached = localStorage.getItem('user');
            return cached ? JSON.parse(cached) : null;
        } catch (e) {
            return null;
        }
    });

    const [loading, setLoading] = useState(() => {
        try {
            return !localStorage.getItem('user');
        } catch (e) {
            return true;
        }
    });

    const checkAuthStatus = async () => {
        try {
            const response = await api.get('/auth/status');
            if (response.data.isAuthenticated) {
                const userData = {
                    email: response.data.email,
                    role: response.data.role
                };
                setUser(userData);
                localStorage.setItem('user', JSON.stringify(userData));
            } else {
                setUser(null);
                localStorage.removeItem('user');
                localStorage.removeItem('token');
            }
        } catch (error) {
            console.error("Auth check failed:", error);
            setUser(null);
            localStorage.removeItem('user');
            localStorage.removeItem('token');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const login = (userData, token) => {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        if (token) {
            localStorage.setItem('token', token);
        }
    };

    const logout = async () => {
        try {
            await api.post('/auth/logout');
        } catch (e) {
            console.error("Logout request failed:", e);
        }
        setUser(null);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    };

    return (
        <AuthContext.Provider value={{ user, loading, checkAuthStatus, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
