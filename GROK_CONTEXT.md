# Grok AI Context Document

This document provides Grok with context about all tools, agents, and capabilities in the OberaConnect AI Operations repository.

---

## Quick Summary

**What this repo does:** Centralized AI automation infrastructure for OberaConnect MSP operations.

**Key capabilities:**
- Multi-AI orchestration (Claude, Gemini, Grok)
- Network device management (UniFi, MikroTik, SonicWall)
- RMM integration (NinjaOne)
- Azure/M365 automation
- n8n workflow orchestration

---

## Repository Structure

```
oberaconnect-ai-ops/
├── core/                    # Core AI frameworks
├── projects/                # Specialized tools
├── skills/                  # Claude CLI skills & agents
├── templates/               # Config templates
├── n8n-workflows/           # Exported n8n workflows
├── scripts/                 # Standalone scripts
└── config/                  # Configuration files
```

---

## Agent System (NEW - January 2025)

**Location:** `/skills/agents/`

A team of specialized AI helpers that make Claude better at specific tasks.

### Available Agents

| Agent | Purpose | Speed |
|-------|---------|-------|
| **Explorer** | Find files and code quickly | Fast |
| **Planner** | Think through projects before building | Balanced |
| **Commander** | Run terminal commands (git, npm, etc.) | Fast |
| **Researcher** | Dig deep on complex questions | Balanced |
| **Guide** | Answer Claude Code questions | Fast |
| **Integrations** | Manage external service connections | Balanced |
| **Strategist** | Business planning and decisions | Thorough |

### Agent Files

```
skills/agents/
├── QUICKSTART.md           # 2-minute user guide
├── README.md               # Overview and team list
├── TROUBLESHOOTING.md      # FAQ and common issues
├── SETUP.md                # Advanced setup (CLI, hooks)
├── cli.py                  # CLI tool for managing agents
├── loader.py               # Python module for loading agents
├── hooks.py                # Claude Code hook integration
├── requirements.txt        # Python dependencies (pyyaml)
├── explore/agent.yaml      # Explorer agent config
├── plan/agent.yaml         # Planner agent config
├── bash/agent.yaml         # Commander agent config
├── general-purpose/agent.yaml  # Researcher agent config
├── claude-code-guide/agent.yaml    # Guide agent config
├── mcp-integration-overseer/agent.yaml  # Integrations agent config
└── strategic-business-analyst/agent.yaml  # Strategist agent config
```

### Using Agents

**From Claude Code:**
- `/agents` - List all agents
- `/agent-show explorer` - Learn about an agent
- `/agent-suggest "my task"` - Get recommendation

**From CLI:**
```bash
cd skills/agents
python3 cli.py list
python3 cli.py show explorer
python3 cli.py suggest "find the login page"
```

---

## Core Frameworks

### 1. Multi-AI Orchestrator
**Location:** `/core/multi-ai-orchestrator/`

CLI tool for coordinating multiple AI providers.

### 2. Secondbrain 5-Layer AI OS
**Location:** `/core/Secondbrain/`

```
Layer 1: Interface      - webhooks, api, cli
Layer 2: Intelligence   - classifier, router, ml
Layer 3: Orchestration  - pipeline, scheduler, state
Layer 4: Agents         - claude, gemini, base agents
Layer 5: Resources      - mcp_manager, data_store
```

### 3. OberaAI Strategy
**Location:** `/core/OberaAIStrategy/`

Daily strategy aggregation from multiple AI sources.

---

## Projects & Tools

### Network Tools
| Project | Location | Purpose |
|---------|----------|---------|
| network-config-builder | `/projects/network-config-builder/` | MikroTik/SonicWall config generators |
| Nmap_Project | `/projects/Nmap_Project/` | Network scanning |
| NetworkScannerSuite | `/projects/NetworkScannerSuite/` | Scanner service |
| network-troubleshooting-tool | `/projects/network-troubleshooting-tool/` | Diagnostics |

### Azure/Cloud
| Project | Location | Purpose |
|---------|----------|---------|
| Azure_Projects | `/projects/Azure_Projects/` | Azure automation |
| Setco_Migration | `/projects/Setco_Migration/` | Migration scripts |

### Assessments
| Project | Location | Purpose |
|---------|----------|---------|
| Assessment | `/projects/Assessment/` | Security assessments |

---

