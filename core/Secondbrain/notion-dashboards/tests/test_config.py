"""
Unit tests for configuration management.

Tests Config loading, validation, and database ID access.
"""

import pytest
import json
import os
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from core.config import (
    Config,
    DatabaseIds,
    SyncSettings,
    MakerCheckerConfig,
    load_config,
)
from core.errors import ConfigurationError


class TestDatabaseIds:
    """Tests for DatabaseIds dataclass."""
    
    def test_get_existing(self):
        """Should return ID for configured database."""
        db_ids = DatabaseIds(customer_status="db_123")
        assert db_ids.get("customer_status") == "db_123"
    
    def test_get_missing(self):
        """Should return None for unconfigured database."""
        db_ids = DatabaseIds()
        assert db_ids.get("customer_status") is None
    
    def test_get_with_hyphen(self):
        """Should handle hyphenated names."""
        db_ids = DatabaseIds(daily_health="db_456")
        assert db_ids.get("daily-health") == "db_456"
    
    def test_require_existing(self):
        """Should return ID when database is configured."""
        db_ids = DatabaseIds(customer_status="db_123")
        assert db_ids.require("customer_status") == "db_123"
    
    def test_require_missing_raises(self):
        """Should raise ConfigurationError for missing database."""
        db_ids = DatabaseIds()
        with pytest.raises(ConfigurationError) as exc_info:
            db_ids.require("customer_status")
        assert "customer_status" in str(exc_info.value)


class TestSyncSettings:
    """Tests for SyncSettings dataclass."""
    
    def test_defaults(self):
        """Should have sensible defaults."""
        settings = SyncSettings()
        assert settings.wifi_signal_threshold_dbm == -65
        assert settings.health_score_warning_threshold == 70
        assert settings.health_score_critical_threshold == 50
        assert settings.batch_pause_seconds == 0.35
        assert settings.max_retries == 3


class TestMakerCheckerConfig:
    """Tests for MakerCheckerConfig dataclass."""
    
    def test_defaults(self):
        """Should be enabled by default with thresholds."""
        mc = MakerCheckerConfig()
        assert mc.enabled is True
        assert mc.health_drop_threshold == 15
        assert mc.bulk_change_threshold == 10
        assert mc.require_rollback_for_high_risk is True


class TestConfigFromDict:
    """Tests for Config.from_dict()."""
    
    def test_minimal_config(self):
        """Should create config from minimal dict."""
        data = {
            "notion_token": "secret_test_123",
            "databases": {}
        }
        config = Config.from_dict(data)
        assert config.notion_token == "secret_test_123"
    
    def test_full_config(self, sample_config):
        """Should parse all configuration options."""
        config = Config.from_dict(sample_config)
        
        assert config.notion_token == "secret_test_token_12345"
        assert config.databases.customer_status == "db_customer_123"
        assert config.settings.wifi_signal_threshold_dbm == -65
        assert config.maker_checker.enabled is True
    
    def test_missing_token_raises(self):
        """Should raise error when token missing."""
        data = {"databases": {}}
        with pytest.raises(ConfigurationError) as exc_info:
            Config.from_dict(data)
        assert "token" in str(exc_info.value).lower()
    
    def test_env_token_override(self, sample_config, monkeypatch):
        """Environment variable should override config file token."""
        monkeypatch.setenv("NOTION_TOKEN", "secret_from_env")
        config = Config.from_dict(sample_config)
        assert config.notion_token == "secret_from_env"
    
    def test_missing_settings_uses_defaults(self):
        """Should use defaults when settings not provided."""
        data = {
            "notion_token": "secret_test_123",
            "databases": {}
        }
        config = Config.from_dict(data)
        assert config.settings.max_retries == 3  # Default value


class TestConfigFromFile:
    """Tests for Config.from_file()."""
    
    def test_load_valid_file(self, config_file, sample_config):
        """Should load configuration from file."""
        config = Config.from_file(str(config_file))
        assert config.notion_token == sample_config["notion_token"]
    
    def test_missing_file_raises(self, tmp_path):
        """Should raise error for missing file."""
        missing_path = tmp_path / "nonexistent.json"
        with pytest.raises(ConfigurationError) as exc_info:
            Config.from_file(str(missing_path))
        assert "not found" in str(exc_info.value).lower()
    
    def test_invalid_json_raises(self, tmp_path):
        """Should raise error for invalid JSON."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ invalid json }")
        
        with pytest.raises(ConfigurationError) as exc_info:
            Config.from_file(str(bad_file))
        assert "invalid json" in str(exc_info.value).lower()


class TestConfigValidation:
    """Tests for Config.validate()."""
    
    def test_valid_config_passes(self, sample_config):
        """Valid config should pass validation."""
        config = Config.from_dict(sample_config)
        config.validate()  # Should not raise
    
    def test_empty_token_fails(self):
        """Empty token should fail validation."""
        config = Config(
            notion_token="",
            databases=DatabaseIds()
        )
        with pytest.raises(ConfigurationError):
            config.validate()


class TestConfigToDict:
    """Tests for Config.to_dict()."""
    
    def test_roundtrip(self, sample_config):
        """Should serialize back to dict."""
        config = Config.from_dict(sample_config)
        result = config.to_dict()
        
        assert result["notion_token"] == sample_config["notion_token"]
        assert "customer_status" in result["databases"]


class TestLoadConfigFunction:
    """Tests for load_config convenience function."""
    
    def test_loads_and_validates(self, config_file):
        """Should load and validate in one call."""
        config = load_config(str(config_file))
        assert config.notion_token is not None
