# SharePoint Features Dashboard Implementation Plan

## Overview
Add 16 SharePoint features to the Engineering Command Center dashboard, implemented in phases.

## Phase 1 (Current Sprint)
1. **Version History** - View/restore previous versions of items
2. **File Attachments** - Attach files to projects/tickets
3. **Full-text Search** - Search across all lists
4. **Export to Excel** - Download filtered data as CSV/Excel

## Phase 2 (Future)
- Document Library (upload/download files)
- Recycle Bin (restore deleted items)
- Item Permissions (sharing)
- Audit Trail (who changed what)
- Calendar View
- Gantt/Timeline
- Rich Text Editor
- @Mentions in comments
- Bulk Edit
- Column Customization

## Skipped
- **Webhooks/Alerts** - Requires external endpoint infrastructure
- **Power Automate** - Requires separate Power Platform setup

---

## Azure Permissions Required

### Add to "Sharepoint Read-Only Interface" App Registration:

| Permission | Type | Purpose |
|------------|------|---------|
| `Sites.FullControl.All` | Application | Version history restore, full list access |
| `Files.ReadWrite.All` | Application | Attachment upload/download |

**Steps:**
1. Azure Portal → Microsoft Entra ID → App registrations
2. Select "Sharepoint Read-Only Interface"
3. API permissions → Add permission → Microsoft Graph → Application permissions
4. Add: `Sites.FullControl.All`, `Files.ReadWrite.All`
5. Grant admin consent

---

## Phase 1 Implementation Details

### Feature 1: Version History

**API Endpoints:**
```
GET /sites/{siteId}/lists/{listId}/items/{itemId}/versions
POST /sites/{siteId}/lists/{listId}/items/{itemId}/versions/{versionId}/restoreVersion
```

**UI Components:**
- Add "History" button to item detail modal header
- Create `#versionHistoryPanel` slide-out panel (right side)
- Version list with timestamp, author, changes summary
- "Restore" button per version with confirmation

**Implementation:**
1. Add `loadVersionHistory(type, itemId)` function
2. Add `restoreVersion(type, itemId, versionId)` function
3. Add CSS for `.version-panel`, `.version-item`, `.version-restore-btn`
4. Add "History" icon button to modal header next to close button
5. Show field-by-field diff between versions

---

### Feature 2: File Attachments

**API Endpoints (SharePoint REST API):**
```
GET /_api/web/lists/getbytitle('{listName}')/items({itemId})/AttachmentFiles
POST /_api/web/lists/getbytitle('{listName}')/items({itemId})/AttachmentFiles/add(FileName='{filename}')
DELETE /_api/web/lists/getbytitle('{listName}')/items({itemId})/AttachmentFiles('{filename}')
GET /_api/web/lists/getbytitle('{listName}')/items({itemId})/AttachmentFiles('{filename}')/$value
```

**UI Components:**
- Add "Attachments" section in item modal (below description)
- File drop zone with drag-and-drop support
- File list showing name, size, type icon, download/delete buttons
- Upload progress indicator

**Implementation:**
1. Add SharePoint REST API base URL: `https://{tenant}.sharepoint.com/sites/{siteName}/_api`
2. Create `loadAttachments(type, itemId)` function
3. Create `uploadAttachment(type, itemId, file)` function
4. Create `deleteAttachment(type, itemId, filename)` function
5. Create `downloadAttachment(type, itemId, filename)` function
6. Add drag-drop event handlers for `.attachment-dropzone`
7. Add file type icons (PDF, Word, Excel, Image, etc.)

**CSS:**
```css
.attachment-section { border-top: 1px solid var(--border); margin-top: 20px; }
.attachment-dropzone { border: 2px dashed var(--border); border-radius: 8px; padding: 20px; text-align: center; }
.attachment-dropzone.dragover { border-color: var(--primary); background: var(--primary-light); }
.attachment-list { margin-top: 12px; }
.attachment-item { display: flex; align-items: center; gap: 12px; padding: 8px; background: var(--surface); border-radius: 6px; margin-bottom: 6px; }
```

---

### Feature 3: Full-text Search

