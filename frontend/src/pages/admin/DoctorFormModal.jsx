import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Modal from '../../components/ui/Modal';
import FormField from '../../components/ui/FormField';

const doctorSchema = z.object({
    doc_name: z.string().min(2, "Name must be at least 2 characters"),
    dob: z.string().refine(val => !isNaN(Date.parse(val)) && new Date(val) < new Date(), {
        message: "Date of birth must be a valid date in the past"
    }),
    gender: z.enum(["Male", "Female", "Other"], {
        errorMap: () => ({ message: "Please select a gender" })
    }),
    specialization: z.string().min(1, "Please select a department"),
    contact_num: z.string().regex(/^\d{10}$/, "Contact number must be exactly 10 digits")
});

const DoctorFormModal = ({ isOpen, onClose, onSave, doctor = null, departments = [], isSubmitting = false }) => {
    const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm({
        resolver: zodResolver(doctorSchema),
        defaultValues: {
            doc_name: '',
            dob: '',
            gender: 'Male',
            specialization: '',
            contact_num: ''
        }
    });

    useEffect(() => {
        if (doctor) {
            setValue('doc_name', doctor.doc_name);
            setValue('dob', doctor.dob);
            setValue('gender', doctor.gender || 'Male');
            setValue('specialization', String(doctor.specialization || ''));
            setValue('contact_num', doctor.contact_num);
        } else {
            reset({
                doc_name: '',
                dob: '',
                gender: 'Male',
                specialization: '',
                contact_num: ''
            });
        }
    }, [doctor, isOpen, reset, setValue]);

    const handleFormSubmit = (data) => {
        onSave(data);
    };

    const departmentOptions = [
        { value: "", label: "Select Dept" },
        ...departments.map(d => ({ value: String(d.department_id), label: d.department_name }))
    ];

    const genderOptions = [
        { value: "Male", label: "Male" },
        { value: "Female", label: "Female" },
        { value: "Other", label: "Other" }
    ];

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={doctor ? 'Edit Doctor' : 'Add Doctor'}>
            <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4 text-left">
                <FormField 
                    label="Name" 
                    name="doc_name" 
                    error={errors.doc_name} 
                    {...register('doc_name')} 
                />

                <div className="grid grid-cols-2 gap-4">
                    <FormField 
                        label="DOB" 
                        name="dob" 
                        type="date"
                        error={errors.dob} 
                        {...register('dob')} 
                    />
                    <FormField 
                        label="Gender" 
                        name="gender" 
                        type="select"
                        options={genderOptions}
                        error={errors.gender} 
                        {...register('gender')} 
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField 
                        label="Specialization" 
                        name="specialization" 
                        type="select"
                        options={departmentOptions}
                        error={errors.specialization} 
                        {...register('specialization')} 
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
                    {isSubmitting ? 'Saving...' : 'Save Doctor'}
                </button>
            </form>
        </Modal>
    );
};

export default DoctorFormModal;
