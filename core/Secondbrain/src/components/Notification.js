import React, { useEffect } from 'react';
import { useNotification } from '../contexts/NotificationContext';
import { XCircle, CheckCircle, Info, AlertTriangle } from 'react-feather';

function Notification() {
    const { notification, showNotification } = useNotification();

    useEffect(() => {
        if (notification && notification.duration) {
            const timer = setTimeout(() => {
                showNotification(null); // Clear notification after duration
            }, notification.duration);
            return () => clearTimeout(timer);
        }
    }, [notification, showNotification]);

    if (!notification) return null;

    let IconComponent;
    let bgColorClass;
    let textColorClass = 'text-white'; // Default text color for dark backgrounds

    switch (notification.type) {
        case 'error':
            IconComponent = XCircle;
            bgColorClass = 'bg-danger';
            break;
        case 'success':
            IconComponent = CheckCircle;
            bgColorClass = 'bg-success';
            break;
        case 'warning':
            IconComponent = AlertTriangle;
            bgColorClass = 'bg-warning';
            textColorClass = 'text-dark'; // Dark text for light warning background
            break;
        case 'info':
        default:
            IconComponent = Info;
            bgColorClass = 'bg-info';
            break;
    }

    return (
        <div
            className={`position-fixed bottom-0 start-50 translate-middle-x p-3`}
            style={{ zIndex: 1050 }}
        >
            <div
                className={`toast show ${bgColorClass} ${textColorClass}`}
                role="alert"
                aria-live="assertive"
                aria-atomic="true"
            >
                <div className="d-flex">
                    <div className="toast-body d-flex align-items-center">
                        {IconComponent && <IconComponent size={20} className="me-2" />}
                        {notification.message}
                    </div>
                    <button
                        type="button"
                        className={`btn-close me-2 m-auto ${textColorClass === 'text-dark' ? 'btn-close-dark' : ''}`}
                        data-bs-dismiss="toast"
                        aria-label="Close"
                        onClick={() => showNotification(null)}
                    ></button>
                </div>
            </div>
        </div>
    );
}

export default Notification;