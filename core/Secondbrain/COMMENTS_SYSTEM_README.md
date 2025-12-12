# Engineer Dashboard - Comment System

## Overview

The comment system allows engineers to add, view, and track comments on projects and tickets directly from the dashboard. Comments are stored in SharePoint and automatically logged to markdown files for backup and record-keeping.

## Features

✅ **Add Comments** - Click the "💬 Comments" button on any project or ticket
✅ **View History** - See all comments with timestamps and author information
✅ **Real-time Updates** - Comments appear immediately in the dashboard
✅ **Markdown Logging** - All comments are automatically saved to .md files
✅ **Author Tracking** - Comments include the name of the user who posted them

## Setup Instructions

### 1. Add Comments Column to SharePoint

First, run the setup script to add the Comments column to your SharePoint lists:

```bash
cd /home/mavrick/Projects/Secondbrain
./venv/bin/python add_comments_column.py
```

This will add a "Comments" column to both:
- Engineering Projects list
- Engineering Tickets list

### 2. Access the Dashboard

Open the interactive dashboard:
- **URL:** https://jolly-island-06ade710f.3.azurestaticapps.net/
- **Local File:** `/home/mavrick/Projects/Secondbrain/engineering_tracker_interactive.html`

### 3. Using Comments

#### To Add a Comment When Creating a Project or Ticket:
1. Click **+ Add Project** or **+ Add Ticket**
2. Fill in the required fields
3. Scroll down to the **Initial Comment (Optional)** field
4. Type your comment
5. Click **Add Project** or **Add Ticket**
6. Your item will be created with the initial comment already attached!

#### To View Comments on Existing Items:
1. Navigate to the Projects or Tickets tab
2. Find the item you want to view comments for
3. Click the **💬 Comments** button in the Actions column
4. The Comments modal will open showing all existing comments

#### To Add a Comment to an Existing Item:
1. Open the Comments modal for an item
2. Scroll to the "Add New Comment" section at the bottom
3. Type your comment in the text area
4. Click **💬 Add Comment**
5. Your comment will be saved and displayed immediately

## Comment Storage

### SharePoint Storage
- Comments are stored as JSON in the "Comments" column
- Each comment includes:
  - `id`: Unique identifier
  - `author`: Name of the person who commented
  - `timestamp`: ISO 8601 format timestamp
  - `comment`: The comment text

### Markdown File Logging

Comments are automatically synced to markdown files located in:
```
/home/mavrick/Projects/Secondbrain/comments/
├── project/
│   ├── [item_id].md
│   └── [item_id].md
└── ticket/
    ├── [item_id].md
    └── [item_id].md
```

#### Manual Sync

To manually sync all comments to markdown files:

```bash
cd /home/mavrick/Projects/Secondbrain
./venv/bin/python sync_comments_to_md.py
```

This will:
- Fetch all projects and tickets from SharePoint
- Extract comments from each item
- Create/update .md files with formatted comments
- Provide a summary of synced items

## Python API Usage

You can also add comments programmatically using the Python utility:

```bash
# Add a comment to a project
./venv/bin/python comment_utils.py <item_id> project <author> "Comment text"

# Add a comment to a ticket
./venv/bin/python comment_utils.py <item_id> ticket <author> "Comment text"
```

### Example:
```bash
./venv/bin/python comment_utils.py 123 project john@oberaconnect.com "Updated the timeline for this project"
```

## Automation

### Auto-Sync Comments to .md Files

You can set up a cron job to automatically sync comments to markdown files:

```bash
# Edit crontab
crontab -e

# Add this line to sync every hour at minute 0
0 * * * * /home/mavrick/Projects/Secondbrain/venv/bin/python /home/mavrick/Projects/Secondbrain/sync_comments_to_md.py >> /home/mavrick/Projects/Secondbrain/logs/comments_sync.log 2>&1
```

## Files

| File | Purpose |
|------|---------|
| `add_comments_column.py` | One-time setup script to add Comments column to SharePoint |
| `comment_utils.py` | Python utility for managing comments programmatically |
| `sync_comments_to_md.py` | Sync all comments from SharePoint to .md files |
| `engineering_tracker_interactive.html` | Interactive dashboard with comment UI |
| `comments/` | Directory containing all comment markdown files |

## Troubleshooting

### Comments not appearing?
- Ensure you're logged in to the dashboard
- Check that the Comments column was added successfully to SharePoint
- Verify your Azure credentials in `.env` file

### Can't add comments?
- Make sure you have write permissions to the SharePoint lists
- Check browser console for any JavaScript errors
- Verify you're using a modern browser (Chrome, Edge, Firefox)

### .md files not syncing?
- Run the sync script manually to test: `./venv/bin/python sync_comments_to_md.py`
- Check that the `/home/mavrick/Projects/Secondbrain/comments/` directory exists
- Verify Azure credentials have read access to SharePoint

## Support

For issues or questions about the comment system:
1. Check the logs in `/home/mavrick/Projects/Secondbrain/logs/`
2. Review this documentation
3. Test the Python utilities directly for debugging

## Future Enhancements

Potential improvements:
- [ ] Edit existing comments
- [ ] Delete comments
- [ ] Comment threading/replies
- [ ] @mentions for notifications
- [ ] Rich text formatting
- [ ] File attachments
- [ ] Comment search functionality
