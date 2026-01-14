# OberaConnect Notion Dashboards - Operational Runbook

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python health_check.py --check` | Check all service health |
| `curl localhost:8080/health` | Liveness probe |
| `curl localhost:8080/ready` | Readiness probe |
| `systemctl status oberaconnect-sync` | Service status |
| `docker logs oberaconnect-sync --tail 50` | Recent logs |

---

## Common Failure Scenarios

### 1. Sync Job Not Running

**Symptoms:**
- Notion dashboards showing stale data
- No recent entries in sync logs
- Health check passes but data not updating

**Diagnosis:**
```bash
# Check if sync service is running
systemctl status oberaconnect-sync

# Check cron/scheduler
crontab -l | grep sync

# Check last sync time
grep "Sync completed" /var/log/oberaconnect/sync.log | tail -5
```

**Resolution:**
```bash
# Restart sync service
systemctl restart oberaconnect-sync

# Or run manual sync
python customer_status_sync.py --verbose
```

**Root Cause Checklist:**
- [ ] Service crashed (check logs)
- [ ] Cron job disabled
- [ ] Credentials expired (check health endpoint)
- [ ] Rate limited by API

---

### 2. HTTP 401 Unauthorized Errors

**Symptoms:**
- `{"error": "Unauthorized"}` in logs
- Health check shows API as unhealthy
- `notion_api`, `unifi_api`, or `ninjaone_api` failing

**Diagnosis:**
```bash
# Check which API is failing
python health_check.py --check --json | jq '.components'

# Test specific API
curl -H "Authorization: Bearer $NOTION_TOKEN" \
  https://api.notion.com/v1/users/me
```

**Resolution:**
```bash
# For Notion
# 1. Verify token in environment
echo $NOTION_TOKEN | head -c 20

# 2. Regenerate if needed (see SECRET_ROTATION.md)

# For UniFi
# Check token expiration in UniFi Site Manager

# For NinjaOne
# Verify OAuth credentials and regenerate if needed
```

---

### 3. HTTP 429 Rate Limited

**Symptoms:**
- `{"code": "rate_limited"}` errors
- Sync jobs taking longer than usual
- Intermittent failures

**Diagnosis:**
```bash
# Check rate limit headers in recent requests
grep "429" /var/log/oberaconnect/sync.log | tail -10

# Check current request rate
grep "API call" /var/log/oberaconnect/sync.log | \
  awk '{print $1}' | uniq -c | tail -5
```

**Resolution:**
```bash
# Reduce sync frequency in config
# Edit config.secure.json:
# "sync_rate_limit_per_second": 2  (was 3)

# Or add delay between batches
python customer_status_sync.py --batch-delay 1.0
```

**Prevention:**
- Notion rate limit: 3 req/sec
- UniFi rate limit: 10 req/sec
- NinjaOne rate limit: Varies by endpoint

---

### 4. Notion Database Schema Mismatch

**Symptoms:**
- `{"code": "validation_error"}` errors
- "Property X does not exist" messages
- New fields not syncing

**Diagnosis:**
```bash
# Compare expected vs actual schema
python -c "
from notion_client_wrapper import NotionWrapper
client = NotionWrapper()
db = client.get_database(client.config['databases']['customer_status'])
for name, prop in db['properties'].items():
    print(f'{name}: {prop[\"type\"]}')"
```

**Resolution:**
```bash
# Option 1: Add missing property in Notion UI
# Open database → + Add a property

# Option 2: Update sync script to match current schema
# Edit customer_status_sync.py to remove/rename field

# Option 3: Recreate database from template
python setup_databases.py --recreate customer_status
```

---

### 5. Duplicate Records in Notion

**Symptoms:**
- Same site/device appearing multiple times
- Record counts higher than source system
- Sync log shows "created" when should be "updated"

**Diagnosis:**
```bash
# Find duplicates
python -c "
from notion_client_wrapper import NotionWrapper
from collections import Counter

client = NotionWrapper()
pages = client.query_database(client.config['databases']['customer_status'])
titles = [client.extract_title(p) for p in pages]
dupes = [t for t, c in Counter(titles).items() if c > 1]
print(f'Duplicates: {dupes}')"
```

**Resolution:**
```bash
# Manual: Archive duplicates in Notion UI

# Automated: Deduplicate script
python -c "
from notion_client_wrapper import NotionWrapper
from collections import defaultdict

client = NotionWrapper()
db_id = client.config['databases']['customer_status']
pages = client.query_database(db_id)

# Group by title
by_title = defaultdict(list)
for p in pages:
    title = client.extract_title(p)
    by_title[title].append(p)

# Archive duplicates (keep newest)
for title, page_list in by_title.items():
    if len(page_list) > 1:
        # Sort by last_edited_time, keep newest
        sorted_pages = sorted(page_list, key=lambda p: p['last_edited_time'], reverse=True)
        for dupe in sorted_pages[1:]:
            print(f'Archiving duplicate: {title}')
            client.archive_page(dupe['id'])
"
```

**Prevention:**
- Use `find_or_create_page()` instead of `create_page()`
- Implement unique constraint checking before insert

---

### 6. Partial Sync Failure

**Symptoms:**
- Some records synced, others failed
- Batch job shows partial success
- Inconsistent data between source and Notion

**Diagnosis:**
```bash
# Check batch results in logs
grep "BatchResult" /var/log/oberaconnect/sync.log | tail -5

# Identify failed records
grep "Failed to sync" /var/log/oberaconnect/sync.log | tail -20
```

**Resolution:**
```bash
# Retry failed records only
python customer_status_sync.py --retry-failed

