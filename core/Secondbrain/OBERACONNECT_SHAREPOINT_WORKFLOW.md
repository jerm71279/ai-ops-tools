# OberaConnect SharePoint Integration Workflow

## 🎯 Goal

Make SharePoint the **source of truth** for OberaConnect documentation, automatically sync to your Second Brain, and create knowledge connections in Obsidian.

---

## 📋 Step 1: Azure App Setup (One-Time)

### Quick Setup:
1. Go to https://portal.azure.com
2. Navigate to: **Azure Active Directory > App registrations**
3. Click **"New registration"**
   - Name: `OberaConnect Second Brain`
   - Account type: `Single tenant`
   - Redirect URI: (leave blank)
4. **Save these values:**
   - Application (client) ID
   - Directory (tenant) ID
5. **Create client secret:**
   - Certificates & secrets > New client secret
   - Description: `Second Brain Access`
   - Expires: 24 months
   - **COPY THE VALUE IMMEDIATELY** (shown only once!)
6. **Grant permissions:**
   - API permissions > Add permission > Microsoft Graph
   - **Application permissions** (not delegated):
     - `Sites.Read.All`
     - `Files.Read.All`
   - Click **"Grant admin consent for [Your Org]"**

### Add to .env file:
```bash
# Add these to /home/mavrick/Projects/Secondbrain/.env
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-secret-value-here
```

---

## 📥 Step 2: Download SharePoint Documents

### List Your SharePoint Sites:
```bash
cd /home/mavrick/Projects/Secondbrain
./venv/bin/python sharepoint_importer.py
```

This will show all SharePoint sites you have access to.

### Download from Specific Site:

**Interactive Python:**
```python
from sharepoint_importer import SharePointImporter

# Initialize
importer = SharePointImporter()

# List sites
sites = importer.list_sites()
# Find your OberaConnect site and note the site ID

# List document libraries in that site
libraries = importer.list_document_libraries(site_id="YOUR_SITE_ID")
# Find the library you want and note the drive ID

# Download files
importer.download_files_from_library(
    site_id="YOUR_SITE_ID",
    drive_id="YOUR_DRIVE_ID",
    output_dir="input_documents/sharepoint/oberaconnect"
)
```

**Supported File Types:**
- ✅ PDF documents
- ✅ Word documents (.docx)
- ✅ HTML files
- ✅ Markdown files (.md)
- ✅ Text files (.txt)

---

## 🔄 Step 3: Process Documents into Obsidian

Once downloaded, process them into structured notes:

```bash
cd /home/mavrick/Projects/Secondbrain

# Process all SharePoint docs
./venv/bin/python process_batch.py "input_documents/sharepoint/**/*.pdf"
./venv/bin/python process_batch.py "input_documents/sharepoint/**/*.docx"
./venv/bin/python process_batch.py "input_documents/sharepoint/**/*.html"
./venv/bin/python process_batch.py "input_documents/sharepoint/**/*.md"
```

This will:
1. Extract content from each document
2. Use Claude AI to structure it (title, summary, concepts, tags)
3. Create a note in your Obsidian vault
4. Add it to the vector store for semantic search
5. Tag it based on folder structure

---

## 🏷️ Step 4: Add Tag Prefixes to Filenames

Make files browsable by tag:

```bash
./venv/bin/python rename_with_tags.py
```

Files will be renamed like:
- `[security][compliance][iso27001] Information Security Policy.md`
- `[customer-deployment][azure][networking] Site-to-Site VPN Guide.md`

---

## 🔗 Step 5: Create Links in Obsidian

### Generate Link Suggestions:
```bash
# Create a report of potential links between notes
./venv/bin/python suggest_links.py --export
```

This creates `link_suggestions.md` showing:
- Which notes should link together
- Similarity scores
- Shared tags and concepts

### Manually Add Links in Obsidian:

1. Open Obsidian to your vault: `C:\Users\JeremySmith\OneDrive - Obera Connect\MyVault`
2. Open `link_suggestions.md` in a second pane
3. For each suggestion:
   - Open the source note
   - Add `[[Target Note Title]]` where relevant
   - The link will be clickable and show in Graph View

### Example Links to Create:

