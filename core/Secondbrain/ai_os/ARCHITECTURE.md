# 5-Layer AI Operating System Architecture

## Overview

The AI Operating System (AI-OS) is a unified framework that coordinates multiple AI agents, tools, and resources to autonomously execute complex workflows. It provides a consistent abstraction layer over heterogeneous AI providers while maintaining intelligent routing, state management, and observability.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         5-LAYER AI OPERATING SYSTEM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 1: INTERFACE                                                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │   CLI    │  │   API    │  │  Webhook │  │  Event   │            │   │
│  │  │ Terminal │  │  REST    │  │ Handlers │  │ Triggers │            │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │   │
│  └───────┴─────────────┴─────────────┴─────────────┴────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 2: INTELLIGENCE                                               │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Mixture of Experts Router                  │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐  │   │   │
│  │  │  │ Intent  │  │ Task    │  │ Context │  │ Agent           │  │   │   │
│  │  │  │ Parser  │  │ Classi- │  │ Manager │  │ Selector        │  │   │   │
│  │  │  │         │  │ fier    │  │         │  │                 │  │   │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘  └─────────────────┘  │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────┬───────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 3: ORCHESTRATION                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │   │
│  │  │   Pipeline   │  │   Workflow   │  │      State Machine       │   │   │
│  │  │   Executor   │  │   Scheduler  │  │      (DAG Engine)        │   │   │
│  │  │              │  │              │  │                          │   │   │
│  │  │ • Sequential │  │ • Cron Jobs  │  │ • Checkpointing          │   │   │
│  │  │ • Parallel   │  │ • Triggers   │  │ • Rollback               │   │   │
│  │  │ • Branching  │  │ • Queues     │  │ • Resume                 │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘   │   │
│  └─────────────────────────────────┬───────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 4: AGENTS                                                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │  Claude  │  │  Gemini  │  │   Fara   │  │  Custom  │            │   │
│  │  │  Agent   │  │  Agent   │  │  Agent   │  │  Agents  │            │   │
│  │  │          │  │          │  │          │  │          │            │   │
│  │  │ • Code   │  │ • Large  │  │ • Web UI │  │ • BA     │            │   │
│  │  │ • Config │  │   Docs   │  │ • Portal │  │ • KB     │            │   │
│  │  │ • Reason │  │ • Video  │  │ • Scrape │  │ • Custom │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────┬───────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 5: RESOURCES                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  MCP Servers │  │  Data Stores │  │   External   │              │   │
│  │  │              │  │              │  │   Services   │              │   │
│  │  │ • Obsidian   │  │ • ChromaDB   │  │ • NinjaOne   │              │   │
│  │  │ • SharePoint │  │ • SQLite     │  │ • MS 365     │              │   │
│  │  │ • Keeper     │  │ • JSON State │  │ • Azure      │              │   │
│  │  │ • NotebookLM │  │ • File Store │  │ • SonicWall  │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Layer 1: Interface Layer
**Purpose:** Entry point for all interactions with the AI OS

- **CLI Terminal:** Direct command-line interaction
- **REST API:** Programmatic access for integrations
- **Webhook Handlers:** Event-driven triggers from external systems
- **Event Triggers:** Scheduled and reactive task initiation

**Key Components:**
- Request parser and validator
- Authentication/authorization
- Rate limiting
- Request logging and tracing

### Layer 2: Intelligence Layer
**Purpose:** Understand intent and route to optimal execution path

- **Intent Parser:** Natural language understanding of user requests
- **Task Classifier:** Categorize tasks by domain and complexity
- **Context Manager:** Maintain conversation/session context
- **Agent Selector:** MoE routing to best-fit agent(s)

**Key Components:**
- Mixture of Experts (MoE) Router
- Task taxonomy and classification models
- Context window management
- Multi-agent selection strategies

### Layer 3: Orchestration Layer
**Purpose:** Coordinate complex multi-step workflows

- **Pipeline Executor:** Sequential/parallel task execution
- **Workflow Scheduler:** Time-based and event-driven scheduling
- **State Machine:** DAG-based workflow management with checkpoints

**Key Components:**
- Directed Acyclic Graph (DAG) engine
- Checkpoint and rollback system
- Retry and error handling
- Progress tracking and reporting

### Layer 4: Agent Layer
**Purpose:** Specialized AI execution units

- **Claude Agent:** Code generation, configuration, reasoning
- **Gemini Agent:** Large document/video analysis
- **Fara Agent:** Web UI automation, portal interaction
- **Custom Agents:** Domain-specific (BA, Knowledge Base, etc.)

**Key Components:**
- Unified agent interface
- Provider-specific adapters
- Tool execution framework
- Output normalization

### Layer 5: Resource Layer
**Purpose:** Data persistence and external integrations

- **MCP Servers:** Model Context Protocol integrations
- **Data Stores:** Vector DB, state storage, file system
- **External Services:** Third-party API integrations

**Key Components:**
- Connection pooling
- Credential management
- Data caching
- Service health monitoring

## Data Flow

```
User Request
    │
    ▼
[Layer 1: Interface]
    │ Parse & Validate
    ▼
[Layer 2: Intelligence]
    │ Classify & Route
    ▼
[Layer 3: Orchestration]
    │ Build & Execute Pipeline
    ▼
[Layer 4: Agents]
    │ Execute Tasks
    ▼
[Layer 5: Resources]
    │ Store & Retrieve Data
    ▼
Response
```

## Key Design Principles

