# OberaConnect Unified Automation Architecture

## The Big Picture: Everything Connected

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                        OBERACONNECT UNIFIED SYSTEM                              │
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │                     INFRASTRUCTURE (Data Sources)                        │  │
│   │                                                                          │  │
│   │   UniFi          NinjaOne       Azure         MikroTik      SonicWall   │  │
│   │   98 Sites       RMM            Cloud         Routers       Firewalls   │  │
│   │      │              │             │              │              │        │  │
│   └──────┼──────────────┼─────────────┼──────────────┼──────────────┼────────┘  │
│          │              │             │              │              │           │
│          ▼              ▼             ▼              ▼              ▼           │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │                      AZURE LINUX VM (Automation Hub)                     │  │
│   │                                                                          │  │
│   │   ┌─────────────────────────┐    ┌─────────────────────────────────┐    │  │
│   │   │   oberaconnect-tools    │    │      notion-dashboards          │    │  │
│   │   │   ==================    │    │      =================          │    │  │
│   │   │   mikrotik-config-builder────────▶ config_change_sync.py       │    │  │
│   │   │   sonicwall-scripts ─────────────▶ (logs all changes)          │    │  │
│   │   │   network-troubleshooter ────────▶                             │    │  │
│   │   │   custom-skills          │    │   customer_status_sync.py      │    │  │
│   │   │                          │    │   daily_health_sync.py         │    │  │
│   │   │                          │    │   azure_pipeline_sync.py       │    │  │
│   │   │                          │    │   runbook_manager.py           │    │  │
│   │   └──────────────────────────┘    └─────────────────────────────────┘    │  │
│   │                                              │                           │  │
│   │                    ┌─────────────────────────┘                           │  │
│   │                    │  Cron: 6 AM daily + real-time hooks                 │  │
│   └────────────────────┼─────────────────────────────────────────────────────┘  │
│                        │                                                        │
│                        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │                    NOTION (Single Source of Truth)                       │  │
│   │                                                                          │  │
│   │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │  │
│   │   │Customer Sites│ │Daily Health  │ │Config Changes│ │Network       │   │  │
│   │   │   98 rows    │ │  Snapshots   │ │  Audit Log   │ │  Devices     │   │  │
│   │   └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │  │
│   │   ┌──────────────┐ ┌──────────────┐                                     │  │
│   │   │Azure Pipeline│ │Runbook       │      ┌─────────────────────────┐    │  │
│   │   │ 75 Services  │ │  Library     │      │    Notion 3.0 AI        │    │  │
│   │   └──────────────┘ └──────────────┘      │    ===============      │    │  │
│   │                                          │  Reads ALL databases    │    │  │
│   │                                          │  Answers in English     │    │  │
│   │                                          └─────────────────────────┘    │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                            │
│                                    ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │                           YOUR TEAM                                      │  │
│   │                                                                          │  │
│   │   Maverick        Director        Field Techs       Support Team        │  │
│   │   (CLI + AI)      (AI Reports)    (AI Lookup)       (AI Troubleshoot)   │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## How oberaconnect-tools Now Integrates

### Before: Tools Were Siloed
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   mikrotik-config-builder                           │
│      └── Runs, deploys config, done                 │
│          (No record of what happened)               │
│                                                     │
│   sonicwall-scripts                                 │
│      └── Runs, changes firewall, done               │
│          (Only you know what changed)               │
│                                                     │
│   network-troubleshooter                            │
│      └── Scans network, outputs text                │
│          (Lost when terminal closes)                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### After: Everything Logs to Notion
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   mikrotik-config-builder                           │
│      └── Runs, deploys config                       │
│      └── Calls log-change.sh                        │
│      └── Change recorded in Notion forever          │
│                                                     │
│   sonicwall-scripts                                 │
│      └── Runs, changes firewall                     │
│      └── Calls log-change.sh                        │
│      └── AI can tell Director what changed          │
│                                                     │
│   network-troubleshooter                            │
│      └── Scans network                              │
│      └── Writes devices to Notion                   │
│      └── Next tech can ask AI about findings        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Integration Example: MikroTik Deployment

### Step 1: You Run the Existing Tool
```bash
# Your existing command stays the same
./mikrotik-config-builder.sh --site "Acme Corp" --config vpn-update.rsc
```

