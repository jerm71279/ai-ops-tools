# Secondbrain Docker Containers

This directory contains Docker configurations for running Secondbrain tools as containerized microservices.

## Container Architecture

| Container | Port | Description | Tools |
|-----------|------|-------------|-------|
| `data-processing` | 8081 | Data import/sync | sharepoint_importer, slack_importer, slab_importer |
| `rag-engine` | 8082 | RAG queries | query_brain, vector_store, rag_web |
| `engineering-api` | 8083 | Engineering tracking | engineering_tracker, daily_summary |
| `call-flow` | 8084 | Call flow processing | call_flow_processor, call_flow_web |
| `agents` | 8085 | AI agents | agent_orchestrator, mcp_obsidian_server |
| `gateway` | 8080 | API gateway | nginx reverse proxy |

## Quick Start (Local Development)

1. **Copy environment file:**
   ```bash
   cp docker/.env.example .env
   # Edit .env with your API keys
   ```

2. **Build and start all containers:**
   ```bash
   docker-compose up -d --build
   ```

3. **Check health:**
   ```bash
   curl http://localhost:8080/health
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

## API Endpoints

### Gateway (port 8080)
- `GET /health` - Gateway health check
- `GET /api/services` - List all services

### Data Processing (port 8081)
- `GET /api/data/health` - Health check
- `GET /api/data/tools` - List available tools
- `POST /api/data/run/<tool>` - Run a tool
- `GET /api/data/jobs` - List running jobs
- `GET /api/data/jobs/<id>` - Get job status

### RAG Engine (port 8082)
- `GET /api/rag/health` - Health check
- `POST /api/rag/query` - Query the knowledge base
- `POST /api/rag/index` - Index new documents

### Engineering API (port 8083)
- `GET /api/engineering/health` - Health check
- `POST /api/engineering/summary/send` - Send daily summary email
- `POST /api/engineering/run/<tool>` - Run engineering tool

### Call Flow (port 8084)
- `GET /api/callflow/health` - Health check
- Web UI available at http://localhost:8084

### Agents (port 8085)
- `GET /api/agents/health` - Health check
- `GET /api/agents/agents` - List available agents
- `POST /api/agents/orchestrate` - Submit task to orchestrator
- `POST /api/agents/agents/<name>/run` - Run specific agent

## Deploy to Azure Container Apps

1. **Ensure Azure CLI is installed and logged in:**
   ```bash
   az login
   ```

2. **Set environment variables in .env**

3. **Run deployment script:**
   ```bash
   ./docker/azure/deploy.sh
   ```

## Container Management

```bash
# Start specific service
docker-compose up -d rag-engine

# Rebuild specific service
docker-compose up -d --build engineering-api

# Stop all
docker-compose down

# View logs for specific service
docker-compose logs -f agents

# Shell into container
docker exec -it sb-rag-engine /bin/bash
```

## Estimated Azure Costs

| Service | Configuration | Est. Monthly Cost |
|---------|--------------|-------------------|
| Container Apps Environment | Consumption tier | $0 (free tier) |
| data-processing | 0.5 vCPU, 1GB, scale 0-3 | ~$5 |
| rag-engine | 1 vCPU, 2GB, scale 1-5 | ~$15 |
| engineering-api | 0.5 vCPU, 1GB, scale 0-3 | ~$5 |
| call-flow | 0.5 vCPU, 1GB, scale 0-2 | ~$3 |
| agents | 0.5 vCPU, 1GB, scale 0-2 | ~$3 |
| **Total** | | **~$30/month** |

*Costs vary based on usage. Scale-to-zero significantly reduces costs when idle.*
