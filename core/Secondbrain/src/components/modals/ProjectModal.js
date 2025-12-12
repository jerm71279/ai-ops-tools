import React, { useState, useEffect } from 'react';
import { Plus, Save, Clock, Edit } from 'react-feather';
import { useNotification } from '../../contexts/NotificationContext'; // Import useNotification
import { getStatusColor, getPriorityColor } from '../../utils/projectsUtils'; // Assuming these exist

// Mock data for dropdowns (will be replaced with actual props or context later)
const MOCK_EMPLOYEES = [
    { displayName: 'Mavrick Faison' },
    { displayName: 'Patrick McFarland' },
    { displayName: 'Robbie McFarland' },
];
const MOCK_TEAMS = ['Engineering', 'Network', 'Security', 'Support'];

function ProjectModal({ show, onClose, onSave, initialProject = null, employees = MOCK_EMPLOYEES }) {
    const [id, setId] = useState('');
    const [sharePointId, setSharePointId] = useState(null);
    const [etag, setEtag] = useState(null);
    const [projectName, setProjectName] = useState('');
    const [description, setDescription] = useState('');
    const [status, setStatus] = useState('Not Started');
    const [priority, setPriority] = useState('Medium');
    const [assignedTo, setAssignedTo] = useState('');
    const [team, setTeam] = useState('Engineering');
    const [customer, setCustomer] = useState('');
    const [dueDate, setDueDate] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [percentComplete, setPercentComplete] = useState(0);
    const [budgetHours, setBudgetHours] = useState(0);
    const [hoursSpent, setHoursSpent] = useState(0);
    const [sow, setSow] = useState('');
    const [validationErrors, setValidationErrors] = useState({});

    useEffect(() => {
        if (initialProject) {
            setId(initialProject.id || '');
            setSharePointId(initialProject.sharePointId || null);
            setEtag(initialProject.etag || null);
            setProjectName(initialProject.fields.ProjectName || '');
            setDescription(initialProject.fields.Description || '');
            setStatus(initialProject.fields.Status || 'Not Started');
            setPriority(initialProject.fields.Priority || 'Medium');
            setAssignedTo(initialProject.fields.AssignedTo || '');
            setTeam(initialProject.fields.Team || 'Engineering'); // Assuming Team field exists
            setCustomer(initialProject.fields.Customer || '');
            setDueDate(initialProject.fields.DueDate || '');
            setStartDate(initialProject.fields.StartDate || '');
            setEndDate(initialProject.fields.EndDate || '');
            setPercentComplete(initialProject.fields.PercentComplete || 0);
            setBudgetHours(initialProject.fields.BudgetHours || 0);
            setHoursSpent(initialProject.fields.HoursSpent || 0);
            setSow(initialProject.fields.SOW || '');
        } else {
            // Reset form for new entry
            setId('');
            setSharePointId(null);
            setEtag(null);
            setProjectName('');
            setDescription('');
            setStatus('Not Started');
            setPriority('Medium');
            setAssignedTo('');
            setTeam('Engineering');
            setCustomer('');
            setDueDate('');
            setStartDate('');
            setEndDate('');
            setPercentComplete(0);
            setBudgetHours(0);
            setHoursSpent(0);
            setSow('');
        }
        setValidationErrors({});
    }, [initialProject, show]);

    const validateForm = () => {
        const errors = {};
        if (!projectName.trim()) errors.projectName = 'Project Name is required.';
        if (percentComplete < 0 || percentComplete > 100) errors.percentComplete = 'Percent Complete must be between 0 and 100.';
        if (budgetHours < 0) errors.budgetHours = 'Budget Hours cannot be negative.';
        if (hoursSpent < 0) errors.hoursSpent = 'Hours Spent cannot be negative.';
        // Add more validation rules as needed
        setValidationErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSave = () => {
        if (!validateForm()) {
            showNotification('Please correct the errors in the form.', 'error');
            return;
        }

        const projectToSave = {
            id: id || `new-${Date.now()}`,
            sharePointId,
            etag,
            fields: {
                ProjectName: projectName,
                Description: description,
                Status: status,
                Priority: priority,
                AssignedTo: assignedTo,
                Team: team, // Assuming Team field exists in SharePoint
                Customer: customer,
                DueDate: dueDate || null,
                StartDate: startDate || null,
                EndDate: endDate || null,
                PercentComplete: parseInt(percentComplete, 10),
                BudgetHours: parseFloat(budgetHours),
                HoursSpent: parseFloat(hoursSpent),
                SOW: sow,
            }
        };
        onSave(projectToSave);
    };

    if (!show) return null;

    return (
        <div className="modal-overlay" style={{ display: 'block' }}>
            <div className="modal" style={{ maxWidth: '600px' }} role="dialog" aria-modal="true" aria-labelledby="projectModalTitle">
                <div className="modal-header">
                    <h2 className="modal-title" id="projectModalTitle">
                        <Folder size={20} className="text-primary me-2" />
                        {initialProject ? 'Edit Project' : 'New Project'}
                    </h2>
                    <button className="btn-close" onClick={onClose} aria-label="Close modal"></button>
                </div>
                <div className="modal-body">
                    <div className="mb-3">
                        <label htmlFor="projectName" className="form-label">Project Name <span className="text-danger">*</span></label>
                        <input type="text" className={`form-control ${validationErrors.projectName ? 'is-invalid' : ''}`} id="projectName" value={projectName} onChange={(e) => setProjectName(e.target.value)} placeholder="Enter project name..." required />
                        {validationErrors.projectName && <div className="invalid-feedback">{validationErrors.projectName}</div>}
                    </div>

                    <div className="mb-3">
                        <label htmlFor="projectDescription" className="form-label">Description</label>
                        <textarea className="form-control" id="projectDescription" rows="3" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe the project..."></textarea>
                    </div>

                    <div className="row mb-3">
                        <div className="col-md-6">
                            <label htmlFor="projectStatus" className="form-label">Status</label>
                            <select className="form-select" id="projectStatus" value={status} onChange={(e) => setStatus(e.target.value)}>
                                <option value="Not Started">Not Started</option>
                                <option value="In Progress">In Progress</option>
                                <option value="On Hold">On Hold</option>
                                <option value="Completed">Completed</option>
                                <option value="Archived">Archived</option>
                            </select>
                        </div>
                        <div className="col-md-6">
                            <label htmlFor="projectPriority" className="form-label">Priority</label>
                            <select className="form-select" id="projectPriority" value={priority} onChange={(e) => setPriority(e.target.value)}>
                                <option value="Low">Low</option>
                                <option value="Medium">Medium</option>
                                <option value="High">High</option>
                                <option value="Critical">Critical</option>
                            </select>
                        </div>
                    </div>

                    <div className="row mb-3">
                        <div className="col-md-6">
                            <label htmlFor="projectAssignedTo" className="form-label">Assigned To</label>
                            <select className="form-select" id="projectAssignedTo" value={assignedTo} onChange={(e) => setAssignedTo(e.target.value)}>
                                <option value="">Unassigned</option>
                                {employees.map(emp => (
                                    <option key={emp.displayName} value={emp.displayName}>{emp.displayName}</option>
                                ))}
                            </select>
                        </div>
                        <div className="col-md-6">
                            <label htmlFor="projectTeam" className="form-label">Team</label>
                            <select className="form-select" id="projectTeam" value={team} onChange={(e) => setTeam(e.target.value)}>
                                {MOCK_TEAMS.map(t => (
                                    <option key={t} value={t}>{t}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="row mb-3">
                        <div className="col-md-6">
                            <label htmlFor="projectCustomer" className="form-label">Customer</label>
                            <input type="text" className="form-control" id="projectCustomer" value={customer} onChange={(e) => setCustomer(e.target.value)} placeholder="Customer name..." />
                        </div>
                        <div className="col-md-6">
                            <label htmlFor="projectDueDate" className="form-label">Due Date</label>
                            <input type="date" className="form-control" id="projectDueDate" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
                        </div>
                    </div>

                    <div className="row mb-3">
                        <div className="col-md-6">
                            <label htmlFor="projectStartDate" className="form-label">Start Date</label>
                            <input type="date" className="form-control" id="projectStartDate" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
                        </div>
                        <div className="col-md-6">
                            <label htmlFor="projectEndDate" className="form-label">End Date</label>
                            <input type="date" className="form-control" id="projectEndDate" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
                        </div>
                    </div>

                    <div className="mb-3">
                        <label htmlFor="projectPercent" className="form-label">Percent Complete: {percentComplete}%</label>
                        <input type="range" className="form-range" id="projectPercent" min="0" max="100" value={percentComplete} onChange={(e) => setPercentComplete(e.target.value)} />
                    </div>

                    <div className="row mb-3">
                        <div className="col-md-6">
                            <label htmlFor="projectBudgetHours" className="form-label">Budget Hours</label>
                            <input type="number" className={`form-control ${validationErrors.budgetHours ? 'is-invalid' : ''}`} id="projectBudgetHours" value={budgetHours} onChange={(e) => setBudgetHours(e.target.value)} placeholder="0" min="0" />
                            {validationErrors.budgetHours && <div className="invalid-feedback">{validationErrors.budgetHours}</div>}
                        </div>
                        <div className="col-md-6">
                            <label htmlFor="projectHoursSpent" className="form-label">Hours Spent</label>
                            <input type="number" className={`form-control ${validationErrors.hoursSpent ? 'is-invalid' : ''}`} id="projectHoursSpent" value={hoursSpent} onChange={(e) => setHoursSpent(e.target.value)} placeholder="0" min="0" />
                            {validationErrors.hoursSpent && <div className="invalid-feedback">{validationErrors.hoursSpent}</div>}
                        </div>
                    </div>

                    <div className="mb-3">
                        <label htmlFor="projectSow" className="form-label">Statement of Work (SOW)</label>
                        <textarea className="form-control" id="projectSow" rows="3" value={sow} onChange={(e) => setSow(e.target.value)} placeholder="Details of the SOW..."></textarea>
                    </div>

                </div>
                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                    <button className="btn btn-primary" onClick={handleSave}>
                        <Save size={14} className="me-1" />
                        Save Project
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ProjectModal;