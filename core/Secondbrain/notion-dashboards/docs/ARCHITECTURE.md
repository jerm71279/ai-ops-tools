# OberaConnect Notion Dashboards - Architecture

## System Overview

```mermaid
flowchart TB
    subgraph Sources["Data Sources"]
        UniFi["UniFi Site Manager<br/>98 Sites | 496 Devices"]
        NinjaOne["NinjaOne RMM<br/>323 Devices | Alerts"]
    end

    subgraph Security["Security Layer"]
        KeyVault["Azure Key Vault<br/>Production Secrets"]
        EnvVars["Environment Variables<br/>Development Fallback"]
    end

    subgraph SyncService["Sync Service (Python)"]
        direction TB
        SecureConfig["secure_config.py<br/>Credential Manager"]
        Resilience["resilience.py<br/>Retry | Circuit Breaker"]
        Logging["structured_logging.py<br/>JSON Audit Logs"]

        subgraph SyncScripts["Sync Scripts"]
            CustomerSync["customer_status_sync.py"]
            HealthSync["daily_health_sync.py"]
            ConfigSync["config_change_sync.py"]
            AlertSync["alert_sync.py"]
        end

        NotionWrapper["notion_client_wrapper.py<br/>API Client + Validation"]
        HealthCheck["health_check.py<br/>/health /ready /metrics"]
    end

    subgraph Notion["Notion Workspace"]
        CustomerDB[("Customer Status<br/>98 Records")]
        HealthDB[("Daily Health<br/>Metrics")]
        ConfigDB[("Config Changes<br/>Audit Trail")]
        AlertsDB[("Alerts<br/>Incidents")]
    end

    subgraph Monitoring["Monitoring"]
        Prometheus["Prometheus<br/>Metrics Scrape"]
        Grafana["Grafana<br/>Dashboards"]
        Logs["Log Aggregator<br/>ELK/Splunk"]
    end

    %% Data Flow
    UniFi -->|"REST API<br/>Bearer Token"| SyncScripts
    NinjaOne -->|"OAuth2<br/>Client Credentials"| SyncScripts

    %% Security Flow
    KeyVault -.->|"Production"| SecureConfig
    EnvVars -.->|"Development"| SecureConfig
    SecureConfig --> SyncScripts

    %% Resilience
    Resilience --> NotionWrapper
    SyncScripts --> NotionWrapper

    %% Output
    NotionWrapper -->|"Notion API<br/>Rate Limited"| CustomerDB
    NotionWrapper --> HealthDB
    NotionWrapper --> ConfigDB
    NotionWrapper --> AlertsDB

    %% Logging
    Logging --> Logs

    %% Health Checks
    HealthCheck -->|":8080/metrics"| Prometheus
    Prometheus --> Grafana
```

## Component Details

### Security Layer

| Component | Purpose | Technology |
|-----------|---------|------------|
| Azure Key Vault | Production secret storage | Azure SDK |
| Environment Variables | Development/fallback | OS native |
| Audit Logging | Compliance trail | JSON structured logs |

### Sync Service Components

| Component | Responsibility | Key Features |
|-----------|---------------|--------------|
| `secure_config.py` | Credential management | Key Vault priority, env fallback, secret stripping |
| `resilience.py` | Fault tolerance | Retry (3x exponential), circuit breaker (5 failures), rate limiting |
| `structured_logging.py` | Observability | JSON format, correlation IDs, operation timing |
| `notion_client_wrapper.py` | API abstraction | Retry wrapper, input validation, audit logging |
| `health_check.py` | Monitoring endpoints | Liveness, readiness, Prometheus metrics |

### Data Flow

```mermaid
sequenceDiagram
    participant Cron as Cron/Scheduler
    participant Sync as Sync Script
    participant Config as SecureConfig
    participant KV as Key Vault
    participant API as Source API
    participant Resilience as Resilience
    participant Notion as Notion API
    participant Log as Audit Log

    Cron->>Sync: Trigger sync job
    Sync->>Config: Get credentials
    Config->>KV: Fetch secrets
    KV-->>Config: Return secrets
    Config-->>Sync: Credentials ready

    loop For each site/device
        Sync->>API: Fetch data
        API-->>Sync: Site/device data
        Sync->>Resilience: Wrap API call
        Resilience->>Notion: Create/update page

        alt Success
            Notion-->>Resilience: 200 OK
            Resilience-->>Sync: Success
            Sync->>Log: Audit: page_updated
        else Rate Limited
            Notion-->>Resilience: 429 Too Many
            Resilience->>Resilience: Backoff wait
            Resilience->>Notion: Retry
        else Circuit Open
            Resilience-->>Sync: CircuitOpenError
            Sync->>Log: Audit: circuit_open
        end
    end

    Sync->>Log: Audit: sync_complete
```

