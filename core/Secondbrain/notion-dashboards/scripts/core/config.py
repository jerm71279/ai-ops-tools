"""
Centralized configuration management for OberaConnect Notion integration.

Handles loading, validation, and access to configuration settings.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Any

from core.errors import ConfigurationError
from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MakerCheckerConfig:
    """Maker/checker validation thresholds."""
    enabled: bool = True
    health_drop_threshold: int = 15
    bulk_change_threshold: int = 10
    require_rollback_for_high_risk: bool = True


@dataclass
class SyncSettings:
    """General sync operation settings."""
    wifi_signal_threshold_dbm: int = -65
    health_score_warning_threshold: int = 70
    health_score_critical_threshold: int = 50
    batch_pause_seconds: float = 0.35
    max_retries: int = 3


@dataclass
class DatabaseIds:
    """Notion database IDs."""
    customer_status: Optional[str] = None
    daily_health: Optional[str] = None
    azure_pipeline: Optional[str] = None
    runbook_library: Optional[str] = None
    config_changes: Optional[str] = None
    deployments: Optional[str] = None
    devices: Optional[str] = None
    device_issues: Optional[str] = None

    def get(self, name: str) -> Optional[str]:
        """Get database ID by name."""
        return getattr(self, name.replace("-", "_"), None)
    
    def require(self, name: str) -> str:
        """Get database ID or raise if not configured."""
        db_id = self.get(name)
        if not db_id:
            raise ConfigurationError(
                f"Database '{name}' not configured",
                {"available": [k for k, v in self.__dict__.items() if v]}
            )
        return db_id


@dataclass
class Config:
    """
    Complete configuration for Notion sync operations.
    
    Loaded from JSON file, with environment variable overrides supported.
    """
    notion_token: str
    databases: DatabaseIds
    settings: SyncSettings = field(default_factory=SyncSettings)
    maker_checker: MakerCheckerConfig = field(default_factory=MakerCheckerConfig)
    
    # Optional external API configs (for future use)
    unifi: Dict[str, Any] = field(default_factory=dict)
    ninjaone: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, path: str) -> 'Config':
        """
        Load configuration from JSON file.
        
        Args:
            path: Path to config JSON file
        
        Returns:
            Validated Config instance
        
        Raises:
            ConfigurationError: If file missing or invalid
        """
        config_path = Path(path)
        
        if not config_path.exists():
            raise ConfigurationError(
                f"Config file not found: {path}",
                {"searched_path": str(config_path.absolute())}
            )
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in config file: {e}",
                {"path": path, "line": e.lineno}
            )
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """
        Create Config from dictionary.
        
        Supports environment variable override for token:
        - Set NOTION_TOKEN env var to override config file value
        """
        # Token: env var takes precedence
        token = os.getenv("NOTION_TOKEN") or data.get("notion_token")
        if not token:
            raise ConfigurationError(
                "Notion token required. Set NOTION_TOKEN env var or add 'notion_token' to config."
            )
        
        # Database IDs
        db_data = data.get("databases", {})
        databases = DatabaseIds(
            customer_status=db_data.get("customer_status"),
            daily_health=db_data.get("daily_health"),
            azure_pipeline=db_data.get("azure_pipeline"),
            runbook_library=db_data.get("runbook_library"),
            config_changes=db_data.get("config_changes"),
            deployments=db_data.get("deployments"),
            devices=db_data.get("devices"),
            device_issues=db_data.get("device_issues"),
        )
        
        # Settings
        settings_data = data.get("settings", {})
        settings = SyncSettings(
            wifi_signal_threshold_dbm=settings_data.get("wifi_signal_threshold_dbm", -65),
            health_score_warning_threshold=settings_data.get("health_score_warning_threshold", 70),
            health_score_critical_threshold=settings_data.get("health_score_critical_threshold", 50),
            batch_pause_seconds=settings_data.get("batch_pause_seconds", 0.35),
            max_retries=settings_data.get("max_retries", 3),
        )
        
        # Maker/checker
        mc_data = data.get("maker_checker", {})
        maker_checker = MakerCheckerConfig(
            enabled=mc_data.get("enabled", True),
            health_drop_threshold=mc_data.get("health_drop_threshold", 15),
            bulk_change_threshold=mc_data.get("bulk_change_threshold", 10),
            require_rollback_for_high_risk=mc_data.get("require_rollback_for_high_risk", True),
        )
        
        return cls(
            notion_token=token,
            databases=databases,
            settings=settings,
            maker_checker=maker_checker,
            unifi=data.get("unifi", {}),
            ninjaone=data.get("ninjaone", {}),
        )
    
    def validate(self) -> None:
        """
        Validate configuration completeness.
        
        Raises:
            ConfigurationError: If required settings missing
        """
        if not self.notion_token:
            raise ConfigurationError("Notion token is required")
        
        if not self.notion_token.startswith("secret_"):
            logger.warning(
                "Notion token doesn't start with 'secret_' - "
                "ensure you're using an integration token"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config back to dictionary (for serialization)."""
        return {
            "notion_token": self.notion_token,
            "databases": {
                k: v for k, v in self.databases.__dict__.items() if v
            },
            "settings": self.settings.__dict__,
            "maker_checker": self.maker_checker.__dict__,
            "unifi": self.unifi,
            "ninjaone": self.ninjaone,
        }


# Convenience function
def load_config(path: str) -> Config:
    """
    Load and validate configuration from file.
    
    Args:
        path: Path to config JSON
    
    Returns:
        Validated Config instance
    """
    config = Config.from_file(path)
    config.validate()
    logger.info(f"Loaded config from {path}")
    return config
