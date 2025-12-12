import { CONFIG as APP_CONFIG } from '../config';
import { fetchWithRetry, discoverList, createList } from './timeReportsUtils';

// Local console-based notification for utility functions
function showNotification(message, type = 'info', duration = 5000) {
    console.log(`Notification (${type}): ${message}`);
}

// Helper to get the number of days in a month
export function getDaysInMonth(year, month) {
    return new Date(year, month + 1, 0).getDate();
}

// Helper to get the first day of the month (0 for Sunday, 1 for Monday, etc.)
export function getFirstDayOfMonth(year, month) {
    return new Date(year, month, 1).getDay();
}

// Helper to format dates for display
export function formatCalendarDate(date) {
    return date.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
}

export function formatMonthYearHeader(date) {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

// Determine event color based on type
export function getEventColor(type) {
    switch (type) {
        case 'project': return 'bg-primary';
        case 'ticket': return 'bg-warning text-dark';
        case 'task': return 'bg-success';
        case 'meeting': return 'bg-info';
        default: return 'bg-secondary';
    }
}

// Determine event icon based on type
export function getEventIcon(type) {
    switch (type) {
        case 'project': return 'folder';
        case 'ticket': return 'alert-triangle';
        case 'task': return 'check-square';
        case 'meeting': return 'users';
        default: return 'circle';
    }
}

// Function to filter events for a specific day
export function getEventsForDay(date, allProjects, allTickets, allTasks) {
    const dayEvents = [];
    const dateString = date.toISOString().split('T')[0];

    // Projects (using DueDate or EndDate)
    allProjects.forEach(p => {
        if (p.fields.DueDate === dateString || p.fields.EndDate === dateString) {
            dayEvents.push({
                id: `project-${p.id}`,
                type: 'project',
                title: p.fields.ProjectName,
                item: p
            });
        }
    });

    // Tickets (using DueDate)
    allTickets.forEach(t => {
        if (t.fields.DueDate === dateString) {
            dayEvents.push({
                id: `ticket-${t.id}`,
                type: 'ticket',
                title: t.fields.TicketTitle,
                item: t
            });
        }
    });

    // Tasks (using DueDate)
    allTasks.forEach(t => {
        if (t.fields.DueDate === dateString) {
            dayEvents.push({
                id: `task-${t.id}`,
                type: 'task',
                title: t.fields.Title,
                item: t
            });
        }
    });

    return dayEvents;
}

// Simplified SharePoint interaction functions
export async function loadCalendarDataFromSharePoint(accessToken, siteId) {
    if (!siteId) {
        showNotification('SharePoint Site ID not configured.', 'warning');
        return { projects: [], tickets: [], tasks: [] };
    }

    try {
        const projectsListId = await discoverList(accessToken, siteId, 'Projects');
        const ticketsListId = await discoverList(accessToken, siteId, 'Tickets');
        const tasksListId = await discoverList(accessToken, siteId, 'Tasks');

        const projectsPromise = projectsListId ? loadProjectsDataFromSharePoint(accessToken, projectsListId) : Promise.resolve([]);
        const ticketsPromise = ticketsListId ? loadTicketsDataFromSharePoint(accessToken, ticketsListId) : Promise.resolve([]);
        const tasksPromise = tasksListId ? loadTasksDataFromSharePoint(accessToken, tasksListId) : Promise.resolve([]);

        const [projects, tickets, tasks] = await Promise.all([
            projectsPromise,
            ticketsPromise,
            tasksPromise
        ]);

        return { projects, tickets, tasks };
    } catch (error) {
        console.error('Error loading calendar data from SharePoint:', error);
        showNotification('Failed to load calendar data from SharePoint.', 'error');
        return { projects: [], tickets: [], tasks: [] };
    }
}

// Placeholder functions for loading specific list data
async function loadProjectsDataFromSharePoint(accessToken, listId) {
    let allItems = [];
    let nextLink = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${listId}/items?expand=fields&$top=200`;
    while (nextLink) {
        const response = await fetchWithRetry(nextLink, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (!response.ok) throw new Error(`SharePoint API error: ${response.status}`);
        const data = await response.json();
        allItems = allItems.concat(data.value || []);
        nextLink = data['@odata.nextLink'] || null;
    }
    return allItems.map(item => ({
        id: String(item.id),
        fields: {
            ProjectName: item.fields.Title, // Assuming Title is ProjectName
            DueDate: item.fields.DueDate ? item.fields.DueDate.split('T')[0] : null,
            EndDate: item.fields.EndDate ? item.fields.EndDate.split('T')[0] : null,
        }
    }));
}

async function loadTicketsDataFromSharePoint(accessToken, listId) {
    let allItems = [];
    let nextLink = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${listId}/items?expand=fields&$top=200`;
    while (nextLink) {
        const response = await fetchWithRetry(nextLink, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (!response.ok) throw new Error(`SharePoint API error: ${response.status}`);
        const data = await response.json();
        allItems = allItems.concat(data.value || []);
        nextLink = data['@odata.nextLink'] || null;
    }
    return allItems.map(item => ({
        id: String(item.id),
        fields: {
            TicketTitle: item.fields.Title, // Assuming Title is TicketTitle
            DueDate: item.fields.DueDate ? item.fields.DueDate.split('T')[0] : null,
        }
    }));
}

async function loadTasksDataFromSharePoint(accessToken, listId) {
    let allItems = [];
    let nextLink = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${listId}/items?expand=fields&$top=200`;
    while (nextLink) {
        const response = await fetchWithRetry(nextLink, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (!response.ok) throw new Error(`SharePoint API error: ${response.status}`);
        const data = await response.json();
        allItems = allItems.concat(data.value || []);
        nextLink = data['@odata.nextLink'] || null;
    }
    return allItems.map(item => ({
        id: String(item.id),
        fields: {
            Title: item.fields.Title,
            DueDate: item.fields.DueDate ? item.fields.DueDate.split('T')[0] : null,
        }
    }));
}
