import React, { useState, useEffect, useCallback } from 'react';
import {
    Search, Plus, Filter, Clock, User, Calendar, Tag,
    ChevronDown, ChevronRight, MoreVertical, Edit2, Trash2,
    CheckCircle, AlertCircle, Folder, RefreshCcw, X
} from 'react-feather';
import { getAccessToken, msalInstance } from '../auth';
import { discoverList, createList, fetchWithRetry } from '../utils/timeReportsUtils';
import { CONFIG as APP_CONFIG } from '../config';
import { useNotification } from '../contexts/NotificationContext';
import TaskModal from './modals/TaskModal';

// Task status columns for Kanban
const KANBAN_COLUMNS = [
    { id: 'not-started', title: 'Not Started', status: 'Not Started', color: '#6c757d' },
    { id: 'in-progress', title: 'In Progress', status: 'In Progress', color: '#0dcaf0' },
    { id: 'on-hold', title: 'On Hold', status: 'On Hold', color: '#ffc107' },
    { id: 'completed', title: 'Completed', status: 'Completed', color: '#198754' }
];

// Task columns definition for SharePoint
const TASKS_COLUMNS = [
    { name: "Title", displayName: "Title", text: { maxLength: 255 } },
    { name: "Description", displayName: "Description", text: { allowMultipleLines: true, maxLength: 5000 } },
    { name: "Status", displayName: "Status", choice: { choices: ["Not Started", "In Progress", "On Hold", "Completed", "Deferred"], displayAs: "dropDownMenu" } },
    { name: "Priority", displayName: "Priority", choice: { choices: ["Low", "Medium", "High", "Critical"], displayAs: "dropDownMenu" } },
    { name: "AssignedTo", displayName: "Assigned To", text: { maxLength: 255 } },
    { name: "DueDate", displayName: "Due Date", dateTime: { format: "dateOnly" } },
    { name: "ProjectId", displayName: "Project ID", text: { maxLength: 255 } },
    { name: "ProjectName", displayName: "Project Name", text: { maxLength: 255 } },
    { name: "TicketId", displayName: "Ticket ID", text: { maxLength: 255 } },
    { name: "EstimatedHours", displayName: "Estimated Hours", number: { decimalPlaces: "two", minimum: 0 } },
    { name: "ActualHours", displayName: "Actual Hours", number: { decimalPlaces: "two", minimum: 0 } }
];

