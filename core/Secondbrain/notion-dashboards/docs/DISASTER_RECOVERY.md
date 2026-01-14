# Disaster Recovery Procedures

## Overview

This document outlines disaster recovery procedures for the OberaConnect Notion Dashboards sync system.
Recovery Time Objective (RTO): 4 hours | Recovery Point Objective (RPO): 24 hours

## Architecture Summary

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  UniFi Sites    │    │   NinjaOne      │    │    Notion       │
│   (98 sites)    │───▶│   (323 devs)    │───▶│   Dashboards    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                      │                      │
         └──────────┬───────────┴──────────────────────┘
                    │
            ┌───────▼───────┐
            │  Sync Service │
            │  (Python)     │
            └───────────────┘
```

## Disaster Scenarios

### Scenario 1: Notion API Outage

**Symptoms:**
- HTTP 5xx errors from api.notion.com
- Health check shows notion_api: unhealthy
- Sync jobs failing with timeout errors

**Impact:** Medium - Data not syncing to dashboards, but source systems unaffected

**Recovery Steps:**
1. Check Notion status: https://status.notion.so/
2. If Notion outage confirmed, no action needed - wait for recovery
3. Monitor health endpoint: `curl http://localhost:8080/health`
4. Once Notion recovers, verify sync resumes automatically
5. If backlog accumulated, trigger manual full sync:
   ```bash
   python customer_status_sync.py --full-sync
   python daily_health_sync.py --full-sync
   ```

**Data Reconciliation:**
- Notion retains all existing data during outage
- Sync resumes from last successful checkpoint
- No data loss expected

---

### Scenario 2: UniFi API Credentials Compromised

**Symptoms:**
- Unauthorized API access detected
- Unknown IP addresses in UniFi logs
- Security alert from SIEM

**Impact:** Critical - Potential network configuration exposure

**Recovery Steps:**
1. **IMMEDIATE**: Revoke compromised token
   ```bash
   # In UniFi Site Manager: Settings → API → Delete compromised key
   ```
2. Generate new API token
3. Update Azure Key Vault:
   ```bash
   az keyvault secret set --vault-name oberaconnect-vault \
     --name unifi-api-token --value "NEW_TOKEN"
   ```
4. Restart sync service:
   ```bash
   systemctl restart oberaconnect-sync
   ```
5. Audit UniFi logs for unauthorized changes
6. Report to security team

**Post-Incident:**
- Review access logs for scope of compromise
- Check for unauthorized site/device changes
- Document incident in security log

---

### Scenario 3: NinjaOne OAuth Token Expired/Revoked

**Symptoms:**
- HTTP 401 errors from NinjaOne API
- `ninjaone_api` health check failing
- Alert sync not working

**Impact:** Medium - Alert data not syncing

**Recovery Steps:**
1. Check if credentials were manually revoked in NinjaOne admin
2. If expired, regenerate OAuth credentials:
   ```
   NinjaOne Admin → Administration → Apps → API → Regenerate
   ```
3. Update Key Vault:
   ```bash
   az keyvault secret set --vault-name oberaconnect-vault \
     --name ninjaone-client-id --value "NEW_ID"
   az keyvault secret set --vault-name oberaconnect-vault \
     --name ninjaone-client-secret --value "NEW_SECRET"
   ```
4. Test OAuth flow:
   ```bash
   python -c "from health_check import check_ninjaone_api; print(check_ninjaone_api())"
   ```
5. Restart sync service

---

### Scenario 4: Sync Service Host Failure

**Symptoms:**
- Health endpoints not responding
- No sync activity in logs
- Container/VM unreachable

**Impact:** High - All syncs stopped

**Recovery Steps:**

**If Docker Container:**
```bash
# Check container status
docker ps -a | grep oberaconnect

# View logs
docker logs oberaconnect-sync --tail 100

# Restart container
docker-compose restart sync

# If corrupt, rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**If VM/Server:**
```bash
# SSH to recovery/backup server
ssh backup-server

# Deploy from Git
git clone https://github.com/oberaconnect/notion-dashboards.git
cd notion-dashboards
cp /secure/backup/.env .env
pip install -r requirements.txt
python health_check.py --check
```

**Data Reconciliation:**
- Run full sync after recovery:
  ```bash
  python customer_status_sync.py --full-sync
  python daily_health_sync.py --full-sync
  python config_change_sync.py --full-sync
  ```

---

### Scenario 5: Notion Database Corruption

**Symptoms:**
- Pages missing or duplicated
- Property values incorrect
- Database schema changed unexpectedly

**Impact:** High - Dashboard data unreliable

**Recovery Steps:**
1. **Stop all sync jobs immediately**
   ```bash
   systemctl stop oberaconnect-sync
   ```

2. **Assess damage scope**
   - Check Notion page history for affected pages
   - Identify time range of corruption
   - Determine if automation or human error

3. **Restore from Notion history** (if recent)
   - Notion retains 30-day page history
   - Open affected pages → "..." menu → "Page history"
   - Restore to last known good state

4. **Rebuild database** (if extensive)
   ```bash
   # Archive corrupted database (rename in Notion)
   # Create fresh database from template
   python setup_databases.py --create-all

   # Full resync from source systems
   python customer_status_sync.py --full-sync --target new_db_id
   ```

5. **Update config with new database IDs**

---

### Scenario 6: Azure Key Vault Unavailable

**Symptoms:**
- `azure.core.exceptions.ServiceRequestError`
- Secrets not retrievable
- Service fails to start

**Impact:** Critical - Cannot authenticate to any service

**Recovery Steps:**

**Temporary: Fall back to environment variables**
```bash
# Set credentials directly (temporary only)
export NOTION_TOKEN="secret_xxx"
export UNIFI_API_TOKEN="xxx"
export NINJAONE_CLIENT_ID="xxx"
export NINJAONE_CLIENT_SECRET="xxx"