**API Endpoint:**
```
POST /search/query
{
  "requests": [{
    "entityTypes": ["listItem"],
    "query": { "queryString": "{searchTerm}" },
    "from": 0,
    "size": 50
  }]
}
```

**UI Components:**
- Replace current filter input with enhanced search bar
- Add search scope dropdown (All, Projects, Tickets, Tasks)
- Search results panel with highlighted matches
- Recent searches (localStorage)

**Implementation:**
1. Create `searchSharePoint(query, entityTypes)` function
2. Add debounced search input handler (300ms delay)
3. Create search results renderer with match highlighting
4. Store recent searches in localStorage (max 10)
5. Add keyboard navigation for results (up/down/enter)

**UI Location:**
- Main search bar in header area
- Results appear in dropdown below search input
- Click result to navigate to item

---

### Feature 4: Export to Excel

**Approach:** Client-side CSV/Excel generation (no server needed)

**Implementation:**
1. Add "Export" button to each tab header (next to view toggle)
2. Create `exportToCSV(type, data)` function
3. Create `exportToExcel(type, data)` function using SheetJS library
4. Include current filters in export
5. Add export options modal:
   - Format: CSV or Excel
   - Scope: Current view or All items
   - Fields: Select which columns to include

**Library:**
```html
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
```

**Export Function:**
```javascript
function exportToExcel(type, data, filename) {
    const ws = XLSX.utils.json_to_sheet(data.map(item => ({
        Title: item.fields.ProjectName || item.fields.TicketTitle,
        Status: item.fields.Status,
        Priority: item.fields.Priority,
        Assignee: item.fields.AssignedTo,
        DueDate: item.fields.DueDate,
        // ... other fields
    })));
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, type);
    XLSX.writeFile(wb, `${filename}.xlsx`);
}
```

---

## File Modifications

**Primary file:** `/home/mavrick/Projects/Secondbrain/engineering_command_center.html`

### Sections to Modify:

1. **CONFIG object** (~line 2528)
   - Add SharePoint REST API base URL
   - Add list names for REST API calls

2. **CSS section** (~lines 1-1800)
   - Add version panel styles
   - Add attachment section styles
   - Add search results styles
   - Add export button styles

3. **HTML - Modal structure** (~lines 2100-2400)
   - Add History button to modal header
   - Add Attachments section to modal body
   - Add version history panel (hidden by default)

4. **HTML - Header/Search** (~lines 1900-1950)
   - Enhance search bar with scope selector
   - Add export buttons to tab headers

5. **JavaScript - New functions** (add after existing functions ~line 4800)
   - `loadVersionHistory(type, itemId)`
   - `restoreVersion(type, itemId, versionId)`
   - `renderVersionPanel(versions)`
   - `loadAttachments(type, itemId)`
   - `uploadAttachment(type, itemId, file)`
   - `deleteAttachment(type, itemId, filename)`
   - `downloadAttachment(type, itemId, filename)`
   - `searchSharePoint(query, scope)`
   - `renderSearchResults(results)`
   - `exportToCSV(type)`
   - `exportToExcel(type)`

6. **Event listeners** (~line 2646 in bindEventListeners)
   - Add history button click handler
   - Add attachment drag-drop handlers
   - Add search input handler with debounce
   - Add export button handlers

---

## Implementation Order

1. **Export to Excel** (simplest, no API changes needed)
2. **Full-text Search** (uses existing Graph API patterns)
3. **Version History** (new Graph API endpoint)
4. **File Attachments** (introduces REST API, most complex)

---

## Testing Checklist

- [ ] Export: CSV downloads with correct data
- [ ] Export: Excel file opens in Excel/Sheets
- [ ] Export: Filters applied to export
- [ ] Search: Returns results from all lists
- [ ] Search: Debounce prevents excessive API calls
- [ ] Search: Click result opens correct item
- [ ] History: Shows all versions with timestamps
- [ ] History: Restore creates new version
- [ ] History: Changes highlighted between versions
- [ ] Attachments: Drag-drop upload works
- [ ] Attachments: File click downloads
- [ ] Attachments: Delete removes file
- [ ] Attachments: Multiple files supported
- [ ] Attachments: Large files handled (progress indicator)
