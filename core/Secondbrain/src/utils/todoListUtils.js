import { CONFIG as APP_CONFIG } from '../config';
import { fetchWithRetry } from './timeReportsUtils';

// Local console-based notification for utility functions
function showNotification(message, type = 'info', duration = 5000) {
    console.log(`Notification (${type}): ${message}`);
}

// Utility functions for TodoList component

// Helper to get the start of the week (Sunday)
export function getWeekStart(date) {
    const d = new Date(date);
    d.setDate(d.getDate() - d.getDay()); // Go to Sunday
    d.setHours(0, 0, 0, 0);
    return d;
}

// Helper to get the end of the week (Saturday)
export function getWeekEnd(date) {
    const d = new Date(date);
    d.setDate(d.getDate() - d.getDay() + 6); // Go to Saturday
    d.setHours(23, 59, 59, 999);
    return d;
}

// Helper to format dates for display
export function formatDisplayDate(date) {
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

export function formatMonthYear(date) {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

// Assignee sections for rendering the planner
export function groupTasksByAssignee(tasks, users) {
    const grouped = {};
    users.forEach(user => {
        grouped[user.displayName] = {
            user: user,
            tasks: []
        };
    });

    tasks.forEach(task => {
        const assignee = task.fields.AssignedTo || 'Unassigned';
        if (!grouped[assignee]) {
            grouped[assignee] = {
                user: { displayName: assignee, mail: '' },
                tasks: []
            };
        }
        grouped[assignee].tasks.push(task);
    });

    return Object.values(grouped).sort((a, b) => {
        if (a.user.displayName === 'Unassigned') return 1;
        if (b.user.displayName === 'Unassigned') return -1;
        return a.user.displayName.localeCompare(b.user.displayName);
    });
}

// Determine CSS class for due date styling
export function getDueClass(dueDate, status) {
    if (status === 'Completed' || status === 'Resolved' || status === 'Closed') {
        return 'task-completed';
    }
    if (!dueDate) return '';

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const due = new Date(dueDate);
    due.setHours(0, 0, 0, 0);

    if (due < today) {
        return 'task-overdue';
    } else if (due.getTime() === today.getTime()) {
        return 'task-due-today';
    } else if (due.getTime() - today.getTime() < 7 * 24 * 60 * 60 * 1000) { // Within 7 days
        return 'task-due-soon';
    }
    return '';
}

// Function to calculate tasks stats
export function calculateTaskStats(tasks) {
    const total = tasks.length;
    const completed = tasks.filter(task => ['Completed', 'Resolved', 'Closed'].includes(task.fields.Status)).length;
    const inProgress = tasks.filter(task => task.fields.Status === 'In Progress').length;
    const overdue = tasks.filter(task => {
        const dueClass = getDueClass(task.fields.DueDate, task.fields.Status);
        return dueClass === 'task-overdue';
    }).length;

    return { total, completed, inProgress, overdue };
}

// Simplified SharePoint interaction functions (will be called from component via context/props)
// These functions will need actual SharePoint API logic when implemented fully.

export async function loadTasksFromSharePoint(accessToken, tasksListId) {
    if (!tasksListId) {
        showNotification('Tasks list not configured.', 'warning');
        return [];
    }

    try {
        let allItems = [];
        let nextLink = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${tasksListId}/items?expand=fields&$top=200`;

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
                Title: item.fields.Title || '',
                Status: item.fields.Status || 'Not Started',
                Priority: item.fields.Priority || 'Medium',
                AssignedTo: item.fields.AssignedTo || 'Unassigned',
                DueDate: item.fields.DueDate ? item.fields.DueDate.split('T')[0] : null,
                ProjectName: item.fields.ProjectName || '',
                ProjectId: item.fields.ProjectId || null,
                TicketId: item.fields.TicketId || null,
            },
            createdDateTime: item.createdDateTime,
            lastModifiedDateTime: item.lastModifiedDateTime
        }));
    } catch (error) {
        console.error('Error loading tasks from SharePoint:', error);
        showNotification('Failed to load tasks from SharePoint.', 'error');
        return [];
    }
}

export async function saveTaskToSharePoint(task, accessToken, tasksListId, isNew = false) {
    if (!tasksListId) {
        showNotification('SharePoint Tasks list not configured. Cannot save.', 'warning');
        return false;
    }

    try {
        const data = {
            fields: {
                Title: task.fields.Title,
                Status: task.fields.Status,
                Priority: task.fields.Priority,
                AssignedTo: task.fields.AssignedTo,
                DueDate: task.fields.DueDate,
                ProjectName: task.fields.ProjectName,
                ProjectId: task.fields.ProjectId,
                TicketId: task.fields.TicketId,
            }
        };

        let response;
        let url;

        if (isNew || !task.sharePointId) {
            url = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${tasksListId}/items`;
            response = await fetchWithRetry(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        } else {
            url = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${tasksListId}/items/${task.sharePointId}`;
            const headers = {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            };
            if (task.etag) {
                headers['If-Match'] = task.etag;
            }
            response = await fetchWithRetry(url, {
                method: 'PATCH',
                headers,
                body: JSON.stringify(data)
            });
        }

        if (response.status === 412) {
            showNotification('This task was modified by someone else. Please refresh and try again.', 'error');
            return false;
        }

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`SharePoint API error: ${response.status} - ${errorText}`);
        }

        const savedItem = await response.json();
        task.sharePointId = savedItem.id;
        task.id = String(savedItem.id);
        task.etag = savedItem['@odata.etag'] || null;
        task.lastModifiedDateTime = savedItem.lastModifiedDateTime;
        if (isNew) task.createdDateTime = savedItem.createdDateTime;

        showNotification(`Task ${isNew ? 'created' : 'updated'} in SharePoint: ${savedItem.id}`, 'success');
        return true;
    } catch (error) {
        console.error('Error saving task to SharePoint:', error);
        showNotification('Failed to save task.', 'error');
        return false;
    }
}

export async function deleteTaskFromSharePoint(taskId, accessToken, tasksListId) {
    if (!tasksListId || !taskId) {
        showNotification('SharePoint Tasks list not configured or task ID missing. Cannot delete.', 'warning');
        return false;
    }

    try {
        const url = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${tasksListId}/items/${taskId}`;

        const response = await fetchWithRetry(url, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        if (!response.ok && response.status !== 404) {
            throw new Error(`SharePoint API error: ${response.status}`);
        }

        showNotification('Task deleted from SharePoint.', 'success');
        return true;
    } catch (error) {
        console.error('Error deleting task from SharePoint:', error);
        showNotification('Failed to delete task.', 'error');
        return false;
    }
}
