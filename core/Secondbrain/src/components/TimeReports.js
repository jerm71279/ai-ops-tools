import React, { useState, useEffect } from 'react';
import { Filter, Clock, Users, Folder, CheckSquare, List, DollarSign, Download, Plus, AlertTriangle, CloudOff } from 'react-feather'; // Import necessary icons
import {
    loadTimeEntriesFromSharePoint,
    getEmployeeBillableRate,
    formatDate,
    getInitials,
    discoverList, // Use generic discoverList
    createList, // Use generic createList
    TIME_ENTRIES_COLUMNS, // Import TIME_ENTRIES_COLUMNS
    saveTimeEntryToSharePoint,
    deleteTimeEntryFromSharePoint
} from '../utils/timeReportsUtils';
import TimeEntryModal from './modals/TimeEntryModal'; // Import TimeEntryModal
import { getAccessToken, msalInstance } from '../auth'; // Import getAccessToken and msalInstance
import { CONFIG as APP_CONFIG } from '../config'; // Import central config
import { useNotification } from '../contexts/NotificationContext'; // Import useNotification hook
import { loadProjectsFromSharePoint, loadTicketsFromSharePoint } from '../utils/projectsUtils';
import { loadTasksFromSharePoint } from '../utils/todoListUtils';



function TimeReports() {
    const { showNotification } = useNotification(); // Get showNotification from context

    const [timeEntriesData, setTimeEntriesData] = useState([]);
    const [timeReportStartDate, setTimeReportStartDate] = useState('');
    const [timeReportEndDate, setTimeReportEndDate] = useState('');
    const [timeReportEmployeeFilter, setTimeReportEmployeeFilter] = useState('');
    const [timeReportProjectFilter, setTimeReportProjectFilter] = useState('');
    const [currentTimeReportView, setCurrentTimeReportView] = useState('byEmployee');
    const [timeEntriesListId, setTimeEntriesListId] = useState(null);
    const [projectsListId, setProjectsListId] = useState(null);
    const [ticketsListId, setTicketsListId] = useState(null);
    const [tasksListId, setTasksListId] = useState(null);
    const [syncQueue, setSyncQueue] = useState([]);
    const [adUsers, setAdUsers] = useState([ // Mock adUsers for now
        { displayName: 'Mavrick Faison', mail: 'mavrick@example.com' },
        { displayName: 'Patrick McFarland', mail: 'patrick@example.com' },
        { displayName: 'Robbie McFarland', mail: 'robbie@example.com' }
    ]);
    const [projectsData, setProjectsData] = useState([]); // Assuming projects data is needed for dropdowns
    const [ticketsData, setTicketsData] = useState([]); // Assuming tickets data is needed for dropdowns
    const [tasksData, setTasksData] = useState([]); // Assuming tasks data is needed for dropdowns
    const [showModal, setShowModal] = useState(false); // State for modal visibility
    const [editingEntry, setEditingEntry] = useState(null); // State for entry being edited


    // Effect for initial data loading and MSAL integration
    useEffect(() => {
        const initTimeReportsData = async () => {
            const accounts = msalInstance.getAllAccounts();
            if (accounts.length === 0) {
                return;
            }

            const accessToken = await getAccessToken();

            // Discover list IDs
            const projListId = await discoverList(accessToken, APP_CONFIG.siteId, 'Projects', showNotification);
            const tixListId = await discoverList(accessToken, APP_CONFIG.siteId, 'Tickets', showNotification);
            const tskListId = await discoverList(accessToken, APP_CONFIG.siteId, 'Tasks', showNotification);

            setProjectsListId(projListId);
            setTicketsListId(tixListId);
            setTasksListId(tskListId);

            // Load Projects, Tickets, and Tasks data
            if (projListId) {
                const loadedProjects = await loadProjectsFromSharePoint(accessToken, APP_CONFIG.siteId, projListId, showNotification);
                setProjectsData(loadedProjects);
            }
            if (tixListId) {
                const loadedTickets = await loadTicketsFromSharePoint(accessToken, APP_CONFIG.siteId, tixListId, showNotification);
                setTicketsData(loadedTickets);
            }
            if (tskListId) {
                const loadedTasks = await loadTasksFromSharePoint(accessToken, tskListId, showNotification);
                setTasksData(loadedTasks);
            }

            // Discover or create TimeEntries list
            let listId = await discoverList(accessToken, APP_CONFIG.siteId, 'TimeEntries', showNotification);
            if (!listId) {
                listId = await createList(accessToken, APP_CONFIG.siteId, 'TimeEntries', 'Time tracking entries for employees', TIME_ENTRIES_COLUMNS, showNotification);
            }
            setTimeEntriesListId(listId);

            if (listId) {
                const entries = await loadTimeEntriesFromSharePoint(accessToken, listId, showNotification);
                setTimeEntriesData(entries);
            }

            // Set default date range (last 30 days)
            const today = new Date();
            const thirtyDaysAgo = new Date(today);
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            setTimeReportStartDate(thirtyDaysAgo.toISOString().split('T')[0]);
            setTimeReportEndDate(today.toISOString().split('T')[0]);

            // Load sync queue from localStorage
            const savedSyncQueue = JSON.parse(localStorage.getItem('timeEntrySyncQueue') || '[]');
            setSyncQueue(savedSyncQueue);

            // Auto-sync on load if there are pending items
            if (savedSyncQueue.length > 0 && listId) {
                // Delay processing to allow MSAL to fully initialize and tokens to be available
                setTimeout(() => processSyncQueue(listId, savedSyncQueue), 3000);
            }
        };

        initTimeReportsData();
    }, [showNotification]); // Add showNotification to dependencies

    // Helper to persist sync queue to localStorage
    const saveSyncQueue = (queue) => {
        localStorage.setItem('timeEntrySyncQueue', JSON.stringify(queue));
        setSyncQueue(queue);
    };

    const processSyncQueue = async (listId, queue) => {
        if (queue.length === 0) return;
        if (!listId) {
            showNotification('SharePoint TimeEntries list not configured. Cannot sync.', 'warning');
            return;
        }

        showNotification(`Syncing ${queue.length} pending changes...`, 'info', 0); // Indefinite duration

        const queueCopy = [...queue];
        let newSyncQueue = [...queue]; // To track remaining items
        let successCount = 0;
        let failCount = 0;

        for (const item of queueCopy) {
            try {
                const accessToken = await getAccessToken(); // Get fresh token for each operation
                let success = false;
                if (item.operation === 'create') {
                    success = await saveTimeEntryToSharePoint(item.entry, accessToken, listId, true, showNotification);
                } else if (item.operation === 'update') {
                    success = await saveTimeEntryToSharePoint(item.entry, accessToken, listId, false, showNotification);
                } else if (item.operation === 'delete') {
                    success = await deleteTimeEntryFromSharePoint(item.entry.sharePointId, accessToken, listId, showNotification);
                }

                if (success) {
                    newSyncQueue = newSyncQueue.filter(q => q.entry.id !== item.entry.id);
                    successCount++;
                } else {
                    failCount++;
                }
            } catch (error) {
                console.error('Sync error:', error);
                failCount++;
            }
        }

        saveSyncQueue(newSyncQueue); // Update local storage with remaining items
        if (failCount === 0) {
            showNotification(`Synced ${successCount} changes successfully!`, 'success');
        } else {
            showNotification(`Synced ${successCount}, failed ${failCount}. Will retry later.`, 'warning');
        }

        // Re-fetch all time entries after sync to ensure UI is up-to-date
        const accessToken = await getAccessToken();
        if (listId && accessToken) {
            const entries = await loadTimeEntriesFromSharePoint(accessToken, listId, showNotification);
            setTimeEntriesData(entries);
        }
    };

    // Helper to add/remove items from the sync queue
    const addToSyncQueue = (operation, entry) => {
        let currentQueue = JSON.parse(localStorage.getItem('timeEntrySyncQueue') || '[]');
        currentQueue = currentQueue.filter(q => q.entry.id !== entry.id); // Remove any existing operation for this entry
        currentQueue.push({ operation, entry: { ...entry }, timestamp: new Date().toISOString() });
        saveSyncQueue(currentQueue);
    };

    const removeFromSyncQueue = (entryId) => {
        let currentQueue = JSON.parse(localStorage.getItem('timeEntrySyncQueue') || '[]');
        currentQueue = currentQueue.filter(q => q.entry.id !== entryId);
        saveSyncQueue(currentQueue);
    };

    // Helper to filter time entries based on state
    const getFilteredTimeEntries = () => {
        return timeEntriesData.filter(entry => {
            if (timeReportStartDate && entry.date < timeReportStartDate) return false;
            if (timeReportEndDate && entry.date > timeReportEndDate) return false;
            if (timeReportEmployeeFilter && entry.employee !== timeReportEmployeeFilter) return false;
            if (timeReportProjectFilter) {
                const [pType, pId] = timeReportProjectFilter.split(':');
                if (pType === 'project' && entry.projectId !== pId) return false;
                if (pType === 'ticket' && entry.ticketId !== pId) return false; // Assuming ticketId on entry
            }
            return true;
        });
    };

    const filteredEntries = getFilteredTimeEntries();

    // Calculate summary stats
    const totalHours = filteredEntries.reduce((sum, e) => sum + e.hours, 0);
    const billableHours = filteredEntries.filter(e => e.billable !== false).reduce((sum, e) => sum + e.hours, 0);
    const uniqueEmployees = new Set(filteredEntries.map(e => e.employee)).size;
    const projectsCovered = new Set(filteredEntries.filter(e => e.projectId).map(e => e.projectId)).size;
    
    let totalBillableAmount = 0;
    filteredEntries.forEach(e => {
        if (e.billable !== false) {
            const rate = getEmployeeBillableRate(e.employee);
            totalBillableAmount += e.hours * rate;
        }
    });
    const utilizationRate = totalHours > 0 ? ((billableHours / totalHours) * 100).toFixed(0) : 0;

    // Functions to handle UI interactions (simplified)
    const applyTimeReportFilters = () => {
        // Re-renders by state change, no explicit re-render needed here
    };

    const setView = (view) => {
        setCurrentTimeReportView(view);
    };

    const showTimeEntryModal = (entry = null) => {
        setEditingEntry(entry);
        setShowModal(true);
    };

    const exportTimeReport = () => {
        showNotification('Export functionality to be implemented', 'info');
    };
    const exportBillingReport = () => {
        showNotification('Export billing functionality to be implemented', 'info');
    };

    const handleSaveTimeEntry = async (entry) => {
        const accessToken = await getAccessToken();
        if (!accessToken) {
            showNotification('Not authenticated. Please log in.', 'error');
            return;
        }

        const isNew = !entry.sharePointId;
        const success = await saveTimeEntryToSharePoint(entry, accessToken, timeEntriesListId, isNew, showNotification);

        if (success) {
            if (isNew) {
                setTimeEntriesData(prev => [...prev, entry]);
            } else {
                setTimeEntriesData(prev => prev.map(e => e.id === entry.id ? entry : e));
            }
            showNotification(`Time entry ${isNew ? 'added' : 'updated'} successfully!`, 'success');
            handleCloseModal();
        } else {
            // If online save fails, add to sync queue
            showNotification(`Failed to ${isNew ? 'add' : 'update'} time entry online. Added to sync queue.`, 'warning');
            addToSyncQueue(isNew ? 'create' : 'update', entry);
            if (isNew) {
                setTimeEntriesData(prev => [...prev, entry]);
            } else {
                setTimeEntriesData(prev => prev.map(e => e.id === entry.id ? entry : e));
            }
            handleCloseModal();
        }
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingEntry(null);
    };

    const handleDeleteEntry = async (entry) => {
        if (window.confirm(`Are you sure you want to delete the time entry for ${entry.employee} on ${entry.date}?`)) {
            const accessToken = await getAccessToken();
            // Optimistically update UI
            setTimeEntriesData(prev => prev.filter(e => e.id !== entry.id));

            const success = await deleteTimeEntryFromSharePoint(entry.sharePointId, accessToken, timeEntriesListId, showNotification);
            if (success) {
                showNotification('Time entry deleted successfully!', 'success');
            } else {
                showNotification('Failed to delete time entry online. Added to sync queue.', 'warning');
                addToSyncQueue('delete', entry);
                // If online delete fails, re-add to UI or mark as pending delete
                setTimeEntriesData(prev => [...prev, entry]); // For now, re-add to UI
            }
        }
    };


    // Render helper functions (for different views)
    const renderByEmployeeView = () => {
        const byEmployee = {};
        filteredEntries.forEach(e => {
            if (!byEmployee[e.employee]) {
                byEmployee[e.employee] = { hours: 0, billableHours: 0, entries: [] };
            }
            byEmployee[e.employee].hours += e.hours;
            if (e.billable) byEmployee[e.employee].billableHours += e.hours;
            byEmployee[e.employee].entries.push(e);
        });

        const sorted = Object.entries(byEmployee).sort(([, a], [, b]) => b.hours - a.hours);

        return (
            <div className="time-report-table">
                <table className="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Employee</th>
                            <th className="text-end">Total Hours</th>
                            <th className="text-end">Billable</th>
                            <th className="text-end">Non-Billable</th>
                            <th className="text-end">Entries</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sorted.map(([employee, data]) => (
                            <tr key={employee}>
                                <td>
                                    <div className="d-flex align-items-center">
                                        <div className="avatar rounded-circle bg-primary text-white me-2" style={{ width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            {getInitials(employee)}
                                        </div>
                                        {employee}
                                    </div>
                                </td>
                                <td className="text-end fw-bold text-primary">{data.hours.toFixed(1)}h</td>
                                <td className="text-end text-success">{data.billableHours.toFixed(1)}h</td>
                                <td className="text-end text-muted">{(data.hours - data.billableHours).toFixed(1)}h</td>
                                <td className="text-end">{data.entries.length}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    const renderByProjectView = () => {
        const byProject = {};
        filteredEntries.forEach(e => {
            const key = e.projectId || 'general';
            if (!byProject[key]) {
                byProject[key] = { name: e.projectName, type: e.projectType, hours: 0, billableHours: 0, employees: new Set() };
            }
            byProject[key].hours += e.hours;
            if (e.billable) byProject[key].billableHours += e.hours;
            byProject[key].employees.add(e.employee);
        });

        const sorted = Object.entries(byProject).sort(([, a], [, b]) => b.hours - a.hours);

        return (
            <div className="time-report-table">
                <table className="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Project/Ticket</th>
                            <th className="text-end">Total Hours</th>
                            <th className="text-end">Billable</th>
                            <th className="text-end">Team Members</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sorted.map(([id, data]) => (
                            <tr key={id}>
                                <td>
                                    <div className="d-flex align-items-center">
                                        {data.type === 'ticket' ? (
                                            <AlertTriangle size={16} className="text-warning me-2" />
                                        ) : (
                                            <Folder size={16} className="text-primary me-2" />
                                        )}
                                        {data.name}
                                    </div>
                                </td>
                                <td className="text-end fw-bold text-primary">{data.hours.toFixed(1)}h</td>
                                <td className="text-end text-success">{data.billableHours.toFixed(1)}h</td>
                                <td className="text-end">{data.employees.size}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    const renderByTaskView = () => {
        // Group by Project first, then by Task
        const byProject = {};

        filteredEntries.forEach(e => {
            const projectKey = e.projectId || 'general';
            if (!byProject[projectKey]) {
                byProject[projectKey] = {
                    name: e.projectName || 'General',
                    type: e.projectType,
                    hours: 0,
                    billableHours: 0,
                    tasks: {},
                    unassignedHours: 0,
                    unassignedBillable: 0
                };
            }

            byProject[projectKey].hours += e.hours;
            if (e.billable) byProject[projectKey].billableHours += e.hours;

            // Group by task within project
            if (e.taskId) {
                const taskKey = e.taskId;
                if (!byProject[projectKey].tasks[taskKey]) {
                    byProject[projectKey].tasks[taskKey] = {
                        name: e.taskName || 'Unnamed Task',
                        hours: 0,
                        billableHours: 0,
                        employees: new Set()
                    };
                }
                byProject[projectKey].tasks[taskKey].hours += e.hours;
                if (e.billable) byProject[projectKey].tasks[taskKey].billableHours += e.hours;
                byProject[projectKey].tasks[taskKey].employees.add(e.employee);
            } else {
                // Time not assigned to a task
                byProject[projectKey].unassignedHours += e.hours;
                if (e.billable) byProject[projectKey].unassignedBillable += e.hours;
            }
        });

        const sortedProjects = Object.entries(byProject).sort(([, a], [, b]) => b.hours - a.hours);

        return (
            <div className="time-report-table">
                {sortedProjects.map(([projectId, project]) => {
                    const taskEntries = Object.entries(project.tasks).sort(([, a], [, b]) => b.hours - a.hours);
                    const hasUnassigned = project.unassignedHours > 0;

                    return (
                        <div key={projectId} className="card mb-4">
                            {/* Project Header */}
                            <div className="card-header d-flex justify-content-between align-items-center">
                                <div className="d-flex align-items-center gap-2">
                                    {project.type === 'ticket' ? (
                                        <AlertTriangle size={20} className="text-warning" />
                                    ) : (
                                        <Folder size={20} className="text-primary" />
                                    )}
                                    <h5 className="mb-0">{project.name}</h5>
                                    <span className="badge bg-secondary">{taskEntries.length} tasks with time logged</span>
                                </div>
                                <div className="text-end">
                                    <div className="fs-5 fw-bold text-primary">{project.hours.toFixed(1)}h</div>
                                    <div className="text-success">{project.billableHours.toFixed(1)}h billable</div>
                                </div>
                            </div>

                            {/* Tasks Table */}
                            <div className="card-body">
                                <table className="table table-sm table-hover mb-0">
                                    <thead>
                                        <tr>
                                            <th>Task</th>
                                            <th className="text-end">Hours</th>
                                            <th className="text-end">Billable</th>
                                            <th className="text-end">% of Project</th>
                                            <th className="text-end">Team</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {taskEntries.map(([taskId, task]) => {
                                            const percentage = project.hours > 0 ? ((task.hours / project.hours) * 100).toFixed(0) : 0;
                                            return (
                                                <tr key={taskId}>
                                                    <td>
                                                        <div className="d-flex align-items-center gap-2">
                                                            <CheckSquare size={14} className="text-muted" />
                                                            {task.name}
                                                        </div>
                                                    </td>
                                                    <td className="text-end fw-bold">{task.hours.toFixed(1)}h</td>
                                                    <td className="text-end text-success">{task.billableHours.toFixed(1)}h</td>
                                                    <td className="text-end">
                                                        <div className="d-flex align-items-center justify-content-end gap-2">
                                                            <div className="progress" style={{ width: '60px', height: '6px' }}>
                                                                <div className="progress-bar" role="progressbar" style={{ width: `${percentage}%` }} aria-valuenow={percentage} aria-valuemin="0" aria-valuemax="100"></div>
                                                            </div>
                                                            <span className="text-muted">{percentage}%</span>
                                                        </div>
                                                    </td>
                                                    <td className="text-end text-muted">{task.employees.size} member{task.employees.size !== 1 ? 's' : ''}</td>
                                                </tr>
                                            );
                                        })}
                                        {hasUnassigned && (
                                            <tr>
                                                <td>
                                                    <div className="d-flex align-items-center gap-2">
                                                        <Clock size={14} className="text-muted" />
                                                        <span className="text-muted fst-italic">Unassigned to task</span>
                                                    </div>
                                                </td>
                                                <td className="text-end text-muted">{project.unassignedHours.toFixed(1)}h</td>
                                                <td className="text-end text-muted">{project.unassignedBillable.toFixed(1)}h</td>
                                                <td className="text-end text-muted">
                                                    {project.hours > 0 ? ((project.unassignedHours / project.hours) * 100).toFixed(0) : 0}%
                                                </td>
                                                <td className="text-end">-</td>
                                            </tr>
                                        )}
                                        {taskEntries.length === 0 && !hasUnassigned && (
                                            <tr>
                                                <td colSpan="5" className="text-center text-muted fst-italic">No time logged for tasks in this project</td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    );
                })}
            </div>
        );
    };


    const renderEntriesView = () => {
        const sorted = [...filteredEntries].sort((a, b) => b.date.localeCompare(a.date));

        return (
            <div className="time-report-table">
                <table className="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Employee</th>
                            <th>Project</th>
                            <th>Description</th>
                            <th className="text-end">Hours</th>
                            <th className="text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sorted.map(entry => (
                            <tr key={entry.id}>
                                <td>{formatDate(entry.date)}</td>
                                <td>
                                    <div className="d-flex align-items-center">
                                        <div className="avatar rounded-circle bg-primary text-white me-2" style={{ width: '24px', height: '24px', fontSize: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            {getInitials(entry.employee)}
                                        </div>
                                        {entry.employee}
                                    </div>
                                </td>
                                <td>
                                    <span className={`badge ${entry.projectType === 'ticket' ? 'bg-warning text-dark' : 'bg-primary'}`}>
                                        {entry.projectName}
                                    </span>
                                </td>
                                <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={entry.description || ''}>{entry.description || '-'}</td>
                                <td className="text-end fw-bold">
                                    {entry.hours.toFixed(2)}h
                                    {entry.billable && <span className="text-success ms-1">$</span>}
                                </td>
                                <td className="text-center">
                                    <button className="btn btn-sm btn-outline-secondary me-1" onClick={() => showTimeEntryModal(entry)}>
                                        <List size={12} />
                                    </button>
                                    <button className="btn btn-sm btn-outline-danger" onClick={() => console.log('Delete Entry', entry.id)}>
                                        <Trash2 size={12} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    const renderBillingView = () => {
        // Group by project with billing calculations
        const byProject = {};
        let grandTotalHours = 0;
        let grandBillableHours = 0;
        let grandBillableAmount = 0;

        filteredEntries.forEach(e => {
            const projectKey = e.projectId || 'general';
            if (!byProject[projectKey]) {
                byProject[projectKey] = {
                    name: e.projectName || 'General / Unassigned',
                    type: e.projectType || 'general',
                    totalHours: 0,
                    billableHours: 0,
                    billableAmount: 0,
                    employees: {},
                    entries: []
                };
            }

            const rate = getEmployeeBillableRate(e.employee);
            const entryBillableAmount = e.billable !== false ? e.hours * rate : 0;

            byProject[projectKey].totalHours += e.hours;
            if (e.billable !== false) {
                byProject[projectKey].billableHours += e.hours;
                byProject[projectKey].billableAmount += entryBillableAmount;
            }
            byProject[projectKey].entries.push(e);

            // Track by employee within project
            if (!byProject[projectKey].employees[e.employee]) {
                byProject[projectKey].employees[e.employee] = { hours: 0, billableHours: 0, amount: 0, rate };
            }
            byProject[projectKey].employees[e.employee].hours += e.hours;
            if (e.billable !== false) {
                byProject[projectKey].employees[e.employee].billableHours += e.hours;
                byProject[projectKey].employees[e.employee].amount += entryBillableAmount;
            }

            grandTotalHours += e.hours;
            if (e.billable !== false) {
                grandBillableHours += e.hours;
                grandBillableAmount += entryBillableAmount;
            }
        });

        const sorted = Object.entries(byProject).sort(([, a], [, b]) => b.billableAmount - a.billableAmount);

        return (
            <div className="time-report-table">
                <div className="billing-summary bg-success text-white p-4 rounded mb-4">
                    <div className="row text-center">
                        <div className="col">
                            <div className="fs-2 fw-bold">${grandBillableAmount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                            <div className="opacity-75">Total Billable Amount</div>
                        </div>
                        <div className="col">
                            <div className="fs-2 fw-bold">{grandBillableHours.toFixed(1)}h</div>
                            <div className="opacity-75">Billable Hours</div>
                        </div>
                        <div className="col">
                            <div className="fs-2 fw-bold">${grandBillableHours > 0 ? (grandBillableAmount / grandBillableHours).toFixed(2) : '0.00'}</div>
                            <div className="opacity-75">Avg Rate/Hour</div>
                        </div>
                    </div>
                </div>

                <table className="table table-striped table-hover mb-0">
                    <thead>
                        <tr className="bg-light">
                            <th>Project / Client</th>
                            <th className="text-end">Total Hours</th>
                            <th className="text-end">Billable Hours</th>
                            <th className="text-end">Billable Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sorted.map(([id, data]) => (
                            <React.Fragment key={id}>
                                <tr className="cursor-pointer" onClick={(e) => {
                                    const nextRow = e.currentTarget.nextElementSibling;
                                    if (nextRow) nextRow.classList.toggle('d-none');
                                }}>
                                    <td>
                                        <div className="d-flex align-items-center">
                                            {data.type === 'ticket' ? (
                                                <AlertTriangle size={16} className="text-warning me-2" />
                                            ) : data.type === 'general' ? (
                                                <Folder size={16} className="text-muted me-2" />
                                            ) : (
                                                <Folder size={16} className="text-primary me-2" />
                                            )}
                                            <span className="fw-bold">{data.name}</span>
                                            <span className="text-muted ms-2">(click to expand)</span>
                                        </div>
                                    </td>
                                    <td className="text-end">{data.totalHours.toFixed(1)}h</td>
                                    <td className="text-end text-success fw-bold">{data.billableHours.toFixed(1)}h</td>
                                    <td className="text-end fs-5 fw-bold text-primary">${data.billableAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                                </tr>
                                <tr className="d-none bg-light-subtle"> {/* Initially hidden */}
                                    <td colSpan="4" className="p-0">
                                        <table className="table table-sm table-borderless mb-0">
                                            <thead>
                                                <tr className="text-muted">
                                                    <th className="ps-5">Employee</th>
                                                    <th className="text-end">Rate</th>
                                                    <th className="text-end">Hours</th>
                                                    <th className="text-end pe-4">Amount</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {Object.entries(data.employees).map(([emp, empData]) => (
                                                    <tr key={emp}>
                                                        <td className="ps-5">{emp}</td>
                                                        <td className="text-end text-muted">${empData.rate}/hr</td>
                                                        <td className="text-end">{empData.billableHours.toFixed(1)}h</td>
                                                        <td className="text-end pe-4 fw-bold">${empData.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                            </React.Fragment>
                        ))}
                    </tbody>
                    <tfoot>
                        <tr className="bg-body-secondary fw-bold">
                            <td className="p-3">TOTAL</td>
                            <td className="text-end p-3">{grandTotalHours.toFixed(1)}h</td>
                            <td className="text-end p-3 text-success">{grandBillableHours.toFixed(1)}h</td>
                            <td className="text-end p-3 text-primary fs-5">${grandBillableAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                        </tr>
                    </tfoot>
                </table>

                <div className="d-flex justify-content-end gap-2 mt-3">
                    <button className="btn btn-outline-secondary" onClick={exportBillingReport}>
                        <Download size={14} className="me-1" />
                        Export Billing Report
                    </button>
                </div>
            </div>
        );
    };


    return (
        <div className="tab-pane fade show active" id="timereports-panel" role="tabpanel" aria-labelledby="tab-timereports">
            <div className="toolbar d-flex flex-wrap align-items-center justify-content-between mb-3">
                <div className="d-flex flex-wrap align-items-center gap-2">
                    <div className="d-flex align-items-center gap-2">
                        <label htmlFor="timeReportStartDate" className="form-label mb-0">From:</label>
                        <input
                            type="date"
                            id="timeReportStartDate"
                            className="form-control"
                            value={timeReportStartDate}
                            onChange={(e) => setTimeReportStartDate(e.target.value)}
                        />
                    </div>
                    <div className="d-flex align-items-center gap-2">
                        <label htmlFor="timeReportEndDate" className="form-label mb-0">To:</label>
                        <input
                            type="date"
                            id="timeReportEndDate"
                            className="form-control"
                            value={timeReportEndDate}
                            onChange={(e) => setTimeReportEndDate(e.target.value)}
                        />
                    </div>
                    <select
                        id="timeReportEmployee"
                        className="form-select"
                        value={timeReportEmployeeFilter}
                        onChange={(e) => setTimeReportEmployeeFilter(e.target.value)}
                    >
                        <option value="">All Employees</option>
                        {adUsers.map(user => (
                            <option key={user.displayName} value={user.displayName}>{user.displayName}</option>
                        ))}
                    </select>
                    <select
                        id="timeReportProject"
                        className="form-select"
                        value={timeReportProjectFilter}
                        onChange={(e) => setTimeReportProjectFilter(e.target.value)}
                    >
                        <option value="">All Projects/Tickets</option>
                        {projectsData.map(p => (
                            <option key={p.id} value={`project:${p.id}`}>{p.fields.ProjectName}</option>
                        ))}
                        {ticketsData.map(t => (
                            <option key={t.id} value={`ticket:${t.id}`}>[Ticket] {t.fields.TicketTitle}</option>
                        ))}
                    </select>
                    <button className="btn btn-secondary" onClick={applyTimeReportFilters}>
                        <Filter size={14} className="me-1" />
                        Apply
                    </button>
                </div>
                {syncQueue.length > 0 && (
                    <div id="syncIndicator" className="d-flex align-items-center gap-2 p-2 bg-warning-subtle rounded me-3">
                        <CloudOff size={14} color="var(--bs-warning)" />
                        <span className="text-warning">{syncQueue.length} pending</span>
                        <button className="btn btn-sm btn-outline-warning" onClick={() => processSyncQueue(timeEntriesListId, syncQueue)}>Sync Now</button>
                    </div>
                )}
                <button className="btn btn-primary" onClick={() => showTimeEntryModal()}>
                    <Plus size={16} className="me-1" />
                    Log Time
                </button>
            </div>

            {/* Time Report Summary Cards */}
            <div className="row g-3 mb-3">
                <div className="col-md-2">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">Total Hours</h6>
                            <p className="card-text fs-5 fw-bold">{totalHours.toFixed(1)}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-2">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">Billable Hours</h6>
                            <p className="card-text fs-5 fw-bold text-success">{billableHours.toFixed(1)}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">Billable Amount</h6>
                            <p className="card-text fs-5 fw-bold text-primary">${totalBillableAmount.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-2">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">Utilization</h6>
                            <p className="card-text fs-5 fw-bold">{utilizationRate}%</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-1">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">Members</h6>
                            <p className="card-text fs-5 fw-bold">{uniqueEmployees}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-2">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">Projects</h6>
                            <p className="card-text fs-5 fw-bold">{projectsCovered}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Time Report Views Toggle */}
            <div className="d-flex gap-2 mb-3 flex-wrap">
                <button className={`btn ${currentTimeReportView === 'byEmployee' ? 'btn-secondary active' : 'btn-outline-secondary'}`} onClick={() => setView('byEmployee')}>
                    <Users size={14} className="me-1" />
                    By Employee
                </button>
                <button className={`btn ${currentTimeReportView === 'byProject' ? 'btn-secondary active' : 'btn-outline-secondary'}`} onClick={() => setView('byProject')}>
                    <Folder size={14} className="me-1" />
                    By Project
                </button>
                <button className={`btn ${currentTimeReportView === 'byTask' ? 'btn-secondary active' : 'btn-outline-secondary'}`} onClick={() => setView('byTask')}>
                    <CheckSquare size={14} className="me-1" />
                    By Task
                </button>
                <button className={`btn ${currentTimeReportView === 'entries' ? 'btn-secondary active' : 'btn-outline-secondary'}`} onClick={() => setView('entries')}>
                    <List size={14} className="me-1" />
                    All Entries
                </button>
                <button className={`btn ${currentTimeReportView === 'billing' ? 'btn-success active' : 'btn-outline-success'}`} onClick={() => setView('billing')}>
                    <DollarSign size={14} className="me-1" />
                    Billing Summary
                </button>
                <div className="flex-grow-1"></div>
                <button className="btn btn-outline-secondary" onClick={exportTimeReport} title="Export to CSV">
                    <Download size={14} className="me-1" />
                    Export
                </button>
            </div>

            {/* Time Report Content */}
            <div id="timeReportContent" className="time-report-content card card-body">
                {filteredEntries.length === 0 ? (
                    <div className="empty-state text-center p-5">
                        <Clock size={48} className="text-muted mb-3" />
                        <h3 className="text-dark mb-2">No Time Entries Yet</h3>
                        <p className="text-muted mb-3">Start logging time to see reports here</p>
                        <button className="btn btn-primary" onClick={() => showTimeEntryModal()}>
                            <Plus size={16} className="me-1" />
                            Log Your First Entry
                        </button>
                    </div>
                ) : (
                    <>
                        {/* Conditional rendering based on currentTimeReportView */}
                        {currentTimeReportView === 'byEmployee' && renderByEmployeeView()}
                        {currentTimeReportView === 'byProject' && renderByProjectView()}
                        {currentTimeReportView === 'byTask' && renderByTaskView()}
                        {currentTimeReportView === 'entries' && renderEntriesView()}
                        {currentTimeReportView === 'billing' && renderBillingView()}
                    </>
                )}
            </div>

            <TimeEntryModal
                show={showModal}
                onClose={handleCloseModal}
                onSave={handleSaveTimeEntry}
                initialEntry={editingEntry}
                employees={adUsers}
                projects={projectsData}
                tickets={ticketsData}
                tasks={tasksData}
            />
        </div>
    );
}

export default TimeReports;