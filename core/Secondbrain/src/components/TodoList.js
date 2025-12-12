import React, { useState, useEffect } from 'react';
import {
    ChevronLeft, ChevronRight, Plus, Download, FileText, File, Filter, CheckSquare, Folder, Calendar as CalendarIcon, User, Clock, Trash2, Edit
} from 'react-feather';
import {
    getWeekStart, getWeekEnd, formatDisplayDate, formatMonthYear, groupTasksByAssignee, getDueClass, calculateTaskStats,
    loadTasksFromSharePoint, saveTaskToSharePoint, deleteTaskFromSharePoint
} from '../utils/todoListUtils';
import TaskModal from './modals/TaskModal'; // Import TaskModal
import { useNotification } from '../contexts/NotificationContext';
import { getAccessToken, msalInstance } from '../auth';
import { discoverList, createList } from '../utils/timeReportsUtils';
import { CONFIG as APP_CONFIG } from '../config';

// Mock data/config for now - MOCK_AD_USERS should eventually come from a centralized data source
const MOCK_AD_USERS = [
    { displayName: 'Mavrick Faison', mail: 'mavrick@example.com' },
    { displayName: 'Patrick McFarland', mail: 'patrick@example.com' },
    { displayName: 'Robbie McFarland', mail: 'robbie@example.com' },
    { displayName: 'Unassigned', mail: '' },
];

const TASKS_COLUMNS = [
    { name: "Title", displayName: "Title", text: { maxLength: 255 } },
    { name: "Status", displayName: "Status", choice: { choices: ["Not Started", "In Progress", "Completed", "Deferred", "Waiting on someone else"], displayAs: "dropDownMenu" } },
    { name: "Priority", displayName: "Priority", choice: { choices: ["Low", "Medium", "High", "Critical"], displayAs: "dropDownMenu" } },
    { name: "AssignedTo", displayName: "Assigned To", text: { maxLength: 255 } },
    { name: "DueDate", displayName: "Due Date", dateTime: { format: "dateOnly" } },
    { name: "ProjectName", displayName: "Project Name", text: { maxLength: 255 } },
    { name: "ProjectId", displayName: "Project ID", text: { maxLength: 255 } },
    { name: "TicketId", displayName: "Ticket ID", text: { maxLength: 255 } },
    { name: "Description", displayName: "Description", text: { allowMultipleLines: true, maxLength: 5000 } },
];

