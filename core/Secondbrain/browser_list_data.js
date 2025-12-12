/**
 * Browser Console Script - List SharePoint Data
 *
 * HOW TO USE:
 * 1. Open https://jolly-island-06ade710f.3.azurestaticapps.net in your browser
 * 2. Log in with your Azure AD account
 * 3. Open Developer Tools (F12) → Console tab
 * 4. Copy and paste this entire script
 * 5. Press Enter to run
 */

(async function listSharePointData() {
    const SITE_ID = 'oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef';
    const GRAPH_API = 'https://graph.microsoft.com/v1.0';

    console.log('📊 SharePoint Data Reader');
    console.log('='.repeat(60));

    // Get token
    let token;
    try {
        const result = await msalInstance.acquireTokenSilent({
            scopes: ["https://graph.microsoft.com/Sites.ReadWrite.All"]
        });
        token = result.accessToken;
        console.log('✅ Token acquired');
    } catch (e) {
        console.error('❌ Failed to get token. Are you logged in?', e);
        return;
    }

    // Fetch function
    async function fetchGraph(url) {
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.json();
    }

    // Get lists
    console.log('\n📋 Discovering Lists...');
    const listsData = await fetchGraph(`${GRAPH_API}/sites/${SITE_ID}/lists`);
    const lists = listsData.value || [];

    if (lists.length === 0) {
        console.log('⚠️ No lists found. Lists will be created when you use the app.');
        return;
    }

    console.log(`Found ${lists.length} lists:`);
    lists.forEach(l => console.log(`  - ${l.displayName}`));

    // Helper to find list
    const findList = (name) => lists.find(l => l.displayName.toLowerCase() === name.toLowerCase());

    // Fetch and display Projects
    const projectsList = findList('Projects');
    if (projectsList) {
        console.log('\n' + '='.repeat(60));
        console.log('📁 PROJECTS');
        console.log('='.repeat(60));

        const items = await fetchGraph(`${GRAPH_API}/sites/${SITE_ID}/lists/${projectsList.id}/items?expand=fields&$top=50`);

        (items.value || []).forEach(item => {
            const f = item.fields;
            console.log(`\n[${item.id}] ${f.Title || f.ProjectName || 'Unnamed'}`);
            console.log(`    Status: ${f.Status || 'N/A'} | Priority: ${f.Priority || 'N/A'} | Progress: ${f.PercentComplete || 0}%`);
            console.log(`    Assigned: ${f.AssignedTo || 'Unassigned'} | Customer: ${f.Customer || ''}`);
        });

        console.log(`\nTotal: ${(items.value || []).length} projects`);
    }

    // Fetch and display Tasks
    const tasksList = findList('Tasks');
    if (tasksList) {
        console.log('\n' + '='.repeat(60));
        console.log('✅ TASKS');
        console.log('='.repeat(60));

        const items = await fetchGraph(`${GRAPH_API}/sites/${SITE_ID}/lists/${tasksList.id}/items?expand=fields&$top=50`);

        (items.value || []).forEach(item => {
            const f = item.fields;
            console.log(`\n[${item.id}] ${f.Title || 'Unnamed'}`);
            console.log(`    Status: ${f.Status || 'N/A'} | Priority: ${f.Priority || 'N/A'}`);
            console.log(`    Project: ${f.ProjectName || 'None'} | Assigned: ${f.AssignedTo || 'Unassigned'}`);
        });

        console.log(`\nTotal: ${(items.value || []).length} tasks`);
    }

    // Fetch and display Tickets
    const ticketsList = findList('Tickets');
    if (ticketsList) {
        console.log('\n' + '='.repeat(60));
        console.log('🎫 TICKETS');
        console.log('='.repeat(60));

        const items = await fetchGraph(`${GRAPH_API}/sites/${SITE_ID}/lists/${ticketsList.id}/items?expand=fields&$top=50`);

        (items.value || []).forEach(item => {
            const f = item.fields;
            console.log(`\n[${item.id}] ${f.Title || f.TicketTitle || 'Unnamed'}`);
            console.log(`    Status: ${f.Status || 'N/A'} | Priority: ${f.Priority || 'N/A'} | SLA: ${f.SLAStatus || 'N/A'}`);
            console.log(`    Customer: ${f.Customer || 'Unknown'}`);
        });

        console.log(`\nTotal: ${(items.value || []).length} tickets`);
    }

    // Fetch and display TimeEntries
    const timeList = findList('TimeEntries') || findList('Time Entries');
    if (timeList) {
        console.log('\n' + '='.repeat(60));
        console.log('⏱️ TIME ENTRIES (Recent)');
        console.log('='.repeat(60));

        const items = await fetchGraph(`${GRAPH_API}/sites/${SITE_ID}/lists/${timeList.id}/items?expand=fields&$top=20&$orderby=fields/EntryDate desc`);

        let totalHours = 0;
        let billableHours = 0;

        (items.value || []).forEach(item => {
            const f = item.fields;
            const hours = parseFloat(f.Hours) || 0;
            totalHours += hours;
            if (f.Billable) billableHours += hours;

            const billMark = f.Billable ? '[$]' : '   ';
            const date = f.EntryDate ? f.EntryDate.split('T')[0] : 'N/A';
            console.log(`  ${billMark} ${date} | ${(f.Employee || 'Unknown').padEnd(20)} | ${hours.toFixed(1)}h | ${f.ProjectName || 'General'}`);
        });

        console.log(`\n  Total: ${totalHours.toFixed(1)}h | Billable: ${billableHours.toFixed(1)}h`);
    }

    console.log('\n' + '='.repeat(60));
    console.log('✅ Done!');
    console.log('='.repeat(60));
})();
