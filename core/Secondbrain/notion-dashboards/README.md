# OberaConnect Notion Dashboards

Notion-based dashboard system for OberaConnect's MSP operations, providing visibility into customer sites, health metrics, Azure migration progress, and documentation.

**Uses the official `notion-client` SDK** for reliable API access with pagination helpers, type safety, and proper error handling.

## Overview

This package provides four integrated dashboards:

| Dashboard | Purpose | Update Frequency |
|-----------|---------|------------------|
| **Customer Status Board** | Site overview for all 98 customers | Daily automated |
| **Daily Health Summaries** | Historical health snapshots | Daily at 6 AM |
| **Azure Migration Pipeline** | Service migration tracking | Manual + CLI |
| **Runbook Library** | Documentation management | Manual + CLI |

## Quick Start

```bash
# 1. Clone to your Azure Linux VM
git clone https://github.com/jerm71279/oberaconnect-ai-ops.git
cd oberaconnect-ai-ops/notion-dashboards

# 2. Install dependencies
pip install requests --break-system-packages

# 3. Configure
cp config/config.example.json config/config.json
# Edit config.json with your credentials

# 4. Test connection
python scripts/notion_client.py

# 5. Run dry-run sync
python scripts/customer_status_sync.py --config config/config.json --dry-run
```

## Directory Structure

```
notion-dashboards/
├── scripts/
│   ├── notion_client.py        # Core Notion API wrapper
│   ├── customer_status_sync.py # Customer site dashboard sync
│   ├── daily_health_sync.py    # Daily health snapshots
│   ├── azure_pipeline_sync.py  # Azure migration tracker
│   └── runbook_manager.py      # Documentation library
├── templates/
│   └── DATABASE_TEMPLATES.md   # Notion database schemas
├── config/
│   └── config.example.json     # Configuration template
├── docs/
│   └── (additional documentation)
└── README.md
```

## Scripts

### Customer Status Sync

Syncs customer site data from UniFi and NinjaOne to Notion.

```bash
# Full sync
python scripts/customer_status_sync.py --config config/config.json

# Sync specific site
python scripts/customer_status_sync.py --config config/config.json --site "Acme Corp"

# Preview without changes
python scripts/customer_status_sync.py --config config/config.json --dry-run
```

### Daily Health Sync

Creates daily health snapshots with trend data.

```bash
# Run daily sync
python scripts/daily_health_sync.py --config config/config.json

# Preview
python scripts/daily_health_sync.py --config config/config.json --dry-run
```

**Exit codes:**
- `0`: Success
- `1`: Error occurred
- `2`: Success but sites flagged for review

### Azure Pipeline Manager

Track services through Lab → Production → Customer pipeline.

```bash
# List all services
python scripts/azure_pipeline_sync.py --config config/config.json list

# Add new service
python scripts/azure_pipeline_sync.py --config config/config.json add \
  --name "Azure VPN Gateway" \
  --category "Networking" \
  --owner "Maverick"

# Update service status
python scripts/azure_pipeline_sync.py --config config/config.json update \
  --name "Azure VPN Gateway" \
  --stage "lab testing" \
  --lab-status "in progress"

# Advance to next stage (validates prerequisites)
python scripts/azure_pipeline_sync.py --config config/config.json advance \
  --name "Azure VPN Gateway"

# Generate report
python scripts/azure_pipeline_sync.py --config config/config.json report
```

### Runbook Manager

Manage documentation with automation tracking and review scheduling.

```bash
# List runbooks
python scripts/runbook_manager.py --config config/config.json list
python scripts/runbook_manager.py --config config/config.json list --category network
python scripts/runbook_manager.py --config config/config.json list --vendor Ubiquiti

# Add runbook
python scripts/runbook_manager.py --config config/config.json add \
  --title "UniFi Site Setup" \
  --category network \
  --type runbook \
  --vendors Ubiquiti \
  --complexity intermediate \
  --owner "Maverick"

# Mark as reviewed
python scripts/runbook_manager.py --config config/config.json review \
  --title "UniFi Site Setup"

# Update automation status (3+ times rule)
python scripts/runbook_manager.py --config config/config.json automate \
  --title "UniFi Site Setup" \
  --status "fully automated" \
  --tool "unifi-site-builder"

# Show docs needing review
python scripts/runbook_manager.py --config config/config.json review-due

# Show automation candidates
python scripts/runbook_manager.py --config config/config.json candidates

# Generate report
python scripts/runbook_manager.py --config config/config.json report
```