function TodoList() {
    const { showNotification } = useNotification();
    const [tasksData, setTasksData] = useState([]);
    const [currentWeekStart, setCurrentWeekStart] = useState(getWeekStart(new Date()));
    const [quickAddInput, setQuickAddInput] = useState('');
    const [quickAddAssignee, setQuickAddAssignee] = useState('');
    const [tasksListId, setTasksListId] = useState(null); // Assuming tasksListId will be discovered or set
    const [showTaskModal, setShowTaskModal] = useState(false);
    const [editingTask, setEditingTask] = useState(null);

    // Effect for initial data loading

    // Effect for initial data loading
    useEffect(() => {
        const initTasksData = async () => {
            const accounts = msalInstance.getAllAccounts();
            if (accounts.length === 0) {
                return;
            }
            const accessToken = await getAccessToken();

            // Discover or create Tasks list
            let listId = await discoverList(accessToken, APP_CONFIG.siteId, 'Tasks');
            if (!listId) {
                listId = await createList(accessToken, APP_CONFIG.siteId, 'Tasks', 'Project and general tasks', TASKS_COLUMNS);
            }
            setTasksListId(listId);

            if (listId) {
                const loadedTasks = await loadTasksFromSharePoint(accessToken, listId);
                setTasksData(loadedTasks);
            }
        };
        initTasksData();
    }, []);

    const navigateWeek = (direction) => {
        const newDate = new Date(currentWeekStart);
        newDate.setDate(newDate.getDate() + (direction * 7));
        setCurrentWeekStart(getWeekStart(newDate));
    };

    const goToToday = () => {
        setCurrentWeekStart(getWeekStart(new Date()));
    };

    const quickAddTask = () => {
        if (!quickAddInput.trim()) {
            showNotification('Task title cannot be empty.', 'error');
            return;
        }
        // Open modal for new task with pre-filled title and assignee
        setEditingTask({
            id: `temp-${Date.now()}`,
            fields: {
                Title: quickAddInput.trim(),
                Status: 'Not Started',
                Priority: 'Medium',
                AssignedTo: quickAddAssignee || 'Unassigned',
                DueDate: null,
                ProjectName: 'General'
            }
        });
        setShowTaskModal(true);
        setQuickAddInput(''); // Clear quick add input after initiating modal
        setQuickAddAssignee('');
    };

    const toggleTaskStatus = async (taskId, currentStatus) => {
        const newStatus = currentStatus === 'Completed' ? 'Not Started' : 'Completed';
        const taskToUpdate = tasksData.find(task => task.id === taskId);

        if (taskToUpdate) {
            const updatedTask = { ...taskToUpdate, fields: { ...taskToUpdate.fields, Status: newStatus } };
            const accessToken = await getAccessToken();
            const success = await saveTaskToSharePoint(updatedTask, accessToken, tasksListId, false);
            if (success) {
                setTasksData(prev => prev.map(task => task.id === taskId ? updatedTask : task));
                showNotification('Task status updated!', 'success');
            } else {
                showNotification('Failed to update task status in SharePoint.', 'error');
            }
        }
    };

    const openTaskDetail = (task) => {
        setEditingTask(task);
        setShowTaskModal(true);
    };

    const deleteTask = async (taskId) => {
        const accessToken = await getAccessToken();
        const success = await deleteTaskFromSharePoint(taskId, accessToken, tasksListId);
        if (success) {
            setTasksData(prevTasks => prevTasks.filter(task => task.id !== taskId));
            showNotification('Task deleted successfully!', 'success');
        } else {
            showNotification('Failed to delete task.', 'error');
        }
    };

    const handleSaveTask = async (task) => {
        const accessToken = await getAccessToken();
        if (!accessToken) {
            showNotification('Not authenticated. Please log in.', 'error');
            return;
        }

        const isNew = !task.sharePointId;
        const success = await saveTaskToSharePoint(task, accessToken, tasksListId, isNew);

        if (success) {
            if (isNew) {
                setTasksData(prev => [...prev, task]);
            } else {
                setTasksData(prev => prev.map(t => t.id === task.id ? task : t));
            }
            showNotification(`Task ${isNew ? 'added' : 'updated'} successfully!`, 'success');
            handleCloseTaskModal();
        } else {
            showNotification(`Failed to ${isNew ? 'add' : 'update'} task.`, 'error');
        }
    };

    const handleDeleteTask = async (taskId) => {
        if (window.confirm('Are you sure you want to delete this task?')) {
            const accessToken = await getAccessToken();
            const success = await deleteTaskFromSharePoint(taskId, accessToken, tasksListId);
            if (success) {
                setTasksData(prevTasks => prevTasks.filter(task => task.id !== taskId));
                showNotification('Task deleted successfully!', 'success');
                handleCloseTaskModal();
            } else {
                showNotification('Failed to delete task.', 'error');
            }
        }
    };

    const handleCloseTaskModal = () => {
        setShowTaskModal(false);
        setEditingTask(null);
    };

    const days = [];
    const weekEnd = getWeekEnd(currentWeekStart);
    for (let d = new Date(currentWeekStart); d <= weekEnd; d.setDate(d.getDate() + 1)) {
        days.push(new Date(d));
    }

    const tasksByAssignee = groupTasksByAssignee(tasksData, MOCK_AD_USERS);

    return (
        <div className="tab-pane fade show active" id="todos-panel" role="tabpanel" aria-labelledby="tab-todos">
            <div className="planner-header d-flex flex-column flex-md-row justify-content-between align-items-center mb-3">
                <div className="d-flex align-items-center mb-2 mb-md-0">
                    <button className="btn btn-outline-secondary btn-sm me-2" onClick={() => navigateWeek(-1)}>
                        <ChevronLeft size={16} />
                    </button>
                    <h4 className="mb-0 mx-2">{formatMonthYear(currentWeekStart)}</h4>
                    <button className="btn btn-outline-secondary btn-sm me-2" onClick={() => navigateWeek(1)}>
                        <ChevronRight size={16} />
                    </button>
                    <button className="btn btn-secondary btn-sm" onClick={goToToday}>Today</button>
                </div>

                <div className="d-flex align-items-center">
                    <div className="dropdown me-2">
                        <button className="btn btn-outline-secondary dropdown-toggle btn-sm" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <Download size={14} className="me-1" /> Export
                        </button>
                        <ul className="dropdown-menu">
                            <li><button className="dropdown-item" onClick={() => showNotification('Export Excel', 'info')}>
                                <FileText size={14} className="me-1" /> Excel (.xlsx)
                            </button></li>
                            <li><button className="dropdown-item" onClick={() => showNotification('Export CSV', 'info')}>
                                <File size={14} className="me-1" /> CSV (.csv)
                            </button></li>
                        </ul>
                    </div>
                </div>
            </div>

            <div className="quick-add card p-3 mb-3">
                <div className="d-flex align-items-center gap-2">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="What needs to be done?"
                        value={quickAddInput}
                        onChange={(e) => setQuickAddInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && quickAddTask()}
                    />
                    <select
                        className="form-select"
                        value={quickAddAssignee}
                        onChange={(e) => setQuickAddAssignee(e.target.value)}
                    >
                        <option value="">Assign to...</option>
                        {MOCK_AD_USERS.filter(u => u.displayName !== 'Unassigned').map(user => (
                            <option key={user.displayName} value={user.displayName}>{user.displayName}</option>
                        ))}
                    </select>
                    <button className="btn btn-primary" onClick={quickAddTask}>
                        <Plus size={16} className="me-1" /> Add
                    </button>
                </div>
            </div>

            <div className="planner-grid row flex-nowrap overflow-auto pb-3">
                {days.map(day => {
                    const dayTasks = tasksData.filter(task => {
                        if (!task.fields.DueDate) return false;
                        const dueDate = new Date(task.fields.DueDate);
                        return dueDate.toDateString() === day.toDateString();
                    });
                    return (
                        <div key={day.toDateString()} className="col-md-3 col-lg-2 col-xl-2" style={{ minWidth: '220px' }}>
                            <div className="card">
                                <div className="card-header text-center">
                                    <h6 className="mb-0">{formatDisplayDate(day)}</h6>
                                </div>
                                <div className="card-body">
                                    {dayTasks.length === 0 ? (
                                        <p className="text-muted fst-italic text-center">No tasks</p>
                                    ) : (
                                        dayTasks.map(task => (
                                            <div key={task.id} className={`card mb-2 task-card ${getDueClass(task.fields.DueDate, task.fields.Status)}`}>
                                                <div className="card-body p-2">
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="form-check">
                                                            <input
                                                                className="form-check-input"
                                                                type="checkbox"
                                                                checked={task.fields.Status === 'Completed'}
                                                                onChange={() => toggleTaskStatus(task.id, task.fields.Status)}
                                                                id={`task-${task.id}`}
                                                            />
                                                            <label className="form-check-label" htmlFor={`task-${task.id}`}>
                                                                {task.fields.Title}
                                                            </label>
                                                        </div>
                                                        <div className="dropdown">
                                                            <button className="btn btn-sm btn-light p-0" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                                                <Edit size={14} />
                                                            </button>
                                                            <ul className="dropdown-menu">
                                                                <li><button className="dropdown-item" onClick={() => openTaskDetail(task)}>
                                                                    <Edit size={14} className="me-1" /> Edit
                                                                </button></li>
                                                                <li><button className="dropdown-item text-danger" onClick={() => deleteTask(task.id)}>
                                                                    <Trash2 size={14} className="me-1" /> Delete
                                                                </button></li>
                                                            </ul>
                                                        </div>
                                                    </div>
                                                    <small className="text-muted d-block mt-1">
                                                        {task.fields.AssignedTo && <span><User size={12} className="me-1" />{task.fields.AssignedTo}</span>}
                                                        {task.fields.ProjectName && <span className="ms-2"><Folder size={12} className="me-1" />{task.fields.ProjectName}</span>}
                                                    </small>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            <h4 className="mt-4 mb-3">Tasks by Assignee</h4>
            <div className="assignee-sections">
                {tasksByAssignee.map(assigneeGroup => {
                    const stats = calculateTaskStats(assigneeGroup.tasks);
                    if (assigneeGroup.tasks.length === 0) return null; // Don't render empty sections
                    return (
                        <div key={assigneeGroup.user.displayName} className="card mb-3">
                            <div className="card-header d-flex justify-content-between align-items-center">
                                <h5 className="mb-0">
                                    <User size={18} className="me-2" />
                                    {assigneeGroup.user.displayName}
                                </h5>
                                <div>
                                    <span className="badge bg-primary me-2">{stats.total} Total</span>
                                    <span className="badge bg-success me-2">{stats.completed} Completed</span>
                                    <span className="badge bg-info me-2">{stats.inProgress} In Progress</span>
                                    {stats.overdue > 0 && <span className="badge bg-danger">{stats.overdue} Overdue</span>}
                                </div>
                            </div>
                            <div className="card-body">
                                <ul className="list-group list-group-flush">
                                    {assigneeGroup.tasks.map(task => (
                                        <li key={task.id} className={`list-group-item d-flex justify-content-between align-items-center ${getDueClass(task.fields.DueDate, task.fields.Status)}`}>
                                            <div className="form-check">
                                                <input
                                                    className="form-check-input"
                                                    type="checkbox"
                                                    checked={task.fields.Status === 'Completed'}
                                                    onChange={() => toggleTaskStatus(task.id, task.fields.Status)}
                                                    id={`assignee-task-${task.id}`}
                                                />
                                                <label className="form-check-label" htmlFor={`assignee-task-${task.id}`}>
                                                    {task.fields.Title}
                                                </label>
                                            </div>
                                            <div>
                                                {task.fields.ProjectName && <span className="badge bg-light text-dark me-2">{task.fields.ProjectName}</span>}
                                                {task.fields.DueDate && <span className="badge bg-secondary">{formatDate(task.fields.DueDate)}</span>}
                                                <button className="btn btn-sm btn-light ms-2" onClick={() => openTaskDetail(task)}>
                                                    <Edit size={14} />
                                                </button>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    );
                })}
            </div>

            <TaskModal
                show={showTaskModal}
                onClose={handleCloseTaskModal}
                onSave={handleSaveTask}
                onDelete={handleDeleteTask}
                initialTask={editingTask}
                employees={MOCK_AD_USERS} // adUsers should come from a central place
                projects={[]} // projectsData should be passed from App.js or loaded here
                tickets={[]} // ticketsData should be passed from App.js or loaded here
            />
        </div>
    );
}

export default TodoList;