"""
OberaConnect Tools - Common Module

Shared utilities for validation, maker/checker patterns, and audit logging.
"""

from .maker_checker import (
    RiskLevel,
    CheckResult,
    ValidationContext,
    CheckerResponse,
    BaseChecker,
    BulkOperationChecker,
    RollbackPlanChecker,
    ValidationResult,
    MakerCheckerValidator,
    validate_operation
)

from .validators import (
    ValidationError,
    Validator,
    collect_errors,
    validate_vlan_id,
    validate_wifi_channel,
    validate_signal_strength,
    validate_ssid
)

from .audit import (
    AuditAction,
    AuditResult,
    AuditEvent,
    AuditLogger,
    get_audit_logger,
    audit_log,
    audit_success,
    audit_failure,
    audit_blocked
)

from .logging import (
    JSONFormatter,
    TextFormatter,
    setup_logging,
    get_logger,
    LogContext
)

from .cache import (
    Cache,
    get_cache,
    cached,
    invalidate_pattern
)

__all__ = [
    # Maker/Checker
    'RiskLevel',
    'CheckResult',
    'ValidationContext',
    'CheckerResponse',
    'BaseChecker',
    'BulkOperationChecker',
    'RollbackPlanChecker',
    'ValidationResult',
    'MakerCheckerValidator',
    'validate_operation',
    # Validators
    'ValidationError',
    'Validator',
    'collect_errors',
    'validate_vlan_id',
    'validate_wifi_channel',
    'validate_signal_strength',
    'validate_ssid',
    # Audit
    'AuditAction',
    'AuditResult',
    'AuditEvent',
    'AuditLogger',
    'get_audit_logger',
    'audit_log',
    'audit_success',
    'audit_failure',
    'audit_blocked',
    # Logging
    'JSONFormatter',
    'TextFormatter',
    'setup_logging',
    'get_logger',
    'LogContext',
    # Cache
    'Cache',
    'get_cache',
    'cached',
    'invalidate_pattern'
]
