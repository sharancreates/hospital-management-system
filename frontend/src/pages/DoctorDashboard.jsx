import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import api from '../api';
import { Calendar, User, Clock, FileText, Plus, Trash2, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import Modal from '../components/ui/Modal';
import FormField from '../components/ui/FormField';

const availabilitySchema = z.object({
    date: z.string().refine(val => {
        if (!val) return false;
        const selectedDate = new Date(val);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return selectedDate >= today;
    }, { message: "Date cannot be in the past" }),
    time_slot: z.string().min(1, "Please select a time slot")
});

const treatmentSchema = z.object({
    ailment: z.string().min(2, "Ailment details are required"),
    prescription: z.string().min(2, "Prescription details are required"),
    notes: z.string().optional()
});

const DoctorDashboard = () => {
    const [data, setData] = useState(() => {
        try {
            const cached = localStorage.getItem('doctor_dashboard_data');
            return cached ? JSON.parse(cached) : { doctor: {}, appointments: [] };
        } catch (e) {
            return { doctor: {}, appointments: [] };
        }
    });
    const [slots, setSlots] = useState(() => {
        try {
            const cached = localStorage.getItem('doctor_dashboard_slots');
            return cached ? JSON.parse(cached) : [];
        } catch (e) {
            return [];
        }
    });
    const [isLoading, setIsLoading] = useState(() => {
        try {
            return !(localStorage.getItem('doctor_dashboard_data') && localStorage.getItem('doctor_dashboard_slots'));
        } catch (e) {
            return true;
        }
    });
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    // Treatment Modal States
    const [selectedAppt, setSelectedAppt] = useState(null);
    
    // Search/Pagination States
    const [apptSearch, setApptSearch] = useState('');
    const [apptPage, setApptPage] = useState(1);
    const apptPageSize = 5;

    const [slotsSearch, setSlotsSearch] = useState('');
    const [slotsPage, setSlotsPage] = useState(1);
    const slotsPageSize = 5;

    // React Hook Forms
    const { 
        register: registerAvail, 
        handleSubmit: handleSubmitAvail, 
        reset: resetAvail,
        formState: { errors: errorsAvail } 
    } = useForm({
        resolver: zodResolver(availabilitySchema),
        defaultValues: { date: '', time_slot: '09:00' }
    });

    const { 
        register: registerTreat, 
        handleSubmit: handleSubmitTreat, 
        reset: resetTreat,
        formState: { errors: errorsTreat } 
    } = useForm({
        resolver: zodResolver(treatmentSchema),
        defaultValues: { ailment: '', prescription: '', notes: '' }
    });

    const fetchData = async () => {
        try {
            const response = await api.get('/doctor/');
            if (typeof response.data === 'string') throw new Error("Unauthorized");
            setData(response.data);
            try {
                localStorage.setItem('doctor_dashboard_data', JSON.stringify(response.data));
            } catch (e) {}
        } catch (err) {
            if (err.response?.status === 401 || err.message === "Unauthorized") navigate('/login');
            else setError("Failed to load dashboard.");
        }
    };

    const fetchSlots = async () => {
        try {
            const response = await api.get('/doctor/set_availability');
            const slotsData = response.data.slots || [];
            setSlots(slotsData);
            try {
                localStorage.setItem('doctor_dashboard_slots', JSON.stringify(slotsData));
            } catch (e) {}
        } catch (err) {
            console.error("Failed to load availability slots.", err);
        }
    };

    useEffect(() => {
        const loadAllData = async () => {
            const hasCache = localStorage.getItem('doctor_dashboard_data') && localStorage.getItem('doctor_dashboard_slots');
            if (!hasCache) {
                setIsLoading(true);
            }
            await Promise.all([fetchData(), fetchSlots()]);
            setIsLoading(false);
        };
        loadAllData();
    }, [navigate]);

    const handleTreatmentSubmit = async (formData) => {
        if (!selectedAppt) return;
        try {
            await api.post(`/doctor/add_treatment/${selectedAppt.appointment_id}`, formData);
            alert("Treatment added successfully!");
            setSelectedAppt(null);
            resetTreat();
            await fetchData();
        } catch (err) {
            alert("Failed to add treatment.");
        }
    };

    const handleAvailSubmit = async (formData) => {
        try {
            const response = await api.post('/doctor/set_availability', formData);
            alert(response.data.message);
            if (response.data.status === 'success' || response.data.status === 'warning') {
                await fetchSlots();
                resetAvail({ date: '', time_slot: '09:00' });
            }
        } catch (err) {
            alert(err.response?.data?.message || "Failed to add availability.");
        }
    };

    const handleRemoveSlot = async (slotId) => {
        if (!window.confirm("Are you sure you want to remove this availability slot?")) return;
        try {
            const response = await api.delete(`/doctor/remove_slot/${slotId}`);
            alert(response.data.message);
            await fetchSlots();
        } catch (err) {
            alert(err.response?.data?.message || "Failed to remove slot.");
        }
    };

    // Filter & Paginate Appointments
    const filteredAppts = data.appointments.filter(appt => 
        appt.patient_name.toLowerCase().includes(apptSearch.toLowerCase()) ||
        appt.status.toLowerCase().includes(apptSearch.toLowerCase())
    );
    const totalApptPages = Math.ceil(filteredAppts.length / apptPageSize) || 1;
    const paginatedAppts = filteredAppts.slice((apptPage - 1) * apptPageSize, apptPage * apptPageSize);

    // Filter & Paginate Slots
    const filteredSlots = slots.filter(slot => 
        slot.date.includes(slotsSearch)
    );
    const totalSlotsPages = Math.ceil(filteredSlots.length / slotsPageSize) || 1;
    const paginatedSlots = filteredSlots.slice((slotsPage - 1) * slotsPageSize, slotsPage * slotsPageSize);

    useEffect(() => {
        setApptPage(1);
    }, [apptSearch]);

    useEffect(() => {
        setSlotsPage(1);
    }, [slotsSearch]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#FDFCF8] dark:bg-[#1a1a19]">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-[#e2e2df] dark:border-[#333330] border-t-[#2d2d2a] dark:border-t-[#e8e8e6] rounded-full animate-spin"></div>
                    <span className="font-serif text-lg text-[#5a5a57] dark:text-[#a0a09e]">Loading...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return <div className="p-10 text-center text-[#c54b4b] bg-[#FDFCF8] dark:bg-[#1a1a19] min-h-screen">{error}</div>;
    }

    const timeSlotOptions = [
        { value: "09:00", label: "09:00 AM - 11:00 AM" },
        { value: "11:00", label: "11:00 AM - 01:00 PM" },
        { value: "13:00", label: "01:00 PM - 03:00 PM" },
        { value: "15:00", label: "03:00 PM - 05:00 PM" },
        { value: "17:00", label: "05:00 PM - 07:00 PM" },
        { value: "19:00", label: "07:00 PM - 09:00 PM" }
    ];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-[#2d2d2a] dark:text-[#e8e8e6] transition-colors duration-300 min-h-screen bg-[#FDFCF8] dark:bg-[#1a1a19]">
            <h1 className="text-3xl font-serif font-medium mb-2">Welcome, Dr. {data.doctor.name}</h1>
            <p className="text-[#a0a09e] dark:text-[#8a8a88] mb-8">Manage your appointments, patient records, and schedule availability.</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="bg-transparent p-6 rounded-none border border-[#f0f0eb] dark:border-[#333330] flex items-center">
                    <div className="p-3 bg-blue-100 dark:bg-blue-950/40 rounded-full text-blue-600 dark:text-blue-400 mr-4">
                        <Calendar className="h-6 w-6" />
                    </div>
                    <div>
                        <p className="text-sm text-[#a0a09e] dark:text-[#8a8a88]">Today's Appointments</p>
                        <p className="text-2xl font-serif font-medium">{data.appointments.filter(a => a.date === new Date().toISOString().split('T')[0]).length}</p>
                    </div>
                </div>
                <div className="bg-transparent p-6 rounded-none border border-[#f0f0eb] dark:border-[#333330] flex items-center">
                    <div className="p-3 bg-purple-100 dark:bg-purple-950/40 rounded-full text-purple-600 dark:text-purple-400 mr-4">
                        <User className="h-6 w-6" />
                    </div>
                    <div>
                        <p className="text-sm text-[#a0a09e] dark:text-[#8a8a88]">Pending Patients</p>
                        <p className="text-2xl font-serif font-medium">{data.appointments.filter(a => a.status === 'Booked').length}</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Appointment Schedule */}
                <div className="lg:col-span-2 border border-[#e2e2df] dark:border-[#333330] bg-transparent self-start">
                    <div className="px-4 py-5 sm:px-6 border-b border-[#e2e2df] dark:border-[#333330] flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                        <h3 className="text-lg leading-6 font-medium">Appointment Schedule</h3>
                        
                        {/* Search Appointments */}
                        <div className="relative w-full sm:w-60">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search className="h-4 w-4 text-[#a0a09e]" />
                            </div>
                            <input
                                type="text"
                                placeholder="Search by patient or status..."
                                value={apptSearch}
                                onChange={(e) => setApptSearch(e.target.value)}
                                className="pl-9 pr-4 py-1.5 w-full text-xs border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6] focus:outline-none"
                            />
                        </div>
                    </div>
                    
                    <ul className="divide-y divide-[#e2e2df] dark:divide-[#333330]">
                        {paginatedAppts.map((appt) => (
                            <li key={appt.appointment_id} className="p-6 hover:bg-[#fcf8f8]/50 dark:hover:bg-[#252523]/30 transition-colors">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-start space-x-4">
                                        <div className="flex-shrink-0">
                                            <div className="h-12 w-12 rounded-full bg-blue-100 dark:bg-blue-950/40 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-lg">
                                                {appt.patient_name.charAt(0)}
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-lg font-medium text-blue-600 dark:text-blue-400">{appt.patient_name}</p>
                                            <div className="flex items-center text-sm text-[#a0a09e] dark:text-[#8a8a88] mt-1">
                                                <Clock className="h-4 w-4 mr-1" />
                                                {appt.date} at {appt.time}
                                            </div>
                                            <div className="mt-2">
                                                <span className={`px-2 py-0.5 text-xs font-semibold rounded-full 
                                                    ${appt.status === 'Booked' ? 'bg-[#f0f0eb] dark:bg-[#252523] text-[#5a5a57] dark:text-[#a0a09e]' : 
                                                      'bg-[#f0f0eb] dark:bg-[#252523] text-[#2d2d2a] dark:text-[#e8e8e6]'}`}
                                                >
                                                    {appt.status}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    {appt.status === 'Booked' && (
                                        <button
                                            onClick={() => {
                                                setSelectedAppt(appt);
                                                resetTreat({ ailment: '', prescription: '', notes: '' });
                                            }}
                                            className="bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] px-4 py-2 rounded-md hover:opacity-80 transition flex items-center font-medium text-xs"
                                        >
                                            <FileText className="h-4 w-4 mr-2" />
                                            Prescribe
                                        </button>
                                    )}
                                </div>
                            </li>
                        ))}
                        {paginatedAppts.length === 0 && <li className="p-6 text-center text-[#a0a09e] dark:text-[#8a8a88]">No appointments found.</li>}
                    </ul>

                    {/* Appointments Pagination Controls */}
                    {totalApptPages > 1 && (
                        <div className="p-4 border-t border-[#e2e2df] dark:border-[#333330] flex items-center justify-end space-x-2">
                            <button
                                onClick={() => setApptPage(prev => Math.max(prev - 1, 1))}
                                disabled={apptPage === 1}
                                className="p-1 border border-[#e2e2df] dark:border-[#333330] disabled:opacity-40 text-[#2d2d2a] dark:text-[#e8e8e6]"
                            >
                                <ChevronLeft className="h-4 w-4" />
                            </button>
                            <span className="text-xs text-[#5a5a57] dark:text-[#a0a09e]">
                                Page {apptPage} of {totalApptPages}
                            </span>
                            <button
                                onClick={() => setApptPage(prev => Math.min(prev + 1, totalApptPages))}
                                disabled={apptPage === totalApptPages}
                                className="p-1 border border-[#e2e2df] dark:border-[#333330] disabled:opacity-40 text-[#2d2d2a] dark:text-[#e8e8e6]"
                            >
                                <ChevronRight className="h-4 w-4" />
                            </button>
                        </div>
                    )}
                </div>

                {/* Right Column: Availability Management */}
                <div className="space-y-8">
                    {/* Set Availability Form */}
                    <div className="border border-[#e2e2df] dark:border-[#333330] p-6 bg-transparent">
                        <h3 className="text-lg font-medium mb-4">Set Availability</h3>
                        <form onSubmit={handleSubmitAvail(handleAvailSubmit)} className="space-y-4 text-left">
                            <FormField 
                                label="Date"
                                name="date"
                                type="date"
                                error={errorsAvail.date}
                                {...registerAvail('date')}
                            />

                            <FormField 
                                label="Time Slot"
                                name="time_slot"
                                type="select"
                                options={timeSlotOptions}
                                error={errorsAvail.time_slot}
                                {...registerAvail('time_slot')}
                            />

                            <button
                                type="submit"
                                className="w-full mt-4 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] py-2.5 hover:opacity-80 transition text-sm font-medium flex items-center justify-center"
                            >
                                <Plus className="h-4 w-4 mr-2" />
                                Add Slot
                            </button>
                        </form>
                    </div>

                    {/* Active Slots list */}
                    <div className="border border-[#e2e2df] dark:border-[#333330] p-6 bg-transparent">
                        <div className="flex flex-col gap-2 mb-4">
                            <h3 className="text-lg font-medium">Your Active Slots</h3>
                            {/* Filter Slots */}
                            <input
                                type="text"
                                placeholder="Filter slots by date (YYYY-MM-DD)..."
                                value={slotsSearch}
                                onChange={(e) => setSlotsSearch(e.target.value)}
                                className="w-full px-3 py-1.5 text-xs border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6] focus:outline-none"
                            />
                        </div>

                        <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2">
                            {paginatedSlots.map((s) => (
                                <div key={s.slot_id} className="flex justify-between items-center p-3 border border-[#f0f0eb] dark:border-[#333330] bg-transparent">
                                    <div>
                                        <p className="text-sm font-medium">{s.date}</p>
                                        <p className="text-xs text-[#a0a09e] dark:text-[#8a8a88]">{s.start_time.substring(0, 5)} - {s.end_time.substring(0, 5)}</p>
                                    </div>
                                    <button
                                        onClick={() => handleRemoveSlot(s.slot_id)}
                                        className="text-[#c54b4b] dark:text-[#e07b7b] hover:opacity-80 p-1"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </div>
                            ))}
                            {paginatedSlots.length === 0 && (
                                <p className="text-sm text-[#a0a09e] dark:text-[#8a8a88] text-center py-4">No matching active slots found.</p>
                            )}
                        </div>

                        {/* Slots Pagination Controls */}
                        {totalSlotsPages > 1 && (
                            <div className="mt-4 flex items-center justify-end space-x-2">
                                <button
                                    onClick={() => setSlotsPage(prev => Math.max(prev - 1, 1))}
                                    disabled={slotsPage === 1}
                                    className="p-1 border border-[#e2e2df] dark:border-[#333330] disabled:opacity-40 text-[#2d2d2a] dark:text-[#e8e8e6]"
                                >
                                    <ChevronLeft className="h-3 w-3" />
                                </button>
                                <span className="text-[10px] text-[#5a5a57] dark:text-[#a0a09e]">
                                    Page {slotsPage} of {totalSlotsPages}
                                </span>
                                <button
                                    onClick={() => setSlotsPage(prev => Math.min(prev + 1, totalSlotsPages))}
                                    disabled={slotsPage === totalSlotsPages}
                                    className="p-1 border border-[#e2e2df] dark:border-[#333330] disabled:opacity-40 text-[#2d2d2a] dark:text-[#e8e8e6]"
                                >
                                    <ChevronRight className="h-3 w-3" />
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Treatment Modal */}
            <Modal 
                isOpen={!!selectedAppt} 
                onClose={() => setSelectedAppt(null)} 
                title={selectedAppt ? `Add Treatment for ${selectedAppt.patient_name}` : ''}
            >
                <form onSubmit={handleSubmitTreat(handleTreatmentSubmit)} className="space-y-4 text-left">
                    <FormField 
                        label="Ailment / Diagnosis"
                        name="ailment"
                        error={errorsTreat.ailment}
                        {...registerTreat('ailment')}
                    />

                    <FormField 
                        label="Prescription"
                        name="prescription"
                        type="textarea"
                        rows={3}
                        error={errorsTreat.prescription}
                        {...registerTreat('prescription')}
                    />

                    <FormField 
                        label="Doctor's Notes"
                        name="notes"
                        type="textarea"
                        rows={2}
                        error={errorsTreat.notes}
                        {...registerTreat('notes')}
                    />

                    <div className="flex justify-end gap-3 mt-6">
                        <button 
                            type="button" 
                            onClick={() => setSelectedAppt(null)} 
                            className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] text-sm text-gray-700 dark:text-[#e8e8e6] hover:bg-[#fcf8f8] dark:hover:bg-[#252523] transition-colors"
                        >
                            Cancel
                        </button>
                        <button 
                            type="submit" 
                            className="px-4 py-2 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-sm hover:opacity-80 transition-opacity font-medium"
                        >
                            Save Treatment
                        </button>
                    </div>
                </form>
            </Modal>
        </div>
    );
};

export default DoctorDashboard;
