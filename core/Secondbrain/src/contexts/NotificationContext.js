import React, { createContext, useState, useContext, useCallback } from 'react';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
    const [notification, setNotification] = useState(null); // { message, type, duration }

    const showNotification = useCallback((message, type = 'info', duration = 5000) => {
        setNotification({ message, type, duration });
        if (duration) {
            setTimeout(() => setNotification(null), duration);
        }
    }, []);

    const value = { notification, showNotification };

    return (
        <NotificationContext.Provider value={value}>
            {children}
        </NotificationContext.Provider>
    );
};

export const useNotification = () => {
    return useContext(NotificationContext);
};
