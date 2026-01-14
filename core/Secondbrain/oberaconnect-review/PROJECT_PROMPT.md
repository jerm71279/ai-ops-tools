# OberaConnect MSP Operations Platform

## Project Overview

**OberaConnect-Tools** is a unified Python platform for Managed Service Provider (MSP) operations automation. It consolidates UniFi network management, NinjaOne RMM integration, and operational safety controls into a single, testable, production-ready system.

### Target Users
- **Network Engineers**: Fleet-wide UniFi management with natural language queries
- **Help Desk**: Quick site status checks and alert triage
- **NOC Team**: Morning health checks, incident response context
- **Management**: Fleet statistics, compliance reporting

---

## Purpose

### Problem Solved
MSPs managing 50+ customer sites face:
1. **Tool Sprawl**: Separate dashboards for UniFi, NinjaOne, ticketing, monitoring
2. **Manual Correlation**: "Is this network outage related to that server alert?"
3. **Human Error**: Bulk changes without safeguards cause multi-customer outages
4. **Knowledge Silos**: Senior engineers know the standards, but they're not codified

### Solution
A unified platform that:
- Queries fleet status in plain English ("show sites with offline APs")
- Enforces OberaConnect standards automatically (WiFi channels, signal strength, VLAN rules)
- Requires confirmation for risky operations (>10 sites, factory resets)
- Correlates UniFi network status with NinjaOne endpoint alerts

---

## Architecture

```
oberaconnect-tools/
├── common/
│   ├── maker_checker.py    # Risk-based validation framework
│   └── validators.py       # Input validation (VLAN, WiFi, IP)
├── unifi/
│   ├── api_client.py       # UniFi Site Manager API client
│   ├── analyzer.py         # Natural language query engine
│   ├── models.py           # UniFiSite, UniFiDevice, FleetSummary
│   ├── checkers.py         # OberaConnect standards validation
│   └── cli.py              # Command-line interface
├── ninjaone/
│   ├── client.py           # NinjaOne OAuth API client
│   └── correlator.py       # Cross-platform incident correlation
├── n8n/
│   └── webhook_api.py      # Flask REST endpoints for n8n workflows
└── tests/
    ├── test_unifi_models.py
    ├── test_analyzer.py
    ├── test_maker_checker.py
    ├── test_validators.py
    └── test_ninjaone_client.py

oberaconnect-mcp/
└── src/server.py           # MCP Server for Claude Code integration

dashboard/
├── index.html              # Visual fleet monitoring UI
└── analyzer.js             # Browser-based query engine
```

---

## Core Functionality

### 1. UniFi Fleet Management

#### Natural Language Queries
```python
from unifi.analyzer import UniFiAnalyzer

analyzer = UniFiAnalyzer(sites)

# Plain English queries
analyzer.analyze("top 10 sites by clients")
analyzer.analyze("sites with more than 3 offline devices")
analyzer.analyze("verizon sites with critical health")
analyzer.analyze("find setco")
analyzer.analyze("group by isp")
```

#### Health Score Calculation
Per OberaConnect formula:
- **40% weight**: Device availability (offline devices penalty)
- **20% weight**: AP load (>50 clients/AP = overloaded)
- **40% weight**: Gateway online status (offline = critical)

#### Supported Query Types
| Intent | Example |
|--------|---------|
| SUMMARY | "fleet overview", "status" |
| TOP/BOTTOM | "top 5 by clients", "worst health" |
| FILTER | "sites with offline devices" |
| SEARCH | "find acme corp" |
| GROUP | "group by isp" |
| COUNT | "how many critical sites" |

---

### 2. Maker/Checker Validation Framework

#### Risk Levels
```python
class RiskLevel(Enum):
    LOW = auto()      # Read-only, no customer impact
    MEDIUM = auto()   # Single-site changes, reversible
    HIGH = auto()     # Multi-site changes, needs approval
    CRITICAL = auto() # Infrastructure-wide, needs rollback plan
```

#### Built-in Checkers
| Checker | Rule |
|---------|------|
| BulkOperationChecker | >10 sites requires `bulk_confirmed=true` |
| RollbackPlanChecker | Critical actions require rollback plan |

