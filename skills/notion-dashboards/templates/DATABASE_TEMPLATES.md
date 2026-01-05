# Notion Database Templates for OberaConnect

These templates define the database schemas for each dashboard. 
Use them to create databases in Notion with the correct properties.

---

## 1. Customer Status Board

**Purpose:** Single source of truth for all 98 customer sites

### Properties

| Property Name | Type | Options/Notes |
|--------------|------|---------------|
| Site Name | Title | Primary identifier |
| Customer ID | Text | Links to NinjaOne/PSA |
| State | Select | Alabama, Arkansas, Florida, Georgia, Kentucky, Louisiana, Mississippi, Missouri, North Carolina, Oklahoma, South Carolina, Tennessee, Texas, Virginia |
| Device Count | Number | Integer, synced from UniFi |
| Stack Type | Multi-select | Ubiquiti, MikroTik, SonicWall, Azure |
| Deployment Status | Select | onboarding, active, maintenance, needs attention, offboarding |
| Health Score | Number | 0-100, calculated from monitoring |
| Last Health Check | Date | Date only |
| Open Tickets | Number | Integer, pulled from PSA |
| Contract Renewal | Date | Date only |
| Primary Contact | Text | Customer contact name |
| Notes | Text | Freeform notes |

### Recommended Views

1. **All Sites** - Table sorted by Site Name
2. **By State** - Table grouped by State property
3. **By Status** - Kanban grouped by Deployment Status
4. **Health Dashboard** - Kanban grouped by Health Score ranges (0-49, 50-79, 80-100)
5. **Renewals Calendar** - Calendar by Contract Renewal

---

## 2. Daily Health Summaries

**Purpose:** Daily snapshots building historical record for trend analysis

### Properties

| Property Name | Type | Options/Notes |
|--------------|------|---------------|
| Date | Title | YYYY-MM-DD format |
| Site | Relation | Links to Customer Status Board |
| Devices Online | Number | Integer |
| Devices Offline | Number | Integer |
| Devices Total | Number | Integer |
| Availability Percentage | Number | Percentage (0-100) |
| WiFi Clients | Number | Integer |
| Signal Warnings | Number | Clients below -65dBm |
| Active Alerts | Number | Integer from NinjaOne |
| Alert Summary | Text | Top 3 alerts |
| Config Drift Detected | Checkbox | Boolean |
| Backup Status | Select | success, partial, failed, unknown |
| Health Score | Number | 0-100 |
| Notes | Text | Manual observations |

### Recommended Views

1. **Today** - Table filtered to current date
2. **By Site** - Table grouped by Site relation
3. **Issues Only** - Table filtered to Health Score < 70 OR Config Drift = true
4. **Weekly Trend** - Table filtered to last 7 days, sorted by date desc

---

## 3. Azure Migration Pipeline

**Purpose:** Track services through Lab → Production → Customer pipeline

### Properties

| Property Name | Type | Options/Notes |
|--------------|------|---------------|
| Service Name | Title | Azure service name |
| Category | Select | Compute, Networking, Storage, Databases, Identity, Security, Management, DevOps, AI/ML, Analytics, Integration, IoT, Migration, Backup, Monitoring |
| Pipeline Stage | Select | backlog, lab testing, production validation, customer ready, deprecated |
| Lab Status | Select | not started, in progress, passed, failed |
| Production Status | Select | not started, in progress, deployed, issues |
| Owner | Text | Assigned person |
| Dependencies | Relation | Self-relation to other services |
| Customer Requests | Number | Count of customer requests |
| Documentation Link | URL | Link to runbook |
| Security Review | Checkbox | AZ-500 relevant review complete |
| Target Date | Date | Target completion |
| Blockers | Text | Current blockers |
| Last Updated | Date | Auto-updated on changes |
| Notes | Text | Additional notes |

### Recommended Views

1. **Pipeline Board** - Kanban grouped by Pipeline Stage
2. **My Services** - Table filtered by Owner
3. **Blocked** - Table filtered to Blockers is not empty
4. **Customer Ready** - Gallery filtered to Pipeline Stage = customer ready
5. **Security Services** - Table filtered to Category = Security
6. **Timeline** - Timeline view by Target Date

---

## 4. Runbook Library

**Purpose:** Centralized, searchable documentation with automation tracking

### Properties

| Property Name | Type | Options/Notes |
|--------------|------|---------------|
| Title | Title | Document title |
| Category | Select | network, security, cloud, hardware, process |
| Vendor | Multi-select | Ubiquiti, MikroTik, SonicWall, Azure, M365 |
| Document Type | Select | SOP, runbook, troubleshooting guide, template, reference |
| Complexity | Select | basic, intermediate, advanced |
| Automation Status | Select | manual, partially automated, fully automated, deprecated |
| Related Tool | Relation | Links to tools inventory (optional) |
| Last Review Date | Date | When last reviewed |
| Next Review Due | Date | Calculated from complexity |
| Owner | Text | Document owner |
| Tags | Multi-select | Searchable keywords |
| Documentation Link | URL | External link if not in Notion |

### Recommended Views

