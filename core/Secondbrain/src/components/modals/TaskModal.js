import React, { useState, useEffect } from 'react';
import { Plus, Save, Trash2, Edit, X, Folder, AlertTriangle, CheckSquare, Clock as ClockIcon, Paperclip, MessageCircle } from 'react-feather';
import { useNotification } from '../../contexts/NotificationContext'; // Import useNotification
import { getStatusColor, getPriorityColor } from '../../utils/projectsUtils'; // Reusing these for tasks
import { formatDate } from '../../utils/timeReportsUtils'; // Correct import for formatDate

// Mock data for dropdowns (will be replaced with actual props or context later)
const MOCK_EMPLOYEES = [
    { displayName: 'Mavrick Faison' },
    { displayName: 'Patrick McFarland' },
    { displayName: 'Robbie McFarland' },
];
const MOCK_TEAMS = ['Engineering', 'Network', 'Security', 'Support'];
const MOCK_PROJECTS = [
    { id: 'proj1', fields: { ProjectName: 'Website Redesign' } },
    { id: 'proj2', fields: { ProjectName: 'Network Upgrade' } },
];
const MOCK_TICKETS = [
    { id: 'tckt1', fields: { TicketTitle: 'Database issue', ProjectID: 'proj1' } },
    { id: 'tckt2', fields: { TicketTitle: 'VPN Connectivity', ProjectID: 'proj2' } },
];

