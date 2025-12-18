# OberaConnect Secondbrain (n8n)

Self-hosted knowledge base with SharePoint ingestion and RAG-powered queries.

## Security Status: HARDENED

This skill has been security-hardened per AI Counsel review (Dec 18, 2025):

- Webhooks require API key authentication (X-API-Key header)
- Qdrant requires API key authentication
- Services bound to localhost only (127.0.0.1)
- Firewall blocks direct external access
- Secrets auto-generated during deployment

## Quick Start

```bash
# 1. Deploy (as root)
sudo ./deploy.sh

# 2. Note the generated credentials (displayed during deploy)

# 3. Add your API keys
sudo nano /opt/oberaconnect-secondbrain/.env
# Add: ANTHROPIC_API_KEY, MICROSOFT_* credentials

# 4. Restart
sudo systemctl restart secondbrain

# 5. Access n8n UI
# Local: http://127.0.0.1:5678
# Via nginx: https://your-domain:443
```

## CLI Usage

```bash
# Set your API key
export SECONDBRAIN_API_KEY="your-webhook-api-key"
export SECONDBRAIN_URL="http://localhost:5678"

# Query
./sb-query.sh "What are UniFi WiFi best practices?"

# Interactive mode
./sb-query.sh --interactive
```

## Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | n8n + Qdrant stack (secured) |
| `deploy.sh` | Automated deployment |
| `workflow-*.json` | n8n workflows |
| `sb-query.sh` | CLI query tool |
| `SKILL.md` | Full documentation |
| `PROJECT_STATUS.md` | Project tracking |

## Architecture

```
SharePoint → n8n Ingestion → Qdrant Vectors
                                   ↓
                            Claude RAG Query
                                   ↓
                         CLI / Webhook / Teams
```

## Cost

| Component | Monthly |
|-----------|---------|
| Anthropic API | ~$155 |
| Self-hosted | $0 |
| **Total** | **~$155** |

## Project Status

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for current progress.

## Security Notes

- Never commit `.env` to git
- API keys auto-generated during deploy
- External access requires nginx reverse proxy with SSL
- Qdrant/n8n ports blocked by firewall

---

*Part of OberaConnect AI Operations*
