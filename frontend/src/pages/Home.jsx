import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
    Moon, 
    Sun, 
    Calendar, 
    User, 
    Users, 
    Clock, 
    Activity, 
    BarChart3, 
    Shield, 
    Receipt, 
    HardDrive, 
    Download, 
    FileJson,
    ChevronRight,
    FileText,
    Heart,
    X
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import api from '../api';

const Home = () => {
    const { darkMode, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        available_beds_pct: null,
        active_admissions: null,
        system_status: 'Checking...',
        queue_delay: null
    });
    const [activeDocument, setActiveDocument] = useState(null);

    const docData = {
        privacy: {
            title: "Privacy Policy",
            icon: <Shield className="w-8 h-8 text-amber-500" />,
            content: (
                <div className="space-y-4 text-[#a0a09e] text-sm leading-relaxed">
                    <p className="border-b border-[#40403d] pb-2"><strong>Last Updated: June 5, 2026</strong></p>
                    <p>Welcome to Arogya Medical Center. We are dedicated to maintaining the privacy and security of your Protected Health Information (PHI) in accordance with global clinical record-keeping standards.</p>
                    <h3 className="font-semibold text-base mt-4 text-[#FDFCF8]">1. Information We Collect</h3>
                    <p>We collect and store patient identification data (names, contact numbers, email addresses), demographic metrics (Date of Birth, gender), appointment slots, diagnoses, prescription records, and payment/insurance details.</p>
                    <h3 className="font-semibold text-base mt-4 text-[#FDFCF8]">2. Use of Medical Records</h3>
                    <p>Your PHI is accessed exclusively to coordinate clinical treatments, process billing invoices, issue digital prescriptions, and compute system live status stats (e.g., lobby queue lengths). We do not share your details with marketing or third-party organizations.</p>
                    <h3 className="font-semibold text-base mt-4 text-[#FDFCF8]">3. Data Protection Practices</h3>
                    <p>All sessions and API actions are protected using double-submit CSRF tokens and role-based route access layers. Passwords are securely hashed using cryptographic salts, and clinical transactions are recorded in encrypted system audit logs.</p>
                </div>
            )
        },
        terms: {
            title: "Terms of Service",
            icon: <FileText className="w-8 h-8 text-blue-500" />,
            content: (
                <div className="space-y-4 text-[#a0a09e] text-sm leading-relaxed">
                    <p className="border-b border-[#40403d] pb-2"><strong>Last Updated: June 5, 2026</strong></p>
                    <p>By registering or using the Arogya HMS portals, you agree to comply with and be bound by the following Terms of Service.</p>
                    <h3 className="font-semibold text-base mt-4 text-[#FDFCF8]">1. User Registrations & Accounts</h3>
                    <p>You must provide accurate, complete, and current details during registration. You are solely responsible for maintaining the confidentiality of your account credentials. You must immediately notify administration of any suspected security breach.</p>
                    <h3 className="font-semibold text-base mt-4 text-[#FDFCF8]">2. Purpose of Portal</h3>
                    <p>The Arogya patient portal is designed for administrative booking, prescription downloads, and inpatient tracking. <strong className="text-amber-400">This portal is not monitored for critical clinical emergencies. If you are experiencing a life-threatening medical emergency, call emergency services or visit the nearest emergency room immediately.</strong></p>
                    <h3 className="font-semibold text-base mt-4 text-[#FDFCF8]">3. System Restraints</h3>
                    <p>Any attempt to scan for vulnerabilities, run denial-of-service (DoS) scripts, upload malicious packages, or bypass API CSRF protection is strictly prohibited and will result in permanent account termination and legal reporting.</p>
                </div>
            )
        },
        rights: {
            title: "Patient Rights",
            icon: <Heart className="w-8 h-8 text-rose-500" />,
            content: (
                <div className="space-y-4 text-[#a0a09e] text-sm leading-relaxed">
                    <p className="border-b border-[#40403d] pb-2"><strong>Last Updated: June 5, 2026</strong></p>
                    <p>As a patient of Arogya Medical Center, you possess fundamental rights regarding your medical treatment, choice of providers, and data access.</p>
                    <h3 className="font-semibold text-base mt-4 text-[#FDFCF8]">1. Right to Access & Records</h3>
                    <p>You have the right to request, view, and download copies of your Electronic Health Records (EHR) and prescriptions at any time. This clinical data is exportable in standard FHIR JSON and HL7 formats.</p>
                    <h3 className="font-semibold text-base mt-4 text-[#FDFCF8]">2. Respect & Dignity</h3>
                    <p>You have the right to receive respectful, compassionate, and non-discriminatory care from all medical officers, nurses, and administrative staff, regardless of your insurance provider or clinical condition.</p>
                    <h3 className="font-semibold text-base mt-4 text-[#FDFCF8]">3. Billing Disclosure</h3>
                    <p>You have the right to a clear, detailed explanation of all clinical services, diagnostic lab orders, pharmacy items, and coverage limits computed on your billing invoices.</p>
                </div>
            )
        }
    };

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await api.get('/public/stats');
                if (res.data && res.data.status === 'success') {
                    setStats({
                        available_beds_pct: res.data.available_beds_pct,
                        active_admissions: res.data.active_admissions,
                        system_status: res.data.system_status,
                        queue_delay: res.data.queue_delay
                    });
                }
            } catch (err) {
                console.error("Failed to load public stats:", err);
                setStats({
                    available_beds_pct: 100,
                    active_admissions: 0,
                    system_status: 'Active',
                    queue_delay: 5
                });
            }
        };
        fetchStats();
    }, []);

    return (
        <div className="min-h-screen bg-[#FDFCF8] dark:bg-[#1a1a19] transition-colors duration-300 font-sans text-[#2d2d2a] dark:text-[#e8e8e6]">
            
            {/* Minimalist Header */}
            <header className="max-w-6xl mx-auto px-6 py-8 flex justify-between items-center sticky top-0 bg-[#FDFCF8]/90 dark:bg-[#1a1a19]/90 backdrop-blur-md z-50 border-b border-[#f0f0eb]/60 dark:border-[#2a2a28]/60">
                <div className="flex items-center gap-2 cursor-pointer" onClick={() => window.scrollTo({top: 0, behavior: 'smooth'})}>
                    <span className="text-xl font-serif font-medium tracking-tight">Arogya Medical</span>
                </div>
                <div className="flex items-center gap-6">
                    <button 
                        onClick={toggleTheme}
                        className="text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
                        aria-label="Toggle dark mode"
                    >
                        {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                    </button>
                    <Link to="/login" className="text-sm font-medium hover:underline underline-offset-4 decoration-1">
                        Sign In
                    </Link>
                </div>
            </header>

            {/* Hero Section */}
            <main className="max-w-6xl mx-auto px-6 pt-24 pb-20 text-center md:text-left">
                <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
                    <div className="md:col-span-8">
                        <span className="text-xs font-semibold uppercase tracking-widest text-[#a0a09e] dark:text-[#8a8a88] mb-3 block">
                            Integrated Clinical Infrastructure
                        </span>
                        <h1 className="text-4xl md:text-6xl font-serif font-medium leading-tight mb-8">
                            A modern ecosystem <br /> for patient-first care.
                        </h1>

                        <p className="text-lg md:text-xl text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed max-w-2xl font-light mb-12">
                            Arogya Medical Center unites hospital operations, digital patient pathways, 
                            and advanced administrative intelligence into a unified, secure dashboard experience.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center gap-4">
                            <Link 
                                to="/patient/register" 
                                className="px-6 py-3 rounded-none bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-sm font-medium hover:opacity-90 transition-opacity w-full sm:w-auto text-center"
                            >
                                Register as Patient
                            </Link>
                            <Link 
                                to="/login" 
                                className="px-6 py-3 rounded-none border border-[#e2e2df] dark:border-[#333330] text-[#2d2d2a] dark:text-[#e8e8e6] hover:bg-[#f5f5f0] dark:hover:bg-[#252523] text-sm font-medium transition-colors w-full sm:w-auto text-center"
                            >
                                Access Staff Portal
                            </Link>
                        </div>
                    </div>
                    
                    {/* Live Stats Preview */}
                    <div className="md:col-span-4 border border-[#e2e2df] dark:border-[#333330] p-6 space-y-6 bg-[#fcf8f8]/30 dark:bg-[#252523]/10">
                        <h3 className="text-sm font-semibold uppercase tracking-wider text-[#a0a09e]">System Live Stats</h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center border-b border-[#e2e2df] dark:border-[#333330] pb-2">
                                <span className="text-xs text-[#5a5a57] dark:text-[#a0a09e]">Available Beds</span>
                                <span className="text-sm font-bold text-green-600 dark:text-green-400">
                                    {stats.available_beds_pct !== null ? `${stats.available_beds_pct}% Available` : 'Loading...'}
                                </span>
                            </div>
                            <div className="flex justify-between items-center border-b border-[#e2e2df] dark:border-[#333330] pb-2">
                                <span className="text-xs text-[#5a5a57] dark:text-[#a0a09e]">Active Admissions</span>
                                <span className="text-sm font-bold">
                                    {stats.active_admissions !== null ? `${stats.active_admissions} Patients` : 'Loading...'}
                                </span>
                            </div>
                            <div className="flex justify-between items-center border-b border-[#e2e2df] dark:border-[#333330] pb-2">
                                <span className="text-xs text-[#5a5a57] dark:text-[#a0a09e]">EHR System Status</span>
                                <span className="text-xs font-semibold px-2 py-0.5 bg-green-100 dark:bg-green-950 text-green-800 dark:text-green-300 rounded-full">
                                    {stats.system_status}
                                </span>
                            </div>
                            <div className="flex justify-between items-center pb-1">
                                <span className="text-xs text-[#5a5a57] dark:text-[#a0a09e]">Queue Delay</span>
                                <span className="text-sm font-bold text-amber-600 dark:text-amber-400">
                                    {stats.queue_delay !== null ? `~${stats.queue_delay} Mins` : 'Loading...'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Portals Deep-Dive Section */}
            <section className="max-w-6xl mx-auto px-6 py-24 border-t border-[#f0f0eb] dark:border-[#2a2a28]">
                <h2 className="text-3xl font-serif font-medium mb-3">System Roles & Features</h2>
                <p className="text-sm text-[#a0a09e] dark:text-[#8a8a88] mb-12">Click any role to log in and access specific workflows.</p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Patient Portal Card */}
                    <div 
                        onClick={() => navigate('/login')}
                        className="group border border-[#e2e2df] dark:border-[#333330] p-8 hover:bg-[#fcf8f8]/50 dark:hover:bg-[#252523]/30 transition-all cursor-pointer flex flex-col justify-between"
                    >
                        <div>
                            <div className="w-10 h-10 border border-[#e2e2df] dark:border-[#333330] flex items-center justify-center mb-6 text-[#2d2d2a] dark:text-[#e8e8e6]">
                                <User className="h-5 w-5" />
                            </div>
                            <h3 className="text-xl font-serif font-medium mb-4 group-hover:text-amber-800 dark:group-hover:text-amber-300 transition-colors">Patient Portal</h3>
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed mb-6">
                                Fully managed self-service portal. Book appointments dynamically based on doctor schedules, monitor real-time consultations, and download prescription PDFs.
                            </p>
                            <ul className="space-y-2 text-xs text-[#5a5a57] dark:text-[#a0a09e]">
                                <li className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-full"></span>
                                    Dynamic scheduling by specialty
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-full"></span>
                                    Live lobby consultation queue
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-full"></span>
                                    Instant PDF Prescription download
                                </li>
                            </ul>
                        </div>
                        <div className="mt-8 flex items-center gap-1 text-xs font-semibold uppercase tracking-wider opacity-60 group-hover:opacity-100 transition-opacity">
                            Patient Login <ChevronRight className="h-3 w-3" />
                        </div>
                    </div>

                    {/* Doctor Portal Card */}
                    <div 
                        onClick={() => navigate('/login')}
                        className="group border border-[#e2e2df] dark:border-[#333330] p-8 hover:bg-[#fcf8f8]/50 dark:hover:bg-[#252523]/30 transition-all cursor-pointer flex flex-col justify-between"
                    >
                        <div>
                            <div className="w-10 h-10 border border-[#e2e2df] dark:border-[#333330] flex items-center justify-center mb-6 text-[#2d2d2a] dark:text-[#e8e8e6]">
                                <Calendar className="h-5 w-5" />
                            </div>
                            <h3 className="text-xl font-serif font-medium mb-4 group-hover:text-amber-800 dark:group-hover:text-amber-300 transition-colors">Doctor Portal</h3>
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed mb-6">
                                Specialized clinical environment. Manage recurring availability slots, review patient histories, write diagnostic logs, and issue secure prescriptions.
                            </p>
                            <ul className="space-y-2 text-xs text-[#5a5a57] dark:text-[#a0a09e]">
                                <li className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-full"></span>
                                    Smart slot availability manager
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-full"></span>
                                    Patient history & diagnosis records
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-full"></span>
                                    Prescription issuance & completion
                                </li>
                            </ul>
                        </div>
                        <div className="mt-8 flex items-center gap-1 text-xs font-semibold uppercase tracking-wider opacity-60 group-hover:opacity-100 transition-opacity">
                            Doctor Login <ChevronRight className="h-3 w-3" />
                        </div>
                    </div>

                    {/* Admin Portal Card */}
                    <div 
                        onClick={() => navigate('/login')}
                        className="group border border-[#e2e2df] dark:border-[#333330] p-8 hover:bg-[#fcf8f8]/50 dark:hover:bg-[#252523]/30 transition-all cursor-pointer flex flex-col justify-between"
                    >
                        <div>
                            <div className="w-10 h-10 border border-[#e2e2df] dark:border-[#333330] flex items-center justify-center mb-6 text-[#2d2d2a] dark:text-[#e8e8e6]">
                                <BarChart3 className="h-5 w-5" />
                            </div>
                            <h3 className="text-xl font-serif font-medium mb-4 group-hover:text-amber-800 dark:group-hover:text-amber-300 transition-colors">Admin Dashboard</h3>
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed mb-6">
                                Executive control plane. Oversee metrics, configure doctors/departments, monitor bed capacities, manage billing, and export HL7/FHIR health records.
                            </p>
                            <ul className="space-y-2 text-xs text-[#5a5a57] dark:text-[#a0a09e]">
                                <li className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-full"></span>
                                    7-day throughput analytics charts
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-full"></span>
                                    Bed occupancy & inpatient tracker
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-full"></span>
                                    Billing, Claims & HL7/FHIR exports
                                </li>
                            </ul>
                        </div>
                        <div className="mt-8 flex items-center gap-1 text-xs font-semibold uppercase tracking-wider opacity-60 group-hover:opacity-100 transition-opacity">
                            Admin Login <ChevronRight className="h-3 w-3" />
                        </div>
                    </div>
                </div>
            </section>

            {/* Advanced Capabilities (Feature Grid) */}
            <section className="bg-[#f5f5f0] dark:bg-[#151514] border-y border-[#f0f0eb] dark:border-[#2a2a28]">
                <div className="max-w-6xl mx-auto px-6 py-24">
                    <h2 className="text-3xl font-serif font-medium mb-16 text-center">Advanced Infrastructure & Integrations</h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                        <div className="bg-[#FDFCF8] dark:bg-[#1a1a19] p-6 border border-[#e2e2df] dark:border-[#333330]">
                            <Clock className="h-6 w-6 mb-4 text-[#a0a09e]" />
                            <h3 className="text-lg font-serif font-medium mb-2">Live Waiting Room Queues</h3>
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed">
                                Real-time patient waiting list calculations, projecting wait times dynamically to minimize lobby wait lines.
                            </p>
                        </div>

                        <div className="bg-[#FDFCF8] dark:bg-[#1a1a19] p-6 border border-[#e2e2df] dark:border-[#333330]">
                            <HardDrive className="h-6 w-6 mb-4 text-[#a0a09e]" />
                            <h3 className="text-lg font-serif font-medium mb-2">Bed & Inpatient Tracking</h3>
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed">
                                Categorized ward capacities (ICU, General, Semi-Private). Admit, discharge, and transition patients instantly with live occupancy tracking.
                            </p>
                        </div>

                        <div className="bg-[#FDFCF8] dark:bg-[#1a1a19] p-6 border border-[#e2e2df] dark:border-[#333330]">
                            <Receipt className="h-6 w-6 mb-4 text-[#a0a09e]" />
                            <h3 className="text-lg font-serif font-medium mb-2">Billing & Claims Registry</h3>
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed">
                                Automates billing invoice creation, tracks insurance providers, policy identifiers, and claim progress states natively.
                            </p>
                        </div>

                        <div className="bg-[#FDFCF8] dark:bg-[#1a1a19] p-6 border border-[#e2e2df] dark:border-[#333330]">
                            <Download className="h-6 w-6 mb-4 text-[#a0a09e]" />
                            <h3 className="text-lg font-serif font-medium mb-2">HL7 v2 Message Exporting</h3>
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed">
                                Seamlessly export diagnostic and clinical events formatted as standard HL7 v2 messages for cross-facility interoperability.
                            </p>
                        </div>

                        <div className="bg-[#FDFCF8] dark:bg-[#1a1a19] p-6 border border-[#e2e2df] dark:border-[#333330]">
                            <FileJson className="h-6 w-6 mb-4 text-[#a0a09e]" />
                            <h3 className="text-lg font-serif font-medium mb-2">FHIR Electronic Records</h3>
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed">
                                Convert patient datasets and consults into structured, compliant FHIR JSON schemas for standard-compliant data exchange.
                            </p>
                        </div>

                        <div className="bg-[#FDFCF8] dark:bg-[#1a1a19] p-6 border border-[#e2e2df] dark:border-[#333330]">
                            <Shield className="h-6 w-6 mb-4 text-[#a0a09e]" />
                            <h3 className="text-lg font-serif font-medium mb-2">CSRF & Rate-Limit Security</h3>
                            <p className="text-sm text-[#5a5a57] dark:text-[#a0a09e] leading-relaxed">
                                Enterprise-grade safety features including CSRF cookie verification and active route rate-limiting to block DoS vectors.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Departments Section */}
            <section className="max-w-6xl mx-auto px-6 py-24">
                <h2 className="text-3xl font-serif font-medium mb-12">Our Specialized Departments</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-12">
                    {[
                        { name: "Cardiology", desc: "Heart & cardiovascular care" },
                        { name: "Neurology", desc: "Brain & nervous system care" },
                        { name: "Pediatrics", desc: "Youth & infant clinical care" },
                        { name: "Orthopedics", desc: "Musculoskeletal & bone care" },
                        { name: "Dermatology", desc: "Skin, hair, & nail conditions" },
                        { name: "General Medicine", desc: "Primary care & routine checkups" }
                    ].map(dept => (
                        <div key={dept.name} className="group block">
                            <div className="h-px w-full bg-[#e2e2df] dark:bg-[#333330] mb-4"></div>
                            <h3 className="text-lg font-serif font-medium">{dept.name}</h3>
                            <p className="text-xs text-[#a0a09e] dark:text-[#8a8a88] mt-1">{dept.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Extended Footer */}
            <footer className="bg-[#2d2d2a] dark:bg-[#111110] text-[#e8e8e6] dark:text-[#8a8a88] pt-16 pb-8 px-6">
                <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
                    <div className="md:col-span-2">
                        <span className="text-xl font-serif font-medium text-[#FDFCF8] tracking-tight block mb-4">Arogya Medical</span>
                        <p className="text-sm leading-relaxed max-w-xs text-[#a0a09e]">
                            Providing state-of-the-art care, secure patient tools, and integrated clinical logistics.
                        </p>
                    </div>
                    <div>
                        <h4 className="text-sm font-medium text-[#FDFCF8] mb-4">Contact</h4>
                        <ul className="space-y-2 text-sm text-[#a0a09e]">
                            <li>+91 1234567859</li>
                            <li>sharanyanagar@yahoo.in</li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="text-sm font-medium text-[#FDFCF8] mb-4">Location</h4>
                        <ul className="space-y-2 text-sm text-[#a0a09e]">
                            <li>Sharanya Nagar</li>
                        </ul>
                    </div>
                </div>
                <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center text-xs text-[#a0a09e] pt-8 border-t border-[#40403d] dark:border-[#222220]">
                    <p>© 2026 Arogya Medical Center. All rights reserved.</p>
                    <div className="flex gap-4 mt-4 md:mt-0">
                        <span onClick={() => setActiveDocument('privacy')} className="hover:text-[#FDFCF8] cursor-pointer transition-colors">Privacy Policy</span>
                        <span onClick={() => setActiveDocument('terms')} className="hover:text-[#FDFCF8] cursor-pointer transition-colors">Terms of Service</span>
                        <span onClick={() => setActiveDocument('rights')} className="hover:text-[#FDFCF8] cursor-pointer transition-colors">Patient Rights</span>
                    </div>
                </div>
            </footer>

            {/* Document Modal */}
            {activeDocument && docData[activeDocument] && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0a0a09]/80 backdrop-blur-sm transition-opacity">
                    <div className="bg-[#2a2a29] border border-[#40403d] rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto shadow-2xl relative flex flex-col transition-all transform scale-100">
                        {/* Modal Header */}
                        <div className="flex items-center justify-between p-6 border-b border-[#40403d] bg-[#222221] rounded-t-2xl">
                            <div className="flex items-center gap-3">
                                {docData[activeDocument].icon}
                                <h2 className="text-xl font-bold text-[#FDFCF8]">{docData[activeDocument].title}</h2>
                            </div>
                            <button 
                                onClick={() => setActiveDocument(null)}
                                className="p-2 text-[#a0a09e] hover:text-[#FDFCF8] hover:bg-[#343432] rounded-lg transition-all"
                                aria-label="Close modal"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        {/* Modal Content */}
                        <div className="p-6 overflow-y-auto text-[#a0a09e] max-h-[60vh]">
                            {docData[activeDocument].content}
                        </div>
                        {/* Modal Footer */}
                        <div className="flex justify-end p-4 border-t border-[#40403d] bg-[#222221] rounded-b-2xl">
                            <button 
                                onClick={() => setActiveDocument(null)}
                                className="px-5 py-2 text-sm font-medium text-[#2d2d2a] bg-[#FDFCF8] hover:bg-[#f6f4ed] rounded-lg transition-all shadow-md"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
};

export default Home;