function TaskModal({ show, onClose, onSave, onDelete, initialTask = null, employees = MOCK_EMPLOYEES, projects = MOCK_PROJECTS, tickets = MOCK_TICKETS }) {
    const [id, setId] = useState('');
    const [sharePointId, setSharePointId] = useState(null);
    const [etag, setEtag] = useState(null);
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [status, setStatus] = useState('Not Started');
    const [priority, setPriority] = useState('Medium');
    const [assignedTo, setAssignedTo] = useState('');
    const [team, setTeam] = useState('Engineering'); // Assuming team for generic item
    const [customer, setCustomer] = useState('');
    const [dueDate, setDueDate] = useState('');
    const [selectedProject, setSelectedProject] = useState(''); // project:id or ticket:id
    const [comments, setComments] = useState([]); // Array of { author, text, timestamp }
    const [newCommentText, setNewCommentText] = useState('');
    const [attachments, setAttachments] = useState([]); // Array of { name, url }
    const [activityLog, setActivityLog] = useState([]); // Array of { user, action, timestamp }
    const [validationErrors, setValidationErrors] = useState({});

    useEffect(() => {
        if (initialTask) {
            setId(initialTask.id || '');
            setSharePointId(initialTask.sharePointId || null);
            setEtag(initialTask.etag || null);
            setTitle(initialTask.fields.Title || '');
            setDescription(initialTask.fields.Description || '');
            setStatus(initialTask.fields.Status || 'Not Started');
            setPriority(initialTask.fields.Priority || 'Medium');
            setAssignedTo(initialTask.fields.AssignedTo || '');
            // Assuming initialTask might have ProjectId/TicketId fields
            if (initialTask.fields.ProjectId) {
                setSelectedProject(`project:${initialTask.fields.ProjectId}`);
            } else if (initialTask.fields.TicketId) {
                setSelectedProject(`ticket:${initialTask.fields.TicketId}`);
            } else {
                setSelectedProject('');
            }
            setCustomer(initialTask.fields.Customer || ''); // Assuming Customer field for generic item
            setDueDate(initialTask.fields.DueDate || '');
            // Populate comments, attachments, activityLog if available
            setComments(initialTask.comments || []);
            setAttachments(initialTask.attachments || []);
            setActivityLog(initialTask.activityLog || []);
        } else {
            // Reset form for new entry
            setId('');
            setSharePointId(null);
            setEtag(null);
            setTitle('');
            setDescription('');
            setStatus('Not Started');
            setPriority('Medium');
            setAssignedTo('');
            setTeam('Engineering');
            setCustomer('');
            setDueDate('');
            setSelectedProject('');
            setComments([]);
            setNewCommentText('');
            setAttachments([]);
            setActivityLog([]);
        }
        setValidationErrors({});
    }, [initialTask, show]);

    const validateForm = () => {
        const errors = {};
        if (!title.trim()) errors.title = 'Title is required.';
        // Add more validation rules as needed
        setValidationErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSave = () => {
        if (!validateForm()) {
            showNotification('Please correct the errors in the form.', 'error');
            return;
        }

        const [projectType, projectId] = selectedProject ? selectedProject.split(':') : ['', ''];
        const projectName = projects.find(p => p.id === projectId)?.fields.ProjectName ||
                            tickets.find(t => t.id === projectId)?.fields.TicketTitle || '';

        const taskToSave = {
            id: id || `new-${Date.now()}`,
            sharePointId,
            etag,
            fields: {
                Title: title,
                Description: description,
                Status: status,
                Priority: priority,
                AssignedTo: assignedTo,
                Customer: customer, // Assuming Customer field
                DueDate: dueDate || null,
                ProjectId: projectType === 'project' ? projectId : null,
                TicketId: projectType === 'ticket' ? projectId : null,
                ProjectName: projectName, // Store project/ticket name for easier display
            },
            comments,
            attachments,
            activityLog,
        };
        onSave(taskToSave);
    };

    const handleAddComment = () => {
        if (newCommentText.trim()) {
            const newComment = {
                author: 'Current User', // Replace with actual current user
                text: newCommentText.trim(),
                timestamp: new Date().toISOString()
            };
            setComments(prev => [...prev, newComment]);
            setNewCommentText('');
            setActivityLog(prev => [...prev, { user: 'Current User', action: 'added a comment', timestamp: new Date().toISOString() }]);
        }
    };

    const handleFileUpload = (event) => {
        const files = Array.from(event.target.files);
        showNotification(`Uploaded ${files.length} file(s). (Not fully implemented)`, 'info');
        // Implement actual file upload logic here
    };

    if (!show) return null;

    // Determine icon for Project/Ticket selection
    const ProjectTicketIcon = selectedProject.startsWith('ticket') ? AlertTriangle : Folder;

    return (
        <div className="modal-overlay" style={{ display: 'block' }}>
            <div className="modal" style={{ maxWidth: '800px' }} role="dialog" aria-modal="true" aria-labelledby="taskModalTitle">
                <div className="modal-header">
                    <h2 className="modal-title" id="taskModalTitle">
                        <CheckSquare size={20} className="text-success me-2" />
                        {initialTask ? 'Edit Task' : 'New Task'}
                    </h2>
                    <button className="btn-close" onClick={onClose} aria-label="Close modal"></button>
                </div>
                <div className="modal-body">
                    <div className="modal-content-grid row">
                        <div className="modal-main col-md-8">
                            <div className="mb-3">
                                <label htmlFor="taskTitle" className="form-label">Title <span className="text-danger">*</span></label>
                                <input type="text" className={`form-control ${validationErrors.title ? 'is-invalid' : ''}`} id="taskTitle" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Enter task title..." required />
                                {validationErrors.title && <div className="invalid-feedback">{validationErrors.title}</div>}
                            </div>

                            <div className="mb-3">
                                <label htmlFor="taskDescription" className="form-label">Description</label>
                                <textarea className="form-control" id="taskDescription" rows="3" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe the task..."></textarea>
                            </div>

                            <div className="row mb-3">
                                <div className="col-md-6">
                                    <label htmlFor="taskStatus" className="form-label">Status</label>
                                    <select className="form-select" id="taskStatus" value={status} onChange={(e) => setStatus(e.target.value)}>
                                        <option value="Not Started">Not Started</option>
                                        <option value="In Progress">In Progress</option>
                                        <option value="Completed">Completed</option>
                                        <option value="Deferred">Deferred</option>
                                        <option value="Waiting on someone else">Waiting on someone else</option>
                                    </select>
                                </div>
                                <div className="col-md-6">
                                    <label htmlFor="taskPriority" className="form-label">Priority</label>
                                    <select className="form-select" id="taskPriority" value={priority} onChange={(e) => setPriority(e.target.value)}>
                                        <option value="Low">Low</option>
                                        <option value="Medium">Medium</option>
                                        <option value="High">High</option>
                                        <option value="Critical">Critical</option>
                                    </select>
                                </div>
                            </div>

                            <div className="row mb-3">
                                <div className="col-md-6">
                                    <label htmlFor="taskAssignedTo" className="form-label">Assigned To</label>
                                    <select className="form-select" id="taskAssignedTo" value={assignedTo} onChange={(e) => setAssignedTo(e.target.value)}>
                                        <option value="">Unassigned</option>
                                        {employees.map(emp => (
                                            <option key={emp.displayName} value={emp.displayName}>{emp.displayName}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="col-md-6">
                                    <label htmlFor="taskDueDate" className="form-label">Due Date</label>
                                    <input type="date" className="form-control" id="taskDueDate" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
                                </div>
                            </div>

                            <div className="mb-3">
                                <label htmlFor="taskRelatedProject" className="form-label">Related Project/Ticket</label>
                                <select className="form-select" id="taskRelatedProject" value={selectedProject} onChange={(e) => setSelectedProject(e.target.value)}>
                                    <option value="">None</option>
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

                            {/* Attachments Section */}
                            <div className="attachments-section mt-4">
                                <h5 className="mb-3 d-flex align-items-center"><Paperclip size={18} className="me-2 text-primary" /> Attachments</h5>
                                <div className="attachment-dropzone p-3 border rounded text-center mb-3">
                                    <input type="file" id="attachmentFileInput" style={{ display: 'none' }} multiple onChange={handleFileUpload} />
                                    <label htmlFor="attachmentFileInput" className="btn btn-sm btn-outline-secondary">
                                        <Plus size={14} className="me-1" /> Upload Files
                                    </label>
                                    <p className="text-muted mt-2 mb-0">Drag files here or click to upload (Max file size: 10MB)</p>
                                </div>
                                <div className="attachment-list">
                                    {attachments.length === 0 ? (
                                        <p className="text-muted fst-italic">No attachments.</p>
                                    ) : (
                                        attachments.map((att, index) => (
                                            <div key={index} className="d-flex align-items-center justify-content-between p-2 mb-2 border rounded">
                                                <span><Paperclip size={14} className="me-2" /> {att.name}</span>
                                                <button className="btn btn-sm btn-outline-danger">
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>

                            {/* Comments Section */}
                            <div className="comments-section mt-4">
                                <h5 className="mb-3 d-flex align-items-center"><MessageCircle size={18} className="me-2" /> Comments</h5>
                                <div className="comments-list mb-3" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                                    {comments.length === 0 ? (
                                        <p className="text-muted fst-italic">No comments yet.</p>
                                    ) : (
                                        comments.map((comment, index) => (
                                            <div key={index} className="card card-body p-2 mb-2 bg-light">
                                                <div className="d-flex justify-content-between align-items-center mb-1">
                                                    <small className="fw-bold">{comment.author}</small>
                                                    <small className="text-muted">{formatDate(comment.timestamp)}</small>
                                                </div>
                                                <p className="mb-0">{comment.text}</p>
                                            </div>
                                        ))
                                    )}
                                </div>
                                <div className="input-group">
                                    <textarea className="form-control" rows="2" placeholder="Add a comment..." value={newCommentText} onChange={(e) => setNewCommentText(e.target.value)}></textarea>
                                    <button className="btn btn-primary" onClick={handleAddComment}>Send</button>
                                </div>
                            </div>
                        </div>

                        <div className="modal-sidebar col-md-4">
                            {/* Activity Log */}
                            <div className="activity-section mb-4">
                                <h5 className="mb-3 d-flex align-items-center"><ClockIcon size={18} className="me-2" /> Activity Log</h5>
                                <div className="activity-list" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                                    {activityLog.length === 0 ? (
                                        <p className="text-muted fst-italic">No activity yet.</p>
                                    ) : (
                                        activityLog.map((activity, index) => (
                                            <div key={index} className="mb-2">
                                                <small className="d-block text-muted">{formatDate(activity.timestamp)}</small>
                                                <p className="mb-0">{activity.user} {activity.action}</p>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>

                            {/* Notes */}
                            <div className="notes-section">
                                <h5 className="mb-3 d-flex align-items-center"><Edit size={18} className="me-2" /> Additional Notes</h5>
                                <textarea className="form-control" rows="6" placeholder="Add additional notes..."></textarea>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                    <button className="btn btn-primary" onClick={handleSave}>
                        <Save size={14} className="me-1" />
                        Save Task
                    </button>
                    {initialTask && (
                        <button className="btn btn-outline-danger ms-auto" onClick={() => onDelete(id)}>
                            <Trash2 size={14} className="me-1" />
                            Delete Task
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}

export default TaskModal;