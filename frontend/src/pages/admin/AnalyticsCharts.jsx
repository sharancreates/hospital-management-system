import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useTheme } from '../../context/ThemeContext';

const AnalyticsCharts = ({ analytics }) => {
    const { darkMode } = useTheme();
    
    if (!analytics) return null;

    const gridColor = darkMode ? '#333330' : '#e2e2df';
    const textColor = darkMode ? '#a0a09e' : '#2d2d2a';
    const tooltipBg = darkMode ? '#1a1a19' : '#FDFCF8';
    const tooltipBorder = darkMode ? '#333330' : '#e2e2df';

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Appointments Trend Chart */}
            <div className="border border-[#e2e2df] dark:border-[#333330] p-6 bg-transparent transition-colors">
                <h3 className="text-lg font-medium text-[#2d2d2a] dark:text-[#e8e8e6] mb-4">Appointments (Last 7 Days)</h3>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={analytics.trend}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
                            <XAxis dataKey="date" tick={{ fontSize: 12, fill: textColor }} />
                            <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: textColor }} />
                            <Tooltip contentStyle={{ backgroundColor: tooltipBg, borderColor: tooltipBorder, color: textColor }} />
                            <Line 
                                type="monotone" 
                                dataKey="appointments" 
                                stroke="#3b82f6" 
                                strokeWidth={3} 
                                dot={{ r: 4, fill: '#3b82f6' }} 
                                activeDot={{ r: 6 }} 
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Doctors by Department Chart */}
            <div className="border border-[#e2e2df] dark:border-[#333330] p-6 bg-transparent transition-colors">
                <h3 className="text-lg font-medium text-[#2d2d2a] dark:text-[#e8e8e6] mb-4">Doctors by Department</h3>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={analytics.departments} layout="vertical" margin={{ left: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={gridColor} />
                            <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12, fill: textColor }} />
                            <YAxis dataKey="name" type="category" tick={{ fontSize: 12, fill: textColor }} width={100} />
                            <Tooltip contentStyle={{ backgroundColor: tooltipBg, borderColor: tooltipBorder, color: textColor }} />
                            <Bar dataKey="value" fill="#10b981" radius={[0, 4, 4, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsCharts;
