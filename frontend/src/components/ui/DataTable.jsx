import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Search } from 'lucide-react';

const DataTable = ({ 
    columns, 
    data = [], 
    pageSize = 5, 
    searchPlaceholder = "Search...", 
    searchKey = "", // Key in the data objects to search by
    searchKeys = [] // Or multiple keys
}) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);

    // Search filter
    const filteredData = data.filter(item => {
        if (!searchTerm) return true;
        
        const term = searchTerm.toLowerCase();
        
        if (searchKeys && searchKeys.length > 0) {
            return searchKeys.some(key => {
                const val = item[key];
                return val ? String(val).toLowerCase().includes(term) : false;
            });
        }
        
        if (searchKey) {
            const val = item[searchKey];
            return val ? String(val).toLowerCase().includes(term) : false;
        }

        // Default: search all values
        return Object.values(item).some(val => 
            val ? String(val).toLowerCase().includes(term) : false
        );
    });

    // Pagination calculations
    const totalItems = filteredData.length;
    const totalPages = Math.ceil(totalItems / pageSize) || 1;
    const startIndex = (currentPage - 1) * pageSize;
    const paginatedData = filteredData.slice(startIndex, startIndex + pageSize);

    // Adjust page if search changes the size
    React.useEffect(() => {
        setCurrentPage(1);
    }, [searchTerm]);

    return (
        <div className="w-full">
            {/* Search Input */}
            {(searchKey || searchKeys.length > 0) && (
                <div className="mb-4 relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Search className="h-4 w-4 text-[#a0a09e]" />
                    </div>
                    <input
                        type="text"
                        placeholder={searchPlaceholder}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-9 pr-4 py-2 w-full text-sm border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6] focus:outline-none focus:ring-1 focus:ring-[#2d2d2a] dark:focus:ring-[#e8e8e6] focus:border-[#2d2d2a] dark:focus:border-[#e8e8e6]"
                    />
                </div>
            )}

            {/* Table */}
            <div className="overflow-x-auto border border-[#e2e2df] dark:border-[#333330]">
                <table className="min-w-full divide-y divide-[#e2e2df] dark:divide-[#333330]">
                    <thead className="bg-[#fcf8f8] dark:bg-[#252523]">
                        <tr>
                            {columns.map((col, idx) => (
                                <th 
                                    key={idx}
                                    scope="col" 
                                    className="px-6 py-3 text-left text-xs font-semibold text-[#a0a09e] dark:text-[#8a8a88] uppercase tracking-wider"
                                >
                                    {col.header}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-transparent divide-y divide-[#e2e2df] dark:divide-[#333330]">
                        {paginatedData.map((row, rowIdx) => (
                            <tr key={rowIdx} className="hover:bg-[#fcf8f8] dark:hover:bg-[#252523]/50 transition-colors">
                                {columns.map((col, colIdx) => (
                                    <td 
                                        key={colIdx} 
                                        className="px-6 py-4 whitespace-nowrap text-sm text-[#2d2d2a] dark:text-[#e8e8e6]"
                                    >
                                        {col.render ? col.render(row) : row[col.key]}
                                    </td>
                                ))}
                            </tr>
                        ))}
                        {paginatedData.length === 0 && (
                            <tr>
                                <td colSpan={columns.length} className="px-6 py-8 text-center text-sm text-[#a0a09e]">
                                    No data found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
                <div className="mt-4 flex items-center justify-between px-2">
                    <span className="text-xs text-[#a0a09e]">
                        Showing {startIndex + 1} to {Math.min(startIndex + pageSize, totalItems)} of {totalItems} items
                    </span>
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                            disabled={currentPage === 1}
                            className="p-1 border border-[#e2e2df] dark:border-[#333330] hover:bg-[#fcf8f8] dark:hover:bg-[#252523] disabled:opacity-40 disabled:hover:bg-transparent text-[#2d2d2a] dark:text-[#e8e8e6] transition-colors"
                            aria-label="Previous page"
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </button>
                        <span className="text-xs font-medium text-[#2d2d2a] dark:text-[#e8e8e6]">
                            Page {currentPage} of {totalPages}
                        </span>
                        <button
                            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                            disabled={currentPage === totalPages}
                            className="p-1 border border-[#e2e2df] dark:border-[#333330] hover:bg-[#fcf8f8] dark:hover:bg-[#252523] disabled:opacity-40 disabled:hover:bg-transparent text-[#2d2d2a] dark:text-[#e8e8e6] transition-colors"
                            aria-label="Next page"
                        >
                            <ChevronRight className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DataTable;
