# How to Access Your RAG (Retrieval-Augmented Generation)

## ✅ Status: READY TO USE
- **486 documents indexed** in vector store
- Semantic search enabled across all teams
- Natural language queries supported

---

## 🚀 Quick Start

### Option 1: One-Time Query (Command Line)

```bash
cd /home/mavrick/Projects/Secondbrain
source venv/bin/activate
python3 query_brain.py "your question here"
```

**Examples:**
```bash
# Find network configs
python3 query_brain.py "mikrotik router configuration"

# Search policies
python3 query_brain.py "ISO 27001 security policy"

# Find procedures
python3 query_brain.py "customer onboarding process"

# Technical docs
python3 query_brain.py "Azure VPN setup"
```

### Option 2: Interactive Mode (Ask Multiple Questions)

```bash
cd /home/mavrick/Projects/Secondbrain
source venv/bin/activate
python3 query_brain.py
```

Then type your questions:
```
💬 Your question: How do I configure SonicWall firewall?
💬 Your question: What are our security policies?
💬 Your question: exit
```

---

## 📊 What You Get

For each query, RAG returns:
- **Top 5 most relevant notes** from your 486 indexed documents
- **Relevance score** (higher is better match)
- **File name with tags** for easy identification
- **Content preview** to verify relevance

**Example Output:**
```
1. ISO 27001 Schema Viewer - Database Structure and Controls
   📂 File: [risk-management][corp-app-idea] ISO_27001_Schema...
   🏷️  Tags: risk-management, corp-app-idea, asset-management
   📊 Relevance: 33.1%
   📝 Preview: This document outlines the database structure...
```

---

## 💡 Query Tips

### Good Queries (Works Best)

✅ **Topic searches:**
- "network configuration mikrotik"
- "ISO 27001 compliance"
- "customer security onboarding"

✅ **Concept finding:**
- "backup and disaster recovery"
- "VPN setup procedures"
- "employee security training"

✅ **Procedural questions:**
- "how to configure firewall"
- "what is the onboarding process"
- "Azure authentication setup"

### Query by Team

**IT Services queries:**
- "ITSM policy"
- "remote access procedures"
- "vulnerability management"
- "patch management policy"

**Engineering queries:**
- "network architecture"
- "router configuration"
- "MikroTik setup"
- "switch VLAN config"

**Plant queries:**
- "site survey procedures"
- "equipment installation"
- "construction buildout"
- "floor plan cabling"

**Sales queries:**
- "customer proposals"
- "service agreements"
- "case studies"
- "pricing contracts"

---

## 🔧 Maintenance

### When to Rebuild the Index

Rebuild after:
- Adding new documents
- Deleting documents
- Major content changes
- If results seem outdated

**Rebuild command:**
```bash
cd /home/mavrick/Projects/Secondbrain
source venv/bin/activate
python3 rebuild_index.py
```

This will:
1. Clear old index
2. Re-scan all notes in your vault
3. Re-index all 316+ markdown files
4. Takes ~2-5 minutes

---

## 🎯 Use Cases

### 1. Quick Research
**Scenario:** Need to find all docs about a topic
```bash
python3 query_brain.py "Azure backup configuration"
```

### 2. Policy Lookup
**Scenario:** What's our policy on X?
```bash
python3 query_brain.py "remote access policy"
```

### 3. Technical Reference
**Scenario:** How to configure something?
```bash
python3 query_brain.py "SonicWall VPN setup"
```

### 4. Customer Info
**Scenario:** Find customer deployment docs
```bash
python3 query_brain.py "customer deployment runbook"
```

### 5. Compliance Check
**Scenario:** What are ISO requirements?
```bash
python3 query_brain.py "ISO 27001 requirements"
```

---

## 📍 File Locations

**RAG Scripts:**
- Query tool: `/home/mavrick/Projects/Secondbrain/query_brain.py`
- Rebuild index: `/home/mavrick/Projects/Secondbrain/rebuild_index.py`
- Vector store: `/home/mavrick/Projects/Secondbrain/chroma_db/`

**Your Vault:**
- Notes: `/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault/notes/`
- Total indexed: **486 documents**

---

## 🆚 RAG vs. Graph View vs. Canvas

Use the right tool for the job:

| Tool | Best For | Access |
|------|----------|--------|
| **RAG** | Finding answers via semantic search | `python3 query_brain.py` |
| **Graph View** | Visual exploration, discovering connections | Obsidian graph icon |
| **Canvas** | Curated presentations, team overviews | `All_Teams_Star_View.canvas` |

---

## 🚨 Troubleshooting

**No results found?**
- Try broader search terms
- Rebuild the index: `python3 rebuild_index.py`
- Check if notes exist: `ls -la notes/`

**Poor relevance scores?**
- Be more specific in query
- Use key terms from your domain
- Try different phrasing

**Error: Module not found?**
- Activate venv first: `source venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`

---

## 🎓 Advanced: Create Aliases

Add to your `~/.bashrc`:

```bash
# RAG shortcuts
alias rag='cd /home/mavrick/Projects/Secondbrain && source venv/bin/activate && python3 query_brain.py'
alias rag-rebuild='cd /home/mavrick/Projects/Secondbrain && source venv/bin/activate && python3 rebuild_index.py'
```

Then reload: `source ~/.bashrc`

Now you can use:
```bash
rag "your question"          # Quick query from anywhere
rag-rebuild                  # Rebuild index from anywhere
```

---

## ✨ Your RAG is Ready!

**Current Status:**
- ✅ 486 documents indexed
- ✅ All 4 teams covered (IT, Engineering, Plant, Sales)
- ✅ Semantic search active
- ✅ Ready for queries

**Try it now:**
```bash
cd /home/mavrick/Projects/Secondbrain
source venv/bin/activate
python3 query_brain.py "customer onboarding"
```
