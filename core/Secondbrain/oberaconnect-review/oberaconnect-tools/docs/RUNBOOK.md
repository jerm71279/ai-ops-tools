# OberaConnect Tools - Operational Runbook

## Overview

This runbook covers day-to-day operations, monitoring, and troubleshooting for the OberaConnect MSP Operations Platform.

---

## Quick Reference

### Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| API Health | `GET /health` | Liveness check |
| API Ready | `GET /ready` | Readiness check |
| API Metrics | `GET /metrics` | Operational metrics |
| UniFi Query | `POST /api/unifi/query` | Natural language queries |
| Morning Check | `GET /api/correlate/morning-check` | Daily health report |

### Key Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `UNIFI_API_TOKEN` | Yes | UniFi Site Manager API token |
| `NINJAONE_CLIENT_ID` | Yes | NinjaOne OAuth client ID |
| `NINJAONE_CLIENT_SECRET` | Yes | NinjaOne OAuth client secret |
| `REDIS_URL` | No | Redis connection (defaults to in-memory) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

---

## Starting the Service

### Docker Compose (Recommended)

```bash
# Production
docker-compose up -d

# Demo mode (no credentials needed)
OBERACONNECT_DEMO=true docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

### Direct Python

```bash
# Install
pip install -e ".[cache]"

# Set credentials
export UNIFI_API_TOKEN="your-token"
export NINJAONE_CLIENT_ID="your-id"
export NINJAONE_CLIENT_SECRET="your-secret"

# Run
python -m oberaconnect_tools.n8n.webhook_api
```

---

## Daily Operations

### Morning Health Check

Run the morning check to get a quick overview:

```bash
curl http://localhost:5000/api/correlate/morning-check | jq
```

Expected output:
```json
{
  "timestamp": "2025-01-01T08:00:00Z",
  "unifi": {
    "total_sites": 45,
    "offline_devices": 2,
    "critical_sites": 1
  },
  "ninjaone": {
    "total_alerts": 12,
    "critical_alerts": 3
  }
}
```

### Checking Service Health

```bash
# Liveness (is it running?)
curl http://localhost:5000/health

# Readiness (can it handle requests?)
curl http://localhost:5000/ready

# Metrics
curl http://localhost:5000/metrics
```

### Common Queries

```bash
# Sites with offline devices
curl -X POST http://localhost:5000/api/unifi/query \
  -H "Content-Type: application/json" \
  -d '{"query": "sites with offline devices"}'

# Top 10 sites by clients
curl -X POST http://localhost:5000/api/unifi/query \
  -H "Content-Type: application/json" \
  -d '{"query": "top 10 sites by clients"}'

# Critical alerts
curl http://localhost:5000/api/ninjaone/alerts/critical
```

---

## Monitoring

### Health Check Endpoints

| Endpoint | Status Code | Meaning |
|----------|-------------|---------|
| `/health` | 200 | Service is alive |
| `/ready` | 200 | Service can handle requests |
| `/ready` | 503 | Backend connectivity issues |

### Key Metrics to Monitor

1. **API Response Time**: Target < 500ms for queries
2. **Cache Hit Ratio**: Target > 80% (check Redis stats)
3. **Token Refresh Success**: Should be 100%
4. **Error Rate**: Target < 1%

### Log Analysis

Logs are JSON-formatted for easy parsing:

```bash
# View recent errors
docker-compose logs api 2>&1 | jq 'select(.level == "ERROR")'

# Count errors by type
docker-compose logs api 2>&1 | jq -s 'group_by(.message) | map({message: .[0].message, count: length})'
```

---

## Troubleshooting

### Service Won't Start

1. **Check credentials**:
   ```bash
   # Verify environment variables are set
   docker-compose config | grep -E "(UNIFI|NINJA)"
   ```

2. **Check Redis**:
   ```bash
   docker-compose exec redis redis-cli ping
   # Should return: PONG
   ```

3. **Check logs**:
   ```bash
   docker-compose logs api --tail 50
   ```

### API Returns 503 (Service Unavailable)

1. **Check readiness endpoint**:
   ```bash
   curl http://localhost:5000/ready | jq
   ```

2. **Common causes**:
   - UniFi API token expired → Refresh token
   - NinjaOne credentials invalid → Check OAuth config
   - Redis down → Service falls back to in-memory cache

### Stale Data

1. **Force data refresh**:
   ```bash
   # If using MCP server
   # Call the force_refresh tool

   # Or restart the service
   docker-compose restart api
   ```

2. **Check cache status**:
   ```bash
   docker-compose exec redis redis-cli keys "*"
   docker-compose exec redis redis-cli ttl "unifi:sites"
   ```

### Token Expired (NinjaOne)

The client automatically refreshes tokens. If issues persist:

1. Check logs for authentication errors
2. Verify client credentials are correct
3. Check NinjaOne service status

### High Memory Usage

1. **Check cache size**:
   ```bash
   docker-compose exec redis redis-cli info memory
   ```

2. **Clear cache if needed**:
   ```bash
   docker-compose exec redis redis-cli flushdb
   ```

---

## Maintenance

### Updating the Service

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose build
docker-compose up -d
```

### Rotating Credentials

1. Generate new credentials from respective dashboards
2. Update `.env` file
3. Restart service:
   ```bash
   docker-compose restart api
   ```

### Backup and Restore

Redis data is persisted to a Docker volume:

```bash
# Backup
docker-compose exec redis redis-cli BGSAVE
docker cp oberaconnect-redis:/data/dump.rdb ./backup/

# Restore
docker cp ./backup/dump.rdb oberaconnect-redis:/data/
docker-compose restart redis
```

---

## Incident Response

### Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| P1 | Service completely down | 15 minutes |
| P2 | Major feature unavailable | 1 hour |
| P3 | Minor issue, workaround exists | 4 hours |
| P4 | Enhancement request | Next sprint |

### P1 Response Checklist

1. [ ] Check service health: `curl /health`
2. [ ] Check container status: `docker-compose ps`
3. [ ] Check logs: `docker-compose logs --tail 100`
4. [ ] Check dependencies (Redis, APIs)
5. [ ] Restart if needed: `docker-compose restart`
6. [ ] Escalate if not resolved in 15 min

### Rollback Procedure

```bash
# Stop current version
docker-compose down

# Checkout previous version
git checkout v1.0.0

# Rebuild and start
docker-compose build
docker-compose up -d
```

---

## Contact

- **Engineering Team**: engineering@oberaconnect.com
- **On-Call**: Check PagerDuty schedule
- **Slack**: #oberaconnect-ops
