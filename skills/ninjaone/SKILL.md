# NinjaOne RMM Skill

Remote Monitoring and Management integration for NinjaOne RMM platform.

## Capabilities

- **Organizations**: List and query customer organizations
- **Devices**: Monitor device status, health, and compliance
- **Alerts**: Track and filter alerts by severity
- **Activities**: View activity logs
- **Scripting**: Execute scripts on managed devices
- **Patching**: Get patch compliance reports
- **Fleet Summary**: Aggregated statistics across all orgs

## Setup

### 1. Create API Credentials

1. Log into NinjaOne Admin Console
2. Go to Administration > Apps > API
3. Create new API application with:
   - Grant Type: Client Credentials
   - Scopes: monitoring, management

### 2. Set Environment Variables

```bash
export NINJAONE_CLIENT_ID="your_client_id"
export NINJAONE_CLIENT_SECRET="your_client_secret"
export NINJAONE_REGION="us"  # us, eu, oc, or ca
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Rate Limits

**IMPORTANT:** NinjaOne enforces API rate limits.

| Tier | Limit |
|------|-------|
| Standard | ~60 requests/minute |
| Enterprise | ~120 requests/minute |

The client will raise `NinjaOneAPIError` with status code 429 when rate limited.

**Best Practices:**
- Cache responses where appropriate (fleet summary, org list)
- Use pagination for large result sets
- Implement backoff on 429 errors (use circuit_breaker.py)
- Batch operations where possible

## Data Schema

### Organization

```json
{
  "id": 123,
  "name": "Customer Corp",
  "description": "Main customer",
  "nodeApprovalMode": "AUTOMATIC"
}
```

### Device

```json
{
  "id": 456,
  "systemName": "DESKTOP-ABC123",
  "dnsName": "desktop-abc123.local",
  "nodeClass": "WINDOWS_WORKSTATION",
  "status": "ONLINE",
  "lastContact": "2025-12-16T10:00:00Z",
  "os": {
    "name": "Windows 11 Pro",
    "version": "23H2"
  },
  "organizationId": 123
}
```

### Alert

```json
{
  "id": 789,
  "deviceId": 456,
  "message": "Disk space low on C:",
  "severity": "MAJOR",
  "status": "ACTIVE",
  "created": "2025-12-16T08:00:00Z"
}
```

### Alert Severities

| Severity | Description |
|----------|-------------|
| NONE | Informational |
| MINOR | Low priority |
| MODERATE | Medium priority |
| MAJOR | High priority |
| CRITICAL | Urgent attention required |

### Device Status

| Status | Description |
|--------|-------------|
| ONLINE | Device is connected |
| OFFLINE | Device not responding |
| APPROVAL_PENDING | Awaiting approval |

### Device Types (nodeClass)

| Type | Description |
|------|-------------|
| WINDOWS_WORKSTATION | Windows desktop/laptop |
| WINDOWS_SERVER | Windows Server |
| MAC | macOS device |
| LINUX_WORKSTATION | Linux desktop |
| LINUX_SERVER | Linux server |
| VMWARE_VM_HOST | VMware host |
| CLOUD_MONITOR_TARGET | Cloud-monitored resource |

## Query Examples

### Get Fleet Summary

```python
client = NinjaOneClient()
summary = await client.get_fleet_summary()
print(f"Devices: {summary['total_devices']}")
print(f"Online: {summary['online_percent']}%")
print(f"Critical Alerts: {summary['critical_alerts']}")
```

### Get Critical Alerts

```python
alerts = await client.get_critical_alerts()
for alert in alerts:
    print(f"{alert['severity']}: {alert['message']}")
```

### Get Offline Devices

```python
offline = await client.get_offline_devices()
for device in offline:
    print(f"{device['systemName']} - Last seen: {device['lastContact']}")
```

### Get Devices by Organization

```python
devices = await client.get_devices(org_id=123)
```

### Run Script on Devices

```python
result = await client.run_script(
    device_ids=[456, 789],
    script_id=100,
    parameters={"param1": "value1"}
)
print(f"Job ID: {result['jobUid']}")
```

## Error Handling

```python
from skills.ninjaone import NinjaOneClient, NinjaOneConfigError, NinjaOneAPIError

client = NinjaOneClient()

try:
    summary = await client.get_fleet_summary()
except NinjaOneConfigError as e:
    print(f"Configuration error: {e}")
    # Missing credentials
except NinjaOneAPIError as e:
    if e.status_code == 429:
        print("Rate limited - implement backoff")
    elif e.status_code == 401:
        print("Authentication failed - check credentials")
    else:
        print(f"API error: {e}")
```

## Integration with Circuit Breaker

```python
from core.validation_framework import with_retry, CircuitBreaker
from skills.ninjaone import NinjaOneClient, NinjaOneAPIError

cb = CircuitBreaker(failure_threshold=3, timeout=60)

@with_retry(max_retries=3, backoff_base=2.0, circuit_breaker=cb)
async def get_summary_with_retry():
    client = NinjaOneClient()
    return await client.get_fleet_summary()
```

## Regional Endpoints

| Region | URL | Use Case |
|--------|-----|----------|
| us | app.ninjarmm.com | United States |
| eu | eu.ninjarmm.com | Europe |
| oc | oc.ninjarmm.com | Oceania (Australia/NZ) |
| ca | ca.ninjarmm.com | Canada |

Select based on your NinjaOne account region for best performance.
