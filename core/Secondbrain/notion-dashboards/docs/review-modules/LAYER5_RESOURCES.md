# Layer 5: RESOURCES Review Summary

## External Service Connections

| Service | URL | Rate Limit | Status |
|---------|-----|------------|--------|
| Notion API | api.notion.com | 3/sec | ✅ Connected |
| UniFi Site Manager | api.ui.com | 10/sec | ✅ Connected |
| NinjaOne RMM | app.ninjarmm.com | Varies | ✅ Connected |
| Azure Key Vault | *.vault.azure.net | N/A | Optional |

## Data Store Integrations

| Store | Purpose | Implementation |
|-------|---------|----------------|
| Notion Databases | Primary data store | notion-client SDK |
| Azure Key Vault | Secret storage | azure-keyvault-secrets |
| Environment Variables | Dev fallback | os.getenv() |

## Caching Strategy

```python
# health_check.py
class HealthChecker:
    _cache_ttl = 10  # seconds
    # Cache prevents redundant API calls during rapid health checks
```

**Cache Locations:**
- Health check results: 10s in-memory
- API tokens: Until expiry (managed by SDK)
- No persistent cache (Notion is source of truth)

## Rate Limiting

```python
# resilience.py - RateLimiter
class RateLimiter:
    rate = 3.0      # tokens per second
    burst = 10      # max tokens
```

**Applied To:**
- Notion API calls: 3/sec (matches API limit)
- Bulk operations: 0.35s pause between items

## Capacity

| Resource | Current | Limit | Headroom |
|----------|---------|-------|----------|
| UniFi Sites | 98 | 500 | 5x |
| NinjaOne Devices | 323 | 1000 | 3x |
| Notion Pages | ~500 | 10,000 | 20x |
| Health Check | <5ms | 1000ms | 200x |

## MCP Compatibility

- **Not MCP-enabled** (standard REST APIs)
- Could add MCP wrapper for Claude Code integration
- Currently uses direct HTTP client

## Score: 8/10

**Strengths**: Well-defined limits, SDK integrations, capacity headroom
**Gap**: No Redis/persistent cache, no MCP support yet
