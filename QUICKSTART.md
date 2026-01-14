# OberaConnect Quick Start Guide

Get the OberaConnect AI Operations stack running in 5 minutes.

## Prerequisites

- Docker Engine 24+ with Compose V2
- 8GB RAM minimum (16GB recommended)
- Git

```bash
# Verify Docker
docker --version   # Docker version 24.0+
docker compose version  # Docker Compose version v2.0+
```

## Step 1: Clone and Configure (1 min)

```bash
git clone https://github.com/jerm71279/oberaconnect-ai-ops.git
cd oberaconnect-ai-ops
cp .env.example .env
```

## Step 2: Set Required Secrets (2 min)

Edit `.env` and set these minimum values:

```bash
# Generate secrets (run each, copy output to .env)
openssl rand -hex 32  # → POSTGRES_PASSWORD
openssl rand -hex 32  # → QDRANT_API_KEY
openssl rand -hex 24  # → SECONDBRAIN_API_KEY

# Required API key
ANTHROPIC_API_KEY=sk-ant-api03-...  # From console.anthropic.com
```

## Step 3: Start Core Services (1 min)

```bash
docker compose up -d
```

## Step 4: Verify (1 min)

```bash
# Check all services are running
docker compose ps

# Test gateway
curl http://localhost:8080/health
# Expected: {"status": "healthy", "gateway": "nginx"}

# List available services
curl http://localhost:8080/api/services
```

## You're Done!

Core services are now running:

| Service | URL | Purpose |
|---------|-----|---------|
| Gateway | http://localhost:8080 | API routing |
| n8n | http://localhost:5678 | Workflow automation |
| Qdrant | http://localhost:6333 | Vector database |

---

## Optional: Add Local LLM

Run AI models locally instead of paying for API calls.

**Requires:** NVIDIA GPU + [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

```bash
# Start Ollama
docker compose --profile local-llm up -d

# Pull a model (one-time, ~4GB download)
docker exec ollama ollama pull llama3.2

# Test
curl http://localhost:11434/api/tags
```

## Optional: Add Chat UI

Get a ChatGPT-like web interface.

```bash
docker compose --profile chat up -d

# Open in browser
open http://localhost:3000
```

First-time setup:
1. Create admin account
2. Settings → Connections → Ollama URL: `http://ollama:11434`
3. Start chatting with local models

## Optional: Full Stack

Run everything:

```bash
docker compose --profile local-llm --profile chat up -d
```

---

## Common Commands

```bash
# Start/stop
docker compose up -d
docker compose down

# View logs
docker compose logs -f gateway
docker compose logs -f --tail=50

# Restart a service
docker compose restart rag-engine

# Rebuild after code changes
docker compose up -d --build

# Check resource usage
docker stats
```

## Troubleshooting

### Services won't start

```bash
# Check for port conflicts
docker compose ps
netstat -tlnp | grep -E '8080|5678|6333'

# View startup errors
docker compose logs gateway
```

### GPU not detected (Ollama)

```bash
# Verify NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi

# If fails, install nvidia-container-toolkit
# See: README.md → GPU Setup
```

### Out of memory

```bash
# Check memory usage
docker stats --no-stream

# Reduce services (stop non-essential)
docker compose stop call-flow engineering-api
```

## Next Steps

- Read [README.md](./README.md) for full architecture overview
- Read [docs/DOCKER.md](./docs/DOCKER.md) for service details
- Configure Azure/M365 integration in `.env`
- Set up n8n workflows at http://localhost:5678
