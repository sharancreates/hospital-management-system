import React, { useState } from 'react';
import api from '../../api';

const WardsPanel = ({ Wards, patients, onRefresh }) => {
    const [admittingBed, setAdmittingBed] = useState(null);
    const [selectedPatientId, setSelectedPatientId] = useState('');
    const [reason, setReason] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleAdmit = async (e) => {
        e.preventDefault();
        if (!selectedPatientId || !reason) {
            alert("Please select a patient and enter admission reason.");
            return;
        }
        setIsSubmitting(true);
        try {
            await api.post('/enterprise/admit', {
                patient_id: parseInt(selectedPatientId),
                bed_id: admittingBed.bed_id,
                reason: reason
            });
            alert("Patient admitted successfully!");
            setAdmittingBed(null);
            setSelectedPatientId('');
            setReason('');
            onRefresh();
        } catch (err) {
            alert(err.response?.data?.message || "Failed to admit patient.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDischarge = async (admissionId) => {
        if (!window.confirm("Are you sure you want to discharge this patient?")) return;
        try {
            await api.post(`/enterprise/discharge/${admissionId}`);
            alert("Patient discharged successfully!");
            onRefresh();
        } catch (err) {
            alert(err.response?.data?.message || "Failed to discharge patient.");
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-serif font-medium">Ward & Inpatient Management</h2>
                <button 
                    onClick={onRefresh}
                    className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] hover:bg-[#f5f5f0] dark:hover:bg-[#252523] text-sm transition-colors"
                >
                    Refresh Layout
                </button>
            </div>

            {admittingBed && (
                <div className="border border-[#e2e2df] dark:border-[#333330] p-6 bg-[#fcf8f8]/30 dark:bg-[#252523]/30">
                    <h3 className="text-lg font-serif mb-4">Admit Patient to Bed {admittingBed.bed_number}</h3>
                    <form onSubmit={handleAdmit} className="space-y-4 max-w-lg">
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-[#a0a09e] mb-1">Select Patient</label>
                            <select 
                                value={selectedPatientId} 
                                onChange={(e) => setSelectedPatientId(e.target.value)}
                                className="w-full px-3 py-2 border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-sm focus:outline-none"
                            >
                                <option value="">-- Choose Patient --</option>
                                {patients.map(p => (
                                    <option key={p.patient_id} value={p.patient_id}>{p.pat_name} (ID: {p.patient_id})</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-[#a0a09e] mb-1">Reason for Admission</label>
                            <textarea 
                                value={reason} 
                                onChange={(e) => setReason(e.target.value)}
                                rows={3}
                                className="w-full px-3 py-2 border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-sm focus:outline-none"
                                placeholder="e.g. Post-operative observation, severe pneumonia, etc."
                            />
                        </div>
                        <div className="flex gap-4">
                            <button 
                                type="submit" 
                                disabled={isSubmitting}
                                className="px-4 py-2 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-sm font-medium hover:opacity-90 transition-opacity"
                            >
                                {isSubmitting ? "Admitting..." : "Admit Patient"}
                            </button>
                            <button 
                                type="button" 
                                onClick={() => setAdmittingBed(null)}
                                className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] text-sm hover:bg-[#f5f5f0] dark:hover:bg-[#252523] transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {Wards.length === 0 ? (
                <div className="border border-dashed border-[#e2e2df] dark:border-[#333330] p-12 text-center text-[#5a5a57] dark:text-[#a0a09e] italic">
                    No wards or beds found in the system. Click "Refresh Layout" or verify your database state.
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {Wards.map(ward => (
                        <div key={ward.ward_id} className="border border-[#e2e2df] dark:border-[#333330] p-6 space-y-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="text-xl font-serif font-medium">{ward.ward_name}</h3>
                                    <span className="text-xs text-[#a0a09e] uppercase tracking-wider">{ward.ward_type} • Capacity: {ward.capacity} Beds</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {ward.beds.map(bed => (
                                    <div 
                                        key={bed.bed_id} 
                                        className={`p-4 border ${
                                            bed.status === 'Available' 
                                                ? 'border-[#e2e2df] dark:border-[#333330]' 
                                                : 'border-[#c54b4b]/30 bg-[#c54b4b]/5'
                                        } flex flex-col justify-between`}
                                    >
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="text-sm font-semibold">Bed {bed.bed_number}</span>
                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                                                bed.status === 'Available'
                                                    ? 'bg-green-100 dark:bg-green-950 text-green-800 dark:text-green-300'
                                                    : 'bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-300'
                                            }`}>
                                                {bed.status}
                                            </span>
                                        </div>

                                        {bed.status === 'Available' ? (
                                            <button 
                                                onClick={() => setAdmittingBed(bed)}
                                                className="w-full mt-2 py-1 text-xs border border-[#2d2d2a] dark:border-[#e8e8e6] text-[#2d2d2a] dark:text-[#e8e8e6] hover:bg-[#2d2d2a] hover:text-[#FDFCF8] dark:hover:bg-[#e8e8e6] dark:hover:text-[#1a1a19] transition-colors"
                                            >
                                                Admit Patient
                                            </button>
                                        ) : (
                                            <div className="space-y-3">
                                                {bed.active_admission ? (
                                                    <div className="text-xs text-[#5a5a57] dark:text-[#a0a09e] space-y-1">
                                                        <p className="font-semibold text-[#2d2d2a] dark:text-[#e8e8e6]">{bed.active_admission.patient_name}</p>
                                                        <p className="italic">Reason: {bed.active_admission.reason}</p>
                                                        <p className="text-[10px]">Admitted: {new Date(bed.active_admission.admitted_at).toLocaleDateString()}</p>
                                                    </div>
                                                ) : (
                                                    <p className="text-xs italic text-red-500">Admission record not found.</p>
                                                )}
                                                {bed.active_admission && (
                                                    <button 
                                                        onClick={() => handleDischarge(bed.active_admission.admission_id)}
                                                        className="w-full py-1 text-xs bg-red-600 text-white hover:bg-red-700 transition-colors"
                                                    >
                                                        Discharge Patient
                                                    </button>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default WardsPanel;
