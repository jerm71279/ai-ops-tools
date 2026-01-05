# Notion Dashboards Skill

Sync NinjaOne alerts and device issues to Notion databases for visibility and triage.

## Features

- **Device Issues Sync**: Pull active NinjaOne alerts → Notion Device Issues database
- **CLI Query Tool**: Quick filtered access to issues from terminal
- **Deduplication**: Updates existing issues instead of creating duplicates
- **Auto-resolve**: Marks issues resolved when alerts clear in NinjaOne

## Setup

1. Copy `.env.example` to `.env` and fill in credentials
2. Create Device Issues database in Notion (see `templates/DATABASE_TEMPLATES.md`)
3. Update `config/config.json` with your database ID

## Usage

### Sync Alerts to Notion
```bash
cd scripts
export $(cat ../.env | xargs)
python3 device_issues_sync.py --config ../config/config.json
```

### Query from CLI
```bash
export NOTION_TOKEN="your-token"

# All active issues
python3 device_issues_query.py

# Filter by type
python3 device_issues_query.py --disk-space
python3 device_issues_query.py --memory

# Filter by organization
python3 device_issues_query.py --org "City of Freeport"

# Group by organization
python3 device_issues_query.py --by-org

# Summary stats
python3 device_issues_query.py --summary
```

### Cron Schedule
```bash
# Run every 15 minutes
*/15 * * * * /path/to/scripts/run_device_issues_sync.sh
```

## Database Schema

See `templates/DATABASE_TEMPLATES.md` for the Device Issues database schema.

## Files

```
notion-dashboards/
├── scripts/
│   ├── device_issues_sync.py    # Main sync script
│   ├── device_issues_query.py   # CLI query tool
│   ├── run_device_issues_sync.sh # Cron runner
│   ├── notion_client_wrapper.py # Notion API wrapper
│   └── core/
│       ├── config.py            # Config loader
│       └── base_sync.py         # Base sync client
├── config/
│   ├── config.json              # Database IDs
│   └── config.example.json      # Example config
└── templates/
    └── DATABASE_TEMPLATES.md    # Notion database schemas
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NOTION_TOKEN` | Notion integration token (ntn_xxx or secret_xxx) |
| `NINJAONE_CLIENT_ID` | NinjaOne OAuth client ID |
| `NINJAONE_CLIENT_SECRET` | NinjaOne OAuth client secret |
| `NINJAONE_BASE_URL` | NinjaOne API URL (e.g., https://us2.ninjarmm.com) |