**Existing Note:** `[security][onboarding] Employee Security Onboarding Master Plan.md`
**SharePoint Note:** `[security][compliance] OberaConnect Security Policy.md`

In the onboarding note, add:
```markdown
## Related Policies
- [[OberaConnect Security Policy]]
- [[Access Control Standards]]
```

---

## 🔄 Step 6: Automated Sync (Optional)

### Option A: Manual Sync (Recommended to start)
Run whenever SharePoint docs are updated:
```bash
cd /home/mavrick/Projects/Secondbrain
./venv/bin/python sharepoint_importer.py
# Download new/updated files
./venv/bin/python process_batch.py "input_documents/sharepoint/**/*.*"
./venv/bin/python rename_with_tags.py
./venv/bin/python rebuild_index.py  # Update RAG search
```

### Option B: Scheduled Sync (Cron)
```bash
# Edit crontab
crontab -e

# Add: Sync SharePoint daily at 6 AM
0 6 * * * cd /home/mavrick/Projects/Secondbrain && ./venv/bin/python sync_sharepoint.sh

# Add: Process new files at 6:30 AM
30 6 * * * cd /home/mavrick/Projects/Secondbrain && ./venv/bin/python process_batch.py "input_documents/**/*.*"
```

---

## 📊 Workflow Visualization

```
SharePoint (Source of Truth)
    ↓
[Azure App] → Download via Microsoft Graph API
    ↓
input_documents/sharepoint/
    ↓
[Claude AI] → Extract + Structure Content
    ↓
Obsidian Vault (/notes/)
    ↓
[Tag-based filenames] + [Wiki Links] + [Vector Search]
    ↓
Your Second Brain 🧠
```

---

## 💡 Best Practices

### SharePoint Organization:
1. **Maintain folder structure** - It becomes tags
   - `Policies/Security/` → `#policies, #security`
   - `Procedures/Customer_Onboarding/` → `#procedures, #customer-onboarding`

2. **Use clear filenames** - They become note titles
   - Good: `Customer_Deployment_Checklist_v2.docx`
   - Bad: `Doc1_final_FINAL_v3.docx`

### Obsidian Linking Strategy:
1. **Link procedures to policies**
   - "Employee Onboarding" → "Security Policy"
2. **Link implementations to guides**
   - "Azure VPN Setup Log" → "Azure VPN Guide"
3. **Create MOCs (Maps of Content)**
   - "Security Overview" note linking to all security docs
   - "Customer Deployment Index" linking to all deployment guides

### Version Control:
- SharePoint versions are preserved
- Each sync creates a new note (timestamp in filename)
- Or configure to overwrite (track in SharePoint versioning)

---

## 🎯 Your OberaConnect Use Cases

### 1. Policy & Procedure Library
- Download all policy documents from SharePoint
- Structure them in Obsidian
- Link related policies together
- Quick search: "What's our data retention policy?"

### 2. Customer Deployment Knowledge
- Customer setup guides from SharePoint
- Link to: equipment configs, credentials, network diagrams
- RAG search: "How did we set up Azure VPN for SetCo?"

### 3. Technical Documentation
- API docs, architecture diagrams, runbooks
- Link between related systems
- Find: "All documents mentioning Keeper Security"

### 4. Compliance & Auditing
- ISO 27001 documentation
- Link controls to implementations
- Generate compliance reports from linked notes

---

## 🚀 Quick Start Checklist

- [ ] Set up Azure App Registration
- [ ] Add credentials to `.env` file
- [ ] Test: `./venv/bin/python sharepoint_importer.py`
- [ ] Download first document library
- [ ] Process documents: `process_batch.py`
- [ ] Rename with tags: `rename_with_tags.py`
- [ ] Open Obsidian and explore
- [ ] Generate link suggestions
- [ ] Create your first wiki links
- [ ] Set up regular sync schedule

---

## 📞 Next Steps

1. **Complete Azure setup** (15 minutes)
2. **Download your first SharePoint library** (5 minutes)
3. **Process and explore in Obsidian** (10 minutes)
4. **Start creating links** between existing and new notes

Your SharePoint docs will become a searchable, interconnected knowledge graph! 🕸️✨