## Configuration

### config.json Structure

```json
{
    "notion_token": "secret_xxx...",
    "databases": {
        "customer_status": "32-char-database-id",
        "daily_health": "32-char-database-id",
        "azure_pipeline": "32-char-database-id",
        "runbook_library": "32-char-database-id"
    },
    "unifi": {
        "site_manager_url": "https://unifi.ui.com",
        "api_token": "your-unifi-token"
    },
    "ninjaone": {
        "api_url": "https://app.ninjarmm.com/api/v2",
        "client_id": "your-client-id",
        "client_secret": "your-secret"
    },
    "settings": {
        "wifi_signal_threshold_dbm": -65,
        "health_score_warning_threshold": 70
    }
}
```

### Environment Variables

Alternative to config file for sensitive values:

```bash
export NOTION_TOKEN="secret_xxx..."
export UNIFI_API_TOKEN="xxx"
export NINJAONE_CLIENT_ID="xxx"
export NINJAONE_CLIENT_SECRET="xxx"
```

## Cron Setup

Add to crontab on Azure Linux VM:

```cron
# Daily health sync at 6 AM Central
0 6 * * * cd /path/to/notion-dashboards && /usr/bin/python3 scripts/daily_health_sync.py --config config/config.json >> /var/log/notion_health.log 2>&1

# Customer status sync at 7 AM Central
0 7 * * * cd /path/to/notion-dashboards && /usr/bin/python3 scripts/customer_status_sync.py --config config/config.json >> /var/log/notion_customer.log 2>&1
```

## OberaConnect Validation Rules

Scripts implement oberaconnect-tools validation patterns:

| Rule | Implementation |
|------|---------------|
| Open SSIDs blocked | Config drift flags open networks |
| VLAN 1/4095 reserved | Checks for reserved VLAN usage |
| Permit-any firewall blocked | Flags overly permissive rules |
| Bulk >10 sites confirmation | Maker/checker pattern |
| HIGH/CRITICAL needs rollback | Review flags for critical issues |

## Maker/Checker Pattern

Daily health sync flags sites for review when:
- Health score drops >15 points from previous day
- Critical alerts present
- Config drift detected
- Backup failures

Flagged sites appear in reports and return exit code 2.

## UniFi Best Practices Applied

- WiFi signal threshold: -65dBm minimum
- BSS Transition > Minimum RSSI for roaming
- 2.4GHz channels 1/6/11 only
- Zone-Based Firewall for inter-VLAN
- ACLs for intra-VLAN isolation

## Integration Points

### UniFi Site Manager API
- Endpoint: unifi.ui.com
- Docs: developer.ui.com
- Required: API token from Account → API

### NinjaOne RMM API
- Endpoint: app.ninjarmm.com/api/v2
- Docs: app.ninjarmm.com/apidocs
- Required: OAuth client credentials

### Notion API
- Endpoint: api.notion.com/v1
- Docs: developers.notion.com
- Required: Integration token

## Extending

### Adding New Data Sources

1. Create fetch function in relevant sync script
2. Add configuration to config.json
3. Update `build_properties()` to include new fields
4. Add property to Notion database schema

### Custom Health Score Weights

Modify `calculate_health_score()` in daily_health_sync.py:

```python
def calculate_health_score(...):
    # Adjust weights as needed
    # Device availability: 30 points
    # WiFi signal quality: 20 points
    # Active alerts: 20 points
    # Backup status: 15 points
    # Config compliance: 15 points
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Notion token required" | Set NOTION_TOKEN or add to config |
| "Database not found" | Check database ID, ensure integration has access |
| "Property X not found" | Create missing property in Notion |
| Rate limit errors | Scripts include backoff, reduce batch size |

### Debug Mode

```bash
python scripts/customer_status_sync.py --config config/config.json --verbose
```

### Log Files

- `/var/log/notion_health.log`
- `/var/log/notion_customer.log`

## License

Internal OberaConnect use only.

## Author

OberaConnect Network Engineering