#### Critical Actions Requiring Rollback Plans
- `firmware_upgrade`
- `factory_reset`
- `config_push`
- `vlan_change`
- `firewall_rule_change`
- `ssid_modify`

#### Usage
```python
from common.maker_checker import validate_operation

result = validate_operation(
    action="firmware_upgrade",
    sites=["site-001", "site-002", ..., "site-015"],  # 15 sites
    plan={
        "firmware_version": "7.0.0",
        "rollback_plan": "Restore from backup if upgrade fails",
        "bulk_confirmed": True
    }
)

if result.can_proceed:
    execute_upgrade()
elif result.needs_approval:
    notify_supervisor(result.summary())
```

---

### 3. OberaConnect Standards Validation

#### WiFi Standards
```python
from common.validators import validate_wifi_channel, validate_signal_strength

# 2.4GHz: Only channels 1, 6, 11 (non-overlapping)
validate_wifi_channel(6, "2.4")   # OK
validate_wifi_channel(3, "2.4")   # FAIL

# Signal minimum: -65dBm
validate_signal_strength(-60)     # OK
validate_signal_strength(-70)     # FAIL (below -65dBm minimum)
```

#### VLAN Standards
```python
from common.validators import validate_vlan_id

validate_vlan_id(100)   # OK
validate_vlan_id(1)     # FAIL (reserved native VLAN)
validate_vlan_id(4095)  # FAIL (out of range)
```

---

### 4. NinjaOne RMM Integration

#### OAuth Client
```python
from ninjaone.client import NinjaOneClient, NinjaOneConfig

config = NinjaOneConfig.from_env()  # Reads NINJAONE_CLIENT_ID, NINJAONE_CLIENT_SECRET
client = NinjaOneClient(config)

# Get critical alerts
alerts = client.get_critical_alerts()

# Get devices for specific org
devices = client.get_devices(org_id="org-001")
```

#### Demo Mode for Testing
```python
from ninjaone.client import get_client

client = get_client(demo=True)  # Returns DemoNinjaOneClient with sample data
```

---

### 5. Cross-Platform Correlation

#### Morning Health Check
Combines UniFi fleet status + NinjaOne alerts for daily operations review.

#### Incident Context
When responding to an incident, gather:
- UniFi site status (gateway, APs, switches)
- NinjaOne devices for that org
- Active alerts for affected site
- Recent changes (if audit logging enabled)

---

## Use Cases

### Use Case 1: Morning Health Check
```
NOC Engineer starts shift at 7 AM:

> "morning check"

Response:
Fleet Status: 47/50 sites healthy
  - 2 sites with offline APs (Gulf Shores, Fairhope)
  - 1 site critical (Saint Annes - gateway offline)

NinjaOne Alerts: 5 active
  - 2 CRITICAL: Disk space (SETCO-DC01, HOODS-FS01)
  - 3 MAJOR: AV definitions outdated

Action Items:
1. Investigate Saint Annes gateway outage
2. Clear disk space on SETCO-DC01
```

### Use Case 2: Bulk Firmware Upgrade
```python
result = validate_operation(
    action="firmware_upgrade",
    sites=[site.id for site in sites],  # All 50 sites
    plan={
        "firmware_version": "7.0.0",
        "rollback_plan": "Revert to 6.6.55 via controller if issues"
    }
)

# Result: ESCALATE
# Issues:
#   - Bulk operation affecting 50 sites requires confirmation
# Risk Flags: BULK_OPERATION
# Suggestions:
#   - Set bulk_confirmed=true in plan to proceed
```

### Use Case 3: Incident Response
```
Ticket: "Users at Setco can't connect to WiFi"

> "incident context for setco"

Response:
=== UniFi Status: Setco Industries ===
Health: 60% (WARNING)
Devices: 10 total, 2 offline
  - UAP-IW-HD (Warehouse) - OFFLINE 45min
  - USW-24 (Server Room) - ONLINE
Gateway: UDM-Pro - ONLINE

=== NinjaOne Status ===
Devices: 15 managed, 14 online
Alerts: 1 MAJOR
  - SETCO-DC01: DNS service stopped

=== Correlation ===
Possible root cause: DNS service on domain controller
may be causing DHCP/WiFi authentication issues.
Recommend: Restart DNS service, then check AP connectivity.
```

