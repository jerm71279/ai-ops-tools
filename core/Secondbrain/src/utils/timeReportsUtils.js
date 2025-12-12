import { CONFIG as APP_CONFIG } from '../config';

// Helper function to escape HTML for security
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

function escapeAttr(text) {
    if (text === null || text === undefined) return '';
    return String(text).replace(/[&<>"']/g, m => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    })[m]);
}

// Toast Notification System (simplified for now, will integrate into React)
function showNotification(message, type = 'info', duration = 5000) {
    console.log(`Notification (${type}): ${message}`);
}

// Sleep utility for retry delays
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Fetch with automatic retry and rate limit handling
export async function fetchWithRetry(url, options = {}, maxRetries = 3, notificationHandler = showNotification) {
    let lastError;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const response = await fetch(url, options);

            // Handle rate limiting (429)
            if (response.status === 429) {
                const retryAfter = parseInt(response.headers.get('Retry-After') || '1', 10);
                const delayMs = Math.min(retryAfter * 1000, 60000); // Max 60 seconds
                notificationHandler('API rate limit reached. Retrying...', 'warning');
                await sleep(delayMs);
                continue;
            }

            // Handle server errors with retry
            if (response.status >= 500 && attempt < maxRetries - 1) {
                const delayMs = Math.pow(2, attempt) * 1000; // Exponential backoff
                await sleep(delayMs);
                continue;
            }

            return response;
        } catch (error) {
            lastError = error;

            // Network errors - retry with exponential backoff
            if (attempt < maxRetries - 1) {
                const delayMs = Math.pow(2, attempt) * 1000;
                await sleep(delayMs);
                continue;
            }
        }
    }

    throw lastError || new Error('Request failed after retries');
}

// Employee billable rates (will be loaded from SharePoint Employees list)
let employeeBillableRates = {
    'Mavrick Faison': 150,
    'Patrick McFarland': 135,
    'Robbie McFarland': 200
};

export function getEmployeeBillableRate(employeeName) {
    return employeeBillableRates[employeeName] || 125; // Default rate
}

// Data loading functions (simplified for now)
export async function loadTimeEntriesFromSharePoint(accessToken, timeEntriesListId, notificationHandler = showNotification) {
    if (!timeEntriesListId) {
        notificationHandler('TimeEntries list not configured.', 'warning');
        return [];
    }

    try {
        let allItems = [];
        let nextLink = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${timeEntriesListId}/items?expand=fields&$top=200`;

        while (nextLink) {
            const response = await fetchWithRetry(
                nextLink,
                { headers: { 'Authorization': `Bearer ${accessToken}` } },
                3, // maxRetries
                notificationHandler // Pass notificationHandler
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
            employee: item.fields.Employee || '',
            date: item.fields.EntryDate ? item.fields.EntryDate.split('T')[0] : '',
            hours: parseFloat(item.fields.Hours) || 0,
            type: item.fields.WorkType || 'Project',
            projectId: item.fields.ProjectId || null,
            projectType: item.fields.ProjectType || null,
            projectName: item.fields.ProjectName || 'General',
            description: item.fields.Description || '',
            billable: item.fields.Billable === true,
            createdAt: item.createdDateTime,
            updatedAt: item.lastModifiedDateTime
        }));
    } catch (error) {
        console.error('Error loading time entries from SharePoint:', error);
        notificationHandler('Failed to load time entries from SharePoint.', 'error');
        return [];
    }
}

export async function saveTimeEntryToSharePoint(entry, accessToken, timeEntriesListId, isNew = false, notificationHandler = showNotification) {
    if (!timeEntriesListId) {
        notificationHandler('SharePoint TimeEntries list not configured. Cannot save.', 'warning');
        return false;
    }

    try {
        const data = {
            fields: {
                Title: `${entry.employee} - ${entry.date}`,
                Employee: entry.employee,
                EntryDate: entry.date,
                Hours: parseFloat(entry.hours),
                WorkType: entry.type,
                ProjectId: entry.projectId || '',
                ProjectType: entry.projectType || '',
                ProjectName: entry.projectName || 'General',
                Description: entry.description || '',
                Billable: entry.billable === true
            }
        };

        let response;
        let url;

        if (isNew || !entry.sharePointId) {
            url = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${timeEntriesListId}/items`;
            response = await fetchWithRetry(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }, 3, notificationHandler); // Pass notificationHandler
        } else {
            url = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${timeEntriesListId}/items/${entry.sharePointId}`;
            const headers = {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            };
            if (entry.etag) {
                headers['If-Match'] = entry.etag;
            }
            response = await fetchWithRetry(url, {
                method: 'PATCH',
                headers,
                body: JSON.stringify(data)
            }, 3, notificationHandler); // Pass notificationHandler
        }

        if (response.status === 412) {
            notificationHandler('This entry was modified by someone else. Please refresh and try again.', 'error');
            return false;
        }

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`SharePoint API error: ${response.status} - ${errorText}`);
        }

        const savedItem = await response.json();
        entry.sharePointId = savedItem.id;
        entry.id = String(savedItem.id);
        entry.etag = savedItem['@odata.etag'] || null;
        entry.updatedAt = savedItem.lastModifiedDateTime;
        if (isNew) entry.createdAt = savedItem.createdDateTime;

        notificationHandler(`Time entry ${isNew ? 'created' : 'updated'} in SharePoint: ${savedItem.id}`, 'success');
        return true;
    } catch (error) {
        console.error('Error saving time entry to SharePoint:', error);
        notificationHandler('Failed to save to SharePoint.', 'error');
        return false;
    }
}

export async function deleteTimeEntryFromSharePoint(sharePointId, accessToken, timeEntriesListId, notificationHandler = showNotification) {
    if (!timeEntriesListId || !sharePointId) {
        notificationHandler('SharePoint TimeEntries list not configured or entry ID missing. Cannot delete.', 'warning');
        return false;
    }

    try {
        const url = `${APP_CONFIG.GRAPH_API}/sites/${APP_CONFIG.siteId}/lists/${timeEntriesListId}/items/${sharePointId}`;

        const response = await fetchWithRetry(url, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${accessToken}` }
        }, 3, notificationHandler); // Pass notificationHandler

        if (!response.ok && response.status !== 404) {
            throw new Error(`SharePoint API error: ${response.status}`);
        }

        notificationHandler('Time entry deleted from SharePoint.', 'success');
        return true;
    } catch (error) {
        console.error('Error deleting time entry from SharePoint:', error);
        notificationHandler('Failed to delete from SharePoint.', 'error');
        return false;
    }
}