# Or force full resync
python customer_status_sync.py --full-sync
```

**Investigation:**
- Check if specific records have invalid data
- Verify network wasn't interrupted
- Check if specific properties cause failures

---

### 7. Connection Timeout Errors

**Symptoms:**
- `ConnectionTimeout` or `ReadTimeout` exceptions
- Health checks intermittently failing
- Sync jobs hanging

**Diagnosis:**
```bash
# Test connectivity
curl -v --connect-timeout 5 https://api.notion.com/v1/users/me \
  -H "Authorization: Bearer $NOTION_TOKEN"

# Check DNS resolution
nslookup api.notion.com
nslookup api.ui.com
nslookup app.ninjarmm.com

# Check for network issues
ping -c 5 api.notion.com
traceroute api.notion.com
```

**Resolution:**
```bash
# Increase timeout in config
# Edit resilience.py or config:
# "api_timeout_seconds": 30  (was 10)

# Check if behind proxy
echo $HTTP_PROXY $HTTPS_PROXY

# Restart network service if needed
sudo systemctl restart systemd-networkd
```

---

### 8. Memory/Disk Exhaustion

**Symptoms:**
- `MemoryError` exceptions
- Sync process killed by OOM
- Health check shows disk/memory unhealthy

**Diagnosis:**
```bash
# Check memory
free -h

# Check disk
df -h

# Check process memory
ps aux --sort=-%mem | head -10

# Check container limits
docker stats oberaconnect-sync
```

**Resolution:**
```bash
# Free memory
sync; echo 3 > /proc/sys/vm/drop_caches

# Clean old logs
find /var/log/oberaconnect -name "*.log" -mtime +30 -delete

# Reduce batch size
# Edit config: "sync_batch_size": 25  (was 50)

# Increase container memory limit
# Edit docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 1G
```

---

### 9. SSL Certificate Errors

**Symptoms:**
- `SSLCertVerificationError`
- `CERTIFICATE_VERIFY_FAILED`
- Works in browser but not in script

**Diagnosis:**
```bash
# Check certificate
openssl s_client -connect api.notion.com:443 -servername api.notion.com

# Check system CA certificates
ls -la /etc/ssl/certs/

# Check Python certifi
python -c "import certifi; print(certifi.where())"
```

**Resolution:**
```bash
# Update CA certificates
sudo apt-get update && sudo apt-get install ca-certificates

# Update Python certifi
pip install --upgrade certifi

# If corporate proxy, add proxy CA cert
export REQUESTS_CA_BUNDLE=/path/to/corporate-ca.crt
```

---

### 10. Circuit Breaker Open

**Symptoms:**
- `CircuitOpenError` exceptions
- API calls failing immediately without trying
- Health check shows circuit open

**Diagnosis:**
```bash
# Check circuit breaker state
python -c "
from resilience import circuit_breaker
# Import any decorated function
from some_module import api_call
print(f'Circuit state: {api_call.circuit_breaker.state}')
print(f'Failures: {api_call.circuit_breaker._state.failures}')
"
```

**Resolution:**
```bash
# Wait for timeout (default 60 seconds)
# Circuit will transition to half-open automatically

# Or manually reset (restart service)
systemctl restart oberaconnect-sync

# Investigate root cause
# Check if underlying API is actually failing
```

---

## Monitoring Integration

### Prometheus Alerts

```yaml
# prometheus/alerts.yml
groups:
  - name: oberaconnect
    rules:
      - alert: NotionSyncUnhealthy
        expr: oberaconnect_healthy == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Notion sync service unhealthy"

      - alert: ComponentDown
        expr: oberaconnect_component_healthy == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Component {{ $labels.component }} is down"

      - alert: HighLatency
        expr: oberaconnect_component_latency_ms > 5000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency on {{ $labels.component }}"
```

### Grafana Dashboard

```json
{
  "panels": [
    {
      "title": "Service Health",
      "type": "stat",
      "targets": [{"expr": "oberaconnect_healthy"}]
    },
    {
      "title": "Component Status",
      "type": "table",
      "targets": [{"expr": "oberaconnect_component_healthy"}]
    },
    {
      "title": "API Latency",
      "type": "graph",
      "targets": [{"expr": "oberaconnect_component_latency_ms"}]
    }
  ]
}
```

### Log Aggregation (ELK/Splunk)

```bash
# Filebeat config for log shipping
# /etc/filebeat/filebeat.yml

filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/oberaconnect/*.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "oberaconnect-%{+yyyy.MM.dd}"
```

---

## Escalation Procedures

### Level 1: On-Call Engineer
- Restart services
- Check health endpoints
- Review recent logs
- Apply documented fixes

### Level 2: Platform Team
- Investigate root cause
- Apply configuration changes
- Coordinate with vendors
- Update runbook

### Level 3: Management
- Data breach notification
- Extended outage communication
- Vendor escalation
- Budget for remediation

---

## Maintenance Windows

### Scheduled Maintenance
- **When**: Sundays 2:00-4:00 AM EST
- **Duration**: 2 hours max
- **Notification**: 48 hours advance

### During Maintenance
```bash
# Pause sync jobs
systemctl stop oberaconnect-sync

# Perform maintenance
# ...

# Restart and verify
systemctl start oberaconnect-sync
python health_check.py --check
```

---

## Contact Information

| Role | Contact | Hours |
|------|---------|-------|
| On-Call | PagerDuty | 24/7 |
| Platform Team | #oberaconnect-platform | Business hours |
| Security Team | security@oberaconnect.com | 24/7 for incidents |
| Notion Support | support.notion.so | Business hours |
| NinjaOne Support | support.ninjarmm.com | 24/7 |
