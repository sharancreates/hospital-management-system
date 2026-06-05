import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

const Modal = ({ isOpen, onClose, title, children, maxWidth = 'max-w-md' }) => {
    const modalRef = useRef(null);

    // Escape key handling
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    const previousFocusRef = useRef(null);

    // Focus management (trapping & restoration)
    useEffect(() => {
        if (isOpen) {
            previousFocusRef.current = document.activeElement;
            // Delay slightly to allow rendering
            setTimeout(() => {
                if (modalRef.current) {
                    const focusableElements = modalRef.current.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex="0"]'
                    );
                    if (focusableElements.length > 0) {
                        focusableElements[0].focus();
                    }
                }
            }, 50);
        } else {
            if (previousFocusRef.current) {
                previousFocusRef.current.focus();
            }
        }
    }, [isOpen]);

    // Handle Tab key focus trapping
    useEffect(() => {
        if (!isOpen) return;

        const handleTabKey = (e) => {
            if (e.key !== 'Tab') return;

            if (modalRef.current) {
                const focusableElements = Array.from(modalRef.current.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex="0"]'
                ));
                if (focusableElements.length === 0) return;

                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];

                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        };

        window.addEventListener('keydown', handleTabKey);
        return () => window.removeEventListener('keydown', handleTabKey);
    }, [isOpen]);

    // Prevent body scroll when modal is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isOpen]);

    if (!isOpen) return null;

    const handleBackdropClick = (e) => {
        if (modalRef.current && !modalRef.current.contains(e.target)) {
            onClose();
        }
    };

    return (
        <div 
            className="fixed inset-0 bg-[#1a1a19]/70 dark:bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 transition-opacity duration-300"
            onClick={handleBackdropClick}
            aria-modal="true"
            role="dialog"
            aria-labelledby="modal-title"
        >
            <div 
                ref={modalRef}
                className={`bg-[#FDFCF8] dark:bg-[#1a1a19] border border-[#e2e2df] dark:border-[#333330] w-full ${maxWidth} p-6 shadow-xl relative animate-in fade-in zoom-in-95 duration-200`}
            >
                <div className="flex justify-between items-center mb-6 border-b border-[#e2e2df] dark:border-[#333330] pb-3">
                    <h2 id="modal-title" className="text-xl font-serif font-medium text-[#2d2d2a] dark:text-[#e8e8e6]">
                        {title}
                    </h2>
                    <button 
                        onClick={onClose} 
                        className="text-[#a0a09e] hover:text-[#2d2d2a] dark:hover:text-[#e8e8e6] transition-colors p-1"
                        aria-label="Close modal"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>
                <div className="text-sm text-[#5a5a57] dark:text-[#a0a09e]">
                    {children}
                </div>
            </div>
        </div>
    );
};

export default Modal;
