import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import api from '../api';
import { io } from 'socket.io-client';
import { Calendar, User, Clock, Trash2, Plus, Download, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import Modal from '../components/ui/Modal';
import FormField from '../components/ui/FormField';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const bookingSchema = z.object({
    doc: z.string().min(1, "Please select a doctor"),
    date: z.string().min(1, "Please select a date"),
    time: z.string().min(1, "Please select a time slot")
});

const PatientDashboard = () => {
    const [data, setData] = useState(() => {
        try {
            const cached = localStorage.getItem('patient_dashboard_data');
            return cached ? JSON.parse(cached) : { patient: {}, appointments: [], doctors: [] };
        } catch (e) {
            return { patient: {}, appointments: [], doctors: [] };
        }
    });
    const [isLoading, setIsLoading] = useState(() => {
        try {
            return !localStorage.getItem('patient_dashboard_data');
        } catch (e) {
            return true;
        }
    });
    const [error, setError] = useState(null);
    const [isBookingOpen, setIsBookingOpen] = useState(false);
    const [doctorSlots, setDoctorSlots] = useState([]);
    
    // Prescription View States
    const [isPrescOpen, setIsPrescOpen] = useState(false);
    const [selectedPresc, setSelectedPresc] = useState(null);
    
    // Search/Pagination States
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const pageSize = 5;

    const navigate = useNavigate();

    const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm({
        resolver: zodResolver(bookingSchema),
        defaultValues: {
            doc: '',
            date: '',
            time: ''
        }
    });

    const watchedDoc = watch('doc');
    const watchedDate = watch('date');

    const fetchData = async () => {
        try {
            const response = await api.get('/patient/dashboard');
            if (typeof response.data === 'string') throw new Error("Unauthorized");
            setData(response.data);
            try {
                localStorage.setItem('patient_dashboard_data', JSON.stringify(response.data));
            } catch (e) {}
        } catch (err) {
            if (err.response?.status === 401 || err.message === "Unauthorized") navigate('/login');
            else setError("Failed to load dashboard.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [navigate]);

    useEffect(() => {
        const socket = io(import.meta.env.VITE_API_URL || 'http://localhost:5000', {
            withCredentials: true
        });

        socket.on('queue_update', (msg) => {
            console.log('Real-time queue update received:', msg);
            fetchData();
        });

        return () => {
            socket.disconnect();
        };
    }, []);

    // Handle doctor slot fetching
    useEffect(() => {
        const fetchDoctorSlots = async () => {
            if (!watchedDoc) {
                setDoctorSlots([]);
                setValue('date', '');
                setValue('time', '');
                return;
            }
            try {
                const resp = await api.get(`/patient/doc_profile/${watchedDoc}`);
                if (resp.data.status === 'success') {
                    setDoctorSlots(resp.data.free_slots || []);
                    setValue('date', '');
                    setValue('time', '');
                }
            } catch (err) {
                console.error("Failed to fetch doctor slots", err);
                setDoctorSlots([]);
            }
        };
        fetchDoctorSlots();
    }, [watchedDoc, setValue]);

    // Clear time slot when date changes
    useEffect(() => {
        setValue('time', '');
    }, [watchedDate, setValue]);

    const handleCancel = async (id) => {
        if (!window.confirm("Cancel this appointment?")) return;
        try {
            await api.delete(`/patient/cancel_appointment/${id}`);
            fetchData();
        } catch (err) {
            alert("Failed to cancel appointment.");
        }
    };

    const handleBookingSubmit = async (formData) => {
        try {
            await api.post('/patient/add_appointment', formData);
            alert("Appointment Requested!");
            setIsBookingOpen(false);
            reset();
            fetchData();
        } catch (err) {
            alert(err.response?.data?.message || "Booking failed. Ensure correct time format (HH:MM).");
        }
    };

    // View Treatment details
    const handleViewPrescription = async (treatmentId) => {
        if (!treatmentId) {
            alert("Prescription details not found.");
            return;
        }
        try {
            const res = await api.get(`/patient/treatment/${treatmentId}`);
            if (res.data.status === 'success') {
                setSelectedPresc({
                    ...res.data.treatment,
                    doctor_name: res.data.doctor?.name || 'N/A',
                    date: res.data.appointment?.date || 'N/A'
                });
                setIsPrescOpen(true);
            } else {
                alert(res.data.message || "Failed to load prescription.");
            }
        } catch (e) {
            alert("Failed to load prescription.");
        }
    };

    const downloadPDF = (presc, patientName) => {
        const doc = new jsPDF();
        doc.setFontSize(20);
        doc.text("Arogya Hospital - Medical Prescription", 105, 20, { align: "center" });
        
        doc.setFontSize(12);
        doc.text(`Patient: ${patientName}`, 20, 40);
        doc.text(`Doctor: Dr. ${presc.doctor_name}`, 20, 50);
        doc.text(`Date: ${presc.date}`, 150, 40);
        
        autoTable(doc, {
            startY: 60,
            head: [['Field', 'Details']],
            body: [
                ['Ailment', presc.ailment],
                ['Prescription', presc.prescription],
                ['Notes', presc.notes]
            ],
        });
        
        doc.save(`${patientName}_Prescription_${presc.date}.pdf`);
    };

    // Search and paginate appointments
    const filteredAppts = data.appointments.filter(appt => 
        appt.doctor_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        appt.status.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const totalPages = Math.ceil(filteredAppts.length / pageSize) || 1;
    const paginatedAppts = filteredAppts.slice((currentPage - 1) * pageSize, currentPage * pageSize);

    useEffect(() => {
        setCurrentPage(1);
    }, [searchTerm]);

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

    const docOptions = [
        { value: "", label: "-- Choose Doctor --" },
        ...data.doctors.map(d => ({ value: String(d.doctor_id), label: `${d.doc_name} (${d.department})` }))
    ];

    const dateOptions = [
        { value: "", label: "-- Choose Date --" },
        ...[...new Set(doctorSlots.map(s => s.date))].sort().map(d => ({ value: d, label: d }))
    ];

    const timeOptions = [
        { value: "", label: "-- Choose Time --" },
        ...doctorSlots
            .filter(s => s.date === watchedDate)
            .map(s => {
                const t = s.start_time.slice(0, 5);
                const hour = parseInt(t.slice(0, 2), 10);
                const displayTime = hour >= 12 
                    ? `${hour === 12 ? 12 : hour - 12}:${t.slice(3, 5)} PM`
                    : `${hour === 0 ? 12 : hour}:${t.slice(3, 5)} AM`;
                return { value: t, label: displayTime };
            })
    ];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-[#2d2d2a] dark:text-[#e8e8e6] transition-colors duration-300 min-h-screen">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
                <div>
                    <h1 className="text-3xl font-serif font-medium text-[#2d2d2a] dark:text-[#e8e8e6] mb-1">Hello, {data.patient.pat_name}</h1>
                    <p className="text-[#a0a09e] dark:text-[#8a8a88]">Patient ID: {data.patient.patient_id}</p>
                </div>
                <button
                    onClick={() => {
                        reset();
                        setDoctorSlots([]);
                        setIsBookingOpen(true);
                    }}
                    className="mt-4 md:mt-0 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] px-5 py-3 rounded-none hover:opacity-80 transition flex items-center font-medium text-sm"
                >
                    <Plus className="h-5 w-5 mr-2" />
                    Book Appointment
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Profile Card */}
                <div className="bg-transparent p-6 rounded-none border border-[#f0f0eb] dark:border-[#333330] h-fit">
                    <h3 className="text-lg font-bold text-[#2d2d2a] dark:text-[#e8e8e6] mb-4 flex items-center">
                        <User className="h-5 w-5 mr-2 text-[#a0a09e]" />
                        My Profile
                    </h3>
                    <div className="space-y-3 text-sm">
                        <div className="flex justify-between border-b border-[#f0f0eb] dark:border-[#333330] pb-2">
                            <span className="text-[#a0a09e] dark:text-[#8a8a88]">Contact</span>
                            <span className="font-medium">{data.patient.contact_num}</span>
                        </div>
                        <div className="flex justify-between border-b border-[#f0f0eb] dark:border-[#333330] pb-2">
                            <span className="text-[#a0a09e] dark:text-[#8a8a88]">Age / Gender</span>
                            <span className="font-medium">{data.patient.age} / {data.patient.gender}</span>
                        </div>
                        <div className="flex justify-between border-b border-[#f0f0eb] dark:border-[#333330] pb-2">
                            <span className="text-[#a0a09e] dark:text-[#8a8a88]">DOB</span>
                            <span className="font-medium">{data.patient.dob}</span>
                        </div>
                    </div>
                </div>

                {/* Appointments List */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
                        <h3 className="text-xl font-serif font-medium text-[#2d2d2a] dark:text-[#e8e8e6]">My Appointments</h3>
                        
                        {/* Search Input */}
                        <div className="relative w-full sm:w-64">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search className="h-4 w-4 text-[#a0a09e]" />
                            </div>
                            <input
                                type="text"
                                placeholder="Search by doctor or status..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-9 pr-4 py-1.5 w-full text-xs border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6] focus:outline-none"
                            />
                        </div>
                    </div>

                    <div className="space-y-4">
                        {paginatedAppts.map((appt) => (
                            <div key={appt.appointment_id} className="bg-transparent p-6 rounded-none border border-[#e2e2df] dark:border-[#333330] flex flex-col md:flex-row justify-between items-start md:items-center hover:bg-[#fcf8f8]/50 dark:hover:bg-[#252523]/30 transition-colors">
                                <div className="mb-4 md:mb-0">
                                    <h4 className="text-lg font-bold text-[#2d2d2a] dark:text-[#e8e8e6] mb-1">Dr. {appt.doctor_name}</h4>
                                    <div className="flex items-center text-[#a0a09e] dark:text-[#8a8a88] text-sm mb-2">
                                        <Clock className="h-4 w-4 mr-1" />
                                        {appt.date} at {appt.time}
                                    </div>
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold 
                                        ${appt.status === 'Booked' ? 'bg-[#f0f0eb] dark:bg-[#252523] text-[#5a5a57] dark:text-[#a0a09e]' :
                                          appt.status === 'Completed' ? 'bg-[#f0f0eb] dark:bg-[#252523] text-[#2d2d2a] dark:text-[#e8e8e6]' :
                                          'bg-[#fcf8f8] dark:bg-[#3d1a1a] text-[#c54b4b] dark:text-[#e07b7b]'}`}
                                    >
                                        {appt.status}
                                    </span>
                                </div>

                                <div className="flex gap-3">
                                    {appt.status === 'Completed' ? (
                                        <button 
                                            onClick={() => handleViewPrescription(appt.treatment_id)}
                                            className="text-blue-600 dark:text-blue-400 hover:opacity-75 text-sm font-medium underline underline-offset-2"
                                        >
                                            View Prescription
                                        </button>
                                    ) : (
                                        appt.status !== 'Cancelled' && (
                                            <button
                                                onClick={() => handleCancel(appt.appointment_id)}
                                                className="text-[#c54b4b] dark:text-[#e07b7b] hover:opacity-75 flex items-center text-sm font-medium"
                                            >
                                                <Trash2 className="h-4 w-4 mr-1" />
                                                Cancel
                                            </button>
                                        )
                                    )}
                                </div>
                            </div>
                        ))}

                        {paginatedAppts.length === 0 && (
                            <div className="bg-transparent p-10 rounded-none border border-dashed border-[#e2e2df] dark:border-[#333330] text-center text-[#a0a09e] dark:text-[#8a8a88]">
                                {searchTerm ? "No matching appointments found." : "No appointments found. Book your first one today!"}
                            </div>
                        )}
                    </div>

                    {/* Pagination Controls */}
                    {totalPages > 1 && (
                        <div className="mt-6 flex items-center justify-end space-x-2">
                            <button
                                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                                disabled={currentPage === 1}
                                className="p-1 border border-[#e2e2df] dark:border-[#333330] disabled:opacity-40 text-[#2d2d2a] dark:text-[#e8e8e6]"
                            >
                                <ChevronLeft className="h-4 w-4" />
                            </button>
                            <span className="text-xs text-[#5a5a57] dark:text-[#a0a09e]">
                                Page {currentPage} of {totalPages}
                            </span>
                            <button
                                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                                disabled={currentPage === totalPages}
                                className="p-1 border border-[#e2e2df] dark:border-[#333330] disabled:opacity-40 text-[#2d2d2a] dark:text-[#e8e8e6]"
                            >
                                <ChevronRight className="h-4 w-4" />
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Booking Modal */}
            <Modal isOpen={isBookingOpen} onClose={() => setIsBookingOpen(false)} title="New Appointment">
                <form onSubmit={handleSubmit(handleBookingSubmit)} className="space-y-4 text-left">
                    <FormField 
                        label="Select Doctor"
                        name="doc"
                        type="select"
                        options={docOptions}
                        error={errors.doc}
                        {...register('doc')}
                    />

                    <FormField 
                        label="Date"
                        name="date"
                        type="select"
                        options={dateOptions}
                        disabled={!watchedDoc}
                        error={errors.date}
                        {...register('date')}
                    />

                    <FormField 
                        label="Time Slot"
                        name="time"
                        type="select"
                        options={timeOptions}
                        disabled={!watchedDate}
                        error={errors.time}
                        {...register('time')}
                    />

                    <div className="flex justify-end gap-3 mt-6">
                        <button 
                            type="button" 
                            onClick={() => setIsBookingOpen(false)} 
                            className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] text-sm text-gray-700 dark:text-[#e8e8e6] hover:bg-[#fcf8f8] dark:hover:bg-[#252523] transition-colors"
                        >
                            Cancel
                        </button>
                        <button 
                            type="submit" 
                            className="px-4 py-2 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-sm hover:opacity-80 transition-opacity font-medium"
                        >
                            Book Now
                        </button>
                    </div>
                </form>
            </Modal>

            {/* Prescription View Modal */}
            {isPrescOpen && selectedPresc && (
                <Modal isOpen={isPrescOpen} onClose={() => setIsPrescOpen(false)} title="Prescription Details">
                    <div className="space-y-4 text-left text-[#2d2d2a] dark:text-[#e8e8e6]">
                        <div className="border-b border-[#e2e2df] dark:border-[#333330] pb-3">
                            <p className="text-sm font-medium">Doctor: <span className="font-semibold">Dr. {selectedPresc.doctor_name}</span></p>
                            <p className="text-xs text-[#a0a09e] dark:text-[#8a8a88]">Date: {selectedPresc.date}</p>
                        </div>
                        <div className="space-y-2 text-sm">
                            <p><strong>Ailment:</strong> {selectedPresc.ailment}</p>
                            <p><strong>Prescription:</strong> {selectedPresc.prescription}</p>
                            <p><strong>Notes:</strong> {selectedPresc.notes}</p>
                        </div>
                        <div className="flex justify-between items-center pt-4 border-t border-[#e2e2df] dark:border-[#333330] mt-6">
                            <button 
                                onClick={() => downloadPDF(selectedPresc, data.patient.pat_name)}
                                className="flex items-center gap-1.5 text-xs bg-[#f0f0eb] dark:bg-[#252523] text-gray-700 dark:text-[#e8e8e6] hover:bg-gray-200 dark:hover:bg-[#333330] py-1 px-3 border border-[#e2e2df] dark:border-[#333330] transition"
                            >
                                <Download className="h-3.5 w-3.5" /> Download PDF
                            </button>
                            <button 
                                onClick={() => setIsPrescOpen(false)}
                                className="px-4 py-1.5 border border-[#e2e2df] dark:border-[#333330] text-xs hover:bg-[#fcf8f8] dark:hover:bg-[#252523]"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </Modal>
            )}
        </div>
    );
};

export default PatientDashboard;
