import React from 'react';
import DataTable from '../../components/ui/DataTable';
import { Trash2, Edit } from 'lucide-react';

const AppointmentsTable = ({ 
    appointments = [], 
    onViewDoctorProfile, 
    onViewPatientProfile, 
    onEditAppt, 
    onCancelAppt, 
    onAddAppt,
    doctorsList = [],
    patientsList = []
}) => {

    const getDoctorIdByName = (name) => {
        return doctorsList.find(d => d.doc_name === name)?.doctor_id;
    };

    const getPatientIdByName = (name) => {
        return patientsList.find(p => p.pat_name === name)?.patient_id;
    };

    const columns = [
        {
            header: "Date/Time",
            key: "date",
            render: (appt) => (
                <span className="text-sm text-[#2d2d2a] dark:text-[#e8e8e6]">
                    {appt.date} <span className="text-[#a0a09e] dark:text-[#8a8a88]">at {appt.time}</span>
                </span>
            )
        },
        {
            header: "Doctor",
            key: "doctor_name",
            render: (appt) => {
                const docId = getDoctorIdByName(appt.doctor_name);
                return docId ? (
                    <button 
                        onClick={() => onViewDoctorProfile(docId)}
                        className="text-left font-medium text-[#2d2d2a] dark:text-[#e8e8e6] underline underline-offset-2 hover:opacity-70"
                    >
                        {appt.doctor_name}
                    </button>
                ) : (
                    <span>{appt.doctor_name}</span>
                );
            }
        },
        {
            header: "Patient",
            key: "patient_name",
            render: (appt) => {
                const patId = getPatientIdByName(appt.patient_name);
                return patId ? (
                    <button 
                        onClick={() => onViewPatientProfile(patId)}
                        className="text-left font-medium text-[#2d2d2a] dark:text-[#e8e8e6] underline underline-offset-2 hover:opacity-70"
                    >
                        {appt.patient_name}
                    </button>
                ) : (
                    <span>{appt.patient_name}</span>
                );
            }
        },
        {
            header: "Status",
            key: "status",
            render: (appt) => (
                <span className={`px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full 
                    ${appt.status === 'Booked' ? 'bg-[#f0f0eb] dark:bg-[#252523] text-[#5a5a57] dark:text-[#a0a09e]' :
                      appt.status === 'Completed' ? 'bg-[#f0f0eb] dark:bg-[#252523] text-[#2d2d2a] dark:text-[#e8e8e6]' :
                      'bg-[#fcf8f8] dark:bg-[#3d1a1a] text-[#c54b4b] dark:text-[#e07b7b]'}`}
                >
                    {appt.status}
                </span>
            )
        },
        {
            header: "Actions",
            key: "actions",
            render: (appt) => (
                <div className="flex gap-3 justify-end">
                    {appt.status !== 'Cancelled' && (
                        <>
                            <button 
                                onClick={() => onEditAppt(appt)} 
                                className="text-xs text-[#a0a09e] hover:text-[#2d2d2a] dark:hover:text-[#e8e8e6]"
                            >
                                <Edit className="h-4 w-4" />
                            </button>
                            <button 
                                onClick={() => onCancelAppt(appt.appointment_id)} 
                                className="text-xs text-[#c54b4b] hover:opacity-75 transition-opacity"
                            >
                                <Trash2 className="h-4 w-4" />
                            </button>
                        </>
                    )}
                </div>
            )
        }
    ];

    return (
        <div className="mt-8 border border-[#e2e2df] dark:border-[#333330] bg-transparent">
            <div className="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-[#e2e2df] dark:border-[#333330]">
                <h3 className="text-lg leading-6 font-medium text-[#2d2d2a] dark:text-[#e8e8e6]">Recent Appointments</h3>
                <button 
                    onClick={onAddAppt} 
                    className="text-sm border border-[#2d2d2a] dark:border-[#e8e8e6] text-[#2d2d2a] dark:text-[#e8e8e6] hover:bg-[#2d2d2a] dark:hover:bg-[#e8e8e6] hover:text-[#FDFCF8] dark:hover:text-[#1a1a19] py-1 px-3 rounded-full transition"
                >
                    + Add Appointment
                </button>
            </div>
            <div className="p-4">
                <DataTable 
                    columns={columns} 
                    data={appointments} 
                    pageSize={10} 
                    searchPlaceholder="Search appointments by doctor, patient or status..."
                    searchKeys={["doctor_name", "patient_name", "status"]}
                />
            </div>
        </div>
    );
};

export default AppointmentsTable;