1. **Separation of Concerns:** Each layer has a single, well-defined responsibility
2. **Loose Coupling:** Layers communicate through defined interfaces
3. **Horizontal Scalability:** Each layer can scale independently
4. **Observability:** Full tracing, logging, and metrics at every layer
5. **Fault Tolerance:** Graceful degradation and automatic recovery
6. **Extensibility:** New agents, providers, and integrations are plug-and-play

## Configuration

```python
AI_OS_CONFIG = {
    "layer1_interface": {
        "api_port": 8080,
        "cli_enabled": True,
        "webhook_enabled": True
    },
    "layer2_intelligence": {
        "moe_model": "gemini-2.0-flash",
        "context_window": 32000,
        "classification_threshold": 0.7
    },
    "layer3_orchestration": {
        "max_parallel_pipelines": 5,
        "checkpoint_enabled": True,
        "retry_policy": {"max_retries": 3, "backoff": "exponential"}
    },
    "layer4_agents": {
        "claude": {"enabled": True, "model": "claude-sonnet-4-20250514"},
        "gemini": {"enabled": True, "model": "gemini-2.0-flash"},
        "fara": {"enabled": True, "headless": True}
    },
    "layer5_resources": {
        "vector_db": "chromadb",
        "state_store": "sqlite",
        "mcp_servers": ["obsidian", "sharepoint", "keeper"]
    }
}
```

## Implementation Status

| Layer | Component | Status |
|-------|-----------|--------|
| L1 | CLI Terminal | ✓ Complete |
| L1 | REST API | ✓ Complete (aiohttp with WebSocket) |
| L1 | Webhook Handlers | ✓ Complete (GitHub, Slack, NinjaOne) |
| L2 | Intent Parser | ✓ Complete (rule-based + ML) |
| L2 | MoE Router | ✓ Complete |
| L2 | Context Manager | ✓ Complete |
| L3 | Pipeline Executor | ✓ Complete |
| L3 | Workflow Scheduler | ✓ Complete |
| L3 | State Machine | ✓ Complete (DAG with checkpointing) |
| L4 | Claude Agent | ✓ Complete (Claude CLI integration) |
| L4 | Gemini Agent | ✓ Complete |
| L4 | Fara Agent | ✓ Complete |
| L4 | BA Agent | ✓ Complete |
| L4 | Obsidian Agent | ✓ Complete |
| L4 | NotebookLM Agent | ✓ Complete |
| L5 | MCP Servers | ✓ Complete (Obsidian, SharePoint, Keeper, NotebookLM) |
| L5 | ChromaDB | ✓ Complete |
| L5 | Data Store | ✓ Complete (SQLite + JSON state) |
| L5 | External Services | Partial (NinjaOne, MS 365 planned)

### Recent Updates (Dec 2024)
- **L3 State Machine**: Full DAG execution engine with:
  - Parallel node execution with semaphore control
  - Retry logic with exponential backoff
  - Conditional branching (ON_SUCCESS, ON_FAILURE, ON_CONDITION)
  - Persistent checkpointing to disk
  - Recovery from checkpoints

- **L1 REST API**: Full aiohttp-based HTTP server with:
  - Sync/async processing endpoints
  - Job queue management
  - WebSocket streaming support
  - CORS handling
  - OpenAPI 3.0 specification

- **L4 Claude Agent**: Fixed CLI integration with correct `--print` flag

- **L1 Webhook Handlers**: Full webhook support for:
  - GitHub (issues, PRs, comments)
  - Slack (messages, commands)
  - NinjaOne (alerts, tickets)
  - Custom webhooks with HMAC validation

- **L2 ML Intent Classification**: Semantic understanding using sentence embeddings:
  - Uses sentence-transformers (all-MiniLM-L6-v2 model)
  - Combines ML similarity with rule-based keyword matching
  - Handles synonyms, paraphrases, and new phrasings
  - Graceful fallback to rule-based when ML unavailable

## Quick Start

### Interactive CLI
```bash
# Start interactive session
python -m ai_os.run

# Or directly
./venv/bin/python3 ai_os/run.py
```

### Single Query
```bash
python -m ai_os.run "Search for Python notes in my knowledge base"
```

### API Server
```bash
# Start API server on port 8080
python -m ai_os.run --api

# With webhooks enabled
python -m ai_os.run --api --webhooks

# Custom port
python -m ai_os.run --api --port 9000
```

### API Endpoints
```
GET  /              - API info
GET  /health        - Health check
GET  /status        - System status
POST /process       - Process request (sync)
POST /process/async - Process request (async job)
GET  /jobs          - List async jobs
GET  /jobs/{id}     - Get job status
GET  /agents        - List available agents
GET  /workflows     - List workflows
GET  /ws            - WebSocket for streaming
GET  /openapi.json  - OpenAPI specification

# Webhooks (when enabled)
POST /webhooks/github   - GitHub webhook
POST /webhooks/slack    - Slack webhook
POST /webhooks/ninjaone - NinjaOne webhook
POST /webhooks/custom   - Custom webhook
GET  /webhooks          - List webhook endpoints
GET  /webhooks/history  - Recent webhook events
```

### Python Usage
```python
import asyncio
from ai_os import AIOS

async def main():
    ai_os = AIOS()
    await ai_os.initialize()

    # Process a request
    response = await ai_os.process("Generate a project status report")
    print(response.content)

    # Get system status
    status = ai_os.get_status()
    print(status)

    await ai_os.shutdown()

asyncio.run(main())
```
