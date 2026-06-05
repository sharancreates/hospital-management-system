import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import api from '../api';
import FormField from '../components/ui/FormField';

const registerSchema = z.object({
    pat_name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().min(1, "Email is required").email("Please enter a valid email"),
    password: z.string()
        .min(8, "Password must be at least 8 characters long")
        .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
        .regex(/[a-z]/, "Password must contain at least one lowercase letter")
        .regex(/\d/, "Password must contain at least one digit")
        .regex(/[!@#$%^&*(),.?":{}|<>]/, "Password must contain at least one special character"),
    confirm_password: z.string().min(1, "Please confirm your password"),
    dob: z.string().refine(val => !isNaN(Date.parse(val)) && new Date(val) < new Date(), {
        message: "Date of birth must be in the past"
    }),
    gender: z.enum(["Male", "Female", "Other"], {
        errorMap: () => ({ message: "Please select a gender" })
    }),
    contact_num: z.string().regex(/^\d{10}$/, "Contact number must be exactly 10 digits"),
    age: z.coerce.number().int().min(0, "Age cannot be negative")
}).refine(data => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"]
});

const Register = () => {
    const navigate = useNavigate();
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
        resolver: zodResolver(registerSchema),
        defaultValues: {
            pat_name: '',
            email: '',
            password: '',
            confirm_password: '',
            dob: '',
            gender: 'Male',
            contact_num: '',
            age: ''
        }
    });

    const watchedDob = watch('dob');

    React.useEffect(() => {
        if (watchedDob) {
            const dob = new Date(watchedDob);
            if (!isNaN(dob.getTime())) {
                const today = new Date();
                let age = today.getFullYear() - dob.getFullYear();
                const monthDiff = today.getMonth() - dob.getMonth();
                if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                    age--;
                }
                setValue('age', age >= 0 ? age : 0, { shouldValidate: true });
            } else {
                setValue('age', '');
            }
        } else {
            setValue('age', '');
        }
    }, [watchedDob, setValue]);

    const handleFormSubmit = async (data) => {
        setIsLoading(true);
        setError('');
        setMessage('');

        try {
            const payload = { ...data };
            delete payload.confirm_password;

            const response = await api.post('/patient/register', payload);

            if (response.data.status === 'success') {
                alert('Registration successful! Please login.');
                navigate('/login');
            } else if (response.data.status === 'info') {
                setMessage(response.data.message);
            } else {
                setError(response.data.message || 'Registration failed');
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Something went wrong. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const genderOptions = [
        { value: "Male", label: "Male" },
        { value: "Female", label: "Female" },
        { value: "Other", label: "Other" }
    ];

    return (
        <div className="min-h-screen flex flex-col bg-[#FDFCF8] dark:bg-[#1a1a19] font-sans text-[#2d2d2a] dark:text-[#e8e8e6] transition-colors duration-300">
            {/* Minimal Header */}
            <header className="px-8 py-8 flex justify-between items-center">
                <Link to="/" className="text-xl font-serif font-medium tracking-tight hover:opacity-70 transition-opacity">
                    Arogya Medical
                </Link>
            </header>

            <div className="flex-grow flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-xl w-full space-y-8">
                    <div>
                        <h2 className="text-center text-3xl font-serif font-medium">
                            Register as a Patient
                        </h2>
                        <p className="mt-2 text-center text-sm text-[#5a5a57] dark:text-[#a0a09e]">
                            Already have an account?{' '}
                            <Link to="/login" className="underline underline-offset-4 decoration-1 hover:opacity-70 transition-opacity">
                                Sign in
                            </Link>
                        </p>
                    </div>

                    {message && (
                        <div className="bg-[#fcf8f8] dark:bg-[#252523] border border-[#e2e2df] dark:border-[#333330] p-4 text-center">
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e]">{message}</p>
                        </div>
                    )}

                    <form className="mt-8 space-y-6" onSubmit={handleSubmit(handleFormSubmit)}>
                        {error && (
                            <div className="bg-[#fcf8f8] dark:bg-[#3d1a1a] border border-[#f5e6e6] dark:border-[#333330] p-4 text-center">
                                <p className="text-sm text-[#c54b4b] dark:text-[#e07b7b]">{error}</p>
                            </div>
                        )}

                        <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                            <div className="sm:col-span-3">
                                <FormField 
                                    label="Full Name" 
                                    name="pat_name" 
                                    error={errors.pat_name} 
                                    {...register('pat_name')} 
                                />
                            </div>

                            <div className="sm:col-span-3">
                                <FormField 
                                    label="Contact Number" 
                                    name="contact_num" 
                                    error={errors.contact_num} 
                                    {...register('contact_num')} 
                                />
                            </div>

                            <div className="sm:col-span-4">
                                <FormField 
                                    label="Email Address" 
                                    name="email" 
                                    type="email"
                                    error={errors.email} 
                                    {...register('email')} 
                                />
                            </div>

                            <div className="sm:col-span-2">
                                <FormField 
                                    label="Age" 
                                    name="age" 
                                    type="number"
                                    readOnly
                                    error={errors.age} 
                                    {...register('age')} 
                                />
                            </div>

                            <div className="sm:col-span-3">
                                <FormField 
                                    label="Password" 
                                    name="password" 
                                    type="password"
                                    error={errors.password} 
                                    {...register('password')} 
                                />
                            </div>

                            <div className="sm:col-span-3">
                                <FormField 
                                    label="Confirm Password" 
                                    name="confirm_password" 
                                    type="password"
                                    error={errors.confirm_password} 
                                    {...register('confirm_password')} 
                                />
                            </div>

                            <div className="sm:col-span-3">
                                <FormField 
                                    label="Date of Birth" 
                                    name="dob" 
                                    type="date"
                                    error={errors.dob} 
                                    {...register('dob')} 
                                />
                            </div>

                            <div className="sm:col-span-3">
                                <FormField 
                                    label="Gender" 
                                    name="gender" 
                                    type="select"
                                    options={genderOptions}
                                    error={errors.gender} 
                                    {...register('gender')} 
                                />
                            </div>
                        </div>

                        <div className="pt-4">
                            <button 
                                type="submit" 
                                disabled={isLoading}
                                className={`w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium text-[#FDFCF8] dark:text-[#1a1a19] bg-[#2d2d2a] dark:bg-[#e8e8e6] hover:opacity-90 focus:outline-none transition-opacity ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
                            >
                                {isLoading ? 'Creating Account...' : 'Register'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Register;
