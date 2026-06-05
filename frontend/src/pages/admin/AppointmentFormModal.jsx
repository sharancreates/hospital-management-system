import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Modal from '../../components/ui/Modal';
import FormField from '../../components/ui/FormField';
import api from '../../api';

const apptSchema = z.object({
    doctor_id: z.string().min(1, "Please select a doctor"),
    patient_id: z.string().min(1, "Please select a patient"),
    date: z.string().refine(val => {
        if (!val) return false;
        const selectedDate = new Date(val);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return selectedDate >= today;
    }, { message: "Date cannot be in the past" }),
    time: z.string().min(1, "Please select a time slot")
});

const AppointmentFormModal = ({ 
    isOpen, 
    onClose, 
    onSave, 
    appointment = null, 
    doctors = [], 
    patients = [], 
    isSubmitting = false 
}) => {
    const isEdit = !!appointment;
    const [availableSlots, setAvailableSlots] = useState([]);
    const [isFetchingSlots, setIsFetchingSlots] = useState(false);

    const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm({
        resolver: zodResolver(apptSchema),
        defaultValues: {
            doctor_id: '',
            patient_id: '',
            date: '',
            time: ''
        }
    });

    // Watch fields to fetch slots
    const watchedDoctorId = watch('doctor_id');
    const watchedDate = watch('date');
    const watchedTime = watch('time');

    useEffect(() => {
        if (appointment) {
            const docId = doctors.find(d => d.doc_name === appointment.doctor_name)?.doctor_id || '';
            const patId = patients.find(p => p.pat_name === appointment.patient_name)?.patient_id || '';
            
            setValue('doctor_id', String(docId));
            setValue('patient_id', String(patId));
            setValue('date', appointment.date);
            setValue('time', appointment.time.substring(0, 5)); // HH:MM
        } else {
            reset({
                doctor_id: '',
                patient_id: '',
                date: '',
                time: ''
            });
        }
    }, [appointment, isOpen, reset, setValue, doctors, patients]);

    // Fetch slots when doctor or date changes
    useEffect(() => {
        const fetchSlots = async () => {
            if (watchedDoctorId && watchedDate) {
                setIsFetchingSlots(true);
                try {
                    const res = await api.get(`/admin/get_slots/${watchedDoctorId}/${watchedDate}`);
                    setAvailableSlots(res.data.slots || []);
                    
                    // If editing and the current time matches the appointment time, keep it.
                    // Otherwise, reset if not in the newly fetched slots
                    if (appointment && appointment.time.substring(0, 5) === watchedTime) {
                        // Keep current time
                    } else {
                        const hasSlot = res.data.slots?.some(s => s.time === watchedTime);
                        if (!hasSlot) {
                            setValue('time', '');
                        }
                    }
                } catch (err) {
                    console.error("Failed to fetch slots", err);
                    setAvailableSlots([]);
                    setValue('time', '');
                } finally {
                    setIsFetchingSlots(false);
                }
            } else {
                setAvailableSlots([]);
                setValue('time', '');
            }
        };
        fetchSlots();
    }, [watchedDoctorId, watchedDate, appointment, setValue]);

    const handleFormSubmit = (data) => {
        onSave(data);
    };

    const doctorOptions = [
        { value: "", label: "Select Doctor" },
        ...doctors.map(d => ({ value: String(d.doctor_id), label: `${d.doc_name} (${d.department})` }))
    ];

    const patientOptions = [
        { value: "", label: "Select Patient" },
        ...patients.map(p => ({ value: String(p.patient_id), label: p.pat_name }))
    ];

    // Build slots select options
    const slotOptions = [
        { value: "", label: isFetchingSlots ? 'Loading slots...' : 'Select Time' }
    ];

    // If editing, add current time if not in fetched slots
    if (isEdit && appointment && watchedTime === appointment.time.substring(0, 5) && !availableSlots.some(s => s.time === watchedTime)) {
        slotOptions.push({ value: watchedTime, label: `${watchedTime} (Current)` });
    }

    availableSlots.forEach(slot => {
        slotOptions.push({ value: slot.time, label: `${slot.display} (${slot.remaining} left)` });
    });

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={isEdit ? 'Edit Appointment' : 'Add Appointment'}>
            <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4 text-left">
                <FormField 
                    label="Doctor" 
                    name="doctor_id" 
                    type="select"
                    options={doctorOptions}
                    error={errors.doctor_id} 
                    {...register('doctor_id')} 
                />

                <FormField 
                    label="Patient" 
                    name="patient_id" 
                    type="select"
                    options={patientOptions}
                    disabled={isEdit} // Patient is not editable for an appointment
                    error={errors.patient_id} 
                    {...register('patient_id')} 
                />

                <div className="grid grid-cols-2 gap-4">
                    <FormField 
                        label="Date" 
                        name="date" 
                        type="date"
                        error={errors.date} 
                        {...register('date')} 
                    />
                    <FormField 
                        label="Time" 
                        name="time" 
                        type="select"
                        options={slotOptions}
                        disabled={!watchedDate || !watchedDoctorId || isFetchingSlots}
                        error={errors.time} 
                        {...register('time')} 
                    />
                </div>

                <button 
                    type="submit" 
                    disabled={isSubmitting || !watchedTime} 
                    className="w-full mt-4 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] rounded-md py-2 px-4 hover:opacity-80 disabled:opacity-50 transition-opacity font-medium text-sm"
                >
                    {isSubmitting ? 'Saving...' : 'Save Appointment'}
                </button>
            </form>
        </Modal>
    );
};

export default AppointmentFormModal;