# Unset Key Vault URL to force env var fallback
unset AZURE_KEY_VAULT_URL

# Restart service
systemctl restart oberaconnect-sync
```

**Permanent: Restore Key Vault access**
1. Check Azure status: https://status.azure.com/
2. Verify Key Vault permissions:
   ```bash
   az keyvault show --name oberaconnect-vault
   az keyvault secret list --vault-name oberaconnect-vault
   ```
3. If permissions lost, re-grant:
   ```bash
   az keyvault set-policy --name oberaconnect-vault \
     --object-id $(az ad signed-in-user show --query id -o tsv) \
     --secret-permissions get list
   ```

---

## Data Reconciliation Procedures

### Full Resync Protocol

When data integrity is uncertain, perform full resync:

```bash
#!/bin/bash
# full_resync.sh

echo "=== OberaConnect Full Resync ==="
echo "Started: $(date)"

# Stop scheduled syncs
systemctl stop oberaconnect-sync

# Clear any cached data
redis-cli FLUSHDB

# Resync each database
echo "Syncing Customer Status..."
python customer_status_sync.py --full-sync 2>&1 | tee -a resync.log

echo "Syncing Daily Health..."
python daily_health_sync.py --full-sync 2>&1 | tee -a resync.log

echo "Syncing Config Changes..."
python config_change_sync.py --full-sync 2>&1 | tee -a resync.log

echo "Syncing Alerts..."
python alert_sync.py --full-sync 2>&1 | tee -a resync.log

# Verify counts
echo "=== Verification ==="
python -c "
from notion_client_wrapper import NotionWrapper
client = NotionWrapper()
dbs = ['customer_status', 'daily_health', 'config_changes']
for db in dbs:
    count = len(client.query_database(client.config['databases'][db]))
    print(f'{db}: {count} records')
"

# Restart scheduled syncs
systemctl start oberaconnect-sync

echo "Completed: $(date)"
```

### Partial Resync (Single Database)

```bash
# Resync specific database
python customer_status_sync.py --full-sync --database-id abc123

# Resync specific date range
python daily_health_sync.py --start-date 2025-01-01 --end-date 2025-01-15
```

### Data Validation

```bash
# Verify record counts match source
python -c "
import requests
import os

# Get UniFi site count
unifi_resp = requests.get(
    'https://api.ui.com/ea/sites',
    headers={'Authorization': f'Bearer {os.getenv(\"UNIFI_API_TOKEN\")}'}
)
unifi_count = len(unifi_resp.json().get('data', []))

# Get Notion record count
from notion_client_wrapper import NotionWrapper
client = NotionWrapper()
notion_count = len(client.query_database(client.config['databases']['customer_status']))

print(f'UniFi sites: {unifi_count}')
print(f'Notion records: {notion_count}')
print(f'Match: {unifi_count == notion_count}')
"
```

---

## Backup Procedures

### What to Backup

| Item | Frequency | Location | Retention |
|------|-----------|----------|-----------|
| .env / secrets | On change | Azure Key Vault | Indefinite |
| config.json | On change | Git repository | Indefinite |
| Sync scripts | On change | Git repository | Indefinite |
| Notion databases | Weekly | Notion export | 90 days |
| Audit logs | Daily | Log aggregator | 1 year |

### Notion Database Export

```bash
# Manual export (Notion UI)
# 1. Open database in Notion
# 2. "..." menu → Export → Markdown & CSV
# 3. Store in secure backup location

# Automated export (via API)
python -c "
from notion_client_wrapper import NotionWrapper
import json
from datetime import datetime

client = NotionWrapper()
for db_name, db_id in client.config['databases'].items():
    pages = client.query_database(db_id)
    filename = f'backup_{db_name}_{datetime.now().strftime(\"%Y%m%d\")}.json'
    with open(filename, 'w') as f:
        json.dump(pages, f, indent=2)
    print(f'Exported {len(pages)} pages to {filename}')
"
```

---

## Communication Plan

### Escalation Matrix

| Severity | Response Time | Notify |
|----------|--------------|--------|
| Critical (data breach) | Immediate | Security Team, Management |
| High (service down) | 15 minutes | Platform Team, On-call |
| Medium (degraded) | 1 hour | Platform Team |
| Low (minor issue) | Next business day | Platform Team |

### Status Page Updates

During incidents, update:
1. Internal Slack channel: #oberaconnect-status
2. Customer-facing status page (if applicable)
3. Incident ticket in ServiceNow/Jira

---

## Testing DR Procedures

### Quarterly DR Test Checklist

- [ ] Simulate Notion API outage (mock 503 responses)
- [ ] Rotate all credentials and verify service recovery
- [ ] Restore from Notion page history
- [ ] Deploy from scratch on new server
- [ ] Run full resync and validate data counts
- [ ] Test Key Vault failover to env vars
- [ ] Verify audit logs capture all events
- [ ] Update this document with lessons learned

### Test Command

```bash
# DR test mode (uses mock APIs)
DR_TEST_MODE=true python health_check.py --check
```
