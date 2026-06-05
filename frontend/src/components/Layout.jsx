import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const Layout = () => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const { darkMode, toggleTheme } = useTheme();
    const { t, i18n } = useTranslation();

    const handleLogout = async () => {
        try {
            await api.post('/auth/logout');
            logout();
            navigate('/login');
        } catch (err) {
            console.error("Logout failed", err);
            logout();
            navigate('/login');
        }
    };

    const getDashboardPath = () => {
        if (!user) return '/';
        if (user.role === 'admin') return '/admin/dashboard';
        if (user.role === 'doctor') return '/doctor/dashboard';
        if (user.role === 'patient') return '/patient/dashboard';
        return '/';
    };

    return (
        <div className="min-h-screen font-sans text-[#2d2d2a] dark:text-[#e8e8e6] bg-[#FDFCF8] dark:bg-[#1a1a19] transition-colors duration-300">
            <nav className="sticky top-0 z-50 border-b border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8]/90 dark:bg-[#1a1a19]/90 backdrop-blur-md">
                <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
                        <span className="font-serif font-medium text-xl tracking-tight text-[#2d2d2a] dark:text-[#e8e8e6]">
                            {t('app_title')}
                        </span>
                    </div>
                    <div className="flex items-center space-x-6 text-sm">
                        <Link to="/" className="text-[#5a5a57] dark:text-[#a0a09e] hover:text-[#2d2d2a] dark:hover:text-[#e8e8e6] transition-colors">
                            {t('home', 'Home')}
                        </Link>
                        {user ? (
                            <>
                                <Link to={getDashboardPath()} className="text-[#5a5a57] dark:text-[#a0a09e] hover:text-[#2d2d2a] dark:hover:text-[#e8e8e6] transition-colors">
                                    {t('dashboard')}
                                </Link>
                                <button onClick={handleLogout} className="text-[#c54b4b] dark:text-[#c54b4b] hover:opacity-70 transition-opacity">
                                    {t('logout')}
                                </button>
                            </>
                        ) : (
                            <>
                                <Link to="/patient/register" className="text-[#5a5a57] dark:text-[#a0a09e] hover:text-[#2d2d2a] dark:hover:text-[#e8e8e6] transition-colors">
                                    {t('register')}
                                </Link>
                                <Link to="/login" className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] text-[#2d2d2a] dark:text-[#e8e8e6] hover:bg-[#f5f5f0] dark:hover:bg-[#252523] transition-colors rounded-sm">
                                    {t('login')}
                                </Link>
                            </>
                        )}
                        <button 
                            onClick={() => i18n.changeLanguage(i18n.language.startsWith('en') ? 'hi' : 'en')}
                            className="px-2 py-1 text-xs border border-[#e2e2df] dark:border-[#333330] rounded hover:bg-[#f5f5f0] dark:hover:bg-[#252523] text-[#5a5a57] dark:text-[#a0a09e] transition-colors font-medium"
                            aria-label="Toggle language"
                        >
                            {i18n.language.startsWith('en') ? 'हिन्दी' : 'EN'}
                        </button>
                        <button 
                            onClick={toggleTheme}
                            className="text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors p-1"
                            aria-label="Toggle dark mode"
                        >
                            {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                        </button>
                    </div>
                </div>
            </nav>
            <main>
                <Outlet />
            </main>
        </div>
    );
};

export default Layout;
