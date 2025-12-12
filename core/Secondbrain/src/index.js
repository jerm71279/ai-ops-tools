import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { NotificationProvider } from './contexts/NotificationContext';
import Notification from './components/Notification';

ReactDOM.render(
    <NotificationProvider>
        <App />
        <Notification />
    </NotificationProvider>,
    document.getElementById('root')
);