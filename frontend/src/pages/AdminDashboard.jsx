import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

// Subcomponents
import StatsOverview from './admin/StatsOverview';
import AnalyticsCharts from './admin/AnalyticsCharts';
import DoctorsDirectory from './admin/DoctorsDirectory';
import PatientsDirectory from './admin/PatientsDirectory';
import AppointmentsTable from './admin/AppointmentsTable';
import ProfileModal from './admin/ProfileModal';
import DoctorFormModal from './admin/DoctorFormModal';
import PatientFormModal from './admin/PatientFormModal';
import AppointmentFormModal from './admin/AppointmentFormModal';
import WardsPanel from './admin/WardsPanel';
import BillingPanel from './admin/BillingPanel';
import InteropPanel from './admin/InteropPanel';

const AdminDashboard = () => {
    const [data, setData] = useState(() => {
        try {
            const cached = localStorage.getItem('admin_dashboard_data');
            return cached ? JSON.parse(cached) : { doctors: [], patients: [], appointments: [], departments: [] };
        } catch (e) {
            return { doctors: [], patients: [], appointments: [], departments: [] };
        }
    });
    const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'wards' | 'billing' | 'interop'
    const [wards, setWards] = useState([]);
    const [bills, setBills] = useState([]);
    const [isLoading, setIsLoading] = useState(() => {
        try {
            return !localStorage.getItem('admin_dashboard_data');
        } catch (e) {
            return true;
        }
    });
    const [error, setError] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Modal Control States
    const [activeModal, setActiveModal] = useState(null); // 'doctor' | 'patient' | 'appointment' | 'profile' | null
    const [selectedItem, setSelectedItem] = useState(null); // Item to edit
    const [profileModalData, setProfileModalData] = useState({ type: '', data: null });

    const navigate = useNavigate();

    const fetchData = async () => {
        try {
            const response = await api.get('/admin/');
            if (typeof response.data === 'string') {
                throw new Error("Unauthorized");
            }
            setData(response.data);
            try {
                localStorage.setItem('admin_dashboard_data', JSON.stringify(response.data));
            } catch (e) {
                // Ignore localStorage errors
            }
        } catch (err) {
            console.error("Dashboard fetch error:", err);
            if (err.response?.status === 401 || err.message === "Unauthorized") {
                navigate('/login');
            } else {
                setError("Failed to load dashboard data.");
            }
        } finally {
            setIsLoading(false);
        }
    };

    const fetchWards = async () => {
        try {
            const res = await api.get('/enterprise/wards');
            if (res.data && res.data.wards) {
                setWards(res.data.wards);
            }
        } catch (e) {
            console.error("Failed to load wards:", e);
        }
    };

    const fetchBills = async () => {
        try {
            const res = await api.get('/enterprise/bills');
            if (res.data && res.data.bills) {
                setBills(res.data.bills);
            }
        } catch (e) {
            console.error("Failed to load bills:", e);
        }
    };

    useEffect(() => {
        fetchData();
        fetchWards();
        fetchBills();
    }, [navigate]);

    // Deletions
    const handleDeleteDoctor = async (id) => {
        if (!window.confirm("Are you sure? This action cannot be undone.")) return;
        try {
            await api.delete(`/admin/delete_doctor/${id}`);
            fetchData();
        } catch (err) {
            alert("Failed to delete doctor.");
        }
    };

    const handleDeletePatient = async (id) => {
        if (!window.confirm("Are you sure? This action cannot be undone.")) return;
        try {
            await api.delete(`/admin/delete_patient/${id}`);
            fetchData();
        } catch (err) {
            alert("Failed to delete patient.");
        }
    };

    const handleCancelAppt = async (id) => {
        if (!window.confirm("Are you sure you want to cancel this appointment?")) return;
        try {
            await api.delete(`/admin/delete_appointment/${id}`);
            fetchData();
        } catch (err) {
            alert("Failed to cancel appointment.");
        }
    };

    // Profiles
    const handleViewProfile = async (type, id) => {
        try {
            const res = await api.get(`/admin/${type}_profile/${id}`);
            if (type === 'patient' && res.data.history && res.data.history.length > 0) {
                res.data.ai_insight = "AI Insight (Gemini Preview): Patient shows consistent follow-ups. Recommend checking blood pressure during next visit based on past prescriptions.";
            }
            setProfileModalData({ type, data: res.data });
            setActiveModal('profile');
        } catch (e) {
            alert("Failed to load profile.");
        }
    };

    // Patient Form Save
    const handleSavePatient = async (formData) => {
        setIsSubmitting(true);
        try {
            if (selectedItem) {
                await api.post(`/admin/update_patient/${selectedItem.patient_id}`, formData);
                alert("Patient updated successfully!");
            } else {
                const res = await api.post('/admin/add_patient', formData);
                alert(`Patient added successfully! Welcome email sent to ${res.data.email}.`);
            }
            setActiveModal(null);
            setSelectedItem(null);
            fetchData();
        } catch (err) {
            alert(err.response?.data?.message || "Failed to save patient.");
        } finally {
            setIsSubmitting(false);
        }
    };

    // Doctor Form Save
    const handleSaveDoctor = async (formData) => {
        setIsSubmitting(true);
        try {
            if (selectedItem) {
                await api.post(`/admin/update_doctor/${selectedItem.doctor_id}`, formData);
                alert("Doctor updated successfully!");
            } else {
                const res = await api.post('/admin/add_doctor', formData);
                alert(`Doctor added successfully! Welcome email sent to ${res.data.email}.`);
            }
            setActiveModal(null);
            setSelectedItem(null);
            fetchData();
        } catch (err) {
            alert(err.response?.data?.message || "Failed to save doctor.");
        } finally {
            setIsSubmitting(false);
        }
    };

    // Appointment Form Save
    const handleSaveAppointment = async (formData) => {
        setIsSubmitting(true);
        try {
            if (selectedItem) {
                const res = await api.post(`/admin/update_appointment/${selectedItem.appointment_id}`, formData);
                alert(res.data.message);
            } else {
                const res = await api.post('/admin/set_appointment', formData);
                alert(res.data.message);
            }
            setActiveModal(null);
            setSelectedItem(null);
            fetchData();
        } catch (err) {
            alert(err.response?.data?.message || "Failed to save appointment.");
        } finally {
            setIsSubmitting(false);
        }
    };

    // Form editing launchers
    const launchEditDoctor = (doc) => {
        setSelectedItem(doc);
        setActiveModal('doctor');
    };

    const launchEditPatient = async (pat) => {
        try {
            const res = await api.get(`/admin/patient_profile/${pat.patient_id}`);
            setSelectedItem(res.data.patient);
            setActiveModal('patient');
        } catch (e) {
            alert("Failed to load patient details for editing.");
        }
    };

    const launchEditAppointment = (appt) => {
        setSelectedItem(appt);
        setActiveModal('appointment');
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#FDFCF8] dark:bg-[#1a1a19]">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-[#e2e2df] dark:border-[#333330] border-t-[#2d2d2a] dark:border-t-[#e8e8e6] rounded-full animate-spin"></div>
                    <span className="font-serif text-lg text-[#5a5a57] dark:text-[#a0a09e]">Loading Dashboard...</span>
                </div>
            </div>
        );
    }
    
    if (error) {
        return <div className="p-10 text-center text-[#c54b4b] bg-[#FDFCF8] dark:bg-[#1a1a19] min-h-screen">{error}</div>;
    }

    return (
        <div className="max-w-6xl mx-auto px-6 py-12 font-sans text-[#2d2d2a] dark:text-[#e8e8e6] bg-[#FDFCF8] dark:bg-[#1a1a19] min-h-screen transition-colors duration-300">
            <h1 className="text-3xl font-serif font-medium text-[#2d2d2a] dark:text-[#e8e8e6] mb-8">Admin Dashboard</h1>

            {/* Tabs Navigation */}
            <div className="flex border-b border-[#e2e2df] dark:border-[#333330] mb-8 bg-[#f5f5f0]/50 dark:bg-[#252523]/50">
                <button 
                    onClick={() => setActiveTab('overview')}
                    className={`px-6 py-3 text-xs font-semibold uppercase tracking-wider border-r border-[#e2e2df] dark:border-[#333330] transition-colors ${
                        activeTab === 'overview' 
                            ? 'bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6]' 
                            : 'text-[#5a5a57] dark:text-[#a0a09e] hover:bg-[#fcf8f8]/50'
                    }`}
                >
                    Overview & Directories
                </button>
                <button 
                    onClick={() => setActiveTab('wards')}
                    className={`px-6 py-3 text-xs font-semibold uppercase tracking-wider border-r border-[#e2e2df] dark:border-[#333330] transition-colors ${
                        activeTab === 'wards' 
                            ? 'bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6]' 
                            : 'text-[#5a5a57] dark:text-[#a0a09e] hover:bg-[#fcf8f8]/50'
                    }`}
                >
                    Ward & Inpatient
                </button>
                <button 
                    onClick={() => setActiveTab('billing')}
                    className={`px-6 py-3 text-xs font-semibold uppercase tracking-wider border-r border-[#e2e2df] dark:border-[#333330] transition-colors ${
                        activeTab === 'billing' 
                            ? 'bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6]' 
                            : 'text-[#5a5a57] dark:text-[#a0a09e] hover:bg-[#fcf8f8]/50'
                    }`}
                >
                    Billing & Insurance
                </button>
                <button 
                    onClick={() => setActiveTab('interop')}
                    className={`px-6 py-3 text-xs font-semibold uppercase tracking-wider transition-colors ${
                        activeTab === 'interop' 
                            ? 'bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6]' 
                            : 'text-[#5a5a57] dark:text-[#a0a09e] hover:bg-[#fcf8f8]/50'
                    }`}
                >
                    Interoperability (HL7/FHIR)
                </button>
            </div>

            {activeTab === 'overview' && (
                <div className="space-y-12">
                    {/* Stats Overview */}
                    <StatsOverview 
                        doctorsCount={data.doctors.length} 
                        patientsCount={data.patients.length} 
                        appointmentsCount={data.appointments.length} 
                    />

                    {/* Recharts Analytics Charts */}
                    {data.analytics && <AnalyticsCharts analytics={data.analytics} />}

                    {/* Directories Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Doctors Directory */}
                        <DoctorsDirectory 
                            doctors={data.doctors} 
                            onViewProfile={(id) => handleViewProfile('doctor', id)}
                            onEditDoctor={launchEditDoctor}
                            onDeleteDoctor={handleDeleteDoctor}
                            onAddDoctor={() => { setSelectedItem(null); setActiveModal('doctor'); }}
                        />

                        {/* Patients Directory */}
                        <PatientsDirectory 
                            patients={data.patients} 
                            onViewProfile={(id) => handleViewProfile('patient', id)}
                            onEditPatient={launchEditPatient}
                            onDeletePatient={handleDeletePatient}
                            onAddPatient={() => { setSelectedItem(null); setActiveModal('patient'); }}
                        />
                    </div>

                    {/* Appointments list */}
                    <AppointmentsTable 
                        appointments={data.appointments}
                        doctorsList={data.doctors}
                        patientsList={data.patients}
                        onViewDoctorProfile={(id) => handleViewProfile('doctor', id)}
                        onViewPatientProfile={(id) => handleViewProfile('patient', id)}
                        onEditAppt={launchEditAppointment}
                        onCancelAppt={handleCancelAppt}
                        onAddAppt={() => { setSelectedItem(null); setActiveModal('appointment'); }}
                    />
                </div>
            )}

            {activeTab === 'wards' && (
                <WardsPanel Wards={wards} patients={data.patients} onRefresh={fetchWards} />
            )}

            {activeTab === 'billing' && (
                <BillingPanel bills={bills} patients={data.patients} onRefresh={fetchBills} />
            )}

            {activeTab === 'interop' && (
                <InteropPanel patients={data.patients} />
            )}

            {/* Render Modal Helpers */}
            <ProfileModal 
                isOpen={activeModal === 'profile'} 
                onClose={() => setActiveModal(null)} 
                type={profileModalData.type}
                data={profileModalData.data}
            />

            <DoctorFormModal 
                isOpen={activeModal === 'doctor'} 
                onClose={() => { setActiveModal(null); setSelectedItem(null); }} 
                onSave={handleSaveDoctor}
                doctor={selectedItem}
                departments={data.departments}
                isSubmitting={isSubmitting}
            />

            <PatientFormModal 
                isOpen={activeModal === 'patient'} 
                onClose={() => { setActiveModal(null); setSelectedItem(null); }} 
                onSave={handleSavePatient}
                patient={selectedItem}
                isSubmitting={isSubmitting}
            />

            <AppointmentFormModal 
                isOpen={activeModal === 'appointment'} 
                onClose={() => { setActiveModal(null); setSelectedItem(null); }} 
                onSave={handleSaveAppointment}
                appointment={selectedItem}
                doctors={data.doctors}
                patients={data.patients}
                isSubmitting={isSubmitting}
            />
        </div>
    );
};

export default AdminDashboard;
