import React from 'react';
import DataTable from '../../components/ui/DataTable';
import { Trash2, Edit } from 'lucide-react';

const PatientsDirectory = ({ patients = [], onViewProfile, onEditPatient, onDeletePatient, onAddPatient }) => {
    
    const columns = [
        {
            header: "Name",
            key: "pat_name",
            render: (pat) => (
                <button 
                    onClick={() => onViewProfile(pat.patient_id)} 
                    className="text-left font-medium text-[#2d2d2a] dark:text-[#e8e8e6] underline underline-offset-2 hover:opacity-70"
                >
                    {pat.pat_name}
                </button>
            )
        },
        {
            header: "Patient ID",
            key: "patient_id",
            render: (pat) => (
                <span className="text-sm text-[#5a5a57] dark:text-[#a0a09e]">
                    ID: {pat.patient_id}
                </span>
            )
        },
        {
            header: "Actions",
            key: "actions",
            render: (pat) => (
                <div className="flex gap-4">
                    <button 
                        onClick={() => onEditPatient(pat)} 
                        className="text-xs text-[#a0a09e] hover:text-[#2d2d2a] dark:hover:text-[#e8e8e6] transition-colors"
                    >
                        <Edit className="h-4 w-4" />
                    </button>
                    <button 
                        onClick={() => onDeletePatient(pat.patient_id)} 
                        className="text-xs text-[#c54b4b] hover:opacity-75 transition-opacity"
                    >
                        <Trash2 className="h-4 w-4" />
                    </button>
                </div>
            )
        }
    ];

    return (
        <div className="border border-[#e2e2df] dark:border-[#333330] bg-transparent">
            <div className="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-[#e2e2df] dark:border-[#333330]">
                <h3 className="text-lg leading-6 font-medium text-[#2d2d2a] dark:text-[#e8e8e6]">Registered Patients</h3>
                <button 
                    onClick={onAddPatient} 
                    className="text-sm border border-[#2d2d2a] dark:border-[#e8e8e6] text-[#2d2d2a] dark:text-[#e8e8e6] hover:bg-[#2d2d2a] dark:hover:bg-[#e8e8e6] hover:text-[#FDFCF8] dark:hover:text-[#1a1a19] py-1 px-3 rounded-full transition"
                >
                    + Add Patient
                </button>
            </div>
            <div className="p-4">
                <DataTable 
                    columns={columns} 
                    data={patients} 
                    pageSize={5} 
                    searchPlaceholder="Search patients by name or ID..."
                    searchKeys={["pat_name", "patient_id"]}
                />
            </div>
        </div>
    );
};

export default PatientsDirectory;
