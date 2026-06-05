import React, { useState } from 'react';
import api from '../../api';

const InteropPanel = ({ patients }) => {
    const [selectedPatientId, setSelectedPatientId] = useState('');
    const [hl7Data, setHl7Data] = useState('');
    const [fhirData, setFhirData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [activeExportTab, setActiveExportTab] = useState('fhir'); // 'fhir' | 'hl7'

    const handleExport = async (e) => {
        e.preventDefault();
        if (!selectedPatientId) return;
        setIsLoading(true);
        setHl7Data('');
        setFhirData(null);
        try {
            // Fetch HL7 and FHIR parallelly
            const [hl7Res, fhirRes] = await Promise.all([
                api.get(`/enterprise/export/hl7/${selectedPatientId}`),
                api.get(`/enterprise/export/fhir/${selectedPatientId}`)
            ]);
            setHl7Data(hl7Res.data);
            setFhirData(fhirRes.data);
        } catch (err) {
            alert("Failed to export patient records.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleCopy = (text) => {
        navigator.clipboard.writeText(text);
        alert("Copied to clipboard!");
    };

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-serif font-medium">Standardized Interoperability Exports</h2>
            </div>

            <div className="border border-[#e2e2df] dark:border-[#333330] p-6 bg-[#fcf8f8]/30 dark:bg-[#252523]/30">
                <h3 className="text-lg font-serif mb-4">Export Patient Health Record (EHR)</h3>
                <form onSubmit={handleExport} className="flex flex-col sm:flex-row items-end gap-4 max-w-xl">
                    <div className="flex-1 w-full">
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
                    <button 
                        type="submit" 
                        disabled={isLoading || !selectedPatientId}
                        className="px-6 py-2 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-sm font-medium hover:opacity-90 transition-opacity w-full sm:w-auto text-center disabled:opacity-50"
                    >
                        {isLoading ? "Exporting..." : "Generate Standard Exports"}
                    </button>
                </form>
            </div>

            {(hl7Data || fhirData) && (
                <div className="border border-[#e2e2df] dark:border-[#333330] overflow-hidden">
                    <div className="flex border-b border-[#e2e2df] dark:border-[#333330] bg-[#f5f5f0] dark:bg-[#252523]">
                        <button 
                            onClick={() => setActiveExportTab('fhir')}
                            className={`px-6 py-3 text-xs font-semibold uppercase tracking-wider border-r border-[#e2e2df] dark:border-[#333330] transition-colors ${
                                activeExportTab === 'fhir' 
                                    ? 'bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6]' 
                                    : 'text-[#5a5a57] dark:text-[#a0a09e] hover:bg-[#fcf8f8]/50'
                            }`}
                        >
                            FHIR JSON Resource
                        </button>
                        <button 
                            onClick={() => setActiveExportTab('hl7')}
                            className={`px-6 py-3 text-xs font-semibold uppercase tracking-wider border-r border-[#e2e2df] dark:border-[#333330] transition-colors ${
                                activeExportTab === 'hl7' 
                                    ? 'bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6]' 
                                    : 'text-[#5a5a57] dark:text-[#a0a09e] hover:bg-[#fcf8f8]/50'
                            }`}
                        >
                            HL7 v2 Message (ADT^A08)
                        </button>
                    </div>

                    <div className="p-6 bg-[#FDFCF8] dark:bg-[#1a1a19]">
                        {activeExportTab === 'fhir' ? (
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-xs font-semibold text-[#a0a09e] uppercase tracking-wider">FHIR JSON Format (HL7 FHIR v4.0.1)</span>
                                    <button 
                                        onClick={() => handleCopy(JSON.stringify(fhirData, null, 4))}
                                        className="px-3 py-1 border border-[#e2e2df] dark:border-[#333330] text-xs hover:bg-[#f5f5f0] dark:hover:bg-[#252523]"
                                    >
                                        Copy JSON
                                    </button>
                                </div>
                                <pre className="p-4 bg-gray-50 dark:bg-black/35 text-xs font-mono overflow-auto max-h-96 border border-[#e2e2df] dark:border-[#333330] text-gray-800 dark:text-gray-300">
                                    {JSON.stringify(fhirData, null, 4)}
                                </pre>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-xs font-semibold text-[#a0a09e] uppercase tracking-wider">HL7 v2.3 Message ADT (Patient Demographics Update)</span>
                                    <button 
                                        onClick={() => handleCopy(hl7Data)}
                                        className="px-3 py-1 border border-[#e2e2df] dark:border-[#333330] text-xs hover:bg-[#f5f5f0] dark:hover:bg-[#252523]"
                                    >
                                        Copy HL7
                                    </button>
                                </div>
                                <pre className="p-4 bg-gray-50 dark:bg-black/35 text-xs font-mono overflow-auto max-h-96 border border-[#e2e2df] dark:border-[#333330] whitespace-pre-wrap text-gray-800 dark:text-gray-300">
                                    {hl7Data}
                                </pre>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default InteropPanel;