## Deployment Architecture

```mermaid
flowchart LR
    subgraph Docker["Docker Host"]
        Container["oberaconnect-sync<br/>Python 3.11"]
        HealthPort[":8080"]
    end

    subgraph External["External Services"]
        NotionAPI["api.notion.com"]
        UniFiAPI["api.ui.com"]
        NinjaAPI["app.ninjarmm.com"]
        AzureKV["*.vault.azure.net"]
    end

    subgraph Monitoring["Monitoring Stack"]
        Prom["Prometheus"]
        Alert["Alertmanager"]
    end

    Container --> NotionAPI
    Container --> UniFiAPI
    Container --> NinjaAPI
    Container -.-> AzureKV

    HealthPort --> Prom
    Prom --> Alert
```

## Error Handling Flow

```mermaid
flowchart TD
    Start([API Call]) --> Try{Try Request}

    Try -->|Success| Log1[Log Success]
    Log1 --> Done([Complete])

    Try -->|Failure| Check{Check Error Type}

    Check -->|429 Rate Limit| Backoff[Exponential Backoff]
    Backoff --> Retry{Retries < 3?}
    Retry -->|Yes| Try
    Retry -->|No| Circuit[Trip Circuit Breaker]

    Check -->|5xx Server| Backoff

    Check -->|401 Unauthorized| Log2[Log Auth Failure]
    Log2 --> Alert1[Alert: Credential Issue]
    Alert1 --> Fail([Fail Fast])

    Check -->|Network Error| Backoff

    Circuit --> Log3[Log Circuit Open]
    Log3 --> Alert2[Alert: Service Degraded]
    Alert2 --> Fail
```

## Security Architecture

```mermaid
flowchart TB
    subgraph Secrets["Secret Management"]
        direction LR
        KV["Azure Key Vault<br/>(Production)"]
        Env["Environment Vars<br/>(Development)"]
    end

    subgraph Validation["Input Validation"]
        SiteName["validate_site_name()<br/>Regex + length"]
        DbId["validate_database_id()<br/>UUID format"]
        Sanitize["sanitize_for_notion()<br/>XSS prevention"]
    end

    subgraph Audit["Audit Trail"]
        SecretAccess["Secret Access Log"]
        PageOps["Page Create/Update Log"]
        SyncOps["Sync Operation Log"]
    end

    KV --> SecureConfig
    Env --> SecureConfig
    SecureConfig --> SecretAccess

    Input([User Input]) --> Validation
    Validation --> SafeData([Sanitized Data])

    SafeData --> NotionAPI
    NotionAPI --> PageOps

    SyncJob --> SyncOps
```

## Metrics & Monitoring

| Metric | Type | Description |
|--------|------|-------------|
| `oberaconnect_healthy` | Gauge | Overall service health (0/1) |
| `oberaconnect_uptime_seconds` | Gauge | Service uptime |
| `oberaconnect_component_healthy` | Gauge | Per-component health |
| `oberaconnect_component_latency_ms` | Gauge | API response time |
| `oberaconnect_sync_total` | Counter | Total sync operations |
| `oberaconnect_sync_errors` | Counter | Failed sync operations |

## Capacity Planning

| Resource | Current | Limit | Headroom |
|----------|---------|-------|----------|
| UniFi Sites | 98 | 500 | 5x |
| NinjaOne Devices | 323 | 1000 | 3x |
| Notion Pages | ~500 | 10,000 | 20x |
| API Rate (Notion) | 3/sec | 3/sec | At limit |
| Sync Frequency | 15 min | 5 min | 3x |

## Failure Domains

| Domain | Impact | Mitigation |
|--------|--------|------------|
| Notion API down | Dashboards stale | Circuit breaker, retry on recovery |
| UniFi API down | No site updates | Continue NinjaOne sync, alert |
| NinjaOne API down | No device/alert updates | Continue UniFi sync, alert |
| Key Vault down | Cannot start | Fallback to env vars |
| Network partition | All syncs fail | Health check degrades, alert |
