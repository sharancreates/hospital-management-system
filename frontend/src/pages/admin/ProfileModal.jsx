import React from 'react';
import Modal from '../../components/ui/Modal';
import { Activity, Download } from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const ProfileModal = ({ isOpen, onClose, type, data }) => {
    if (!isOpen || !data) return null;

    const downloadPrescription = (hist, patientName) => {
        const doc = new jsPDF();
        doc.setFontSize(20);
        doc.text("Arogya Hospital - Medical Prescription", 105, 20, { align: "center" });
        
        doc.setFontSize(12);
        doc.text(`Patient: ${patientName}`, 20, 40);
        doc.text(`Doctor: Dr. ${hist.doctor}`, 20, 50);
        doc.text(`Date: ${hist.date}`, 150, 40);
        
        autoTable(doc, {
            startY: 60,
            head: [['Field', 'Details']],
            body: [
                ['Ailment', hist.ailment],
                ['Prescription', hist.prescription],
                ['Notes', hist.notes]
            ],
        });
        
        doc.save(`${patientName}_Prescription_${hist.date}.pdf`);
    };

    const title = type === 'doctor' ? data.doctor.doc_name : data.patient.pat_name;
    const sub = type === 'doctor' ? `Doctor Profile • ${data.doctor.department}` : 'Patient Profile';

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={title} maxWidth="max-w-2xl">
            <div className="space-y-6 text-[#2d2d2a] dark:text-[#e8e8e6]">
                <p className="text-xs text-[#a0a09e] dark:text-[#8a8a88] uppercase tracking-wider -mt-4 mb-4">
                    {sub}
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-[#fcf8f8] dark:bg-[#252523] p-4 border border-[#e2e2df] dark:border-[#333330]">
                        <h3 className="text-xs font-semibold text-[#a0a09e] dark:text-[#8a8a88] uppercase tracking-wider">Contact Details</h3>
                        <p className="mt-1 text-sm">{type === 'doctor' ? data.doctor.contact_num : data.patient.contact_num}</p>
                    </div>
                    <div className="bg-[#fcf8f8] dark:bg-[#252523] p-4 border border-[#e2e2df] dark:border-[#333330]">
                        <h3 className="text-xs font-semibold text-[#a0a09e] dark:text-[#8a8a88] uppercase tracking-wider">Personal Info</h3>
                        <p className="mt-1 text-sm">
                            {type === 'doctor' ? data.doctor.gender : data.patient.gender}, 
                            Born: {type === 'doctor' ? data.doctor.dob : data.patient.dob}
                            {type === 'patient' && ` (Age: ${data.patient.age})`}
                        </p>
                    </div>
                </div>

                {type === 'doctor' && (
                    <div>
                        <h3 className="text-base font-serif font-medium mb-3">Performance Stats</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-blue-50 dark:bg-blue-950/20 p-4 border border-blue-100 dark:border-blue-900/50 text-center">
                                <span className="block text-2xl font-serif font-medium text-blue-600 dark:text-blue-400">{data.stats.total_appointments}</span>
                                <span className="text-xs text-[#a0a09e] dark:text-blue-300 uppercase tracking-wider">Total Appointments</span>
                            </div>
                            <div className="bg-green-50 dark:bg-green-950/20 p-4 border border-green-100 dark:border-green-900/50 text-center">
                                <span className="block text-2xl font-serif font-medium text-green-600 dark:text-green-400">{data.stats.total_treated}</span>
                                <span className="text-xs text-[#a0a09e] dark:text-green-300 uppercase tracking-wider">Patients Treated</span>
                            </div>
                        </div>
                    </div>
                )}

                {type === 'patient' && (
                    <div>
                        <h3 className="text-base font-serif font-medium mb-3">Treatment History</h3>
                        {data.ai_insight && (
                            <div className="bg-purple-50 dark:bg-purple-950/20 text-purple-800 dark:text-purple-300 p-4 border border-purple-100 dark:border-purple-900/50 mb-4 text-sm flex items-start gap-3">
                                <Activity className="h-5 w-5 flex-shrink-0 mt-0.5" />
                                <p>{data.ai_insight}</p>
                            </div>
                        )}
                        <div className="space-y-4 max-h-60 overflow-y-auto pr-1">
                            {data.history && data.history.length > 0 ? data.history.map((hist, idx) => (
                                <div key={idx} className="border border-[#e2e2df] dark:border-[#333330] p-4 bg-[#fcf8f8] dark:bg-[#252523]">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium text-[#2d2d2a] dark:text-[#e8e8e6]">{hist.date} - Dr. {hist.doctor}</span>
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${hist.status === 'Completed' ? 'bg-[#f0f0eb] dark:bg-[#252523] text-[#2d2d2a] dark:text-[#e8e8e6]' : 'bg-[#f0f0eb] dark:bg-[#252523] text-gray-800 dark:text-gray-300'}`}>{hist.status}</span>
                                    </div>
                                    {hist.status === 'Completed' ? (
                                        <div className="text-sm text-[#5a5a57] dark:text-[#a0a09e] space-y-3">
                                            <p><strong>Ailment:</strong> {hist.ailment}</p>
                                            <p><strong>Prescription:</strong> {hist.prescription}</p>
                                            <p><strong>Notes:</strong> {hist.notes}</p>
                                            <button 
                                                onClick={() => downloadPrescription(hist, data.patient.pat_name)} 
                                                className="flex items-center gap-1.5 text-xs bg-[#f0f0eb] dark:bg-[#252523] text-gray-700 dark:text-[#e8e8e6] hover:bg-gray-200 dark:hover:bg-[#333330] py-1 px-3 border border-[#e2e2df] dark:border-[#333330] transition"
                                            >
                                                <Download className="h-3.5 w-3.5" /> Download PDF
                                            </button>
                                        </div>
                                    ) : (
                                        <p className="text-xs text-[#a0a09e] dark:text-[#8a8a88] italic">Treatment not yet completed.</p>
                                    )}
                                </div>
                            )) : (
                                <p className="text-sm text-[#a0a09e] dark:text-[#8a8a88] text-center py-4">No past treatments found.</p>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </Modal>
    );
};

export default ProfileModal;
