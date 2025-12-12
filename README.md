# OberaConnect AI Operations Infrastructure

Centralized AI automation infrastructure for OberaConnect MSP operations.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    External Triggers                         │
│              (Slack / Webhooks / Schedules)                 │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    n8n Orchestrator                          │
│                  (Azure DevEnvironment)                      │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Secondbrain 5-Layer AI OS                       │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Interface      │ webhooks, api, cli               │
│  Layer 2: Intelligence   │ classifier, router, ml           │
│  Layer 3: Orchestration  │ pipeline, scheduler, state       │
│  Layer 4: Agents         │ claude, gemini, base agents      │
│  Layer 5: Resources      │ mcp_manager, data_store          │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure                             │
│        (UniFi / MikroTik / Azure / Customer Networks)       │
└─────────────────────────────────────────────────────────────┘
```

## Repository Structure

```
oberaconnect-ai-ops/
├── core/                          # Core AI frameworks
│   ├── multi-ai-orchestrator/     # MAI CLI tool
│   ├── Secondbrain/               # 5-layer AI OS
│   └── OberaAIStrategy/           # Daily strategy aggregation
├── projects/                      # Specialized tools
│   ├── network-config-builder/    # MikroTik/SonicWall generators
│   ├── Nmap_Project/              # Network scanning
│   ├── NetworkScannerSuite/       # Scanner service
│   ├── network-troubleshooting-tool/
│   ├── Assessment/                # Security assessments
│   ├── Azure_Projects/            # Azure automation
│   └── Setco_Migration/           # Migration scripts
├── skills/                        # Claude CLI skills
│   └── siem-integration/          # Future SIEM platform (TBD)
├── templates/                     # Config templates
│   ├── mikrotik/
│   ├── unifi/
│   └── sonicwall/
├── n8n-workflows/                 # Exported n8n workflows
├── config/                        # Configuration files
│   └── claude/                    # Claude CLI settings
├── scripts/                       # Standalone scripts
│   ├── bash/
│   ├── python/
│   └── powershell/
└── docs/                          # Documentation
    ├── customers/
    └── reference-scans/
```

## Deployment

### Azure DevEnvironment

```bash
# Clone repository
git clone https://github.com/jerm71279/oberaconnect-ai-ops.git ~/oberaconnect-ai-ops

# Run bootstrap
chmod +x azure-bootstrap.sh
./azure-bootstrap.sh

# Authenticate Claude CLI
claude

# Start n8n
sudo systemctl start n8n
```

### Development Workflow

1. Develop/test in WSL
2. Commit and push to GitHub
3. Pull on Azure: `cd ~/oberaconnect-ai-ops && git pull`

## Key Components

| Component | Purpose |
|-----------|---------|
| **Secondbrain** | 5-layer AI OS for intelligent automation |
| **multi-ai-orchestrator** | CLI for multi-AI workflows |
| **network-config-builder** | MikroTik/SonicWall config generation |
| **siem-integration** | Future SIEM platform integration (TBD) |

## n8n Integration

n8n connects to the AI infrastructure via SSH, executing commands through the Secondbrain pipeline or directly via Claude CLI.

## License

Proprietary - OberaConnect Internal Use Only