### Use Case 4: Compliance Audit
```
> "sites not meeting signal standard"

Query: Sites with APs reporting < -65dBm signal

Response: 3 sites flagged
  - Hoods Discount: AP-Breakroom at -72dBm
  - Kinder Academy: AP-Playground at -68dBm
  - Gulf Shores: AP-Lobby at -70dBm

Recommendation: Site survey needed for AP repositioning
```

---

## Configuration

### Environment Variables
```bash
# UniFi Site Manager (browser auth headers)
UNIFI_AUTH_HEADERS='{"x-amz-date":"...","authorization":"AWS4-HMAC-SHA256..."}'

# NinjaOne OAuth
NINJAONE_CLIENT_ID=your-client-id
NINJAONE_CLIENT_SECRET=your-client-secret
NINJAONE_BASE_URL=https://api.ninjarmm.com

# Demo mode (no credentials needed)
DEMO_MODE=true
```

### Installation
```bash
cd oberaconnect-tools
pip install -e ".[dev]"  # Includes pytest, black, mypy

# Run tests
pytest tests/ -v --cov=.

# Type checking
mypy .

# Linting
ruff check .
```

---

## Integration Points

### MCP Server (Claude Code)
Exposes 13 tools for AI-assisted operations:
- `unifi_fleet_summary` - Fleet statistics
- `unifi_search_sites` - Site filtering
- `unifi_query` - Natural language queries
- `ninjaone_get_alerts` - Alert retrieval
- `oberaconnect_morning_check` - Daily health check

### n8n Webhooks
Flask REST API for workflow automation:
- `POST /api/query` - Execute natural language query
- `GET /api/sites` - List all sites
- `GET /api/alerts` - Get active alerts

### Dashboard
Browser-based monitoring UI with:
- Fleet health overview
- Site drill-down
- Real-time refresh
- Natural language query bar

---

## Security Considerations

### Current State (Pre-Hardening)
- CLI accepts passwords as arguments (INSECURE)
- SSL verification disabled for self-signed certs
- No audit logging
- No RBAC

### Required Before Production
1. **Credential Management**: Move to environment variables or Keeper integration
2. **SSL Verification**: Enable with proper cert handling
3. **Audit Logging**: Log all operations with user, timestamp, action, target
4. **OAuth Validation**: Proper token refresh and error handling
5. **RBAC**: Role-based access (read-only vs admin operations)

---

## Development Roadmap

### Phase 1: Foundation (Current)
- [x] Core data models
- [x] Natural language analyzer
- [x] Maker/checker framework
- [x] Test suite structure
- [ ] Security hardening

### Phase 2: Production Hardening
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] 80%+ test coverage
- [ ] Audit logging
- [ ] Secure credential handling

### Phase 3: Integration
- [ ] Merge with Secondbrain tools
- [ ] n8n workflow templates
- [ ] Teams/Slack notifications

### Phase 4: Scale
- [ ] Redis caching for API responses
- [ ] Background job queue (Celery/RQ)
- [ ] Multi-tenant isolation

---

## AI Council Verdict

| AI | Verdict | Confidence | Key Insight |
|----|---------|------------|-------------|
| Gemini | MERGE | 9/10 | "Expert-in-a-box" potential |
| Claude | MERGE | 8/10 | Superior architecture |
| Grok | ARCHIVE | 3/10 | "Fix fundamentals first" |

**Consensus**: CONDITIONAL MERGE - Fix security gaps before production deployment.

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/jerm71279/oberaconnect-ai-ops.git
cd oberaconnect-ai-ops/oberaconnect-tools
pip install -e .

# Run in demo mode
DEMO_MODE=true python -m unifi.cli summary

# Or use programmatically
from unifi.analyzer import UniFiAnalyzer
from unifi.models import UniFiSite

# Load your sites from API or demo
sites = [UniFiSite(...)]
analyzer = UniFiAnalyzer(sites)
result = analyzer.analyze("top 5 by clients")
print(result.message)
```

---

## Contact

**OberaConnect Engineering Team**
- Repository: https://github.com/jerm71279/oberaconnect-ai-ops
- Internal Docs: /home/mavrick/Projects/Secondbrain/SOPs/
