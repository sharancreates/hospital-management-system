import React from 'react';
import DataTable from '../../components/ui/DataTable';
import { Trash2, Edit } from 'lucide-react';

const DoctorsDirectory = ({ doctors = [], onViewProfile, onEditDoctor, onDeleteDoctor, onAddDoctor }) => {
    
    const columns = [
        {
            header: "Name",
            key: "doc_name",
            render: (doc) => (
                <button 
                    onClick={() => onViewProfile(doc.doctor_id)} 
                    className="text-left font-medium text-[#2d2d2a] dark:text-[#e8e8e6] underline underline-offset-2 hover:opacity-70"
                >
                    {doc.doc_name}
                </button>
            )
        },
        {
            header: "Department",
            key: "department",
            render: (doc) => (
                <span className="text-sm text-[#5a5a57] dark:text-[#a0a09e]">
                    {doc.department}
                </span>
            )
        },
        {
            header: "Actions",
            key: "actions",
            render: (doc) => (
                <div className="flex gap-4">
                    <button 
                        onClick={() => onEditDoctor(doc)} 
                        className="text-xs text-[#a0a09e] hover:text-[#2d2d2a] dark:hover:text-[#e8e8e6] transition-colors"
                    >
                        <Edit className="h-4 w-4" />
                    </button>
                    <button 
                        onClick={() => onDeleteDoctor(doc.doctor_id)} 
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
                <h3 className="text-lg leading-6 font-medium text-[#2d2d2a] dark:text-[#e8e8e6]">Doctors Directory</h3>
                <button 
                    onClick={onAddDoctor} 
                    className="text-sm border border-[#2d2d2a] dark:border-[#e8e8e6] text-[#2d2d2a] dark:text-[#e8e8e6] hover:bg-[#2d2d2a] dark:hover:bg-[#e8e8e6] hover:text-[#FDFCF8] dark:hover:text-[#1a1a19] py-1 px-3 rounded-full transition"
                >
                    + Add Doctor
                </button>
            </div>
            <div className="p-4">
                <DataTable 
                    columns={columns} 
                    data={doctors} 
                    pageSize={5} 
                    searchPlaceholder="Search doctors by name or department..."
                    searchKeys={["doc_name", "department"]}
                />
            </div>
        </div>
    );
};

export default DoctorsDirectory;
