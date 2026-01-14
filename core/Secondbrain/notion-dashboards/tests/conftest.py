"""
Pytest fixtures for OberaConnect Notion integration tests.

Provides common test fixtures and configuration.
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


@pytest.fixture
def sample_config() -> Dict:
    """Sample configuration dictionary."""
    return {
        "notion_token": "secret_test_token_12345",
        "databases": {
            "customer_status": "db_customer_123",
            "daily_health": "db_health_123",
            "azure_pipeline": "db_azure_123",
            "runbook_library": "db_runbook_123",
            "config_changes": "db_changes_123",
            "devices": "db_devices_123",
        },
        "settings": {
            "wifi_signal_threshold_dbm": -65,
            "health_score_warning_threshold": 70,
            "health_score_critical_threshold": 50,
            "batch_pause_seconds": 0.35,
        },
        "maker_checker": {
            "enabled": True,
            "health_drop_threshold": 15,
            "bulk_change_threshold": 10,
        }
    }


@pytest.fixture
def config_file(sample_config: Dict, tmp_path: Path) -> Path:
    """Create temporary config file."""
    config_path = tmp_path / "config.json"
    with open(config_path, 'w') as f:
        json.dump(sample_config, f)
    return config_path


@pytest.fixture
def healthy_site_metrics() -> Dict:
    """Metrics for a perfectly healthy site."""
    return {
        "devices_online": 10,
        "devices_total": 10,
        "wifi_clients": 50,
        "signal_warnings": 0,
        "critical_alerts": 0,
        "warning_alerts": 0,
        "backup_status": "success",
        "config_drift": False,
    }


@pytest.fixture
def unhealthy_site_metrics() -> Dict:
    """Metrics for an unhealthy site."""
    return {
        "devices_online": 5,
        "devices_total": 10,
        "wifi_clients": 50,
        "signal_warnings": 25,
        "critical_alerts": 2,
        "warning_alerts": 5,
        "backup_status": "failed",
        "config_drift": True,
    }


@pytest.fixture
def sample_site_data() -> Dict:
    """Sample UniFi site data."""
    return {
        "site_id": "site_001",
        "name": "Acme Corp - Main Office",
        "state": "Alabama",
        "devices_online": 12,
        "devices_offline": 0,
        "devices_total": 12,
        "wifi_clients": 45,
        "signal_warnings": 2,
        "last_seen": "2025-01-01T00:00:00Z",
        "has_mikrotik": False,
        "has_sonicwall": False,
        "has_azure": True,
    }


@pytest.fixture
def sample_change_data() -> Dict:
    """Sample config change data."""
    return {
        "tool": "mikrotik-config-builder",
        "site": "Acme Corp",
        "action": "deploy",
        "summary": "Updated VPN configuration",
        "details": "Added IPSec peer, updated firewall rules",
        "risk_level": "high",
    }
