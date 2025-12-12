import React, { useState, useEffect } from 'react';
import { Plus, Save } from 'react-feather';
import { useNotification } from '../../contexts/NotificationContext'; // Import useNotification

// Mock data for dropdowns (will be replaced with actual props or context later)
const MOCK_EMPLOYEES = [
    { displayName: 'Mavrick Faison' },
    { displayName: 'Patrick McFarland' },
    { displayName: 'Robbie McFarland' },
];
const MOCK_PROJECTS = [
    { id: 'proj1', fields: { ProjectName: 'Website Redesign' } },
    { id: 'proj2', fields: { ProjectName: 'Network Upgrade' } },
];
const MOCK_TICKETS = [
    { id: 'tckt1', fields: { TicketTitle: 'Database issue', ProjectID: 'proj1' } },
    { id: 'tckt2', fields: { TicketTitle: 'VPN Connectivity', ProjectID: 'proj2' } },
];
const MOCK_TASKS = [
    { id: 'task1', fields: { Title: 'Implement UI', ProjectID: 'proj1', TicketID: 'tckt1' } },
    { id: 'task2', fields: { Title: 'Configure Firewall', ProjectID: 'proj2', TicketID: 'tckt2' } },
];

function TimeEntryModal({ show, onClose, onSave, initialEntry = null, employees = MOCK_EMPLOYEES, projects = MOCK_PROJECTS, tickets = MOCK_TICKETS, tasks = MOCK_TASKS }) {
    const [employee, setEmployee] = useState('');
    const [date, setDate] = useState('');
    const [hours, setHours] = useState('');
    const [workType, setWorkType] = useState('Project');
    const [selectedProject, setSelectedProject] = useState(''); // Stores project:id or ticket:id
    const [selectedTask, setSelectedTask] = useState('');
    const [description, setDescription] = useState('');
    const [billable, setBillable] = useState(true);

    useEffect(() => {
        if (initialEntry) {
            setEmployee(initialEntry.employee || '');
            setDate(initialEntry.date || '');
            setHours(initialEntry.hours || '');
            setWorkType(initialEntry.type || 'Project');
            if (initialEntry.projectId && initialEntry.projectType) {
                setSelectedProject(`${initialEntry.projectType}:${initialEntry.projectId}`);
            } else {
                setSelectedProject('');
            }
            setSelectedTask(initialEntry.taskId || '');
            setDescription(initialEntry.description || '');
            setBillable(initialEntry.billable !== false);
        } else {
            // Reset form for new entry
            setEmployee('');
            setDate(new Date().toISOString().split('T')[0]); // Default to today
            setHours('');
            setWorkType('Project');
            setSelectedProject('');
            setSelectedTask('');
            setDescription('');
            setBillable(true);
        }
    }, [initialEntry, show]);

    const handleSave = () => {
        if (!employee || !date || !hours) {
            showNotification('Employee, Date, and Hours are required.', 'error');
            return;
        }
        if (isNaN(parseFloat(hours)) || parseFloat(hours) <= 0) {
            showNotification('Hours must be a positive number.', 'error');
            return;
        }

        const [projectType, projectId] = selectedProject ? selectedProject.split(':') : ['', ''];
        const projectName = projects.find(p => p.id === projectId)?.fields.ProjectName ||
                            tickets.find(t => t.id === projectId)?.fields.TicketTitle ||
                            'General';

        const newEntry = {
            id: initialEntry ? initialEntry.id : `new-${Date.now()}`,
            sharePointId: initialEntry ? initialEntry.sharePointId : null,
            etag: initialEntry ? initialEntry.etag : null,
            employee,
            date,
            hours: parseFloat(hours),
            type: workType,
            projectId: projectId || null,
            projectType: projectType || null,
            projectName,
            taskId: selectedTask || null,
            description,
            billable,
        };
        onSave(newEntry);
    };

    const filteredTasks = tasks.filter(task => {
        const [projectType, projectId] = selectedProject.split(':');
        if (projectType === 'project') {
            return task.fields.ProjectID === projectId;
        } else if (projectType === 'ticket') {
            return task.fields.TicketID === projectId;
        }
        return false;
    });

    if (!show) return null;

    return (
        <div className="modal-overlay" style={{ display: 'block' }}>
            <div className="modal" style={{ maxWidth: '500px' }} role="dialog" aria-modal="true" aria-labelledby="timeEntryModalTitle">
                <div className="modal-header">
                    <h2 className="modal-title" id="timeEntryModalTitle">
                        <Clock size={20} className="text-primary me-2" />
                        {initialEntry ? 'Edit Time Entry' : 'Log Time Entry'}
                    </h2>
                    <button className="btn-close" onClick={onClose} aria-label="Close modal"></button>
                </div>
                <div className="modal-body">
                    <div className="form-group mb-3">
                        <label className="form-label" htmlFor="timeEntryEmployee">Employee <span className="text-danger">*</span></label>
                        <select className="form-select" id="timeEntryEmployee" value={employee} onChange={(e) => setEmployee(e.target.value)} required>
                            <option value="">Select Employee</option>
                            {employees.map(emp => (
                                <option key={emp.displayName} value={emp.displayName}>{emp.displayName}</option>
                            ))}
                        </select>
                    </div>

                    <div className="row mb-3">
                        <div className="col">
                            <label className="form-label" htmlFor="timeEntryDate">Date <span className="text-danger">*</span></label>
                            <input type="date" className="form-control" id="timeEntryDate" value={date} onChange={(e) => setDate(e.target.value)} required />
                        </div>
                        <div className="col">
                            <label className="form-label" htmlFor="timeEntryHours">Hours <span className="text-danger">*</span></label>
                            <input type="number" className="form-control" id="timeEntryHours" min="0.25" max="24" step="0.25" value={hours} onChange={(e) => setHours(e.target.value)} placeholder="0.00" required />
                        </div>
                    </div>

                    <div className="form-group mb-3">
                        <label className="form-label" htmlFor="timeEntryType">Work Type</label>
                        <select className="form-select" id="timeEntryType" value={workType} onChange={(e) => setWorkType(e.target.value)}>
                            <option value="Project">Project Work</option>
                            <option value="Ticket">Ticket/Support</option>
                            <option value="Meeting">Meeting</option>
                            <option value="Admin">Administrative</option>
                            <option value="Training">Training</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>

                    <div className="form-group mb-3">
                        <label className="form-label" htmlFor="timeEntryProject">Project/Ticket</label>
                        <select className="form-select" id="timeEntryProject" value={selectedProject} onChange={(e) => { setSelectedProject(e.target.value); setSelectedTask(''); }}>
                            <option value="">None (General)</option>
                            <optgroup label="Projects">
                                {projects.map(p => (
                                    <option key={`project-${p.id}`} value={`project:${p.id}`}>{p.fields.ProjectName}</option>
                                ))}
                            </optgroup>
                            <optgroup label="Tickets">
                                {tickets.map(t => (
                                    <option key={`ticket-${t.id}`} value={`ticket:${t.id}`}>{t.fields.TicketTitle}</option>
                                ))}
                            </optgroup>
                        </select>
                    </div>

                    <div className="form-group mb-3">
                        <label className="form-label" htmlFor="timeEntryTask">Task (Optional)</label>
                        <select className="form-select" id="timeEntryTask" value={selectedTask} onChange={(e) => setSelectedTask(e.target.value)} disabled={!selectedProject}>
                            <option value="">No Task Selected</option>
                            {filteredTasks.map(task => (
                                <option key={task.id} value={task.id}>{task.fields.Title}</option>
                            ))}
                        </select>
                        <small className="form-text text-muted mt-1 d-block">Select a project/ticket first to see linked tasks</small>
                    </div>

                    <div className="form-group mb-3">
                        <label className="form-label" htmlFor="timeEntryDescription">Description</label>
                        <textarea className="form-control" id="timeEntryDescription" rows="3" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What did you work on?"></textarea>
                    </div>

                    <div className="form-check">
                        <input className="form-check-input" type="checkbox" id="timeEntryBillable" checked={billable} onChange={(e) => setBillable(e.target.checked)} />
                        <label className="form-check-label" htmlFor="timeEntryBillable">
                            Billable Time
                        </label>
                    </div>
                </div>
                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                    <button className="btn btn-primary" onClick={handleSave}>
                        <Save size={14} className="me-1" />
                        Save Entry
                    </button>
                </div>
            </div>
        </div>
    );
}

export default TimeEntryModal;