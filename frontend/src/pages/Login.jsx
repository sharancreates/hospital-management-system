import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import FormField from '../components/ui/FormField';

const loginSchema = z.object({
    email: z.string().min(1, "Email is required").email("Please enter a valid email"),
    password: z.string().min(1, "Password is required")
});

const Login = () => {
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const { register, handleSubmit, formState: { errors } } = useForm({
        resolver: zodResolver(loginSchema),
        defaultValues: {
            email: '',
            password: ''
        }
    });

    const handleFormSubmit = async (data) => {
        setIsLoading(true);
        setError('');

        try {
            const response = await api.post('/auth/login', data);

            if (response.data.status === 'success') {
                const role = response.data.role;
                login({ email: data.email, role });
                if (role === 'admin') navigate('/admin/dashboard');
                else if (role === 'doctor') navigate('/doctor/dashboard');
                else if (role === 'patient') navigate('/patient/dashboard');
                else navigate('/');
            } else {
                setError(response.data.message || 'Login failed');
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Something went wrong. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col bg-[#FDFCF8] dark:bg-[#1a1a19] font-sans text-[#2d2d2a] dark:text-[#e8e8e6] transition-colors duration-300">
            {/* Minimal Header */}
            <header className="px-8 py-8 flex justify-between items-center">
                <Link to="/" className="text-xl font-serif font-medium tracking-tight hover:opacity-70 transition-opacity">
                    Arogya Medical
                </Link>
            </header>

            <div className="flex-grow flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-sm w-full space-y-8">
                    <div>
                        <h2 className="text-center text-3xl font-serif font-medium">
                            Sign In
                        </h2>
                        <p className="mt-2 text-center text-sm text-[#5a5a57] dark:text-[#a0a09e]">
                            Don't have an account?{' '}
                            <Link to="/patient/register" className="underline underline-offset-4 decoration-1 hover:opacity-70 transition-opacity">
                                Register
                            </Link>
                        </p>
                    </div>
                    <form className="mt-8 space-y-6" onSubmit={handleSubmit(handleFormSubmit)}>
                        {error && (
                            <div className="bg-[#fcf8f8] dark:bg-[#3d1a1a] border border-[#f5e6e6] dark:border-[#333330] p-4 text-center">
                                <p className="text-sm text-[#c54b4b] dark:text-[#e07b7b]">{error}</p>
                            </div>
                        )}

                        <div className="space-y-4">
                            <FormField 
                                label="Email address"
                                name="email"
                                type="email"
                                error={errors.email}
                                {...register('email')}
                            />

                            <div>
                                <FormField 
                                    label="Password"
                                    name="password"
                                    type="password"
                                    error={errors.password}
                                    {...register('password')}
                                />
                                <div className="text-sm mt-2 text-right">
                                    <Link to="/forgot_password" className="font-medium hover:opacity-85 underline decoration-1">
                                        Forgot your password?
                                    </Link>
                                </div>
                            </div>
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={isLoading}
                                className={`w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium text-[#FDFCF8] dark:text-[#1a1a19] bg-[#2d2d2a] dark:bg-[#e8e8e6] hover:opacity-90 focus:outline-none transition-opacity ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
                            >
                                {isLoading ? 'Authenticating...' : 'Sign in'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Login;