### Step 2: Add One Line to Log It
```bash
# Add this to the end of mikrotik-config-builder.sh:
source /path/to/notion-dashboards/scripts/log-change.sh
log_change "mikrotik-config-builder" "Acme Corp" "deploy" "Updated VPN tunnel to new office"
```

### Step 3: The Change is Now in Notion
```
┌─────────────────────────────────────────────────────────────────────┐
│ Config Changes Log (Notion Database)                                │
├─────────────────────────────────────────────────────────────────────┤
│ Change ID          │ Acme Corp-20250101-083042                      │
│ Site               │ Acme Corp (linked)                             │
│ Tool               │ mikrotik-config-builder                        │
│ Action             │ deploy                                         │
│ Summary            │ Updated VPN tunnel to new office               │
│ Engineer           │ Maverick                                       │
│ Timestamp          │ 2025-01-01 08:30:42                            │
│ Risk Level         │ high (auto-detected: VPN change)               │
└─────────────────────────────────────────────────────────────────────┘
```

### Step 4: Anyone Can Ask the AI
```
Director: "What changes were made to Acme Corp this week?"

AI: "This week there was 1 change to Acme Corp:

     On January 1st, Maverick deployed a VPN configuration update
     using mikrotik-config-builder. The change was classified as
     high-risk because it modified VPN settings. The summary was:
     'Updated VPN tunnel to new office.'

     No issues have been reported since this change."
```

## What Each Script Does (Updated)

```
┌────────────────────────────┬────────────────────────────────────────────────┐
│ Script                     │ What It Does                                   │
├────────────────────────────┼────────────────────────────────────────────────┤
│                            │                                                │
│ NOTION-DASHBOARDS PACKAGE  │                                                │
│ ════════════════════════   │                                                │
│                            │                                                │
│ notion_client_wrapper.py   │ SDK connection layer for all scripts           │
│                            │                                                │
│ customer_status_sync.py    │ UniFi + NinjaOne data → Customer Sites DB      │
│                            │                                                │
│ daily_health_sync.py       │ Daily snapshots → Daily Health DB              │
│                            │                                                │
│ config_change_sync.py      │ NEW: Logs all changes from oberaconnect-tools  │
│                            │      → Config Changes DB                       │
│                            │                                                │
│ azure_pipeline_sync.py     │ Azure service tracking → Azure Pipeline DB     │
│                            │                                                │
│ runbook_manager.py         │ Documentation management → Runbook Library DB  │
│                            │                                                │
│ log-change.sh              │ NEW: Bash wrapper for easy integration         │
│                            │      Source this in your existing tools        │
│                            │                                                │
│ setup_databases.py         │ One-time: Creates all 6 databases in Notion    │
│                            │                                                │
├────────────────────────────┼────────────────────────────────────────────────┤
│                            │                                                │
│ OBERACONNECT-TOOLS         │ (Your existing tools - just add log calls)     │
│ ══════════════════         │                                                │
│                            │                                                │
│ mikrotik-config-builder    │ Add: source log-change.sh at end               │
│                            │                                                │
│ sonicwall-scripts          │ Add: log_change call after deployment          │
│                            │                                                │
│ network-troubleshooter     │ Write device findings to Devices DB            │
│                            │                                                │
└────────────────────────────┴────────────────────────────────────────────────┘
```

