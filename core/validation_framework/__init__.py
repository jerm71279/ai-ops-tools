"""
Validation Framework
====================
Maker/Checker pattern for validating operations before execution.
"""

from .maker_checker import (
    RiskLevel,
    CheckResult,
    ValidationContext,
    CheckerResponse,
    ExecutionResult,
    BaseChecker,
    CompositeChecker,
    RuleBasedChecker,
    NetworkSafetyChecker,
    MakerChecker,
    rule_required_fields,
    rule_no_empty_strings,
    rule_valid_ip,
    rule_valid_cidr,
    rule_valid_mac,
    rule_in_list,
    rule_max_length,
    rule_positive_number,
    rule_rollback_required,
    rule_bulk_confirmation,
)

from .circuit_breaker import CircuitBreaker, with_retry

__all__ = [
    # Enums
    "RiskLevel",
    "CheckResult",
    # Data classes
    "ValidationContext",
    "CheckerResponse",
    "ExecutionResult",
    # Checkers
    "BaseChecker",
    "CompositeChecker",
    "RuleBasedChecker",
    "NetworkSafetyChecker",
    # Orchestrator
    "MakerChecker",
    # Built-in rules
    "rule_required_fields",
    "rule_no_empty_strings",
    "rule_valid_ip",
    "rule_valid_cidr",
    "rule_valid_mac",
    "rule_in_list",
    "rule_max_length",
    "rule_positive_number",
    "rule_rollback_required",
    "rule_bulk_confirmation",
    # Circuit breaker
    "CircuitBreaker",
    "with_retry",
]
