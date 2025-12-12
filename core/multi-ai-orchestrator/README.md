# Multi-AI CLI Orchestrator

[![CI](https://github.com/jerm71279/multi-ai-orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/jerm71279/multi-ai-orchestrator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Unified orchestration framework for Claude CLI, Gemini CLI, and Fara-7B. Chain multiple AI tools together for complex MSP workflows.

**Author:** Jeremy Smith ([@jerm71279](https://github.com/jerm71279)) / OberaConnect

## Quick Start

```bash
# Check available providers
./mai status

# Run quick task with auto-selected provider
./mai run "Generate a MikroTik firewall config for 192.168.1.0/24"

# Run with specific provider
./mai run --provider gemini --file large_log.txt "Analyze this log"

# Run pre-built workflow
./mai workflow customer_onboarding --customer "Acme Corp" --portal-url https://...
```

## Provider Matrix

| Use Case | Claude | Gemini | Fara-7B |
|----------|--------|--------|---------|
| Code generation/refactoring | ✅ Primary | ✅ Good | ❌ |
| Agentic coding (multi-file) | ✅ Primary | ⚠️ Limited | ❌ |
| Web UI automation | ❌ | ❌ | ✅ Primary |
| Portal automation (no API) | ❌ | ❌ | ✅ Primary |
| Long docs (1M+ tokens) | ⚠️ 200K | ✅ Primary | ❌ |
| Video/audio analysis | ❌ | ✅ Primary | ❌ |
| Complex reasoning | ✅ Primary | ✅ Good | ❌ |
| Local/air-gapped | ❌ Cloud | ❌ Cloud | ✅ On-device |
| Sensitive data | ⚠️ Cloud | ⚠️ Cloud | ✅ Local |
| Config generation | ✅ Primary | ✅ Good | ❌ |
| Network scripting | ✅ Primary | ✅ Good | ❌ |

## Installation

### Prerequisites

1. **Claude CLI** - [Install instructions](https://docs.anthropic.com/claude-cli)
   ```bash
   npm install -g @anthropic-ai/claude-cli
   claude auth
   ```

2. **Gemini CLI** - [Install instructions](https://github.com/google/gemini-cli)
   ```bash
   npm install -g @google/gemini-cli
   gemini auth
   ```

3. **Fara-7B** - [Install instructions](https://github.com/microsoft/fara)
   ```bash
   git clone https://github.com/microsoft/fara.git ~/fara
   cd ~/fara
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   playwright install
   ```

### Setup Orchestrator

```bash
cd multi-ai-orchestrator
chmod +x mai
pip install -r requirements.txt  # if any dependencies needed
```

## Usage

### Single Tasks

```bash
# Auto-select best provider
./mai run "Explain Kubernetes pod networking"

# Force specific provider
./mai run --provider claude "Write a Python decorator for retry logic"
./mai run --provider gemini --file video.mp4 "Summarize this video"
./mai run --provider fara --url https://azure.portal.com "Navigate to VM settings"

# With files
./mai run --provider gemini --file log1.txt --file log2.txt "Correlate errors"

# With output file
./mai run "Generate bash backup script" -o backup.sh
```

### Pre-Built Workflows

```bash
# List available workflows
./mai workflow --list

# Customer onboarding
./mai workflow customer_onboarding \
  --customer "Acme Corp" \
  --portal-url https://vendor.portal.com/customers \
  --deployment-type standard

# Vendor data extraction
./mai workflow vendor_data_extraction \
  --vendor "Microsoft" \
  --portal-url https://partner.microsoft.com \
  --data-type licensing

# Incident analysis
./mai workflow incident_analysis \
  --incident-id INC-2024-0042 \
  --log-files /var/log/syslog /var/log/auth.log \
  --systems firewall webserver database

# Azure deployment
./mai workflow azure_service_deployment \
  --service "LogAnalytics" \
  --environment lab \
  --portal-automation

# SOP capture
./mai workflow sop_from_portal \
  --sop-name "Create Azure VM" \
  --portal-url https://portal.azure.com \
  --task "Create a new Windows Server 2022 VM with 4 vCPUs"

# Price comparison
./mai workflow vendor_price_comparison \
  --product "Ubiquiti U6-Pro" \
  --vendor-urls https://store.ui.com https://amazon.com https://bhphoto.com
```

### Custom Chains (JSON)

```bash
./mai chain '{
  "steps": [
    {
      "name": "extract_data",
      "provider": "fara",
      "prompt": "Go to {url} and extract pricing table"
    },
    {
      "name": "analyze",
      "provider": "claude", 
      "prompt": "Analyze this data: {extract_data}"
    }
  ],
  "context": {
    "url": "https://example.com/pricing"
  }
}'
```

## Workflow Details

### Customer Onboarding

**Pipeline:**
```
Fara (portal extraction) → Claude (MikroTik config) → Claude (UniFi config) 
→ Claude (Azure Bicep) → Claude (documentation)
```

**Outputs:**
- MikroTik RouterOS configuration
- UniFi site configuration (JSON)
- Azure Bicep templates
- Onboarding documentation (Markdown)

### Incident Analysis

**Pipeline:**
```
Gemini (large log analysis) → Claude (correlation) → Claude (remediation scripts)
→ Claude (incident report)
```

**Outputs:**
- Timeline analysis
- Root cause determination
- Bash remediation scripts
- Formal incident report

### SOP from Portal

**Pipeline:**
```
Fara (execute & capture workflow) → Claude (generate SOP)
```

**Outputs:**
- Screenshots of each step
- Scribe-formatted SOP document

## Architecture

```
multi-ai-orchestrator/
├── mai                          # Main CLI entry point
├── lib/
│   ├── __init__.py
│   ├── ai_clients.py           # Provider wrappers
│   └── orchestrator.py         # Pipeline engine
├── workflows/
│   └── oberaconnect_workflows.py  # Pre-built pipelines
├── config/
│   └── settings.json           # Configuration
├── output/                     # Workflow outputs
├── logs/                       # Execution logs
└── README.md
```

## Configuration

Edit `config/settings.json`:

```json
{
  "providers": {
    "claude": {
      "enabled": true,
      "model": "sonnet",
      "timeout": 300
    },
    "gemini": {
      "enabled": true,
      "model": "gemini-2.5-pro",
      "timeout": 600
    },
    "fara": {
      "enabled": true,
      "sandbox": true,
      "max_steps": 50
    }
  }
}
```

## Creating Custom Workflows

```python
from lib import PipelineBuilder, AIProvider

pipeline = (
    PipelineBuilder("my_workflow")
    .description("Custom workflow description")
    
    # Fara step for web automation
    .fara_step(
        name="extract_data",
        task="Navigate to {url} and extract data",
        provider_options={"url": "https://example.com"}
    )
    
    # Claude step for processing
    .claude_step(
        name="process_data",
        prompt="Process this data: {extract_data}\nGenerate a report."
    )
    
    # Gemini step for large file analysis
    .gemini_step(
        name="analyze_logs",
        prompt="Analyze the log files for patterns",
        provider_options={"files": ["/var/log/syslog"]}
    )
    
    .build()
)

result = pipeline.execute({"url": "https://example.com"})
print(result.outputs)
```

## Orchestration Patterns

### Pattern 1: Portal → Config

```
Fara (extract from portal) → Claude (generate config)
```

Best for: Customer onboarding, vendor data extraction

### Pattern 2: Large File → Analysis → Scripts

```
Gemini (analyze large files) → Claude (generate scripts)
```

Best for: Log analysis, incident response

### Pattern 3: Capture → Document

```
Fara (capture workflow) → Claude (generate documentation)
```

Best for: SOP creation, training materials

### Pattern 4: Multi-Source Comparison

```
Fara (site 1) + Fara (site 2) + Fara (site 3) → Claude (compare & recommend)
```

Best for: Price comparison, vendor evaluation

## Error Handling

- Automatic retry with exponential backoff
- Per-step timeout configuration
- Conditional step execution
- Detailed error logging
- Result persistence (JSON)

## Output Management

All workflow outputs are saved to:
- `./output/` - Working directory
- `./output/customers/{name}/` - Customer-specific archives
- `./logs/` - Execution logs

## Contributing

1. Add new workflows to `workflows/oberaconnect_workflows.py`
2. Follow the `PipelineBuilder` pattern
3. Document inputs/outputs
4. Add CLI arguments in `mai`

## License

Internal use - OberaConnect Engineering