1. **All Docs** - Table grouped by Category
2. **By Vendor** - Table grouped by Vendor
3. **Review Due** - Table filtered to Next Review Due <= Today + 14 days
4. **Automation Board** - Kanban grouped by Automation Status
5. **Search** - Table with all filters visible

---

## 5. Device Issues Dashboard

**Purpose:** Track NinjaOne alerts and device health issues for triage and maintenance scheduling

### Properties

| Property Name | Type | Options/Notes |
|--------------|------|---------------|
| Device Name | Title | NinjaOne system name |
| Organization | Text | Customer organization name |
| Issue Type | Select | disk_space, memory, disk_io, offline, backup_failed, cpu, service_down |
| Severity | Select | critical, warning, info |
| Details | Text | Full alert message with specifics |
| Status | Select | new, acknowledged, scheduled, in_progress, resolved |
| Device ID | Number | NinjaOne device ID (for script targeting) |
| Scheduled Action | Select | disk_cleanup, restart_service, reboot, manual, none |
| Scheduled Time | Date | When maintenance is planned |
| Alert UID | Text | NinjaOne alert UID for deduplication |
| Created | Date | When first synced to Notion |
| Last Seen | Date | Last time alert was active in NinjaOne |

### Recommended Views

1. **Active Issues** - Table filtered to Status != resolved, sorted by Severity desc
2. **By Organization** - Table grouped by Organization
3. **Triage Board** - Kanban grouped by Status
4. **Disk Space Issues** - Table filtered to Issue Type = disk_space
5. **Scheduled Maintenance** - Table filtered to Scheduled Action != none, sorted by Scheduled Time

---

## Setup Instructions

### Step 1: Create Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it "OberaConnect Dashboards"
4. Select the workspace
5. Copy the integration token
6. Add to config.json as `notion_token`

### Step 2: Create Databases

1. In Notion, create a new page for your dashboards
2. Create each database with properties from templates above
3. Share each database with your integration:
   - Click "..." menu → "Connections" → Add your integration

### Step 3: Get Database IDs

1. Open each database in Notion
2. Copy the URL: `notion.so/workspace/DATABASE_ID?v=...`
3. Extract the 32-character DATABASE_ID (before the `?`)
4. Add to config.json under `databases`

### Step 4: Configure API Credentials

1. **UniFi Site Manager**: Get API token from unifi.ui.com → Account → API
2. **NinjaOne**: Create API credentials in Administration → Apps → API

### Step 5: Test the Integration

```bash
# Install dependencies
pip install requests --break-system-packages

# Test Notion connection
python scripts/notion_client.py

# Dry run customer sync
python scripts/customer_status_sync.py --config config/config.json --dry-run

# Dry run health sync
python scripts/daily_health_sync.py --config config/config.json --dry-run
```

### Step 6: Schedule Automation

Add to crontab on your Azure Linux VM:

```cron
# Daily health sync at 6 AM
0 6 * * * /path/to/venv/bin/python /path/to/daily_health_sync.py --config /path/to/config.json >> /var/log/notion_health.log 2>&1

# Customer status sync at 7 AM
0 7 * * * /path/to/venv/bin/python /path/to/customer_status_sync.py --config /path/to/config.json >> /var/log/notion_customer.log 2>&1
```

---

## Integration with oberaconnect-tools

These scripts are designed to integrate with your existing oberaconnect-tools package:

### Directory Structure (suggested)

```
oberaconnect-tools/
├── notion/
│   ├── __init__.py
│   ├── client.py          # notion_client.py
│   ├── customer_sync.py   # customer_status_sync.py
│   ├── health_sync.py     # daily_health_sync.py
│   ├── pipeline.py        # azure_pipeline_sync.py
│   └── runbooks.py        # runbook_manager.py
├── config/
│   └── notion.json
└── ...
```

### Validation Rules Applied

The scripts implement your oberaconnect-tools validation patterns:

- **Open SSIDs blocked**: Config drift detection flags open networks
- **VLAN 1/4095 reserved**: Checks for reserved VLAN usage
- **Permit-any firewall blocked**: Flags overly permissive rules
- **Bulk >10 sites needs confirmation**: Maker/checker for large changes
- **HIGH/CRITICAL needs rollback_plan**: Review flags for critical issues

### Maker/Checker Pattern

Daily health sync implements maker/checker:

1. Health score drops >15 points → flagged for review
2. Critical alerts present → flagged for review
3. Config drift detected → flagged for review
4. Exit code 2 indicates reviews needed (for alerting)

---

## Troubleshooting

### Common Issues

**"Notion token required"**
- Ensure NOTION_TOKEN env var is set or token is in config.json

**"Database not found"**
- Verify database ID is correct (32 chars, no dashes)
- Ensure integration has access to the database

**"Property X not found"**
- Database schema doesn't match template
- Create missing properties in Notion

**API rate limits**
- Notion rate limit: 3 requests/second
- Scripts include backoff logic

### Logs

Check logs for detailed error information:
- `/var/log/notion_health.log`
- `/var/log/notion_customer.log`

### Support

For issues with:
- **Notion API**: https://developers.notion.com
- **UniFi API**: https://developer.ui.com
- **NinjaOne API**: https://app.ninjarmm.com/apidocs
