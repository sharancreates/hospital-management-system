import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Modal from '../../components/ui/Modal';
import FormField from '../../components/ui/FormField';

const getPatientSchema = (isEdit) => z.object({
    pat_name: z.string().min(2, "Name must be at least 2 characters"),
    email: isEdit 
        ? z.string().optional()
        : z.string().min(1, "Email is required").email("Please enter a valid email"),
    dob: z.string().refine(val => !isNaN(Date.parse(val)) && new Date(val) < new Date(), {
        message: "Date of birth must be in the past"
    }),
    age: z.coerce.number().int().min(0, "Age cannot be negative"),
    gender: z.enum(["Male", "Female", "Other"], {
        errorMap: () => ({ message: "Please select a gender" })
    }),
    contact_num: z.string().regex(/^\d{10}$/, "Contact number must be exactly 10 digits")
});

const PatientFormModal = ({ isOpen, onClose, onSave, patient = null, isSubmitting = false }) => {
    const isEdit = !!patient;
    const schema = getPatientSchema(isEdit);

    const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm({
        resolver: zodResolver(schema),
        defaultValues: {
            pat_name: '',
            email: '',
            dob: '',
            age: '',
            gender: 'Male',
            contact_num: ''
        }
    });

    const watchedDob = watch('dob');

    useEffect(() => {
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

    useEffect(() => {
        if (patient) {
            setValue('pat_name', patient.pat_name);
            setValue('dob', patient.dob);
            setValue('age', String(patient.age));
            setValue('gender', patient.gender || 'Male');
            setValue('contact_num', patient.contact_num);
            setValue('email', ''); // email is not editable
        } else {
            reset({
                pat_name: '',
                email: '',
                dob: '',
                age: '',
                gender: 'Male',
                contact_num: ''
            });
        }
    }, [patient, isOpen, reset, setValue]);

    const handleFormSubmit = (data) => {
        // Filter out email when editing to avoid sending blank
        const payload = { ...data };
        if (isEdit) {
            delete payload.email;
        }
        onSave(payload);
    };

    const genderOptions = [
        { value: "Male", label: "Male" },
        { value: "Female", label: "Female" },
        { value: "Other", label: "Other" }
    ];

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={isEdit ? 'Edit Patient' : 'Add Patient'}>
            <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4 text-left">
                <FormField 
                    label="Name" 
                    name="pat_name" 
                    error={errors.pat_name} 
                    {...register('pat_name')} 
                />

                {!isEdit && (
                    <FormField 
                        label="Email" 
                        name="email" 
                        type="email"
                        error={errors.email} 
                        {...register('email')} 
                    />
                )}

                <div className="grid grid-cols-2 gap-4">
                    <FormField 
                        label="DOB" 
                        name="dob" 
                        type="date"
                        error={errors.dob} 
                        {...register('dob')} 
                    />
                    <FormField 
                        label="Age" 
                        name="age" 
                        type="number"
                        readOnly
                        error={errors.age} 
                        {...register('age')} 
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField 
                        label="Gender" 
                        name="gender" 
                        type="select"
                        options={genderOptions}
                        error={errors.gender} 
                        {...register('gender')} 
                    />
                    <FormField 
                        label="Contact" 
                        name="contact_num" 
                        error={errors.contact_num} 
                        {...register('contact_num')} 
                    />
                </div>

                <button 
                    type="submit" 
                    disabled={isSubmitting} 
                    className="w-full mt-4 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] rounded-md py-2 px-4 hover:opacity-80 disabled:opacity-50 transition-opacity font-medium text-sm"
                >
                    {isSubmitting ? 'Saving...' : 'Save Patient'}
                </button>
            </form>
        </Modal>
    );
};

export default PatientFormModal;
