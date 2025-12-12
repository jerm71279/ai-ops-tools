import { CONFIG as APP_CONFIG } from '../config';
import { fetchWithRetry, discoverList, createList } from './timeReportsUtils';

// Column definitions for SharePoint Lists
export const PROJECTS_COLUMNS = [
    { name: "ProjectName", displayName: "Project Name", text: { maxLength: 255 } },
    { name: "Description", displayName: "Description", text: { allowMultipleLines: true, maxLength: 5000 } },
    { name: "Status", displayName: "Status", choice: { choices: ["Not Started", "In Progress", "On Hold", "Completed", "Archived"], displayAs: "dropDownMenu" } },
    { name: "Priority", displayName: "Priority", choice: { choices: ["Low", "Medium", "High", "Critical"], displayAs: "dropDownMenu" } },
    { name: "AssignedTo", displayName: "Assigned To", text: { maxLength: 255 } },
    { name: "Customer", displayName: "Customer", text: { maxLength: 255 } },
    { name: "DueDate", displayName: "Due Date", dateTime: { format: "dateOnly" } },
    { name: "StartDate", displayName: "Start Date", dateTime: { format: "dateOnly" } },
    { name: "EndDate", displayName: "End Date", dateTime: { format: "dateOnly" } },
    { name: "PercentComplete", displayName: "Percent Complete", number: { decimalPlaces: "zero", minimum: 0, maximum: 100 } },
    { name: "BudgetHours", displayName: "Budget Hours", number: { decimalPlaces: "two", minimum: 0 } },
    { name: "HoursSpent", displayName: "Hours Spent", number: { decimalPlaces: "two", minimum: 0 } },
    { name: "SOW", displayName: "SOW", text: { allowMultipleLines: true, maxLength: 5000 } },
];

export const TICKETS_COLUMNS = [
    { name: "TicketTitle", displayName: "Ticket Title", text: { maxLength: 255 } },
    { name: "Description", displayName: "Description", text: { allowMultipleLines: true, maxLength: 5000 } },
    { name: "Status", displayName: "Status", choice: { choices: ["Open", "In Progress", "On Hold", "Pending", "Resolved", "Closed"], displayAs: "dropDownMenu" } },
    { name: "Priority", displayName: "Priority", choice: { choices: ["Low", "Medium", "High", "Critical"], displayAs: "dropDownMenu" } },
    { name: "AssignedTo", displayName: "Assigned To", text: { maxLength: 255 } },
    { name: "Customer", displayName: "Customer", text: { maxLength: 255 } },
    { name: "DueDate", displayName: "Due Date", dateTime: { format: "dateOnly" } },
    { name: "Source", displayName: "Source", choice: { choices: ["Portal", "Email", "Phone", "Teams", "Internal", "Other"], displayAs: "dropDownMenu" } },
    { name: "SLAStatus", displayName: "SLA Status", choice: { choices: ["N/A", "On Track", "At Risk", "Breached"], displayAs: "dropDownMenu" } },
    { name: "TimeSpent", displayName: "Time Spent", text: { maxLength: 50 } }, // e.g., "5h 30m"
    { name: "ResolutionNotes", displayName: "Resolution Notes", text: { allowMultipleLines: true, maxLength: 5000 } },
    { name: "ProjectId", displayName: "Project ID", text: { maxLength: 255 } }, // Link to project
    { name: "ProjectName", displayName: "Project Name", text: { maxLength: 255 } },
];


export async function loadProjectsFromSharePoint(accessToken, siteId, projectsListId, showNotification) {
    if (!projectsListId) {
        showNotification('Projects list not configured.', 'warning');
        return [];
    }

    try {
        let allItems = [];
        let nextLink = `${APP_CONFIG.GRAPH_API}/sites/${siteId}/lists/${projectsListId}/items?expand=fields&$top=200`;

        while (nextLink) {
            const response = await fetchWithRetry(
                nextLink,
                { headers: { 'Authorization': `Bearer ${accessToken}` } }
            );

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`SharePoint API error: ${response.status} - ${errorText}`);
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
                ProjectName: item.fields.Title, // Assuming 'Title' field is used for ProjectName
                Description: item.fields.Description || '',
                Status: item.fields.Status || 'Not Started',
                Priority: item.fields.Priority || 'Medium',
                AssignedTo: item.fields.AssignedTo || 'Unassigned',
                Customer: item.fields.Customer || '',
                DueDate: item.fields.DueDate ? item.fields.DueDate.split('T')[0] : null,
                StartDate: item.fields.StartDate ? item.fields.StartDate.split('T')[0] : null,
                EndDate: item.fields.EndDate ? item.fields.EndDate.split('T')[0] : null,
                PercentComplete: item.fields.PercentComplete || 0,
                BudgetHours: item.fields.BudgetHours || 0,
                HoursSpent: item.fields.HoursSpent || 0,
                SOW: item.fields.SOW || '',
            },
            createdDateTime: item.createdDateTime,
            lastModifiedDateTime: item.lastModifiedDateTime
        }));
    } catch (error) {
        console.error('Error loading projects from SharePoint:', error);
        showNotification('Failed to load projects from SharePoint.', 'error');
        return [];
    }
}

