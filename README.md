# OberaConnect AI Operations Infrastructure

Centralized AI automation infrastructure for OberaConnect MSP operations.

## Quick Start

```bash
# Clone and configure
git clone https://github.com/jerm71279/oberaconnect-ai-ops.git
cd oberaconnect-ai-ops
cp .env.example .env
# Edit .env with your API keys and secrets

# Start core services
docker compose up -d

# Add local LLM (optional - requires NVIDIA GPU)
docker compose --profile local-llm up -d
docker exec ollama ollama pull llama3.2

# Add chat UI (optional)
docker compose --profile chat up -d
# Open http://localhost:3000
```

## Architecture

### 5-Layer Docker Stack

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: UI/Interface                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Open WebUI │  │     n8n     │  │  Claude CLI │             │
│  │    :3000    │  │    :5678    │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: Orchestration                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              nginx gateway :8080                         │   │
│  │    /api/data  /api/rag  /api/agents  /api/ollama        │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: Services                                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │   data-    │ │    rag-    │ │engineering-│ │  call-flow │  │
│  │ processing │ │   engine   │ │    api     │ │            │  │
│  │   :8081    │ │   :8082    │ │   :8083    │ │   :8084    │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│  ┌────────────┐                                                │
│  │   agents   │  ← UniFi, NinjaOne, Azure MCP integrations    │
│  │   :8085    │                                                │
│  └────────────┘                                                │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Persistence                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ PostgreSQL  │  │   Qdrant    │  │  ChromaDB   │             │
│  │    :5432    │  │    :6333    │  │  (volumes)  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Models                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Ollama :11434 (local)  │  Claude/GPT APIs (cloud)      │   │
│  │  llama3.2, qwen2.5      │  via ANTHROPIC_API_KEY        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Docker Compose Profiles

| Profile | Services Added | Use Case |
|---------|----------------|----------|
| (default) | gateway, services, n8n, qdrant, postgres | Core stack |
| `local-llm` | ollama | Local LLM inference (NVIDIA GPU) |
| `chat` | open-webui | ChatGPT-like web interface |
| `ssl` | nginx-ssl | HTTPS termination |
| `scan` | kali-nmap | Network scanning tools |

```bash
# Examples
docker compose up -d                                    # Core only
docker compose --profile local-llm up -d               # + Ollama
docker compose --profile local-llm --profile chat up -d # + Chat UI
docker compose --profile ssl up -d                      # + HTTPS
```

## Repository Structure

```
oberaconnect-ai-ops/
├── docker-compose.yml            # Unified 13-service stack
├── .env.example                  # Environment template
├── core/                         # Core AI frameworks
│   ├── Secondbrain/              # 5-layer AI OS + Docker configs
│   │   ├── docker/               # Dockerfiles and nginx.conf
│   │   ├── ai_os/                # Python services
│   │   └── procedures/           # SOPs and workflows
│   ├── multi-ai-orchestrator/    # MAI CLI tool
│   └── OberaAIStrategy/          # Daily strategy aggregation
├── projects/                     # Specialized tools
│   ├── network-migration/        # MikroTik/SonicWall → UniFi
│   ├── network-config-builder/   # Multi-vendor config generators
│   ├── NetworkScannerSuite/      # NinjaOne-deployed scanner
│   ├── Nmap_Project/             # Network scanning + Kali Docker
│   ├── Assessment/               # Security assessments
│   ├── Azure_Projects/           # Azure backup/migration tools
│   └── network-troubleshooting-tool/
├── skills/                       # Claude CLI skills
│   └── n8n-secondbrain/          # n8n + Qdrant stack
├── templates/                    # Config templates
│   ├── mikrotik/
│   ├── unifi/
│   └── sonicwall/
├── config/                       # Configuration
│   └── claude/                   # Claude CLI settings + agents
├── scripts/                      # Standalone scripts
│   ├── bash/
│   ├── python/
│   └── powershell/
└── docs/                         # Documentation
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| gateway | 8080 | nginx API gateway with service routing |
| data-processing | 8081 | Document ingestion and processing |
| rag-engine | 8082 | RAG queries with vector search |
| engineering-api | 8083 | Engineering documentation API |
| call-flow | 8084 | Phone system call flow generation |
| agents | 8085 | AI agents (UniFi, NinjaOne, Azure MCP) |
| n8n | 5678 | Workflow automation |
| qdrant | 6333 | Vector database |
| postgres | 5432 | Relational database (chat persistence) |
| ollama | 11434 | Local LLM server (profile: local-llm) |
| open-webui | 3000 | Chat interface (profile: chat) |

## MCP Integrations

The agents service connects to external systems via MCP (Model Context Protocol):

- **UniFi Site Manager** - Fleet monitoring, site status, offline device tracking
- **NinjaOne RMM** - Device management, alerts, patch compliance
- **Azure/M365** - Users, groups, SharePoint, app registrations
- **Keeper Security** - Credential management (via CLI)

## Deployment

### Prerequisites

- Docker Engine 24+ with Compose V2
- NVIDIA Container Toolkit (for local-llm profile)
- 16GB+ RAM recommended

### Environment Setup

```bash
cp .env.example .env

# Generate secrets
openssl rand -hex 32  # For POSTGRES_PASSWORD, QDRANT_API_KEY, etc.

# Required API keys
# - ANTHROPIC_API_KEY from console.anthropic.com
# - AZURE_* from Azure portal app registration
```

### GPU Setup (for Ollama)

```bash
# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verify
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### Start Services

```bash
# Core services
docker compose up -d

# Check health
docker compose ps
curl http://localhost:8080/health
curl http://localhost:8080/api/services

# View logs
docker compose logs -f --tail=50
```

## Development

### Local Development (WSL)

```bash
cd ~/oberaconnect-ai-ops
# Make changes
git add . && git commit -m "Description"
git push origin main
```

### Azure DevEnvironment

```bash
cd ~/oberaconnect-ai-ops && git pull
docker compose up -d --build
```

## Documentation

- [QUICKSTART.md](./QUICKSTART.md) - Get running in 5 minutes
- [docs/DOCKER.md](./docs/DOCKER.md) - Docker architecture details
- [core/Secondbrain/README.md](./core/Secondbrain/README.md) - AI OS documentation
- [core/Secondbrain/RAG_USAGE_GUIDE.md](./core/Secondbrain/RAG_USAGE_GUIDE.md) - RAG system usage

## License

Proprietary - OberaConnect Internal Use Only