## The 6 Notion Databases

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  NOTION DATABASES (API-Populated, AI-Readable)                                 │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 1. Customer Sites                                                        │   │
│  │    ────────────────                                                      │   │
│  │    98 rows (one per site)                                                │   │
│  │    Source: UniFi Site Manager + NinjaOne                                 │   │
│  │    Updates: Daily at 6 AM                                                │   │
│  │    Fields: Site Name, State, Device Count, Health Score, Status         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 2. Daily Health Summaries                                                │   │
│  │    ───────────────────────                                               │   │
│  │    New row for each site each day (historical data)                      │   │
│  │    Source: UniFi + NinjaOne                                              │   │
│  │    Updates: Daily at 6 AM                                                │   │
│  │    Fields: Date, Devices Online/Offline, Alerts, Config Drift            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 3. Config Changes Log (NEW)                                              │   │
│  │    ────────────────────────                                              │   │
│  │    Every change from oberaconnect-tools                                  │   │
│  │    Source: log-change.sh / config_change_sync.py                         │   │
│  │    Updates: Real-time (when tools run)                                   │   │
│  │    Fields: Tool, Site, Action, Summary, Engineer, Risk Level            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 4. Network Devices (NEW)                                                 │   │
│  │    ───────────────────────                                               │   │
│  │    Full inventory of all network hardware                                │   │
│  │    Source: UniFi API + network-troubleshooter discoveries                │   │
│  │    Updates: Daily + after discoveries                                    │   │
│  │    Fields: Device Name, Type, Vendor, IP, MAC, Status, Firmware          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 5. Azure Migration Pipeline                                              │   │
│  │    ───────────────────────────                                           │   │
│  │    75 Azure services: Lab → Prod → Customer Ready                        │   │
│  │    Source: Manual CLI updates (azure_pipeline_sync.py)                   │   │
│  │    Updates: As you progress                                              │   │
│  │    Fields: Service, Category, Stage, Lab Status, Prod Status            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 6. Runbook Library                                                       │   │
│  │    ──────────────────                                                    │   │
│  │    SOPs, runbooks, troubleshooting guides                                │   │
│  │    Source: Manual + runbook_manager.py CLI                               │   │
│  │    Updates: As docs are created/reviewed                                 │   │
│  │    Fields: Title, Category, Vendor, Complexity, Automation Status       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start: Integrate Existing Tools

### 1. Install the Notion Package
```bash
# On your Azure Linux VM
cd /home/maverick
git clone https://github.com/jerm71279/oberaconnect-ai-ops.git
cd oberaconnect-ai-ops/notion-dashboards
pip install notion-client --break-system-packages
```

### 2. Set Up Notion Databases
```bash
# Get your Notion token from notion.so/my-integrations
python scripts/setup_databases.py \
    --token secret_YOUR_TOKEN \
    --parent-page YOUR_PAGE_ID \
    --output ~/.config/notion-dashboards/config.json
```

### 3. Add Logging to Existing Tools
```bash
# Edit your mikrotik-config-builder.sh and add at the end:
source ~/oberaconnect-ai-ops/notion-dashboards/scripts/log-change.sh
log_change "mikrotik-config-builder" "$SITE_NAME" "deploy" "$CHANGE_SUMMARY"
```

### 4. Set Up Cron for Daily Sync
```bash
crontab -e
# Add:
0 6 * * * python ~/oberaconnect-ai-ops/notion-dashboards/scripts/daily_health_sync.py --config ~/.config/notion-dashboards/config.json
0 7 * * * python ~/oberaconnect-ai-ops/notion-dashboards/scripts/customer_status_sync.py --config ~/.config/notion-dashboards/config.json
```

### 5. Use the System
```bash
# CLI: Deploy a config (change gets logged automatically now)
./mikrotik-config-builder.sh --site "Acme Corp" --config new-vpn.rsc

# CLI: View recent changes
python config_change_sync.py --config config.json recent --days 7

# NOTION: Ask the AI
"What changes were made to Acme Corp this month?"
"Show me all high-risk deployments in the last week"
"Which sites have config drift?"
```

## The Key Insight (Updated)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│   BEFORE: Siloed Tools                                                         │
│   ────────────────────                                                         │
│                                                                                 │
│   • Changes happen, no record                                                   │
│   • Tribal knowledge in engineers' heads                                        │
│   • Director has to ask for updates                                             │
│   • New techs start from scratch                                                │
│   • "What did we do last time?" = digging through notes                         │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   AFTER: Unified System                                                        │
│   ─────────────────────                                                        │
│                                                                                 │
│   • Every change logged automatically                                           │
│   • Knowledge captured in Notion databases                                      │
│   • Director asks AI, gets instant report                                       │
│   • New techs ask AI about site history                                         │
│   • "What did we do last time?" = AI knows instantly                            │
│                                                                                 │
│   Time saved: 45+ minutes per day                                               │
│   Knowledge preserved: 100%                                                     │
│   Compliance: Audit trail built-in                                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```
