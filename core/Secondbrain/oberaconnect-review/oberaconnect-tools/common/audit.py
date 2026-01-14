"""
OberaConnect Audit Logging

Provides structured audit logging for all operations that modify state.
Logs are written in JSON format for easy parsing and integration with SIEM tools.

Usage:
    from oberaconnect_tools.common.audit import audit_log, AuditAction

    # Log a successful operation
    audit_log(
        action=AuditAction.SITE_CONFIG_CHANGE,
        target="Setco Industries",
        result="success",
        user="jeremy.smith",
        details={"vlan_id": 100, "change": "enabled network isolation"}
    )

    # Log a failed operation
    audit_log(
        action=AuditAction.SCRIPT_EXECUTION,
        target="device-001",
        result="failed",
        user="api-service",
        details={"script_id": 42, "error": "Permission denied"}
    )

Environment Variables:
    AUDIT_LOG_FILE      - Path to audit log file (default: stdout)
    AUDIT_LOG_LEVEL     - Minimum level to log (default: INFO)
"""

import json
import logging
import os
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class AuditAction(str, Enum):
    """Categorized audit actions for filtering and analysis."""

    # Authentication
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_TOKEN_REFRESH = "auth.token_refresh"
    AUTH_FAILED = "auth.failed"

    # UniFi Operations
    SITE_QUERY = "unifi.site.query"
    SITE_CONFIG_CHANGE = "unifi.site.config_change"
    DEVICE_CONFIG_CHANGE = "unifi.device.config_change"
    NETWORK_CREATE = "unifi.network.create"
    NETWORK_DELETE = "unifi.network.delete"
    NETWORK_MODIFY = "unifi.network.modify"

    # NinjaOne Operations
    ALERT_QUERY = "ninjaone.alert.query"
    ALERT_ACKNOWLEDGE = "ninjaone.alert.acknowledge"
    DEVICE_QUERY = "ninjaone.device.query"
    SCRIPT_EXECUTION = "ninjaone.script.execute"
    PATCH_DEPLOY = "ninjaone.patch.deploy"

    # Validation
    VALIDATION_BLOCKED = "validation.blocked"
    VALIDATION_APPROVED = "validation.approved"

    # Data Operations
    DATA_REFRESH = "data.refresh"
    DATA_EXPORT = "data.export"

    # System
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    SYSTEM_ERROR = "system.error"


class AuditResult(str, Enum):
    """Standard result codes."""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    PENDING = "pending"


@dataclass
class AuditEvent:
    """Structured audit event."""
    timestamp: str
    action: str
    target: str
    result: str
    user: str
    source_ip: Optional[str] = None
    session_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), separators=(',', ':'))


class AuditLogger:
    """
    Audit logger that writes structured JSON events.

    Can write to file or stdout, with automatic log rotation support
    when used with standard log rotation tools.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize audit logger.

        Args:
            log_file: Path to log file. If None, logs to stdout.
        """
        self.log_file = log_file or os.getenv('AUDIT_LOG_FILE')
        self._logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure the audit logger."""
        logger = logging.getLogger('oberaconnect.audit')
        logger.setLevel(logging.INFO)

        # Remove existing handlers
        logger.handlers = []

        # Create handler based on config
        if self.log_file:
            handler = logging.FileHandler(self.log_file, encoding='utf-8')
        else:
            handler = logging.StreamHandler(sys.stdout)

        # Use minimal formatter - JSON already has structure
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)

        # Prevent propagation to root logger
        logger.propagate = False

        return logger

    def log(
        self,
        action: AuditAction,
        target: str,
        result: str,
        user: str = "system",
        source_ip: Optional[str] = None,
        session_id: Optional[str] = None,
        **details
    ) -> AuditEvent:
        """
        Log an audit event.

        Args:
            action: The action being performed
            target: The target of the action (site, device, user, etc.)
            result: The outcome (success, failed, blocked)
            user: The user or service performing the action
            source_ip: Source IP address if available
            session_id: Session identifier if available
            **details: Additional context as key-value pairs

        Returns:
            The created AuditEvent
        """
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action.value if isinstance(action, AuditAction) else action,
            target=target,
            result=result,
            user=user,
            source_ip=source_ip,
            session_id=session_id,
            details=details
        )

        self._logger.info(event.to_json())
        return event


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create the global audit logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def audit_log(
    action: AuditAction,
    target: str,
    result: str,
    user: str = "system",
    source_ip: Optional[str] = None,
    session_id: Optional[str] = None,
    **details
) -> AuditEvent:
    """
    Convenience function for logging audit events.

    Example:
        audit_log(
            action=AuditAction.NETWORK_CREATE,
            target="Unit-101",
            result="success",
            user="jeremy.smith",
            vlan_id=101,
            subnet="10.10.10.0/24"
        )
    """
    return get_audit_logger().log(
        action=action,
        target=target,
        result=result,
        user=user,
        source_ip=source_ip,
        session_id=session_id,
        **details
    )


# Convenience functions for common patterns
def audit_success(action: AuditAction, target: str, user: str = "system", **details):
    """Log a successful operation."""
    return audit_log(action, target, AuditResult.SUCCESS, user, **details)


def audit_failure(action: AuditAction, target: str, user: str = "system", error: str = None, **details):
    """Log a failed operation."""
    if error:
        details['error'] = error
    return audit_log(action, target, AuditResult.FAILED, user, **details)


def audit_blocked(action: AuditAction, target: str, user: str = "system", reason: str = None, **details):
    """Log a blocked operation (by maker-checker validation)."""
    if reason:
        details['blocked_reason'] = reason
    return audit_log(action, target, AuditResult.BLOCKED, user, **details)


__all__ = [
    'AuditAction',
    'AuditResult',
    'AuditEvent',
    'AuditLogger',
    'get_audit_logger',
    'audit_log',
    'audit_success',
    'audit_failure',
    'audit_blocked'
]
