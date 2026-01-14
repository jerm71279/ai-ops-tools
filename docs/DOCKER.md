# Docker Architecture

Detailed documentation for the OberaConnect unified Docker stack.

## Overview

The stack consists of 13 services organized into 5 layers, managed by a single `docker-compose.yml` with profile-based activation.

## Service Reference

### Layer 1: Models

#### Ollama (Profile: `local-llm`)

Local LLM inference server with NVIDIA GPU acceleration.

| Property | Value |
|----------|-------|
| Image | `ollama/ollama:latest` |
| Port | 11434 |
| Volume | `ollama_models:/root/.ollama` |
| GPU | NVIDIA (all available) |

```bash
# Start
docker compose --profile local-llm up -d

# Pull models
docker exec ollama ollama pull llama3.2
docker exec ollama ollama pull qwen2.5:7b
docker exec ollama ollama pull codellama:7b

# List models
docker exec ollama ollama list

# Test inference
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

**Recommended Models:**
| Model | Size | Use Case |
|-------|------|----------|
| llama3.2 | 2GB | General chat, fast |
| qwen2.5:7b | 4GB | Technical tasks |
| codellama:7b | 4GB | Code generation |

### Layer 2: Persistence

#### PostgreSQL

Relational database for chat history and session persistence.

| Property | Value |
|----------|-------|
| Image | `postgres:16-alpine` |
| Port | 5432 (localhost only) |
| Volume | `postgres_data:/var/lib/postgresql/data` |

```bash
# Connect
docker exec -it postgres psql -U obera -d oberaconnect

# Backup
docker exec postgres pg_dump -U obera oberaconnect > backup.sql

# Restore
cat backup.sql | docker exec -i postgres psql -U obera oberaconnect
```

#### Qdrant

Vector database for RAG and semantic search.

| Property | Value |
|----------|-------|
| Image | `qdrant/qdrant:latest` |
| Ports | 6333 (HTTP), 6334 (gRPC) |
| Volumes | `qdrant_storage`, `qdrant_snapshots` |

```bash
# Check collections
curl http://localhost:6333/collections

# Create collection
curl -X PUT http://localhost:6333/collections/documents \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 1536, "distance": "Cosine"}}'

# Health check
curl http://localhost:6333/health
```

### Layer 3: Services

All services use the same base pattern:

| Property | Value |
|----------|-------|
| Base Image | Python 3.11-slim |
| Server | Gunicorn with 4 workers |
| Health Check | GET /health |
| User | Non-root (appuser) |

#### data-processing (8081)

Document ingestion, parsing, and chunking.

```bash
curl http://localhost:8080/api/data/health
curl -X POST http://localhost:8080/api/data/ingest \
  -H "Content-Type: application/json" \
  -d '{"source": "sharepoint", "path": "/Documents"}'
```

#### rag-engine (8082)

RAG queries with vector search.

```bash
curl http://localhost:8080/api/rag/health
curl -X POST http://localhost:8080/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I configure VLANs?", "top_k": 5}'
```

#### engineering-api (8083)

Engineering documentation and technical queries.

```bash
curl http://localhost:8080/api/engineering/health
```

#### call-flow (8084)

Phone system call flow generation.

```bash
curl http://localhost:8080/api/callflow/health
curl -X POST http://localhost:8080/api/callflow/generate \
  -H "Content-Type: application/json" \
  -d '{"customer": "Acme Corp", "extensions": [...]}'
```

#### agents (8085)

AI agents with MCP integrations.

```bash
curl http://localhost:8080/api/agents/health
```

### Layer 4: Orchestration

#### Gateway (nginx)

API gateway with path-based routing.

| Property | Value |
|----------|-------|
| Image | `nginx:alpine` |
| Port | 8080 |
| Config | `core/Secondbrain/docker/nginx.conf` |

**Routes:**
| Path | Upstream | Timeout |
|------|----------|---------|
| /api/data/* | data-processing:8080 | 3600s |
| /api/rag/* | rag-engine:8080 | 120s |
| /api/engineering/* | engineering-api:8080 | 1800s |
| /api/callflow/* | call-flow:8080 | 300s |
| /api/agents/* | agents:8080 | 7200s |
| /api/ollama/* | ollama:11434 | 600s |
| /api/qdrant/* | qdrant:6333 | - |

```bash
# Service discovery
curl http://localhost:8080/api/services

# Health check
curl http://localhost:8080/health
```

### Layer 5: UI/Interface

#### n8n

Workflow automation platform.

| Property | Value |
|----------|-------|
| Image | `docker.n8n.io/n8nio/n8n` |
| Port | 5678 |
| Volume | `n8n_data:/home/node/.n8n` |

```bash
# Access UI
open http://localhost:5678

# Default credentials in .env:
# N8N_BASIC_AUTH_USER / N8N_BASIC_AUTH_PASSWORD
```

#### Open WebUI (Profile: `chat`)

ChatGPT-like web interface for local and cloud models.

| Property | Value |
|----------|-------|
| Image | `ghcr.io/open-webui/open-webui:main` |
| Port | 3000 |
| Volume | `open_webui_data:/app/backend/data` |

```bash
# Start
docker compose --profile chat up -d