export async function loadTicketsFromSharePoint(accessToken, siteId, ticketsListId, showNotification) {
    if (!ticketsListId) {
        showNotification('Tickets list not configured.', 'warning');
        return [];
    }

    try {
        let allItems = [];
        let nextLink = `${APP_CONFIG.GRAPH_API}/sites/${siteId}/lists/${ticketsListId}/items?expand=fields&$top=200`;

        while (nextLink) {
            const response = await fetchWithRetry(
                nextLink,
                { headers: { 'Authorization': `Bearer ${accessToken}` } }
            );

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`SharePoint API error: ${response.status} - ${errorText}`);
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
                TicketTitle: item.fields.Title, // Assuming 'Title' field is used for TicketTitle
                Description: item.fields.Description || '',
                Status: item.fields.Status || 'Open',
                Priority: item.fields.Priority || 'Medium',
                AssignedTo: item.fields.AssignedTo || 'Unassigned',
                Customer: item.fields.Customer || '',
                DueDate: item.fields.DueDate ? item.fields.DueDate.split('T')[0] : null,
                Source: item.fields.Source || 'Portal',
                SLAStatus: item.fields.SLAStatus || 'N/A',
                TimeSpent: item.fields.TimeSpent || '0h',
                ResolutionNotes: item.fields.ResolutionNotes || '',
                ProjectId: item.fields.ProjectId || null,
                ProjectName: item.fields.ProjectName || '',
            },
            createdDateTime: item.createdDateTime,
            lastModifiedDateTime: item.lastModifiedDateTime
        }));
    } catch (error) {
        console.error('Error loading tickets from SharePoint:', error);
        showNotification('Failed to load tickets from SharePoint.', 'error');
        return [];
    }
}

// Helper to get status color class
export function getStatusColor(status) {
    switch (status) {
        case 'Completed':
        case 'Resolved':
            return 'bg-success';
        case 'In Progress':
        case 'Open':
            return 'bg-info';
        case 'On Hold':
        case 'Pending':
            return 'bg-warning text-dark';
        case 'Not Started':
            return 'bg-secondary';
        case 'Archived':
        case 'Closed':
            return 'bg-dark';
        default:
            return 'bg-light text-dark';
    }
}

// Helper to get priority color class
export function getPriorityColor(priority) {
    switch (priority) {
        case 'Critical':
            return 'text-danger';
        case 'High':
            return 'text-warning';
        case 'Medium':
            return 'text-info';
        case 'Low':
            return 'text-success';
        default:
            return 'text-muted';
    }
}

// Placeholder for project progress calculation (will need tasks data)
export function calculateProjectProgress(project, tasks) {
    // This function will need to be properly implemented using tasks linked to the project
    return project.fields.PercentComplete || 0;
}

export async function saveProjectToSharePoint(project, accessToken, projectsListId, isNew = false, showNotification) {
    if (!projectsListId) {
        showNotification('SharePoint Projects list not configured. Cannot save.', 'warning');
        return false;
    }

    try {
        const data = {
            fields: {
                Title: project.fields.ProjectName,
                Description: project.fields.Description,
                Status: project.fields.Status,
                Priority: project.fields.Priority,
                AssignedTo: project.fields.AssignedTo,
                Customer: project.fields.Customer,
                DueDate: project.fields.DueDate,
                StartDate: project.fields.StartDate,
                EndDate: project.fields.EndDate,
                PercentComplete: project.fields.PercentComplete,
                BudgetHours: project.fields.BudgetHours,
                HoursSpent: project.fields.HoursSpent,
                SOW: project.fields.SOW,
            }
        };

        let response;
        let url;

        if (isNew || !project.sharePointId) {
            url = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${projectsListId}/items`;
            response = await fetchWithRetry(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        } else {
            url = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${projectsListId}/items/${project.sharePointId}`;
            const headers = {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            };
            if (project.etag) {
                headers['If-Match'] = project.etag;
            }
            response = await fetchWithRetry(url, {
                method: 'PATCH',
                headers,
                body: JSON.stringify(data)
            });
        }

        if (response.status === 412) {
            showNotification('This project was modified by someone else. Please refresh and try again.', 'error');
            return false;
        }

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`SharePoint API error: ${response.status} - ${errorText}`);
        }

        const savedItem = await response.json();
        project.sharePointId = savedItem.id;
        project.id = String(savedItem.id);
        project.etag = savedItem['@odata.etag'] || null;
        project.lastModifiedDateTime = savedItem.lastModifiedDateTime;
        if (isNew) project.createdDateTime = savedItem.createdDateTime;

        showNotification(`Project ${isNew ? 'created' : 'updated'} in SharePoint: ${savedItem.id}`, 'success');
        return true;
    } catch (error) {
        console.error('Error saving project to SharePoint:', error);
        showNotification('Failed to save project.', 'error');
        return false;
    }
}

export async function deleteProjectFromSharePoint(sharePointId, accessToken, projectsListId, showNotification) {
    if (!projectsListId || !sharePointId) {
        showNotification('SharePoint Projects list not configured or project ID missing. Cannot delete.', 'warning');
        return false;
    }

    try {
        const url = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${projectsListId}/items/${sharePointId}`;

        const response = await fetchWithRetry(url, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        if (!response.ok && response.status !== 404) {
            throw new Error(`SharePoint API error: ${response.status}`);
        }

        showNotification('Project deleted from SharePoint.', 'success');
        return true;
    } catch (error) {
        console.error('Error deleting project from SharePoint:', error);
        showNotification('Failed to delete project.', 'error');
        return false;
    }
}