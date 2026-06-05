import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import api from '../api';
import FormField from '../components/ui/FormField';

const forgotPasswordSchema = z.object({
    email: z.string().min(1, "Email is required").email("Please enter a valid email")
});

const ForgotPassword = () => {
    const [status, setStatus] = useState({ type: '', message: '' });
    const [isLoading, setIsLoading] = useState(false);

    const { register, handleSubmit, formState: { errors } } = useForm({
        resolver: zodResolver(forgotPasswordSchema),
        defaultValues: {
            email: ''
        }
    });

    const handleFormSubmit = async (data) => {
        setIsLoading(true);
        setStatus({ type: '', message: '' });

        try {
            const response = await api.post('/auth/reset_password', data);
            setStatus({ type: 'success', message: response.data.message });
        } catch (error) {
            setStatus({ 
                type: 'error', 
                message: error.response?.data?.message || 'An error occurred. Please try again.' 
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6] flex flex-col justify-center py-12 sm:px-6 lg:px-8 transition-colors duration-300">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <div className="text-center mb-8">
                    <span className="text-2xl font-serif tracking-tight text-[#2d2d2a] dark:text-[#e8e8e6]">
                        Arogya
                    </span>
                    <span className="text-2xl font-serif tracking-tight text-[#a0a09e] dark:text-[#8a8a88] ml-2">
                        Portal
                    </span>
                </div>
                <h2 className="mt-6 text-center text-3xl font-serif">
                    Reset your password
                </h2>
                <p className="mt-2 text-center text-sm text-[#a0a09e] dark:text-[#8a8a88]">
                    Enter your email address and we'll send you a link to reset your password.
                </p>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                <div className="bg-[#FDFCF8] dark:bg-[#1a1a19] py-8 px-4 sm:px-10 border border-[#e2e2df] dark:border-[#333330]">
                    <form className="space-y-6" onSubmit={handleSubmit(handleFormSubmit)}>
                        {status.message && (
                            <div className={`p-4 text-sm ${status.type === 'error' ? 'bg-[#fcf8f8] dark:bg-[#3d1a1a] text-[#c54b4b] dark:text-[#e07b7b] border border-[#f0e6e6] dark:border-[#333330]' : 'bg-[#f8fcf8] dark:bg-[#1a3d1a] text-[#4bc55f] dark:text-[#7be07b] border border-[#e6f0e8] dark:border-[#333330]'}`}>
                                {status.message}
                            </div>
                        )}
                        
                        <FormField 
                            label="Email address"
                            name="email"
                            type="email"
                            error={errors.email}
                            {...register('email')}
                        />

                        <div>
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium text-[#FDFCF8] dark:text-[#1a1a19] bg-[#2d2d2a] dark:bg-[#e8e8e6] hover:opacity-80 focus:outline-none transition-opacity disabled:opacity-50"
                            >
                                {isLoading ? 'Sending...' : 'Send reset link'}
                            </button>
                        </div>
                    </form>
                    <div className="mt-6 text-center">
                        <Link to="/login" className="text-sm text-[#5a5a57] dark:text-[#a0a09e] hover:text-[#2d2d2a] dark:hover:text-[#e8e8e6] underline underline-offset-2">
                            Return to sign in
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ForgotPassword;
