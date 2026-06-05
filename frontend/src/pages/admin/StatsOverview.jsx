import React from 'react';
import { Users, UserPlus, Calendar } from 'lucide-react';

const StatsOverview = ({ doctorsCount = 0, patientsCount = 0, appointmentsCount = 0 }) => {
    const stats = [
        {
            label: "Total Doctors",
            value: doctorsCount,
            icon: Users,
        },
        {
            label: "Total Patients",
            value: patientsCount,
            icon: UserPlus,
        },
        {
            label: "Total Appointments",
            value: appointmentsCount,
            icon: Calendar,
        }
    ];

    return (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mb-8">
            {stats.map((stat, idx) => {
                const Icon = stat.icon;
                return (
                    <div key={idx} className="border border-[#e2e2df] dark:border-[#333330] p-6 bg-transparent transition-colors">
                        <div className="flex items-center">
                            <div className="flex-shrink-0 bg-[#2d2d2a] dark:bg-[#e8e8e6] rounded-md p-3">
                                <Icon className="h-6 w-6 text-[#FDFCF8] dark:text-[#1a1a19]" />
                            </div>
                            <div className="ml-5 w-0 flex-1">
                                <dl>
                                    <dt className="text-sm font-medium text-[#a0a09e] dark:text-[#8a8a88] truncate">{stat.label}</dt>
                                    <dd className="text-lg font-medium text-[#2d2d2a] dark:text-[#e8e8e6]">{stat.value}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export default StatsOverview;
