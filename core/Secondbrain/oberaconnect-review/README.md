# OberaConnect AI Operations Platform

Unified tooling for OberaConnect MSP operations - combining UniFi fleet management, NinjaOne integration, and AI-powered natural language querying.

## Architecture

```
oberaconnect-ai-ops/
├── oberaconnect-tools/          # Core Python library
│   ├── common/                  # Shared validation framework
│   │   ├── maker_checker.py     # Maker/checker pattern implementation
│   │   └── validators.py        # Reusable validation rules
│   ├── unifi/                   # UniFi Site Manager integration
│   │   ├── models.py            # Data models (UniFiSite, UniFiDevice)
│   │   ├── api_client.py        # Site Manager API client
│   │   ├── analyzer.py          # Natural language query engine
│   │   ├── checkers.py          # UniFi-specific validation rules
│   │   └── cli.py               # Command-line interface
│   ├── ninjaone/                # NinjaOne RMM integration
│   │   ├── client.py            # NinjaOne API client
│   │   └── correlator.py        # Cross-platform correlation
│   └── n8n/                     # Workflow automation
│       └── webhook_api.py       # Flask REST endpoints
├── oberaconnect-mcp/            # Claude Code MCP server
│   └── src/
│       └── server.py            # MCP tool definitions
└── dashboard/                   # Web UI
    ├── index.html               # Interactive dashboard
    └── analyzer.js              # JavaScript query engine
```

## Quick Start

### Install Core Library
```bash
cd oberaconnect-tools
pip install -e .
```

### Run UniFi CLI
```bash
# Demo mode (no API credentials needed)
python -m unifi.cli --demo --query "summary"
python -m unifi.cli --demo --query "sites with more than 3 offline devices"
python -m unifi.cli --demo  # Interactive mode

# Production mode
export UNIFI_API_TOKEN="your-token"
python -m unifi.cli --query "show offline APs"
```

### Run MCP Server (for Claude Code)
```bash
cd oberaconnect-mcp
pip install -e .
# Add to Claude Code config per documentation
```

## Features

### UniFi Fleet Query Engine
Natural language queries across 98+ customer sites:
- "Show sites with offline devices"
- "Which sites have more than 100 clients?"
- "Top 5 sites by firmware age"
- "Group sites by ISP"
- "What's the fleet health summary?"

### Maker/Checker Validation
Built-in safety checks for high-risk operations:
- Risk levels: LOW, MEDIUM, HIGH, CRITICAL
- Automatic escalation for bulk operations (>10 sites)
- Rollback plan requirements for critical changes
- SSID, VLAN, and firewall rule validation

### NinjaOne Correlation
Cross-reference network issues with endpoint alerts:
- AP down + endpoint connectivity correlation
- Customer-scoped incident context
- Unified alerting across platforms

### n8n Integration
REST API endpoints for workflow automation:
- POST /api/unifi/query - Natural language queries
- POST /api/unifi/validate - Pre-flight checks
- GET /api/health - System status

## OberaConnect Best Practices (Built-in)

Per memory, these validations are enforced:
- WiFi signal minimum: -65dBm
- 2.4GHz channels: 1, 6, 11 only
- VLAN 1 and 4095 reserved
- Open SSIDs blocked
- Permit-any firewall rules blocked
- Bulk operations (>10 sites) require confirmation
- HIGH/CRITICAL risk operations require rollback_plan

## Configuration

### Environment Variables
```bash
# UniFi Site Manager
UNIFI_API_TOKEN=your-api-token

# NinjaOne (optional)
NINJAONE_CLIENT_ID=your-client-id
NINJAONE_CLIENT_SECRET=your-client-secret

# n8n Webhook API (optional)
FLASK_SECRET_KEY=your-secret-key
```

### Demo Mode
All tools support `--demo` flag for testing without credentials.

## Development

### Run Tests
```bash
cd oberaconnect-tools
pytest tests/
```

### Project Structure
- `common/` - Shared code, import with `from oberaconnect_tools.common import ...`
- `unifi/` - UniFi-specific code
- `ninjaone/` - NinjaOne-specific code
- `n8n/` - Workflow automation endpoints

## License

Internal OberaConnect use only.

## Changelog

### v1.0.0 (December 2024)
- Consolidated UniFi Fleet Query Engine
- Added maker/checker validation framework
- NinjaOne correlation module
- MCP server for Claude Code
- Interactive web dashboard
