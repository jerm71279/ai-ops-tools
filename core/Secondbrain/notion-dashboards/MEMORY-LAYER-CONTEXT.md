# Memory Layer Context: Notion Dashboard System

## Project Identity
```yaml
project: notion-dashboards
type: infrastructure-automation
owner: Maverick
team: OberaConnect Network Engineering
created: December 2024
refactored: January 2025
status: production-ready
```

---

## Technical Context

### Architecture
```yaml
pattern: sync-scripts-with-shared-infrastructure
base_class: BaseSyncClient
databases:
  - customer_status (98 sites)
  - daily_health (daily snapshots)
  - config_changes (audit log)
  - azure_pipeline (service migration)
  - runbook_library (documentation)
  - network_devices (inventory)
```

### Dependencies
```yaml
runtime:
  - python: ">=3.10"
  - notion-client: ">=2.0.0,<3.0.0"
  - python-dateutil: ">=2.8.0"
  
dev:
  - pytest: ">=7.0.0"
  - pytest-cov: ">=4.0.0"
  - mypy: ">=1.0.0"
```

### External APIs
```yaml
notion:
  rate_limit: 3 requests/second
  retry_on: [429, 500, 502, 503, 504]
  max_retries: 3
  backoff: exponential (1s, 2s, 4s)

unifi_site_manager:
  endpoint: unifi.ui.com
  auth: bearer_token
  docs: developer.ui.com
  ports:
    adoption: TCP/8080
    management: TCP/443, TCP/8883

ninjaone:
  purpose: RMM monitoring
  data: alerts, backup_status, device_counts
```

---

## Business Rules (Codified)

### UniFi Best Practices
```yaml
wifi:
  min_signal: -65 dBm
  roaming: BSS_Transition > Minimum_RSSI
  channels_2g: [1, 6, 11]  # Only these
  
vlans:
  reserved: [1, 4095]  # Never use
  
firewall:
  zone_based: inter-VLAN traffic
  acls: intra-VLAN isolation
```

### Maker/Checker Rules
```yaml
bulk_operations:
  threshold: 10 sites
  action: require_confirmation
  
high_risk_changes:
  triggers:
    - action: [delete, rollback]
    - keywords: [firewall, vpn, ipsec, production]
    - tool: sonicwall-scripts
  requires: rollback_plan
  
health_alerts:
  score_drop_threshold: 20 points
  action: flag_for_review
```

### Health Scoring Weights
```yaml
default_weights:
  device_availability: 30
  wifi_quality: 20
  alerts: 20
  backup: 15
  config_compliance: 15
  
thresholds:
  healthy: 80+
  warning: 50-79
  critical: <50
```

---

## Code Patterns

### Creating a New Sync Script
```python
from core import BaseSyncClient, ValidationError

class MySyncClient(BaseSyncClient):
    @property
    def primary_database(self) -> str:
        return "my_database"
    
    def sync(self, **kwargs) -> List[Dict]:
        # Use inherited methods:
        # - self.create_page(db, properties)
        # - self.update_page(page_id, properties)
        # - self.upsert_page(db, title, properties)
        # - self.query_database(db, filter_obj, sorts)
        # - self.check_bulk_operation(count)
        pass
```

### Adding a Typed Data Model
```python
from dataclasses import dataclass
from core.errors import ValidationError

@dataclass
class MyModel:
    name: str
    value: int
    
    def __post_init__(self):
        if not self.name:
            raise ValidationError("name", "Name is required")
        if self.value < 0:
            raise ValidationError("value", "Value must be non-negative")
```

### Creating a Data Source
```python
from data_sources.interface import MyDataSource

class RealMyAPI(MyDataSource):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def fetch_items(self) -> List[MyItem]:
        # Real API implementation
        pass

# Register with factory
from data_sources import get_factory
get_factory().register_my(RealMyAPI(key))
```

---

## Test Patterns

### Fixture in conftest.py
```python
@pytest.fixture
def config_file(tmp_path):
    config = {
        "notion_token": "test-token",
        "databases": {
            "customer_status": "db-123",
            "daily_health": "db-456",
        }
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    return path
```

### Testing Dry-Run Mode
```python
def test_dry_run_returns_preview(self, config_file):
    sync = MySyncClient(str(config_file), dry_run=True)
    result = sync.do_something()
    assert result["status"] == "dry_run"
```

### Testing Validation
```python
def test_empty_name_raises(self):
    with pytest.raises(ValidationError) as exc_info:
        MyModel(name="", value=10)
    assert "name" in str(exc_info.value).lower()
```

---

## Deployment Context

### Repository
```yaml
github: jerm71279/oberaconnect-ai-ops
path: notion-dashboards/
branch: main
```

### Azure VM
```yaml
host: Azure Linux VM
purpose: 24/7 automation
cron: daily_health_sync @ 6 AM
```

### Migration from v1 to v2
```bash
# Test in dry-run
python customer_status_sync_v2.py --config config.json --dry-run

# If successful, update cron/scripts to use _v2 versions
# Keep originals for 2 weeks, then archive
```

---

## Related Projects

| Project | Relation |
|---------|----------|
| oberaconnect-tools | Config changes logged to Notion |
| network-troubleshooter | Assessment results synced |
| mikrotik-config-builder | Deployment logged via config_change_sync |

---

## Revision History

| Date | Change |
|------|--------|
| 2024-12 | Initial Notion SDK implementation |
| 2025-01 | Major refactoring: BaseSyncClient, typed models, 197 tests |

---

*Memory Layer context for RAG/Obsidian integration*
