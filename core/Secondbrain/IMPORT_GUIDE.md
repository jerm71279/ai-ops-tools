# SharePoint & Slack Import Guide

Your Second Brain can now import documents from SharePoint and Slack!

---

## 📁 SharePoint Import

### Quick Start:

```bash
# Get setup instructions
./venv/bin/python sharepoint_importer.py --setup

# After setup, list your sites
./venv/bin/python sharepoint_importer.py
```

### Setup Steps:

1. **Register Azure App** (one-time setup)
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to: Azure Active Directory > App registrations
   - Create new app with API permissions:
     - `Sites.Read.All`
     - `Files.Read.All`

2. **Configure credentials** in `.env`:
   ```
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_CLIENT_SECRET=your-client-secret
   ```

3. **Download files**:
   ```python
   from sharepoint_importer import SharePointImporter

   importer = SharePointImporter()

   # List sites
   sites = importer.list_sites()

   # List libraries in a site
   libraries = importer.list_document_libraries(site_id)

   # Download files
   importer.download_files_from_library(
       site_id="your-site-id",
       drive_id="your-drive-id",
       output_dir="input_documents/sharepoint"
   )
   ```

4. **Process downloaded files**:
   ```bash
   ./venv/bin/python process_batch.py "*.pdf"
   ./venv/bin/python process_batch.py "*.docx"
   ```

---

## 💬 Slack Import

### Quick Start:

```bash
# Get setup instructions
./venv/bin/python slack_importer.py --setup

# After setup, list channels
./venv/bin/python slack_importer.py
```

### Setup Steps:

1. **Create Slack App** (one-time setup)
   - Go to [Slack API](https://api.slack.com/apps)
   - Create app with OAuth scopes:
     - `channels:history`
     - `channels:read`
     - `files:read`
     - `users:read`

2. **Configure token** in `.env`:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token-here
   ```

3. **Invite bot to channels**:
   ```
   In Slack: /invite @SecondBrain Importer
   ```

4. **Export channel messages**:
   ```python
   from slack_importer import SlackImporter

   importer = SlackImporter()

   # List channels
   channels = importer.list_channels()

   # Export messages from a channel
   importer.export_channel_messages(
       channel_id="C12345678",
       channel_name="general",
       output_dir="input_documents/slack",
       days=30  # Last 30 days
   )

   # Download files from a channel
   importer.download_files_from_channel(
       channel_id="C12345678",
       output_dir="input_documents/slack/files"
   )
   ```

5. **Process exported messages**:
   ```bash
   ./venv/bin/python process_batch.py "*.md"
   ```

---

## 🔄 Automated Workflow

### Option 1: Manual Import

1. Run SharePoint/Slack importers
2. Review downloaded files in `input_documents/`
3. Run batch processor
4. Check new notes in Obsidian vault

### Option 2: Scheduled Import (Cron)

```bash
# Add to crontab
crontab -e

# Import from SharePoint daily at 6 AM
0 6 * * * cd /home/mavrick/Projects/Secondbrain && ./venv/bin/python sharepoint_importer.py

# Import from Slack weekly on Monday at 6 AM
0 6 * * 1 cd /home/mavrick/Projects/Secondbrain && ./venv/bin/python slack_importer.py

# Process all new files daily at 7 AM
0 7 * * * cd /home/mavrick/Projects/Secondbrain && ./venv/bin/python process_batch.py "*.*"
```

---

## 💡 Tips

### SharePoint:
- You can sync specific SharePoint libraries to your OneDrive for easier access
- The importer downloads files to `input_documents/sharepoint/`
- Supports: PDF, DOCX, HTML, MD, TXT

### Slack:
- Messages are exported as markdown files
- Files are downloaded separately
- Set `days` parameter to control how far back to export
- Bot must be invited to private channels to access them

### Processing:
- All imported files go to `input_documents/`
- Run batch processor to convert to structured notes
- Files are automatically tagged and added to vault
- Duplicates are handled by checking existing notes

---

## 🔐 Security

**Important:**
- Store API tokens in `.env` file (already in `.gitignore`)
- Never commit credentials to git
- Rotate tokens periodically
- Use minimum required permissions

---

## 🚀 Next Steps

1. Choose your import source (SharePoint or Slack)
2. Run setup script to see configuration instructions
3. Configure credentials in `.env`
4. Test with one channel/library first
5. Automate with cron if desired

Your Second Brain can now pull knowledge from anywhere! 🧠✨