export async function discoverList(accessToken, siteId, targetListName, notificationHandler = showNotification) {
    try {
        const response = await fetchWithRetry(
            `${APP_CONFIG.GRAPH_API}/sites/${siteId}/lists`,
            { headers: { 'Authorization': `Bearer ${accessToken}` } },
            3, // maxRetries
            notificationHandler // Pass notificationHandler
        );

        if (!response.ok) {
            throw new Error(`Failed to fetch lists: ${response.status}`);
        }

        const data = await response.json();
        const lists = data.value || [];

        for (const list of lists) {
            const name = list.displayName.toLowerCase();
            if (name === targetListName.toLowerCase() || name === targetListName.toLowerCase().replace(/entries/g, ' entries')) { // Handle "timeentries" vs "time entries"
                return list.id;
            }
        }
        return null;
    } catch (error) {
        console.error(`Error discovering ${targetListName} list:`, error);
        notificationHandler(`Error discovering SharePoint ${targetListName} list.`, 'error');
        return null;
    }
}

export async function createList(accessToken, siteId, listName, description, columns, notificationHandler = showNotification) {
    try {
        const listData = {
            displayName: listName,
            description: description,
            list: { template: "genericList" }
        };

        const listResponse = await fetchWithRetry(
            `${APP_CONFIG.GRAPH_API}/sites/${siteId}/lists`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(listData)
            }, 3, notificationHandler); // Pass notificationHandler

        if (!listResponse.ok) {
            const errorText = await listResponse.text();
            throw new Error(`Failed to create ${listName} list: ${errorText}`);
        }

        const newList = await listResponse.json();

        for (const col of columns) {
            try {
                await fetchWithRetry(
                    `${APP_CONFIG.GRAPH_API}/sites/${siteId}/lists/${newList.id}/columns`,
                    {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(col)
                    }, 3, notificationHandler); // Pass notificationHandler
            } catch (colError) {
                console.warn(`Could not add column ${col.displayName} to ${listName}:`, colError);
            }
        }

        notificationHandler(`${listName} list created in SharePoint!`, 'success');
        return newList.id;
    } catch (error) {
        console.error(`Error creating ${listName} list:`, error);
        notificationHandler(`Error creating ${listName} list.`, 'error');
        return null;
    }
}

export function formatDate(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Function to get initials (moved from Header.js for reusability if needed elsewhere)
export function getInitials(name) {
    if (!name || name === 'Unassigned') return '?';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
}

export const TIME_ENTRIES_COLUMNS = [
    { name: "Employee", displayName: "Employee", text: { maxLength: 255 } },
    { name: "EntryDate", displayName: "Entry Date", dateTime: { format: "dateOnly" } },
    { name: "Hours", displayName: "Hours", number: { decimalPlaces: "two", minimum: 0, maximum: 24 } },
    { name: "WorkType", displayName: "Work Type", choice: { choices: ["Project", "Ticket", "Meeting", "Admin", "Training", "Other"], displayAs: "dropDownMenu" } },
    { name: "ProjectId", displayName: "Project ID", text: { maxLength: 255 } },
    { name: "ProjectType", displayName: "Project Type", choice: { choices: ["project", "ticket"], displayAs: "dropDownMenu" } },
    { name: "ProjectName", displayName: "Project Name", text: { maxLength: 255 } },
    { name: "Description", displayName: "Description", text: { allowMultipleLines: true, maxLength: 5000 } },
    { name: "Billable", displayName: "Billable", boolean: {} }
];
