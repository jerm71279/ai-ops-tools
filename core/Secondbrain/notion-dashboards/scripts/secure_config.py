#!/usr/bin/env python3
"""
Secure Configuration Manager for OberaConnect Notion Dashboards

Security Features:
- Azure Key Vault integration for production secrets
- Environment variable fallback for development
- NEVER stores secrets in config files
- Validates all credentials on load
- Audit logging for credential access

Usage:
    from secure_config import SecureConfig
    config = SecureConfig()

    # Get secret (tries Key Vault first, then env var)
    notion_token = config.get_secret("NOTION_TOKEN")

    # Get non-sensitive config
    threshold = config.get("settings.health_score_warning_threshold", default=70)

Environment Variables:
    AZURE_KEY_VAULT_URL - Azure Key Vault URL (optional, for production)
    NOTION_TOKEN - Notion integration token (required)
    UNIFI_API_TOKEN - UniFi Site Manager token
    NINJAONE_CLIENT_ID - NinjaOne OAuth client ID
    NINJAONE_CLIENT_SECRET - NinjaOne OAuth client secret

Author: OberaConnect
Created: 2025
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from functools import lru_cache

# Structured logging
logger = logging.getLogger("oberaconnect.config")


@dataclass
class SecretAuditEvent:
    """Audit event for secret access."""
    timestamp: str
    secret_name: str
    source: str  # "keyvault", "env", "failed"
    success: bool
    caller: str


class SecureConfig:
    """
    Secure configuration manager with multi-source secret retrieval.

    Priority order for secrets:
    1. Azure Key Vault (production)
    2. Environment variables (development/fallback)
    3. NEVER from config files
    """

    # Secrets that MUST come from secure sources (never config files)
    PROTECTED_SECRETS = frozenset({
        "NOTION_TOKEN",
        "UNIFI_API_TOKEN",
        "NINJAONE_CLIENT_ID",
        "NINJAONE_CLIENT_SECRET",
        "SMTP_PASSWORD",
    })

    def __init__(
        self,
        config_path: Optional[str] = None,
        keyvault_url: Optional[str] = None
    ):
        """
        Initialize secure config manager.

        Args:
            config_path: Path to non-sensitive config JSON (database IDs, thresholds)
            keyvault_url: Azure Key Vault URL (or set AZURE_KEY_VAULT_URL env var)
        """
        self._config: Dict[str, Any] = {}
        self._keyvault_client = None
        self._keyvault_url = keyvault_url or os.getenv("AZURE_KEY_VAULT_URL")

        # Load non-sensitive config
        if config_path:
            self._load_config(config_path)

        # Initialize Key Vault if available
        if self._keyvault_url:
            self._init_keyvault()

    def _load_config(self, config_path: str) -> None:
        """Load non-sensitive configuration from JSON file."""
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return

        with open(path, 'r') as f:
            data = json.load(f)

        # Strip any secrets that may have been accidentally included
        self._config = self._sanitize_config(data)
        logger.info(f"Loaded config from {config_path}")

    def _sanitize_config(self, data: Dict) -> Dict:
        """Remove any secrets from config data."""
        sanitized = {}

        for key, value in data.items():
            # Skip any keys that look like secrets
            key_upper = key.upper()
            if any(secret in key_upper for secret in ["TOKEN", "SECRET", "PASSWORD", "KEY", "CREDENTIAL"]):
                logger.warning(f"Stripped potential secret from config: {key}")
                continue

            if isinstance(value, dict):
                # Recursively sanitize nested dicts
                sanitized[key] = self._sanitize_config(value)
            else:
                sanitized[key] = value

        return sanitized

    def _init_keyvault(self) -> None:
        """Initialize Azure Key Vault client."""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            credential = DefaultAzureCredential()
            self._keyvault_client = SecretClient(
                vault_url=self._keyvault_url,
                credential=credential
            )
            logger.info(f"Connected to Azure Key Vault: {self._keyvault_url}")
        except ImportError:
            logger.warning(
                "Azure SDK not installed. Install with: "
                "pip install azure-identity azure-keyvault-secrets"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Key Vault: {e}")

    def get_secret(self, name: str, required: bool = True) -> Optional[str]:
        """
        Get a secret value from secure sources.

        Priority:
        1. Azure Key Vault (if configured)
        2. Environment variable

        Args:
            name: Secret name (e.g., "NOTION_TOKEN")
            required: Raise error if not found

        Returns:
            Secret value or None

        Raises:
            ValueError: If required and not found
        """
        value = None
        source = "failed"

        # Try Key Vault first
        if self._keyvault_client:
            try:
                # Key Vault uses hyphens, not underscores
                kv_name = name.lower().replace("_", "-")
                secret = self._keyvault_client.get_secret(kv_name)
                value = secret.value
                source = "keyvault"
                logger.debug(f"Retrieved {name} from Key Vault")
            except Exception as e:
                logger.debug(f"Key Vault lookup failed for {name}: {e}")

        # Fallback to environment variable
        if value is None:
            value = os.getenv(name)
            if value:
                source = "env"
                logger.debug(f"Retrieved {name} from environment variable")

        # Audit log the access
        self._audit_secret_access(name, source, value is not None)

        if value is None and required:
            raise ValueError(
                f"Required secret '{name}' not found. "
                f"Set {name} environment variable or configure Azure Key Vault."
            )

        return value

    def _audit_secret_access(self, name: str, source: str, success: bool) -> None:
        """Log audit event for secret access."""
        import traceback
        from datetime import datetime

        # Get caller info
        stack = traceback.extract_stack()
        caller = "unknown"
        for frame in reversed(stack[:-2]):
            if "secure_config" not in frame.filename:
                caller = f"{frame.filename}:{frame.lineno}"
                break

        event = SecretAuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            secret_name=name,
            source=source,
            success=success,
            caller=caller
        )

        # Log as structured JSON for audit trail
        audit_logger = logging.getLogger("oberaconnect.audit")
        audit_logger.info(json.dumps({
            "event": "secret_access",
            "timestamp": event.timestamp,
            "secret_name": event.secret_name,
            "source": event.source,
            "success": event.success,
            "caller": event.caller
        }))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a non-sensitive config value.

        Supports dot notation for nested values:
            config.get("settings.health_score_warning_threshold")

        Args:
            key: Config key (dot notation supported)
            default: Default value if not found

        Returns:
            Config value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def get_database_id(self, name: str) -> Optional[str]:
        """Get a Notion database ID by name."""
        return self.get(f"databases.{name}")

    def validate(self) -> Dict[str, bool]:
        """
        Validate all required credentials are available.

        Returns:
            Dict of credential name -> is_available
        """
        results = {}

        for secret_name in self.PROTECTED_SECRETS:
            try:
                value = self.get_secret(secret_name, required=False)
                results[secret_name] = value is not None
            except Exception:
                results[secret_name] = False

        return results

    def print_status(self) -> None:
        """Print configuration status (safe for logs)."""
        print("\n=== OberaConnect Config Status ===")
        print(f"Key Vault: {'Connected' if self._keyvault_client else 'Not configured'}")

        print("\nCredential Status:")
        for name, available in self.validate().items():
            status = "OK" if available else "MISSING"
            print(f"  {name}: {status}")

        print("\nNon-Sensitive Config:")
        for key in ["databases", "settings", "maker_checker"]:
            if key in self._config:
                print(f"  {key}: {len(self._config[key])} items")


@lru_cache(maxsize=1)
def get_config(config_path: Optional[str] = None) -> SecureConfig:
    """Get singleton config instance."""
    return SecureConfig(config_path=config_path)


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """CLI for testing secure config."""
    import argparse

    parser = argparse.ArgumentParser(description="Secure config manager")
    parser.add_argument("--status", action="store_true", help="Show config status")
    parser.add_argument("--validate", action="store_true", help="Validate all credentials")
    parser.add_argument("--config", type=str, help="Path to config file")

    args = parser.parse_args()

    config = SecureConfig(config_path=args.config)

    if args.status:
        config.print_status()

    if args.validate:
        results = config.validate()
        all_ok = all(results.values())

        print("\nValidation Results:")
        for name, ok in results.items():
            print(f"  {name}: {'PASS' if ok else 'FAIL'}")

        return 0 if all_ok else 1

    return 0


if __name__ == "__main__":
    exit(main())