# Access UI
open http://localhost:3000
```

**Configuration:**
1. Create admin account on first visit
2. Settings → Connections:
   - Ollama URL: `http://ollama:11434`
   - OpenAI URL: `http://mcp-gateway:9011/v1` (if using MCP gateway)

#### nginx-ssl (Profile: `ssl`)

HTTPS termination with Let's Encrypt.

| Property | Value |
|----------|-------|
| Ports | 443, 80 |
| Volumes | SSL certs, webroot |

```bash
docker compose --profile ssl up -d
```

### Optional: kali-nmap (Profile: `scan`)

Network scanning with Kali Linux tools.

| Property | Value |
|----------|-------|
| Image | Custom Kali |
| Network | Host mode |
| Privileged | Yes |

```bash
docker compose --profile scan up -d
docker exec -it kali-nmap nmap -sV 192.168.1.0/24
```

## Profiles

| Profile | Services | Memory | Use Case |
|---------|----------|--------|----------|
| (none) | 9 services | ~4GB | Core operations |
| `local-llm` | +ollama | +4-8GB | Local LLM |
| `chat` | +open-webui | +512MB | Web chat UI |
| `ssl` | +nginx-ssl | +64MB | HTTPS |
| `scan` | +kali-nmap | +1GB | Network scanning |

```bash
# Combine profiles
docker compose --profile local-llm --profile chat up -d

# List active services
docker compose --profile local-llm --profile chat config --services
```

## Networking

All services connect to `oberaconnect-network` (bridge mode).

**Internal DNS:**
- Services resolve each other by container name
- Example: `http://rag-engine:8080` from agents service

**External Access:**
| Service | External Port | Binding |
|---------|---------------|---------|
| gateway | 8080 | 0.0.0.0 |
| n8n | 5678 | 0.0.0.0 |
| qdrant | 6333-6334 | 0.0.0.0 |
| postgres | 5432 | 127.0.0.1 |
| ollama | 11434 | 0.0.0.0 |
| open-webui | 3000 | 0.0.0.0 |

## Volumes

| Volume | Service | Purpose |
|--------|---------|---------|
| postgres_data | postgres | Database files |
| qdrant_storage | qdrant | Vector data |
| qdrant_snapshots | qdrant | Backups |
| n8n_data | n8n | Workflows, credentials |
| ollama_models | ollama | Downloaded models |
| open_webui_data | open-webui | Chat history, settings |

```bash
# List volumes
docker volume ls | grep oberaconnect

# Backup a volume
docker run --rm -v qdrant_storage:/data -v $(pwd):/backup alpine \
  tar czf /backup/qdrant_backup.tar.gz /data

# Volume sizes
docker system df -v | grep -E "VOLUME|oberaconnect"
```

## Environment Variables

See `.env.example` for all variables. Key ones:

| Variable | Service | Required |
|----------|---------|----------|
| POSTGRES_PASSWORD | postgres | Yes |
| QDRANT_API_KEY | qdrant, services | Yes |
| ANTHROPIC_API_KEY | services | Yes |
| AZURE_TENANT_ID | services | For Azure |
| AZURE_CLIENT_ID | services | For Azure |
| AZURE_CLIENT_SECRET | services | For Azure |
| N8N_BASIC_AUTH_PASSWORD | n8n | Yes |
| N8N_ENCRYPTION_KEY | n8n | Yes |

## Health Checks

All services have health checks configured:

```bash
# Check all services
docker compose ps

# Individual health
docker inspect --format='{{.State.Health.Status}}' gateway

# Health endpoint
curl http://localhost:8080/health
```

## Scaling

Services can be scaled horizontally (except postgres, qdrant):

```bash
# Scale rag-engine to 3 instances
docker compose up -d --scale rag-engine=3

# Note: Requires load balancer config changes
```

## Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f rag-engine

# Last 100 lines
docker compose logs --tail=100 gateway

# With timestamps
docker compose logs -t gateway
```

## Maintenance

### Update Images

```bash
# Pull latest images
docker compose pull

# Recreate with new images
docker compose up -d

# For profile services
docker compose --profile local-llm pull ollama
docker compose --profile local-llm up -d ollama
```

### Cleanup

```bash
# Remove stopped containers
docker compose down

# Remove containers + volumes (DESTRUCTIVE)
docker compose down -v

# Prune unused images
docker image prune -a

# Prune everything unused
docker system prune -a
```

### Backup

```bash
# Stop services
docker compose stop

# Backup all volumes
for vol in postgres_data qdrant_storage n8n_data; do
  docker run --rm -v ${vol}:/data -v $(pwd)/backups:/backup alpine \
    tar czf /backup/${vol}_$(date +%Y%m%d).tar.gz /data
done

# Start services
docker compose up -d
```

## Troubleshooting

### Service won't start

```bash
# Check logs
docker compose logs <service>

# Check config
docker compose config

# Validate compose file
docker compose config --quiet
```

### Port conflict

```bash
# Find what's using a port
lsof -i :8080
netstat -tlnp | grep 8080

# Kill process or change port in compose
```

### Out of memory

```bash
# Check usage
docker stats --no-stream

# Limit memory per service (add to compose)
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

### GPU not detected

```bash
# Verify NVIDIA runtime
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi

# Check Docker daemon config
cat /etc/docker/daemon.json
# Should contain: "default-runtime": "nvidia"
```