function TaskKanban() {
    const { showNotification } = useNotification();

    // Data state
    const [tasks, setTasks] = useState([]);
    const [projects, setProjects] = useState([]);
    const [tasksListId, setTasksListId] = useState(null);
    const [loading, setLoading] = useState(true);

    // Filter state
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedProject, setSelectedProject] = useState('');
    const [selectedAssignee, setSelectedAssignee] = useState('');
    const [selectedPriority, setSelectedPriority] = useState('');
    const [showFilters, setShowFilters] = useState(false);

    // Modal state
    const [showTaskModal, setShowTaskModal] = useState(false);
    const [editingTask, setEditingTask] = useState(null);
    const [quickAddColumn, setQuickAddColumn] = useState(null);

    // Drag state
    const [draggedTask, setDraggedTask] = useState(null);
    const [dragOverColumn, setDragOverColumn] = useState(null);

    // Group by project toggle
    const [groupByProject, setGroupByProject] = useState(false);

    // Get unique assignees from tasks
    const uniqueAssignees = [...new Set(tasks.map(t => t.fields?.AssignedTo).filter(Boolean))];

    // Load data
    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const accounts = msalInstance.getAllAccounts();
            if (accounts.length === 0) {
                showNotification('Please log in to view tasks', 'warning');
                setLoading(false);
                return;
            }

            const accessToken = await getAccessToken();

            // Discover or create Tasks list
            let listId = await discoverList(accessToken, APP_CONFIG.siteId, 'Tasks', showNotification);
            if (!listId) {
                listId = await createList(accessToken, APP_CONFIG.siteId, 'Tasks', 'Engineering tasks', TASKS_COLUMNS, showNotification);
            }
            setTasksListId(listId);

            // Load tasks
            if (listId) {
                const loadedTasks = await loadTasksFromSharePoint(accessToken, listId);
                setTasks(loadedTasks);
            }

            // Load projects for linking
            let projectsListId = await discoverList(accessToken, APP_CONFIG.siteId, 'Projects', showNotification);
            if (projectsListId) {
                const loadedProjects = await loadProjectsFromSharePoint(accessToken, projectsListId);
                setProjects(loadedProjects);
            }

        } catch (error) {
            console.error('Error loading data:', error);
            showNotification('Failed to load data', 'error');
        }
        setLoading(false);
    };

    const loadTasksFromSharePoint = async (accessToken, listId) => {
        try {
            let allItems = [];
            let nextLink = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${listId}/items?expand=fields&$top=200`;

            while (nextLink) {
                const response = await fetchWithRetry(nextLink, {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });

                if (!response.ok) {
                    throw new Error(`SharePoint API error: ${response.status}`);
                }

                const data = await response.json();
                allItems = allItems.concat(data.value || []);
                nextLink = data['@odata.nextLink'] || null;
            }

            return allItems.map(item => ({
                id: String(item.id),
                sharePointId: item.id,
                etag: item['@odata.etag'] || null,
                fields: {
                    Title: item.fields.Title || '',
                    Description: item.fields.Description || '',
                    Status: item.fields.Status || 'Not Started',
                    Priority: item.fields.Priority || 'Medium',
                    AssignedTo: item.fields.AssignedTo || '',
                    DueDate: item.fields.DueDate ? item.fields.DueDate.split('T')[0] : null,
                    ProjectId: item.fields.ProjectId || '',
                    ProjectName: item.fields.ProjectName || '',
                    TicketId: item.fields.TicketId || '',
                    EstimatedHours: item.fields.EstimatedHours || 0,
                    ActualHours: item.fields.ActualHours || 0
                },
                createdDateTime: item.createdDateTime,
                lastModifiedDateTime: item.lastModifiedDateTime
            }));
        } catch (error) {
            console.error('Error loading tasks:', error);
            return [];
        }
    };

    const loadProjectsFromSharePoint = async (accessToken, listId) => {
        try {
            const response = await fetchWithRetry(
                `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${listId}/items?expand=fields&$top=200`,
                { headers: { 'Authorization': `Bearer ${accessToken}` } }
            );

            if (!response.ok) return [];

            const data = await response.json();
            return (data.value || []).map(item => ({
                id: String(item.id),
                name: item.fields.Title || item.fields.ProjectName || 'Unnamed Project',
                status: item.fields.Status
            }));
        } catch (error) {
            console.error('Error loading projects:', error);
            return [];
        }
    };

    // Filter tasks
    const getFilteredTasks = useCallback(() => {
        return tasks.filter(task => {
            const f = task.fields;

            // Search filter
            if (searchQuery) {
                const search = searchQuery.toLowerCase();
                const matches = (f.Title || '').toLowerCase().includes(search) ||
                    (f.Description || '').toLowerCase().includes(search) ||
                    (f.ProjectName || '').toLowerCase().includes(search);
                if (!matches) return false;
            }

            // Project filter
            if (selectedProject && f.ProjectId !== selectedProject) return false;

            // Assignee filter
            if (selectedAssignee && f.AssignedTo !== selectedAssignee) return false;

            // Priority filter
            if (selectedPriority && f.Priority !== selectedPriority) return false;

            return true;
        });
    }, [tasks, searchQuery, selectedProject, selectedAssignee, selectedPriority]);

    const filteredTasks = getFilteredTasks();

    // Get tasks for a specific column
    const getTasksForColumn = (status) => {
        return filteredTasks.filter(task => task.fields.Status === status);
    };

    // Drag and drop handlers
    const handleDragStart = (e, task) => {
        setDraggedTask(task);
        e.dataTransfer.effectAllowed = 'move';
    };

    const handleDragOver = (e, columnId) => {
        e.preventDefault();
        setDragOverColumn(columnId);
    };

    const handleDragLeave = () => {
        setDragOverColumn(null);
    };

    const handleDrop = async (e, column) => {
        e.preventDefault();
        setDragOverColumn(null);

        if (!draggedTask || draggedTask.fields.Status === column.status) {
            setDraggedTask(null);
            return;
        }

        // Optimistic update
        const updatedTasks = tasks.map(t =>
            t.id === draggedTask.id
                ? { ...t, fields: { ...t.fields, Status: column.status } }
                : t
        );
        setTasks(updatedTasks);

        // Update in SharePoint
        try {
            const accessToken = await getAccessToken();
            const success = await updateTaskStatus(draggedTask.sharePointId, column.status, accessToken);

            if (success) {
                showNotification(`Task moved to ${column.title}`, 'success');
            } else {
                // Revert on failure
                setTasks(tasks);
                showNotification('Failed to update task', 'error');
            }
        } catch (error) {
            setTasks(tasks);
            showNotification('Failed to update task', 'error');
        }

        setDraggedTask(null);
    };

    const updateTaskStatus = async (taskId, newStatus, accessToken) => {
        if (!tasksListId) return false;

        try {
            const response = await fetchWithRetry(
                `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${tasksListId}/items/${taskId}`,
                {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        fields: { Status: newStatus }
                    })
                }
            );

            return response.ok;
        } catch (error) {
            console.error('Error updating task:', error);
            return false;
        }
    };

    // Task save handler
    const handleSaveTask = async (task) => {
        const accessToken = await getAccessToken();
        if (!accessToken || !tasksListId) {
            showNotification('Unable to save task', 'error');
            return;
        }

        const isNew = !task.sharePointId;

        try {
            const data = {
                fields: {
                    Title: task.fields.Title,
                    Description: task.fields.Description || '',
                    Status: task.fields.Status || 'Not Started',
                    Priority: task.fields.Priority || 'Medium',
                    AssignedTo: task.fields.AssignedTo || '',
                    DueDate: task.fields.DueDate || null,
                    ProjectId: task.fields.ProjectId || '',
                    ProjectName: task.fields.ProjectName || '',
                    TicketId: task.fields.TicketId || '',
                    EstimatedHours: task.fields.EstimatedHours || 0,
                    ActualHours: task.fields.ActualHours || 0
                }
            };

            let response;
            if (isNew) {
                response = await fetchWithRetry(
                    `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${tasksListId}/items`,
                    {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    }
                );
            } else {
                response = await fetchWithRetry(
                    `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${tasksListId}/items/${task.sharePointId}`,
                    {
                        method: 'PATCH',
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    }
                );
            }

            if (response.ok) {
                const savedItem = await response.json();
                const savedTask = {
                    id: String(savedItem.id),
                    sharePointId: savedItem.id,
                    etag: savedItem['@odata.etag'],
                    fields: task.fields,
                    createdDateTime: savedItem.createdDateTime,
                    lastModifiedDateTime: savedItem.lastModifiedDateTime
                };

                if (isNew) {
                    setTasks(prev => [...prev, savedTask]);
                } else {
                    setTasks(prev => prev.map(t => t.id === task.id ? savedTask : t));
                }

                showNotification(`Task ${isNew ? 'created' : 'updated'} successfully`, 'success');
                handleCloseModal();
            } else {
                showNotification('Failed to save task', 'error');
            }
        } catch (error) {
            console.error('Error saving task:', error);
            showNotification('Failed to save task', 'error');
        }
    };

    // Delete task handler
    const handleDeleteTask = async (task) => {
        if (!window.confirm(`Delete task "${task.fields.Title}"?`)) return;

        try {
            const accessToken = await getAccessToken();
            const response = await fetchWithRetry(
                `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${tasksListId}/items/${task.sharePointId}`,
                {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                }
            );

            if (response.ok || response.status === 404) {
                setTasks(prev => prev.filter(t => t.id !== task.id));
                showNotification('Task deleted', 'success');
            }
        } catch (error) {
            showNotification('Failed to delete task', 'error');
        }
    };

    // Modal handlers
    const handleCloseModal = () => {
        setShowTaskModal(false);
        setEditingTask(null);
        setQuickAddColumn(null);
    };

    const handleQuickAdd = (column) => {
        setQuickAddColumn(column);
        setEditingTask({
            fields: {
                Title: '',
                Status: column.status,
                Priority: 'Medium',
                AssignedTo: '',
                ProjectId: selectedProject || '',
                ProjectName: selectedProject ? projects.find(p => p.id === selectedProject)?.name : ''
            }
        });
        setShowTaskModal(true);
    };

    // Priority badge
    const getPriorityBadge = (priority) => {
        const colors = {
            'Critical': 'danger',
            'High': 'warning',
            'Medium': 'info',
            'Low': 'secondary'
        };
        return <span className={`badge bg-${colors[priority] || 'secondary'}`}>{priority}</span>;
    };

    // Due date formatting
    const formatDueDate = (date) => {
        if (!date) return null;
        const dueDate = new Date(date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const diffDays = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));

        let colorClass = 'text-muted';
        if (diffDays < 0) colorClass = 'text-danger';
        else if (diffDays === 0) colorClass = 'text-warning';
        else if (diffDays <= 3) colorClass = 'text-info';

        return (
            <small className={colorClass}>
                <Calendar size={12} className="me-1" />
                {dueDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </small>
        );
    };

    // Task card component
    const TaskCard = ({ task }) => (
        <div
            className={`card mb-2 task-card ${draggedTask?.id === task.id ? 'dragging' : ''}`}
            draggable
            onDragStart={(e) => handleDragStart(e, task)}
            onClick={() => { setEditingTask(task); setShowTaskModal(true); }}
            style={{ cursor: 'grab' }}
        >
            <div className="card-body p-2">
                <div className="d-flex justify-content-between align-items-start mb-1">
                    <h6 className="card-title mb-0 small fw-semibold" style={{ fontSize: '0.875rem' }}>
                        {task.fields.Title}
                    </h6>
                    <div className="dropdown" onClick={(e) => e.stopPropagation()}>
                        <button
                            className="btn btn-sm btn-link p-0 text-muted"
                            data-bs-toggle="dropdown"
                        >
                            <MoreVertical size={14} />
                        </button>
                        <ul className="dropdown-menu dropdown-menu-end">
                            <li>
                                <button
                                    className="dropdown-item small"
                                    onClick={() => { setEditingTask(task); setShowTaskModal(true); }}
                                >
                                    <Edit2 size={12} className="me-2" /> Edit
                                </button>
                            </li>
                            <li><hr className="dropdown-divider" /></li>
                            <li>
                                <button
                                    className="dropdown-item small text-danger"
                                    onClick={() => handleDeleteTask(task)}
                                >
                                    <Trash2 size={12} className="me-2" /> Delete
                                </button>
                            </li>
                        </ul>
                    </div>
                </div>

                {task.fields.ProjectName && (
                    <div className="mb-1">
                        <small className="text-primary">
                            <Folder size={10} className="me-1" />
                            {task.fields.ProjectName}
                        </small>
                    </div>
                )}

                <div className="d-flex flex-wrap gap-1 align-items-center mt-2">
                    {getPriorityBadge(task.fields.Priority)}
                    {formatDueDate(task.fields.DueDate)}
                    {task.fields.AssignedTo && (
                        <small className="text-muted">
                            <User size={10} className="me-1" />
                            {task.fields.AssignedTo.split(' ')[0]}
                        </small>
                    )}
                    {task.fields.EstimatedHours > 0 && (
                        <small className="text-muted">
                            <Clock size={10} className="me-1" />
                            {task.fields.EstimatedHours}h
                        </small>
                    )}
                </div>
            </div>
        </div>
    );

    // Kanban column component
    const KanbanColumn = ({ column }) => {
        const columnTasks = getTasksForColumn(column.status);
        const isOver = dragOverColumn === column.id;

        return (
            <div
                className={`kanban-column flex-shrink-0 ${isOver ? 'drag-over' : ''}`}
                style={{ width: '280px', minWidth: '280px' }}
                onDragOver={(e) => handleDragOver(e, column.id)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, column)}
            >
                <div
                    className="card h-100"
                    style={{ backgroundColor: '#f8f9fa' }}
                >
                    <div
                        className="card-header d-flex justify-content-between align-items-center py-2"
                        style={{ borderTop: `3px solid ${column.color}` }}
                    >
                        <span className="fw-semibold small">
                            {column.title}
                            <span className="badge bg-secondary ms-2">{columnTasks.length}</span>
                        </span>
                        <button
                            className="btn btn-sm btn-link p-0"
                            onClick={() => handleQuickAdd(column)}
                            title="Add task"
                        >
                            <Plus size={16} />
                        </button>
                    </div>
                    <div
                        className="card-body p-2 overflow-auto"
                        style={{ maxHeight: 'calc(100vh - 300px)' }}
                    >
                        {columnTasks.length === 0 ? (
                            <div className="text-center text-muted py-4">
                                <small>No tasks</small>
                            </div>
                        ) : (
                            columnTasks.map(task => (
                                <TaskCard key={task.id} task={task} />
                            ))
                        )}
                    </div>
                </div>
            </div>
        );
    };

    // Stats
    const totalTasks = filteredTasks.length;
    const completedTasks = filteredTasks.filter(t => t.fields.Status === 'Completed').length;
    const overdueTasks = filteredTasks.filter(t => {
        if (!t.fields.DueDate || t.fields.Status === 'Completed') return false;
        return new Date(t.fields.DueDate) < new Date();
    }).length;

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="task-kanban">
            {/* Header Stats */}
            <div className="row g-3 mb-3">
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body py-2">
                            <h6 className="card-title text-muted mb-1 small">Total Tasks</h6>
                            <p className="card-text fs-5 fw-bold mb-0">{totalTasks}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body py-2">
                            <h6 className="card-title text-muted mb-1 small">In Progress</h6>
                            <p className="card-text fs-5 fw-bold text-info mb-0">
                                {filteredTasks.filter(t => t.fields.Status === 'In Progress').length}
                            </p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body py-2">
                            <h6 className="card-title text-muted mb-1 small">Completed</h6>
                            <p className="card-text fs-5 fw-bold text-success mb-0">{completedTasks}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body py-2">
                            <h6 className="card-title text-muted mb-1 small">Overdue</h6>
                            <p className="card-text fs-5 fw-bold text-danger mb-0">{overdueTasks}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Toolbar */}
            <div className="d-flex flex-wrap align-items-center justify-content-between mb-3 gap-2">
                <div className="d-flex flex-wrap align-items-center gap-2">
                    {/* Search */}
                    <div className="input-group" style={{ width: '250px' }}>
                        <span className="input-group-text"><Search size={14} /></span>
                        <input
                            type="text"
                            className="form-control form-control-sm"
                            placeholder="Search tasks..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                        {searchQuery && (
                            <button
                                className="btn btn-outline-secondary btn-sm"
                                onClick={() => setSearchQuery('')}
                            >
                                <X size={14} />
                            </button>
                        )}
                    </div>

                    {/* Project Filter */}
                    <select
                        className="form-select form-select-sm"
                        style={{ width: '180px' }}
                        value={selectedProject}
                        onChange={(e) => setSelectedProject(e.target.value)}
                    >
                        <option value="">All Projects</option>
                        {projects.map(p => (
                            <option key={p.id} value={p.id}>{p.name}</option>
                        ))}
                    </select>

                    {/* Toggle Filters */}
                    <button
                        className={`btn btn-sm ${showFilters ? 'btn-primary' : 'btn-outline-secondary'}`}
                        onClick={() => setShowFilters(!showFilters)}
                    >
                        <Filter size={14} className="me-1" />
                        Filters
                    </button>
                </div>

                <div className="d-flex align-items-center gap-2">
                    <button
                        className="btn btn-sm btn-outline-secondary"
                        onClick={loadData}
                        title="Refresh"
                    >
                        <RefreshCcw size={14} />
                    </button>
                    <button
                        className="btn btn-sm btn-primary"
                        onClick={() => {
                            setEditingTask(null);
                            setShowTaskModal(true);
                        }}
                    >
                        <Plus size={14} className="me-1" /> New Task
                    </button>
                </div>
            </div>

            {/* Extended Filters */}
            {showFilters && (
                <div className="card mb-3">
                    <div className="card-body py-2">
                        <div className="row g-2 align-items-center">
                            <div className="col-auto">
                                <label className="col-form-label col-form-label-sm">Assignee:</label>
                            </div>
                            <div className="col-auto">
                                <select
                                    className="form-select form-select-sm"
                                    value={selectedAssignee}
                                    onChange={(e) => setSelectedAssignee(e.target.value)}
                                >
                                    <option value="">All</option>
                                    {uniqueAssignees.map(a => (
                                        <option key={a} value={a}>{a}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="col-auto">
                                <label className="col-form-label col-form-label-sm">Priority:</label>
                            </div>
                            <div className="col-auto">
                                <select
                                    className="form-select form-select-sm"
                                    value={selectedPriority}
                                    onChange={(e) => setSelectedPriority(e.target.value)}
                                >
                                    <option value="">All</option>
                                    <option value="Critical">Critical</option>
                                    <option value="High">High</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Low">Low</option>
                                </select>
                            </div>
                            <div className="col-auto">
                                <button
                                    className="btn btn-sm btn-link"
                                    onClick={() => {
                                        setSelectedAssignee('');
                                        setSelectedPriority('');
                                        setSelectedProject('');
                                        setSearchQuery('');
                                    }}
                                >
                                    Clear All
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Kanban Board */}
            <div
                className="kanban-board d-flex gap-3 pb-3 overflow-auto"
                style={{ minHeight: '500px' }}
            >
                {KANBAN_COLUMNS.map(column => (
                    <KanbanColumn key={column.id} column={column} />
                ))}
            </div>

            {/* Task Modal */}
            <TaskModal
                show={showTaskModal}
                onClose={handleCloseModal}
                onSave={handleSaveTask}
                initialTask={editingTask}
                projects={projects}
            />

            {/* Styles */}
            <style>{`
                .task-card {
                    transition: transform 0.2s, box-shadow 0.2s;
                    border: 1px solid #dee2e6;
                }
                .task-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                .task-card.dragging {
                    opacity: 0.5;
                    transform: rotate(3deg);
                }
                .kanban-column.drag-over .card {
                    background-color: #e3f2fd !important;
                    border: 2px dashed #2196f3;
                }
                .kanban-board::-webkit-scrollbar {
                    height: 8px;
                }
                .kanban-board::-webkit-scrollbar-thumb {
                    background-color: #ccc;
                    border-radius: 4px;
                }
            `}</style>
        </div>
    );
}

export default TaskKanban;