## Skills (Claude CLI)

**Location:** `/skills/`

| Skill | Purpose |
|-------|---------|
| agents/ | Agent management system (NEW) |
| unifi-fleet/ | UniFi fleet management |
| ninjaone/ | NinjaOne RMM integration |
| notion-dashboards/ | Notion dashboard tools |
| n8n-secondbrain/ | n8n workflow integration |
| siem-integration/ | SIEM platform (TBD) |

---

## Templates

**Location:** `/templates/`

Configuration templates for:
- MikroTik routers
- UniFi devices
- SonicWall firewalls

---

## n8n Workflows

**Location:** `/n8n-workflows/`

Exported n8n workflow definitions for automation orchestration.

---

## MCP Servers (Model Context Protocol)

The following MCP servers are configured:

| Server | Purpose |
|--------|---------|
| oberaconnect | UniFi + NinjaOne fleet management |
| azure-m365 | Azure AD, SharePoint, Graph API |

### MCP Tools Available

**UniFi Tools:**
- `unifi_fleet_summary` - Fleet statistics
- `unifi_search_sites` - Search/filter sites
- `unifi_site_status` - Specific site details
- `unifi_offline_devices` - List offline devices
- `unifi_query` - Natural language queries

**NinjaOne Tools:**
- `ninjaone_fleet_summary` - Fleet statistics
- `ninjaone_search_devices` - Search devices
- `ninjaone_get_alerts` - Get alerts
- `ninjaone_patch_report` - Patch compliance

**Combined Tools:**
- `oberaconnect_morning_check` - Daily health check
- `oberaconnect_site_status` - Combined site status
- `oberaconnect_incident_context` - Incident response
- `oberaconnect_fleet_comparison` - Fleet comparison

**Azure/M365 Tools:**
- `list_tenants` / `switch_tenant` - Tenant management
- `list_users` / `search_users` / `get_user` - User management
- `list_groups` / `get_group_members` - Group management
- `list_app_registrations` - App registrations
- `list_sharepoint_sites` - SharePoint sites
- `graph_api_call` - Generic Graph API

---

## Slash Commands (Claude Code)

| Command | Purpose |
|---------|---------|
| `/agents` | List AI agents |
| `/agent-show` | Show agent details |
| `/agent-suggest` | Get agent recommendation |
| `/morning-check` | Daily health check |
| `/unifi-status` | UniFi fleet status |
| `/ninjaone-status` | NinjaOne device status |
| `/site-status` | Combined site status |
| `/incident-response` | Incident context gathering |
| `/fleet-compare` | Compare UniFi vs NinjaOne |
| `/health-check` | MCP server health |
| `/azure-switch` | Switch Azure tenants |
| `/azure-users` | List Azure users |
| `/azure-groups` | List Azure groups |
| `/azure-apps` | List app registrations |
| `/sharepoint-sites` | List SharePoint sites |
| `/network-config` | Generate network configs |
| `/nmap-scan` | Run network scans |
| `/keeper` | Query Keeper vault |

---

## For Grok: Key Integration Points

### 1. Where to Find Code
- Agent definitions: `/skills/agents/*/agent.yaml`
- MCP server: Look for `oberaconnect` MCP tools
- Network tools: `/projects/network-config-builder/`

### 2. How to Run Things
```bash
# Agent CLI
python3 skills/agents/cli.py list

# Network config builder
python3 projects/network-config-builder/main.py
```

### 3. Key APIs Used
- UniFi Site Manager API (cloudaccess.svc.ui.com)
- NinjaOne API (app.ninjarmm.com)
- Microsoft Graph API (graph.microsoft.com)

### 4. Architecture Patterns
- 5-Layer AI OS pattern (Secondbrain)
- Maker/Checker pattern for validation
- MCP for tool integration with Claude

---

## Recent Changes (January 2025)

1. **Agent System Added** - 7 specialized agents for Claude Code
2. **User-Friendly Documentation** - QUICKSTART, TROUBLESHOOTING guides
3. **Slash Commands** - /agents, /agent-show, /agent-suggest
4. **CLI Tool** - Python-based agent management

---

## Questions for Grok

When reviewing this repository, consider:

1. Is the agent architecture scalable?
2. Are there redundancies between agents and skills?
3. What's missing for production MSP operations?
4. How should Grok integrate with this system?
