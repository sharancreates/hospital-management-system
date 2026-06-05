import React, { useState } from 'react';
import api from '../../api';

const BillingPanel = ({ bills, patients, onRefresh }) => {
    // Generate Bill State
    const [isGenerating, setIsGenerating] = useState(false);
    const [genPatientId, setGenPatientId] = useState('');
    const [genAmount, setGenAmount] = useState('');
    const [genIsSubmitting, setGenIsSubmitting] = useState(false);

    // Insurance Policy State
    const [isRegisteringInsurance, setIsRegisteringInsurance] = useState(false);
    const [insPatientId, setInsPatientId] = useState('');
    const [insProvider, setInsProvider] = useState('');
    const [insPolicyNum, setInsPolicyNum] = useState('');
    const [insLimit, setInsLimit] = useState('');
    const [insIsSubmitting, setInsIsSubmitting] = useState(false);

    // Payment States
    const [payingBillId, setPayingBillId] = useState(null);
    const [paymentAmount, setPaymentAmount] = useState('');
    const [paymentIsSubmitting, setPaymentIsSubmitting] = useState(false);

    const handleGenerateBill = async (e) => {
        e.preventDefault();
        if (!genPatientId || !genAmount) {
            alert("Patient ID and Amount are required.");
            return;
        }
        setGenIsSubmitting(true);
        try {
            await api.post('/enterprise/bill/generate', {
                patient_id: parseInt(genPatientId),
                total_amount: parseFloat(genAmount)
            });
            alert("Invoice generated successfully!");
            setIsGenerating(false);
            setGenPatientId('');
            setGenAmount('');
            onRefresh();
        } catch (err) {
            alert(err.response?.data?.message || "Failed to generate bill.");
        } finally {
            setGenIsSubmitting(false);
        }
    };

    const handleRegisterInsurance = async (e) => {
        e.preventDefault();
        if (!insPatientId || !insProvider || !insPolicyNum || !insLimit) {
            alert("All fields are required.");
            return;
        }
        setInsIsSubmitting(true);
        try {
            await api.post('/enterprise/insurance/add', {
                patient_id: parseInt(insPatientId),
                provider_name: insProvider,
                policy_number: insPolicyNum,
                coverage_limit: parseFloat(insLimit)
            });
            alert("Insurance policy registered successfully!");
            setIsRegisteringInsurance(false);
            setInsPatientId('');
            setInsProvider('');
            setInsPolicyNum('');
            setInsLimit('');
            onRefresh();
        } catch (err) {
            alert(err.response?.data?.message || "Failed to register insurance policy.");
        } finally {
            setInsIsSubmitting(false);
        }
    };

    const handleRecordPayment = async (e) => {
        e.preventDefault();
        if (!paymentAmount) return;
        setPaymentIsSubmitting(true);
        try {
            await api.post('/enterprise/bill/pay', {
                bill_id: payingBillId,
                amount: parseFloat(paymentAmount)
            });
            alert("Payment recorded successfully!");
            setPayingBillId(null);
            setPaymentAmount('');
            onRefresh();
        } catch (err) {
            alert(err.response?.data?.message || "Failed to record payment.");
        } finally {
            setPaymentIsSubmitting(false);
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <h2 className="text-2xl font-serif font-medium">Billing & Insurance Management</h2>
                <div className="flex gap-4">
                    <button 
                        onClick={() => { setIsGenerating(true); setIsRegisteringInsurance(false); }}
                        className="px-4 py-2 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-sm font-medium hover:opacity-90 transition-opacity"
                    >
                        Generate Invoice
                    </button>
                    <button 
                        onClick={() => { setIsRegisteringInsurance(true); setIsGenerating(false); }}
                        className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] hover:bg-[#f5f5f0] dark:hover:bg-[#252523] text-sm font-medium transition-colors"
                    >
                        Register Insurance Policy
                    </button>
                    <button 
                        onClick={onRefresh}
                        className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] hover:bg-[#f5f5f0] dark:hover:bg-[#252523] text-sm transition-colors"
                    >
                        Refresh List
                    </button>
                </div>
            </div>

            {/* Generate Invoice Form */}
            {isGenerating && (
                <div className="border border-[#e2e2df] dark:border-[#333330] p-6 bg-[#fcf8f8]/30 dark:bg-[#252523]/30">
                    <h3 className="text-lg font-serif mb-4">Generate Patient Invoice</h3>
                    <form onSubmit={handleGenerateBill} className="space-y-4 max-w-lg">
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-[#a0a09e] mb-1">Patient</label>
                            <select 
                                value={genPatientId} 
                                onChange={(e) => setGenPatientId(e.target.value)}
                                className="w-full px-3 py-2 border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-sm focus:outline-none"
                            >
                                <option value="">-- Select Patient --</option>
                                {patients.map(p => (
                                    <option key={p.patient_id} value={p.patient_id}>{p.pat_name} (ID: {p.patient_id})</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-[#a0a09e] mb-1">Total Amount ($)</label>
                            <input 
                                type="number" 
                                step="0.01"
                                value={genAmount} 
                                onChange={(e) => setGenAmount(e.target.value)}
                                className="w-full px-3 py-2 border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-sm focus:outline-none"
                                placeholder="e.g. 250.00"
                            />
                        </div>
                        <div className="flex gap-4">
                            <button 
                                type="submit" 
                                disabled={genIsSubmitting}
                                className="px-4 py-2 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-sm font-medium hover:opacity-90"
                            >
                                {genIsSubmitting ? "Generating..." : "Generate Bill"}
                            </button>
                            <button 
                                type="button" 
                                onClick={() => setIsGenerating(false)}
                                className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] text-sm hover:bg-[#f5f5f0] dark:hover:bg-[#252523] transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Register Insurance Form */}
            {isRegisteringInsurance && (
                <div className="border border-[#e2e2df] dark:border-[#333330] p-6 bg-[#fcf8f8]/30 dark:bg-[#252523]/30">
                    <h3 className="text-lg font-serif mb-4">Register Insurance Policy</h3>
                    <form onSubmit={handleRegisterInsurance} className="space-y-4 max-w-lg">
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-[#a0a09e] mb-1">Patient</label>
                            <select 
                                value={insPatientId} 
                                onChange={(e) => setInsPatientId(e.target.value)}
                                className="w-full px-3 py-2 border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-sm focus:outline-none"
                            >
                                <option value="">-- Select Patient --</option>
                                {patients.map(p => (
                                    <option key={p.patient_id} value={p.patient_id}>{p.pat_name} (ID: {p.patient_id})</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-[#a0a09e] mb-1">Provider Name</label>
                            <input 
                                type="text" 
                                value={insProvider} 
                                onChange={(e) => setInsProvider(e.target.value)}
                                className="w-full px-3 py-2 border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-sm focus:outline-none"
                                placeholder="e.g. Blue Cross, Aetna, Cigna"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-[#a0a09e] mb-1">Policy Number</label>
                            <input 
                                type="text" 
                                value={insPolicyNum} 
                                onChange={(e) => setInsPolicyNum(e.target.value)}
                                className="w-full px-3 py-2 border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-sm focus:outline-none"
                                placeholder="e.g. POL-99201"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-[#a0a09e] mb-1">Coverage Limit ($)</label>
                            <input 
                                type="number" 
                                step="1"
                                value={insLimit} 
                                onChange={(e) => setInsLimit(e.target.value)}
                                className="w-full px-3 py-2 border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-sm focus:outline-none"
                                placeholder="e.g. 5000"
                            />
                        </div>
                        <div className="flex gap-4">
                            <button 
                                type="submit" 
                                disabled={insIsSubmitting}
                                className="px-4 py-2 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-sm font-medium hover:opacity-90"
                            >
                                {insIsSubmitting ? "Registering..." : "Save Policy"}
                            </button>
                            <button 
                                type="button" 
                                onClick={() => setIsRegisteringInsurance(false)}
                                className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] text-sm hover:bg-[#f5f5f0] dark:hover:bg-[#252523] transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Record Payment Inline Form */}
            {payingBillId && (
                <div className="border border-amber-600/30 p-6 bg-amber-500/5">
                    <h3 className="text-lg font-serif mb-4">Record Payment on Bill #{payingBillId}</h3>
                    <form onSubmit={handleRecordPayment} className="flex items-end gap-4 max-w-md">
                        <div className="flex-1">
                            <label className="block text-xs font-semibold uppercase tracking-wider text-[#a0a09e] mb-1">Payment Amount ($)</label>
                            <input 
                                type="number" 
                                step="0.01"
                                value={paymentAmount} 
                                onChange={(e) => setPaymentAmount(e.target.value)}
                                className="w-full px-3 py-2 border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-sm focus:outline-none"
                                placeholder="0.00"
                            />
                        </div>
                        <button 
                            type="submit" 
                            disabled={paymentIsSubmitting}
                            className="px-4 py-2 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-sm font-medium hover:opacity-90"
                        >
                            {paymentIsSubmitting ? "Processing..." : "Record"}
                        </button>
                        <button 
                            type="button" 
                            onClick={() => setPayingBillId(null)}
                            className="px-4 py-2 border border-[#e2e2df] dark:border-[#333330] text-sm hover:bg-[#f5f5f0] dark:hover:bg-[#252523]"
                        >
                            Cancel
                        </button>
                    </form>
                </div>
            )}

            {/* Bills list */}
            <div className="border border-[#e2e2df] dark:border-[#333330] overflow-hidden">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-[#f5f5f0] dark:bg-[#252523] border-b border-[#e2e2df] dark:border-[#333330] text-xs font-semibold uppercase tracking-wider text-[#5a5a57] dark:text-[#a0a09e]">
                            <th className="px-6 py-3">Bill ID</th>
                            <th className="px-6 py-3">Patient</th>
                            <th className="px-6 py-3">Total Amount</th>
                            <th className="px-6 py-3">Ins. Covered</th>
                            <th className="px-6 py-3">Paid Amount</th>
                            <th className="px-6 py-3">Balance Due</th>
                            <th className="px-6 py-3">Status</th>
                            <th className="px-6 py-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-[#e2e2df] dark:divide-[#333330] text-sm">
                        {bills.length === 0 ? (
                            <tr>
                                <td colSpan="8" className="px-6 py-8 text-center text-gray-500 italic">No bills or invoices generated yet.</td>
                            </tr>
                        ) : (
                            bills.map(bill => {
                                const balance = bill.total_amount - bill.insurance_covered - bill.paid_amount;
                                return (
                                    <tr key={bill.bill_id} className="hover:bg-[#fcf8f8]/20 dark:hover:bg-[#252523]/10">
                                        <td className="px-6 py-4 font-mono">#{bill.bill_id}</td>
                                        <td className="px-6 py-4 font-medium">{bill.patient_name}</td>
                                        <td className="px-6 py-4">${bill.total_amount.toFixed(2)}</td>
                                        <td className="px-6 py-4 text-green-600 dark:text-green-400">${bill.insurance_covered.toFixed(2)}</td>
                                        <td className="px-6 py-4">${bill.paid_amount.toFixed(2)}</td>
                                        <td className="px-6 py-4 font-semibold">${balance > 0 ? balance.toFixed(2) : '0.00'}</td>
                                        <td className="px-6 py-4">
                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                                                bill.status === 'Paid'
                                                    ? 'bg-green-100 dark:bg-green-950 text-green-800 dark:text-green-300'
                                                    : bill.status === 'Partial'
                                                    ? 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300'
                                                    : 'bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-300'
                                            }`}>
                                                {bill.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            {bill.status !== 'Paid' && (
                                                <button 
                                                    onClick={() => setPayingBillId(bill.bill_id)}
                                                    className="px-3 py-1 bg-[#2d2d2a] dark:bg-[#e8e8e6] text-[#FDFCF8] dark:text-[#1a1a19] text-xs font-semibold hover:opacity-90"
                                                >
                                                    Record Payment
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default BillingPanel;
