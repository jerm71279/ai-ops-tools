# OberaConnect Secondbrain: n8n Knowledge Base System

## Overview

This skill deploys a self-hosted knowledge base system that replaces NotebookLM functionality with an automated, integrated solution. The system ingests documents from SharePoint, processes them into a vector database, and provides RAG-powered query capabilities through multiple interfaces.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OberaConnect Secondbrain                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │  SharePoint  │────▶│    n8n       │────▶│   Qdrant     │                 │
│  │  (Source)    │     │  Workflows   │     │ Vector Store │                 │
│  └──────────────┘     └──────────────┘     └──────────────┘                 │
│         │                    │                    │                          │
│         │                    ▼                    │                          │
│         │             ┌──────────────┐            │                          │
│         │             │   Claude     │◀───────────┘                          │
│         │             │  (Anthropic) │                                       │
│         │             └──────────────┘                                       │
│         │                    │                                               │
│         ▼                    ▼                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   Obsidian   │◀───▶│  Teams Bot   │     │  CLI/Webhook │                 │
│  │    Vault     │     │  Interface   │     │    API       │                 │
│  └──────────────┘     └──────────────┘     └──────────────┘                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Document Ingestion Pipeline (`workflow-ingestion.json`)
- **Trigger**: Schedule (daily) or manual
- **Source**: SharePoint folders/document libraries
- **Processing**: PDF/DOCX text extraction, chunking, embedding
- **Storage**: Qdrant vector database with metadata

### 2. RAG Query System (`workflow-query.json`)
- **Trigger**: Chat interface, webhook, or Teams bot
- **Retrieval**: Semantic search against Qdrant
- **Generation**: Claude AI with retrieved context
- **Output**: Cited responses with source references

### 3. Obsidian Sync (`workflow-obsidian-sync.json`)
- **Bidirectional**: Notes to vector store, insights to vault
- **Format**: Markdown with YAML frontmatter preservation

## Prerequisites

- Azure Linux VM (existing OberaConnect infrastructure)
- Docker and Docker Compose
- Anthropic API key
- Microsoft 365 credentials (for SharePoint access)
- GitHub access (for version control)

## Deployment

### Quick Start

```bash
# 1. Clone to your Azure VM
cd /opt
git clone https://github.com/jerm71279/oberaconnect-ai-ops.git
cd oberaconnect-ai-ops/secondbrain-n8n

# 2. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 3. Deploy stack
docker-compose up -d

# 4. Access n8n
# https://your-vm-ip:5678
```

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
N8N_ENCRYPTION_KEY=<generate-random-32-char>
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=<secure-password>

# SharePoint (Microsoft Graph)
MICROSOFT_CLIENT_ID=<app-registration-id>
MICROSOFT_CLIENT_SECRET=<app-secret>
MICROSOFT_TENANT_ID=<tenant-id>
SHAREPOINT_SITE_ID=<site-id>

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=oberaconnect-docs

# Optional
WEBHOOK_URL=https://your-domain/webhook
TEAMS_WEBHOOK_URL=<teams-incoming-webhook>
```

## Workflow Details

### Ingestion Pipeline

**Trigger Options:**
- Cron schedule: `0 2 * * *` (daily at 2 AM)
- Manual trigger for immediate sync
- Webhook for event-driven updates

**Processing Steps:**
1. List files from SharePoint folder (new/modified since last run)
2. Download files to temporary storage
3. Extract text using appropriate method:
   - PDF: `Extract From File` node
   - DOCX: `Extract From File` node
   - Markdown: Direct read
4. Split into chunks (500 tokens, 50 token overlap)
5. Generate embeddings via Anthropic
6. Upsert to Qdrant with metadata:
   - `source_file`: Original filename
   - `sharepoint_path`: Full path in SharePoint
   - `modified_date`: Last modification timestamp
   - `chunk_index`: Position in document
   - `customer`: Extracted customer name (if applicable)

### Query System

**Input Handling:**
- Natural language questions
- Filters: customer name, date range, document type
- Context: Previous conversation (via Simple Memory node)

**Retrieval Configuration:**
- Top-K: 5 chunks
- Similarity threshold: 0.7
- Metadata filtering supported

**Response Format:**
```
[Answer based on retrieved context]

---
Sources:
- [Document Name](sharepoint-link) - Chunk 3
- [Document Name](sharepoint-link) - Chunk 7
```

## Integration Points

### Teams Bot
The query workflow exposes a webhook that can be connected to a Teams bot:
1. Create Azure Bot Service
2. Configure messaging endpoint to n8n webhook URL
3. Install bot in Teams channel

### CLI Integration
For your multi-AI orchestration workflow:
```bash
curl -X POST https://your-n8n/webhook/secondbrain-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the WiFi best practices for UniFi?", "customer": "optional-filter"}'
```

### Obsidian
Using the Post Webhook plugin:
1. Install Post Webhook in Obsidian
2. Configure webhook URL to n8n endpoint
3. Send notes with `post-webhook: true` frontmatter

## Maintenance

### Monitoring
- n8n execution logs: `docker logs n8n`
- Qdrant health: `curl http://localhost:6333/health`
- Failed executions visible in n8n UI

### Backup
```bash
# Backup Qdrant data
docker exec qdrant qdrant-backup /snapshots/backup-$(date +%Y%m%d)

# Backup n8n workflows
docker exec n8n n8n export:workflow --all --output=/data/backups/
```

### Scaling
- Increase Qdrant resources for larger document sets
- Add n8n workers for parallel processing
- Consider Qdrant Cloud for >10GB vector data

## Troubleshooting

### Common Issues

**SharePoint authentication fails:**
- Verify Microsoft Graph permissions: `Sites.Read.All`, `Files.Read.All`
- Check token expiration and refresh

**Embedding errors:**
- Verify Anthropic API key is valid
- Check rate limits (consider batching)

**Qdrant connection refused:**
- Ensure Qdrant container is running
- Verify network connectivity between containers

**No results returned:**
- Check if documents were ingested (query Qdrant directly)
- Lower similarity threshold
- Verify chunk size isn't too large

## Cost Estimation

| Component | Usage | Monthly Cost |
|-----------|-------|--------------|
| Azure VM | Existing | $0 |
| Qdrant | Self-hosted | $0 |
| Anthropic API | ~100K tokens/day | $30-50 |
| **Total** | | **~$30-50** |

## Version History

- **v1.0.0** (2024-12): Initial release
  - SharePoint ingestion pipeline
  - RAG query system
  - Obsidian bidirectional sync
  - Teams bot integration

## References

- [n8n Documentation](https://docs.n8n.io/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Anthropic API](https://docs.anthropic.com/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)
