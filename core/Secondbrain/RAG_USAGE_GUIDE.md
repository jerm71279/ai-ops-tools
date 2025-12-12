# RAG (Retrieval-Augmented Generation) Usage Guide

## 🔍 What is RAG?

RAG allows you to semantically search your Second Brain knowledge base using natural language queries. Instead of keyword matching, it understands the meaning of your question and finds relevant notes.

## 📚 Your Current Setup

**Status:** System is set up but needs reconfiguration after recent cleanup

**Components:**
- ✅ `vector_store.py` - ChromaDB integration for embeddings
- ✅ `query_brain.py` - Query interface
- ✅ `rebuild_index.py` - Re-index after changes
- ⚠️ Vector index needs to be rebuilt

## 🚀 How to Use RAG

### 1. Rebuild the Index (After Any Changes)

```bash
cd /home/mavrick/Projects/Secondbrain
./venv/bin/python rebuild_index.py
```

This indexes all 116 notes in your vault for semantic search.

### 2. Query Your Knowledge Base

**Command Line:**
```bash
# Ask a question
./venv/bin/python query_brain.py "How do I set up Azure backup?"

# Search for topics
./venv/bin/python query_brain.py "SonicWall configuration"

# Find procedures
./venv/bin/python query_brain.py "employee onboarding security"
```

**Interactive Mode:**
```bash
# No arguments = interactive mode
./venv/bin/python query_brain.py

# Then type your questions
💬 Your question: How do I configure Keeper Security?
💬 Your question: What are the ISO 27001 requirements?
💬 Your question: exit
```

## 📊 What RAG Returns

For each query, you'll get:
- **Top 5 most relevant notes**
- **Relevance score** (0-100%)
- **File name and tags**
- **Content preview**

Example output:
```
1. Azure Backup - Recovery Services Vault Setup and Monitoring
   📂 File: [recovery-services][customers][backup] Azure_Backup_Setup.md
   🏷️  Tags: backup, disaster-recovery, azure, setco
   📊 Relevance: 92.3%
   📝 Preview: This guide covers Azure Backup configuration for...
```

## 💡 Query Tips

**Good Queries:**
- "How do I onboard a new customer to Keeper Security?"
- "What are the steps for Azure Site-to-Site VPN?"
- "Show me information about ISO 27001 compliance"
- "Employee security onboarding checklist"

**Works Best With:**
- Questions about procedures
- Topic searches
- Finding related concepts
- Discovering connections between notes

## 🔧 Maintenance

**When to Rebuild Index:**
- After adding new documents
- After deleting documents
- After cleaning up content (like we just did)
- If search results seem stale

**Auto-Rebuild (Optional):**
Add to your process_batch.py workflow to auto-index new documents.

## 🎯 Next Steps

1. **Rebuild the index** to make RAG functional
2. **Try some queries** related to your OberaConnect work
3. **Integrate with Obsidian** - Consider creating Obsidian community plugin for RAG search
4. **Add to workflow** - Auto-index when processing new documents

## 📖 Alternative: Traditional Search

While RAG is being set up, you can use:
- **Obsidian Search**: Ctrl+Shift+F in Obsidian
- **Tag browsing**: Files are alphabetically sorted by tags
- **Grep search**: `grep -r "keyword" notes/`

---

**Your Second Brain is ready for semantic search once the index is rebuilt!** 🧠✨
