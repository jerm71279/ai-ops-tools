import React, { useState, useEffect } from 'react';
import { Search, List, Columns, Download, Plus, Folder, AlertTriangle, CheckCircle, Sliders, RefreshCcw, Edit2, User, X, CloudOff } from 'react-feather';
import { getAccessToken, msalInstance } from '../auth'; // Added msalInstance
import { discoverList, createList } from '../utils/timeReportsUtils'; // Reusing common utils
import { CONFIG as APP_CONFIG } from '../config'; // Import central config
import {
    loadProjectsFromSharePoint,
    loadTicketsFromSharePoint,
    PROJECTS_COLUMNS,
    TICKETS_COLUMNS,
    getStatusColor,
    getPriorityColor,
    calculateProjectProgress,
    saveProjectToSharePoint, // Imported saveProjectToSharePoint
    deleteProjectFromSharePoint // Imported deleteProjectFromSharePoint
} from '../utils/projectsUtils';
import ProjectModal from './modals/ProjectModal';
import { useNotification } from '../contexts/NotificationContext'; // Import useNotification hook

function Projects() {
    const { showNotification } = useNotification(); // Get showNotification from context

    const [projectsData, setProjectsData] = useState([]);
    const [ticketsData, setTicketsData] = useState([]); // Needed for project progress calculation
    const [projectSearchInput, setProjectSearchInput] = useState('');
    const [projectStatusFilter, setProjectStatusFilter] = useState('');
    const [projectPriorityFilter, setProjectPriorityFilter] = useState('');
    const [projectShowArchived, setProjectShowArchived] = useState(false);
    const [currentView, setCurrentView] = useState('cards'); // 'cards' or 'kanban'

    const [showProjectModal, setShowProjectModal] = useState(false);
    const [editingProject, setEditingProject] = useState(null);

    useEffect(() => {
        const initProjectsData = async () => {
            const accounts = msalInstance.getAllAccounts();
            if (accounts.length === 0) {
                return;
            }
            const accessToken = await getAccessToken();

            // Discover or create Projects list
            let projectsListId = await discoverList(accessToken, APP_CONFIG.siteId, 'Projects', showNotification);
            if (!projectsListId) {
                projectsListId = await createList(accessToken, APP_CONFIG.siteId, 'Projects', 'Project tracking items', PROJECTS_COLUMNS, showNotification);
            }
            // Discover or create Tickets list
            let ticketsListId = await discoverList(accessToken, APP_CONFIG.siteId, 'Tickets', showNotification);
            if (!ticketsListId) {
                ticketsListId = await createList(accessToken, APP_CONFIG.siteId, 'Tickets', 'Customer support tickets', TICKETS_COLUMNS, showNotification);
            }

            if (projectsListId) {
                const loadedProjects = await loadProjectsFromSharePoint(accessToken, APP_CONFIG.siteId, projectsListId, showNotification);
                setProjectsData(loadedProjects);
            }
            if (ticketsListId) {
                const loadedTickets = await loadTicketsFromSharePoint(accessToken, APP_CONFIG.siteId, ticketsListId, showNotification);
                setTicketsData(loadedTickets);
            }
        };
        initProjectsData();
    }, [showNotification]);

    // Filtered Projects (memoized or derived state)
    const getFilteredProjects = () => {
        const search = projectSearchInput.toLowerCase();
        const status = projectStatusFilter;
        const priority = projectPriorityFilter;
        const showArchived = projectShowArchived;

        return projectsData.filter(project => {
            const f = project.fields;
            const itemStatus = f.Status || 'Not Started';

            // Hide archived unless checkbox is checked or specific status selected
            const ARCHIVED_PROJECT_STATUSES = ['Completed', 'Archived'];
            if (!showArchived && !status && ARCHIVED_PROJECT_STATUSES.includes(itemStatus)) return false;

            if (search && !(f.ProjectName || '').toLowerCase().includes(search) && !(f.Description || '').toLowerCase().includes(search)) return false;
            if (status && itemStatus !== status) return false;
            if (priority && f.Priority !== priority) return false;
            return true;
        });
    };

    const filteredProjects = getFilteredProjects();

    // Calculate summary stats
    const totalProjects = filteredProjects.length;
    const inProgressProjects = filteredProjects.filter(p => p.fields.Status === 'In Progress').length;
    const highPriorityProjects = filteredProjects.filter(p => ['High', 'Critical'].includes(p.fields.Priority)).length;
    const completedProjects = filteredProjects.filter(p => p.fields.Status === 'Completed').length;


    const handleSaveProject = async (project) => {
        const accessToken = await getAccessToken();
        if (!accessToken) {
            showNotification('Not authenticated. Please log in.', 'error');
            return;
        }

        const isNew = !project.sharePointId;
        // Need to get projectListId
        let projectsListId = await discoverList(accessToken, APP_CONFIG.siteId, 'Projects', showNotification);
        if (!projectsListId) {
            projectsListId = await createList(accessToken, APP_CONFIG.siteId, 'Projects', 'Project tracking items', PROJECTS_COLUMNS, showNotification);
        }

        const success = await saveProjectToSharePoint(project, accessToken, projectsListId, isNew, showNotification);

        if (success) {
            if (isNew) {
                setProjectsData(prev => [...prev, project]);
            } else {
                setProjectsData(prev => prev.map(p => p.id === project.id ? project : p));
            }
            showNotification(`Project ${isNew ? 'added' : 'updated'} successfully!`, 'success');
            handleCloseProjectModal();
        } else {
            showNotification(`Failed to ${isNew ? 'add' : 'update'} project.`, 'error');
        }
    };

    const handleCloseProjectModal = () => {
        setShowProjectModal(false);
        setEditingProject(null);
    };

    // Render functions for different views (placeholder for now)
    const renderChatView = () => (
        <div id="projects-chat-view" className="chat-cards-container">
            {filteredProjects.length === 0 ? (
                <div className="empty-state text-center p-5">
                    <Folder size={36} className="text-muted mb-3" />
                    <h3 className="text-dark mb-2">No Projects Found</h3>
                    <p className="text-muted mb-3">Create a new project to get started</p>
                    <button className="btn btn-primary" onClick={() => { setEditingProject(null); setShowProjectModal(true); }}>
                        <Plus size={16} className="me-1" /> Add Project
                    </button>
                </div>
            ) : (
                filteredProjects.map(project => (
                    <div className="card mb-3" key={project.id}>
                        <div className="card-body">
                            <h5 className="card-title">{project.fields.ProjectName}</h5>
                            <p className="card-text">{project.fields.Description}</p>
                            {/* More project details */}
                            <div className="d-flex justify-content-end">
                                <button className="btn btn-sm btn-outline-primary" onClick={() => { setEditingProject(project); setShowProjectModal(true); }}>
                                    <Edit2 size={14} /> Edit
                                </button>
                            </div>
                        </div>
                    </div>
                ))
            )}
        </div>
    );

    const renderKanbanView = () => (
        <div id="projects-kanban-view" className="kanban-board d-flex overflow-auto pb-3">
            {/* Kanban columns */}
            <div className="card me-3" style={{ minWidth: '300px' }}>
                <div className="card-header">Not Started</div>
                <div className="card-body">
                    {/* Projects for this status */}
                    {filteredProjects.filter(p => p.fields.Status === 'Not Started').map(project => (
                        <div className="card mb-2" key={project.id} onClick={() => { setEditingProject(project); setShowProjectModal(true); }}>
                            <div className="card-body p-2">
                                <h6 className="card-title">{project.fields.ProjectName}</h6>
                                <small className="text-muted">{project.fields.Description.substring(0, 50)}...</small>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            {/* Add more columns for In Progress, Completed, etc. */}
            <div className="card me-3" style={{ minWidth: '300px' }}>
                <div className="card-header">In Progress</div>
                <div className="card-body">
                    {/* Projects for this status */}
                    {filteredProjects.filter(p => p.fields.Status === 'In Progress').map(project => (
                        <div className="card mb-2" key={project.id} onClick={() => { setEditingProject(project); setShowProjectModal(true); }}>
                            <div className="card-body p-2">
                                <h6 className="card-title">{project.fields.ProjectName}</h6>
                                <small className="text-muted">{project.fields.Description.substring(0, 50)}...</small>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <div className="card" style={{ minWidth: '300px' }}>
                <div className="card-header">Completed</div>
                <div className="card-body">
                    {/* Projects for this status */}
                    {filteredProjects.filter(p => p.fields.Status === 'Completed').map(project => (
                        <div className="card mb-2" key={project.id} onClick={() => { setEditingProject(project); setShowProjectModal(true); }}>
                            <div className="card-body p-2">
                                <h6 className="card-title">{project.fields.ProjectName}</h6>
                                <small className="text-muted">{project.fields.Description.substring(0, 50)}...</small>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <div className="card" style={{ minWidth: '300px' }}>
                <div className="card-header">On Hold</div>
                <div className="card-body">
                    {/* Projects for this status */}
                    {filteredProjects.filter(p => p.fields.Status === 'On Hold').map(project => (
                        <div className="card mb-2" key={project.id} onClick={() => { setEditingProject(project); setShowProjectModal(true); }}>
                            <div className="card-body p-2">
                                <h6 className="card-title">{project.fields.ProjectName}</h6>
                                <small className="text-muted">{project.fields.Description.substring(0, 50)}...</small>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <div className="card" style={{ minWidth: '300px' }}>
                <div className="card-header">Archived</div>
                <div className="card-body">
                    {/* Projects for this status */}
                    {filteredProjects.filter(p => p.fields.Status === 'Archived').map(project => (
                        <div className="card mb-2" key={project.id} onClick={() => { setEditingProject(project); setShowProjectModal(true); }}>
                            <div className="card-body p-2">
                                <h6 className="card-title">{project.fields.ProjectName}</h6>
                                <small className="text-muted">{project.fields.Description.substring(0, 50)}...</small>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );


    return (
        <div className="tab-pane fade show active" id="projects-panel" role="tabpanel" aria-labelledby="tab-projects">
            <div className="row g-3 mb-3">
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">Total Projects</h6>
                            <p className="card-text fs-5 fw-bold" id="stat-projects-total">{totalProjects}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">In Progress</h6>
                            <p className="card-text fs-5 fw-bold text-info" id="stat-projects-progress">{inProgressProjects}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">High Priority</h6>
                            <p className="card-text fs-5 fw-bold text-danger" id="stat-projects-high">{highPriorityProjects}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body">
                            <h6 className="card-title text-muted">Completed</h6>
                            <p className="card-text fs-5 fw-bold text-success" id="stat-projects-completed">{completedProjects}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="d-flex flex-wrap align-items-center justify-content-between mb-3">
                <div className="d-flex flex-wrap align-items-center gap-2">
                    <div className="input-group">
                        <span className="input-group-text"><Search size={16} /></span>
                        <input
                            type="text"
                            className="form-control"
                            placeholder="Search projects..."
                            value={projectSearchInput}
                            onChange={(e) => setProjectSearchInput(e.target.value)}
                        />
                    </div>
                    <select
                        className="form-select"
                        value={projectStatusFilter}
                        onChange={(e) => setProjectStatusFilter(e.target.value)}
                    >
                        <option value="">Active Only</option>
                        <option value="Not Started">Not Started</option>
                        <option value="In Progress">In Progress</option>
                        <option value="On Hold">On Hold</option>
                        <option value="Completed">Completed</option>
                        <option value="Archived">Archived</option>
                    </select>
                    <select
                        className="form-select"
                        value={projectPriorityFilter}
                        onChange={(e) => setProjectPriorityFilter(e.target.value)}
                    >
                        <option value="">All Priorities</option>
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                        <option value="Critical">Critical</option>
                    </select>
                    <div className="form-check">
                        <input
                            className="form-check-input"
                            type="checkbox"
                            id="projectShowArchived"
                            checked={projectShowArchived}
                            onChange={(e) => setProjectShowArchived(e.target.checked)}
                        />
                        <label className="form-check-label" htmlFor="projectShowArchived">
                            Show Archived
                        </label>
                    </div>
                </div>
                <div className="d-flex align-items-center gap-2">
                    <div className="btn-group">
                        <button
                            className={`btn btn-outline-secondary ${currentView === 'cards' ? 'active' : ''}`}
                            onClick={() => setCurrentView('cards')}
                        >
                            <List size={14} /> Cards
                        </button>
                        <button
                            className={`btn btn-outline-secondary ${currentView === 'kanban' ? 'active' : ''}`}
                            onClick={() => setCurrentView('kanban')}
                        >
                            <Columns size={14} /> Kanban
                        </button>
                    </div>
                    <div className="dropdown">
                        <button className="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <Download size={14} /> Export
                        </button>
                        <ul className="dropdown-menu">
                            <li><button className="dropdown-item" onClick={() => showNotification('Export to Excel', 'info')}>Excel (.xlsx)</button></li>
                            <li><button className="dropdown-item" onClick={() => showNotification('Export to CSV', 'info')}>CSV (.csv)</button></li>
                        </ul>
                    </div>
                    <button className="btn btn-primary" onClick={() => { setEditingProject(null); setShowProjectModal(true); }}>
                        <Plus size={16} /> New Project
                    </button>
                </div>
            </div>

            <div className="scrollable-content">
                {currentView === 'cards' && renderChatView()}
                {currentView === 'kanban' && renderKanbanView()}
            </div>

            <ProjectModal
                show={showProjectModal}
                onClose={handleCloseProjectModal}
                onSave={handleSaveProject}
                initialProject={editingProject}
                // employees={adUsers} // Assuming adUsers will be passed from App.js or loaded here
            />
        </div>
    );
}

export default Projects;