# OberaConnect Second Brain

## Internal Knowledge Management System

**Purpose:** Centralize OberaConnect's knowledge base from SharePoint into a searchable, interconnected system using Obsidian.

---

## 🎯 What This System Does

This is OberaConnect's internal solution for:

1. **Centralizing Knowledge** - Pull all company documentation from SharePoint
2. **Making it Searchable** - Semantic search across all docs using AI
3. **Creating Connections** - Link related procedures, policies, and guides
4. **Improving Access** - Quick retrieval of any company information
5. **Maintaining Single Source of Truth** - SharePoint remains authoritative, this adds discoverability

---

## 📊 Current Status

### Your Knowledge Base:
- **116 notes** currently indexed
- **Source:** OberaConnect operational documentation
- **Categories:** Security, Azure, Networking, Customer Procedures, Compliance

### Ready to Import:
- ✅ SharePoint integration configured
- ✅ Document processing pipeline ready
- ✅ Obsidian vault structure created
- ✅ RAG (semantic search) available
- ✅ Link suggestion system functional

---

## 🚀 Getting Started

### 1. Set Up SharePoint Access

Follow: `OBERACONNECT_SHAREPOINT_WORKFLOW.md`

Quick steps:
- Register Azure app for OberaConnect
- Grant SharePoint read permissions
- Add credentials to `.env`

### 2. Import Company Knowledge Base

```bash
# Download from SharePoint
./venv/bin/python sharepoint_importer.py

# Process into structured notes
./venv/bin/python process_batch.py "input_documents/sharepoint/**/*.*"

# Add tag prefixes for browsing
./venv/bin/python rename_with_tags.py
```

### 3. Access in Obsidian

Open vault: `C:\Users\JeremySmith\OneDrive - Obera Connect\MyVault`

Browse by:
- **Tags** - Files sorted alphabetically by category
- **Search** - Ctrl+Shift+F for full-text search
- **Graph View** - Visual map of connected documents
- **Links** - Navigate between related docs

---

## 🔍 Search Your Knowledge Base

### RAG (Semantic Search)

Ask questions in natural language:

```bash
# Find information
./venv/bin/python query_brain.py "How do we onboard new customers to Keeper?"

# Discover procedures
./venv/bin/python query_brain.py "Azure Site-to-Site VPN setup steps"

# Locate policies
./venv/bin/python query_brain.py "ISO 27001 compliance requirements"
```

### Traditional Search

In Obsidian:
- `Ctrl+O` - Quick switcher (find any note)
- `Ctrl+Shift+F` - Global search
- Tag search: `tag:#security`

---

## 📁 Folder Structure

```
Secondbrain/
├── input_documents/         # Drop files here to process
│   └── sharepoint/         # SharePoint downloads
├── chroma_db/              # Vector search index
├── venv/                   # Python environment
│
├── sharepoint_importer.py  # Download from SharePoint
├── process_batch.py        # Convert docs to notes
├── rename_with_tags.py     # Add tag prefixes
├── suggest_links.py        # Find connections
├── query_brain.py          # Semantic search
└── rebuild_index.py        # Refresh search index
```

**Obsidian Vault:** `C:\Users\JeremySmith\OneDrive - Obera Connect\MyVault`
```
MyVault/
└── notes/                  # All your knowledge base notes
    ├── [security][policy] ...
    ├── [customer][azure] ...
    └── [compliance][iso27001] ...
```

---

## 💼 OberaConnect Use Cases

### For IT Operations Team:
- Quick lookup of customer configurations
- Find related setup procedures
- Access network diagrams and credentials
- Troubleshooting guides and runbooks

### For Security & Compliance:
- ISO 27001 documentation
- Security policies and procedures
- Audit requirements and evidence
- Incident response playbooks

### For Customer Success:
- Onboarding procedures
- Service delivery guides
- SLA requirements
- Customer-specific configurations

### For Management:
- Strategic documentation
- Process definitions
- Organizational policies
- Vendor relationships

---

## 🔄 Regular Workflows

### Daily: Quick Search
```bash
# Find what you need
./venv/bin/python query_brain.py "your question"
```

### Weekly: Sync SharePoint
```bash
# Download new/updated docs
./venv/bin/python sharepoint_importer.py
./venv/bin/python process_batch.py "input_documents/sharepoint/**/*.*"
```

### Monthly: Maintain Connections
```bash
# Find new relationships
./venv/bin/python suggest_links.py --export

# Review and add links in Obsidian
```

---

## 🛠️ Maintenance

### Rebuild Search Index
After adding/removing documents:
```bash
./venv/bin/python rebuild_index.py
```

### Clean Up Irrelevant Content
```bash
# Example: Remove old platform dev docs (already done)
./venv/bin/python remove_copilot_content.py
./venv/bin/python remove_platform_dev.py
```

### Update Link Suggestions
```bash
./venv/bin/python suggest_links.py --export
# Review link_suggestions.md
```

---

## 📚 Documentation

- **`OBERACONNECT_SHAREPOINT_WORKFLOW.md`** - SharePoint integration guide
- **`IMPORT_GUIDE.md`** - SharePoint & Slack import instructions
- **`RAG_USAGE_GUIDE.md`** - Semantic search usage
- **`link_suggestions.md`** - Suggested connections between notes

---

## 🔐 Security Notes

- **SharePoint as Source of Truth** - All company docs remain in SharePoint
- **Read-Only Access** - This system only reads, never modifies SharePoint
- **Local Processing** - All AI processing happens locally via Claude API
- **Access Control** - Inherits your SharePoint permissions
- **Credentials** - Stored securely in `.env` (not committed to git)

---

## 🎯 Benefits for OberaConnect

### Before:
- ❌ Documents scattered across SharePoint
- ❌ Hard to find related information
- ❌ No way to search by concept
- ❌ Knowledge silos by department

### After:
- ✅ Centralized searchable knowledge base
- ✅ Discover connections between docs
- ✅ Ask questions in natural language
- ✅ Quick access to any company information
- ✅ Visual knowledge graph in Obsidian

---

## 👥 Who Uses This

**Current User:** Jeremy Smith (You)

**Potential Future Users:**
- IT Operations team members
- Security & Compliance team
- Management (for strategic docs)
- Any OberaConnect staff needing quick knowledge access

**Scalability:**
- Can be shared via OneDrive sync
- Or individual setups with shared SharePoint source
- Or central server with web interface (future enhancement)

---

## 🚀 Next Steps

1. ✅ System is set up and ready
2. ⏳ **Complete Azure app registration** (15 min)
3. ⏳ **Download first SharePoint library** (5 min)
4. ⏳ **Process and explore in Obsidian** (10 min)
5. ⏳ **Start creating wiki links** between docs

---

## 📞 Support

**System Location:** `/home/mavrick/Projects/Secondbrain`

**Questions or Issues:**
- Check the documentation files listed above
- Review error logs in processing_logs/
- Rebuild index if search isn't working

---

**Built for OberaConnect's internal knowledge management** 🧠✨

*Making company knowledge accessible, searchable, and interconnected.*
