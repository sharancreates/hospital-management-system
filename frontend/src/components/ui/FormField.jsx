import React from 'react';

const FormField = React.forwardRef(({ 
    label, 
    name, 
    type = 'text', 
    error, 
    options = [], // for 'select' type
    className = '',
    placeholder = '',
    disabled = false,
    ...rest 
}, ref) => {
    const inputId = `field-${name}`;
    const baseInputClass = `mt-1 block w-full border border-[#e2e2df] dark:border-[#333330] bg-[#FDFCF8] dark:bg-[#1a1a19] text-[#2d2d2a] dark:text-[#e8e8e6] focus:outline-none focus:ring-1 focus:ring-[#2d2d2a] dark:focus:ring-[#e8e8e6] focus:border-[#2d2d2a] dark:focus:border-[#e8e8e6] p-2 text-sm disabled:opacity-50 transition-colors ${
        error ? 'border-[#c54b4b] focus:ring-[#c54b4b] focus:border-[#c54b4b]' : ''
    }`;

    return (
        <div className={`w-full ${className}`}>
            {label && (
                <label 
                    htmlFor={inputId} 
                    className="block text-xs font-semibold text-[#5a5a57] dark:text-[#a0a09e] uppercase tracking-wider"
                >
                    {label}
                </label>
            )}
            
            {type === 'select' ? (
                <select
                    id={inputId}
                    name={name}
                    ref={ref}
                    disabled={disabled}
                    className={baseInputClass}
                    {...rest}
                >
                    {options.map((opt, idx) => (
                        <option key={idx} value={opt.value}>
                            {opt.label}
                        </option>
                    ))}
                </select>
            ) : type === 'textarea' ? (
                <textarea
                    id={inputId}
                    name={name}
                    ref={ref}
                    disabled={disabled}
                    placeholder={placeholder}
                    className={baseInputClass}
                    {...rest}
                />
            ) : (
                <input
                    id={inputId}
                    name={name}
                    type={type}
                    ref={ref}
                    disabled={disabled}
                    placeholder={placeholder}
                    className={baseInputClass}
                    {...rest}
                />
            )}

            {/* Accessible Validation Error Announcement */}
            {error && (
                <span 
                    role="alert" 
                    className="mt-1 block text-xs text-[#c54b4b] animate-in fade-in slide-in-from-top-1 duration-150"
                >
                    {error.message || error}
                </span>
            )}
        </div>
    );
});

FormField.displayName = 'FormField';

export default FormField;
