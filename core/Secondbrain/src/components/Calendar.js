import React, { useState, useEffect } from 'react';
import {
    ChevronLeft, ChevronRight, Folder, AlertTriangle, CheckSquare, Users, Circle, Plus, Edit, Trash2, Clock
} from 'react-feather';
import {
    getDaysInMonth, getFirstDayOfMonth, formatCalendarDate, formatMonthYearHeader,
    getEventColor, getEventIcon, getEventsForDay, loadCalendarDataFromSharePoint
} from '../utils/calendarUtils';
import { getAccessToken, msalInstance } from '../auth'; // Assuming getAccessToken is needed
import { CONFIG as APP_CONFIG } from '../config';
import { useNotification } from '../contexts/NotificationContext'; // Import useNotification hook

function Calendar() {
    const { showNotification } = useNotification(); // Get showNotification from context

    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [allProjects, setAllProjects] = useState([]);
    const [allTickets, setAllTickets] = useState([]);
    const [allTasks, setAllTasks] = useState([]);
    const [showProjects, setShowProjects] = useState(true);
    const [showTickets, setShowTickets] = useState(true);


    // Effect for initial data loading
    useEffect(() => {
        const initCalendarData = async () => {
            const accounts = msalInstance.getAllAccounts();
            if (accounts.length === 0) {
                return;
            }
            const accessToken = await getAccessToken();

            const data = await loadCalendarDataFromSharePoint(accessToken, APP_CONFIG.siteId, showNotification);
            setAllProjects(data.projects);
            setAllTickets(data.tickets);
            setAllTasks(data.tasks);
        };
        initCalendarData();
    }, []);

    const prevMonth = () => {
        setCurrentMonth(prev => {
            const newDate = new Date(prev);
            newDate.setMonth(newDate.getMonth() - 1);
            return newDate;
        });
    };

    const nextMonth = () => {
        setCurrentMonth(prev => {
            const newDate = new Date(prev);
            newDate.setMonth(newDate.getMonth() + 1);
            return newDate;
        });
    };

    const goToToday = () => {
        setCurrentMonth(new Date());
    };

    const renderCalendarDays = () => {
        const year = currentMonth.getFullYear();
        const month = currentMonth.getMonth();
        const numDays = getDaysInMonth(year, month);
        const firstDay = getFirstDayOfMonth(year, month); // 0 = Sunday, 1 = Monday

        const days = [];
        // Fill leading empty days
        for (let i = 0; i < firstDay; i++) {
            days.push(<div key={`empty-prev-${i}`} className="calendar-day empty"></div>);
        }

        // Fill days of the month
        for (let i = 1; i <= numDays; i++) {
            const date = new Date(year, month, i);
            const isToday = date.toDateString() === new Date().toDateString();
            const dayEvents = getEventsForDay(
                date,
                showProjects ? allProjects : [],
                showTickets ? allTickets : [],
                showTasks ? allTasks : []
            );

            days.push(
                <div key={date.toDateString()} className={`calendar-day ${isToday ? 'today' : ''}`}>
                    <div className="day-number">{i}</div>
                    <div className="day-events">
                        {dayEvents.map(event => (
                            <div
                                key={event.id}
                                className={`event-badge ${getEventColor(event.type)}`}
                                onClick={() => showNotification(`Event: ${event.title}`, 'info')}
                                title={event.title}
                            >
                                {event.title}
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        return days;
    };

    return (
        <div className="tab-pane fade show active" id="calendar-panel" role="tabpanel" aria-labelledby="tab-calendar">
            <div className="calendar-header d-flex flex-column flex-md-row justify-content-between align-items-center mb-3">
                <div className="calendar-nav d-flex align-items-center mb-2 mb-md-0">
                    <button className="btn btn-outline-secondary btn-sm me-2" onClick={prevMonth}>
                        <ChevronLeft size={20} />
                    </button>
                    <h2 className="calendar-title h4 mb-0 me-2">{formatMonthYearHeader(currentMonth)}</h2>
                    <button className="btn btn-outline-secondary btn-sm" onClick={nextMonth}>
                        <ChevronRight size={20} />
                    </button>
                </div>

                <div className="calendar-actions d-flex flex-wrap align-items-center gap-2">
                    <button className="btn btn-secondary btn-sm" onClick={goToToday}>Today</button>
                    <div className="form-check">
                        <input
                            className="form-check-input"
                            type="checkbox"
                            id="calShowProjects"
                            checked={showProjects}
                            onChange={(e) => setShowProjects(e.target.checked)}
                        />
                        <label className="form-check-label" htmlFor="calShowProjects">
                            <Folder size={14} className="text-primary me-1" /> Projects
                        </label>
                    </div>
                    <div className="form-check">
                        <input
                            className="form-check-input"
                            type="checkbox"
                            id="calShowTickets"
                            checked={showTickets}
                            onChange={(e) => setShowTickets(e.target.checked)}
                        />
                        <label className="form-check-label" htmlFor="calShowTickets">
                            <AlertTriangle size={14} className="text-warning me-1" /> Tickets
                        </label>
                    </div>
                    <div className="form-check">
                        <input
                            className="form-check-input"
                            type="checkbox"
                            id="calShowTasks"
                            checked={showTasks}
                            onChange={(e) => setShowTasks(e.target.checked)}
                        />
                        <label className="form-check-label" htmlFor="calShowTasks">
                            <CheckSquare size={14} className="text-success me-1" /> Tasks
                        </label>
                    </div>
                </div>
            </div>

            <div className="calendar-grid card card-body">
                <div className="calendar-weekdays row g-0 text-center fw-bold mb-2">
                    <div className="col">Sun</div>
                    <div className="col">Mon</div>
                    <div className="col">Tue</div>
                    <div className="col">Wed</div>
                    <div className="col">Thu</div>
                    <div className="col">Fri</div>
                    <div className="col">Sat</div>
                </div>
                <div className="calendar-days row g-0">
                    {renderCalendarDays()}
                </div>
            </div>
        </div>
    );
}

export default Calendar;