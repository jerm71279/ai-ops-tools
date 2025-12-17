"""
Maker/Checker Validation Framework
==================================

Reusable validation pattern for autonomous operations.
Import this for any tool that needs pre-execution validation.

Usage:
    from core.validation_framework import MakerChecker, RiskLevel, BaseChecker

    class MyChecker(BaseChecker):
        def check(self, context): ...

    mc = MakerChecker(checker=MyChecker(), risk_level=RiskLevel.HIGH)
    result = mc.execute("action", data, execute_fn)
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class RiskLevel(Enum):
    """Risk classification for operations."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CheckResult(Enum):
    """Result of a validation check."""
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATE = "escalate"
    NEEDS_INFO = "needs_info"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ValidationContext:
    """Context passed to checkers."""
    action_name: str
    plan: Dict[str, Any]
    risk_level: RiskLevel
    operator_id: Optional[str] = None
    iteration: int = 0
    previous_issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckerResponse:
    """Response from a checker."""
    result: CheckResult
    message: str
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    modified_plan: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionResult:
    """Result of executing an action through maker/checker."""
    success: bool
    action_name: str
    result: Any = None
    error: Optional[str] = None
    iterations_required: int = 0
    validation_history: List[Dict] = field(default_factory=list)
    final_plan: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0


# ============================================================================
# BASE CHECKER
# ============================================================================

class BaseChecker(ABC):
    """Abstract base class for all checkers."""

    @abstractmethod
    def check(self, context: ValidationContext) -> CheckerResponse:
        """Validate the action plan."""
        pass

    def get_name(self) -> str:
        return self.__class__.__name__


class CompositeChecker(BaseChecker):
    """Combines multiple checkers - all must pass."""

    def __init__(self, checkers: List[BaseChecker]):
        self.checkers = checkers

    def check(self, context: ValidationContext) -> CheckerResponse:
        all_issues = []
        all_suggestions = []
        all_risk_flags = []

        for checker in self.checkers:
            response = checker.check(context)

            if response.result == CheckResult.REJECTED:
                return response

            all_issues.extend(response.issues)
            all_suggestions.extend(response.suggestions)
            all_risk_flags.extend(response.risk_flags)

            if response.result == CheckResult.ESCALATE:
                return CheckerResponse(
                    CheckResult.ESCALATE,
                    f"Escalated by {checker.get_name()}",
                    all_issues,
                    all_suggestions,
                    all_risk_flags
                )

        return CheckerResponse(
            CheckResult.APPROVED,
            "All checks passed",
            all_issues,
            all_suggestions,
            all_risk_flags
        )

    def get_name(self) -> str:
        return f"Composite({', '.join(c.get_name() for c in self.checkers)})"


class RuleBasedChecker(BaseChecker):
    """Checker that applies a list of rule functions."""

    def __init__(self):
        self.rules: List[Callable[[ValidationContext], Tuple[bool, str]]] = []

    def add_rule(self, rule: Callable[[ValidationContext], Tuple[bool, str]]) -> 'RuleBasedChecker':
        self.rules.append(rule)
        return self

    def check(self, context: ValidationContext) -> CheckerResponse:
        issues = []

        for rule in self.rules:
            passed, message = rule(context)
            if not passed:
                issues.append(message)

        if issues:
            return CheckerResponse(
                CheckResult.REJECTED,
                "Rule validation failed",
                issues
            )

        return CheckerResponse(CheckResult.APPROVED, "All rules passed")

    def get_name(self) -> str:
        return f"RuleBasedChecker({len(self.rules)} rules)"


# ============================================================================
# BUILT-IN CHECKERS
# ============================================================================

class NetworkSafetyChecker(BaseChecker):
    """Validates network-related operations for safety."""

    DANGEROUS_PORTS = [22, 23, 3389, 445, 135, 139]
    PRIVATE_RANGES = ['10.', '172.16.', '172.17.', '172.18.', '172.19.',
                      '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
                      '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
                      '172.30.', '172.31.', '192.168.']

    def check(self, context: ValidationContext) -> CheckerResponse:
        issues = []
        suggestions = []
        risk_flags = []

        plan = context.plan or {}

        # Check for dangerous port exposure
        ports = plan.get('ports', [])
        for port in ports:
            if isinstance(port, int) and port in self.DANGEROUS_PORTS:
                risk_flags.append(f"Exposing sensitive port: {port}")

        # Check for public exposure of private IPs
        target_ip = plan.get('target_ip') or plan.get('ip')
        if target_ip:
            is_private = any(target_ip.startswith(r) for r in self.PRIVATE_RANGES)
            if plan.get('public_access') and is_private:
                issues.append(f"Cannot expose private IP {target_ip} publicly")

        # Check for firewall rule dangers
        if 'firewall' in str(plan).lower():
            if plan.get('action') == 'allow' and plan.get('source') == 'any':
                risk_flags.append("Firewall rule allows traffic from any source")

        if issues:
            return CheckerResponse(CheckResult.REJECTED, "Network safety check failed", issues, suggestions, risk_flags)

        if risk_flags and context.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return CheckerResponse(CheckResult.ESCALATE, "Network operation flagged for review", [], suggestions, risk_flags)

        return CheckerResponse(CheckResult.APPROVED, "Network safety check passed", [], suggestions, risk_flags)

    def get_name(self) -> str:
        return "NetworkSafetyChecker"


# ============================================================================
# BUILT-IN RULES
# ============================================================================

def rule_required_fields(*fields: str) -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: Required fields must be present."""
    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        plan = ctx.plan or {}
        missing = [f for f in fields if f not in plan or plan[f] is None]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        return True, ""
    return check


def rule_no_empty_strings(*fields: str) -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: Specified fields cannot be empty strings."""
    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        plan = ctx.plan or {}
        empty = [f for f in fields if f in plan and plan[f] == ""]
        if empty:
            return False, f"Fields cannot be empty: {', '.join(empty)}"
        return True, ""
    return check


def rule_valid_ip(field_name: str) -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: Field must be valid IP address."""
    pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')

    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        plan = ctx.plan or {}
        value = plan.get(field_name)
        if value and not pattern.match(str(value)):
            return False, f"Invalid IP in '{field_name}': {value}"
        return True, ""
    return check


def rule_valid_cidr(field_name: str) -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: Field must be valid CIDR notation."""
    pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$')

    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        plan = ctx.plan or {}
        value = plan.get(field_name)
        if value and not pattern.match(str(value)):
            return False, f"Invalid CIDR in '{field_name}': {value}"
        return True, ""
    return check


def rule_valid_mac(field_name: str) -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: Field must be valid MAC address."""
    patterns = [
        re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'),
        re.compile(r'^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$'),
        re.compile(r'^[0-9A-Fa-f]{12}$')
    ]

    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        plan = ctx.plan or {}
        value = plan.get(field_name)
        if value and not any(p.match(str(value)) for p in patterns):
            return False, f"Invalid MAC in '{field_name}': {value}"
        return True, ""
    return check


def rule_in_list(field_name: str, allowed: List[str]) -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: Field value must be in allowed list."""
    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        plan = ctx.plan or {}
        value = plan.get(field_name)
        if value and value not in allowed:
            return False, f"'{field_name}' must be one of: {allowed}"
        return True, ""
    return check


def rule_max_length(field_name: str, max_len: int) -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: String field must not exceed max length."""
    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        plan = ctx.plan or {}
        value = plan.get(field_name, "")
        if len(str(value)) > max_len:
            return False, f"'{field_name}' exceeds {max_len} chars"
        return True, ""
    return check


def rule_positive_number(field_name: str) -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: Numeric field must be positive."""
    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        plan = ctx.plan or {}
        value = plan.get(field_name)
        if value is not None:
            try:
                if float(value) <= 0:
                    return False, f"'{field_name}' must be positive"
            except (ValueError, TypeError):
                return False, f"'{field_name}' must be a number"
        return True, ""
    return check


def rule_rollback_required() -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: HIGH/CRITICAL operations need rollback_plan."""
    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        if ctx.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            if not ctx.plan.get("rollback_plan"):
                return False, "rollback_plan required for HIGH/CRITICAL operations"
        return True, ""
    return check


def rule_bulk_confirmation(threshold: int = 10) -> Callable[[ValidationContext], Tuple[bool, str]]:
    """Rule: Bulk operations need confirmation."""
    def check(ctx: ValidationContext) -> Tuple[bool, str]:
        plan = ctx.plan or {}
        targets = plan.get("targets") or plan.get("site_ids") or plan.get("device_ids") or []
        if isinstance(targets, list) and len(targets) > threshold:
            if not plan.get("bulk_confirmed"):
                return False, f"Bulk operation ({len(targets)} targets) requires bulk_confirmed=True"
        return True, ""
    return check


# ============================================================================
# MAKER/CHECKER ORCHESTRATOR
# ============================================================================

class MakerChecker:
    """
    Orchestrates the maker/checker validation pattern.

    Usage:
        mc = MakerChecker(checker=MyChecker(), risk_level=RiskLevel.HIGH)
        result = mc.execute(
            action_name="deploy_config",
            input_data={"site_id": "abc", "config": {...}},
            execute_fn=lambda plan: api.deploy(plan)
        )
    """

    def __init__(
        self,
        checker: BaseChecker,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        max_iterations: int = 3,
        audit_log_path: Optional[str] = None,
        operator_id: Optional[str] = None
    ):
        self.checker = checker
        self.risk_level = risk_level
        self.max_iterations = max_iterations
        self.operator_id = operator_id
        self.audit_log_path = audit_log_path or os.path.join(
            os.getcwd(), "logs", "maker_checker", "audit_trail.jsonl"
        )

    def execute(
        self,
        action_name: str,
        input_data: Dict[str, Any],
        execute_fn: Callable[[Dict[str, Any]], Any],
        auto_fix: bool = False
    ) -> ExecutionResult:
        """
        Execute an action through the maker/checker pattern.

        Args:
            action_name: Name of the action being performed
            input_data: The action plan/parameters
            execute_fn: Function to execute if validation passes
            auto_fix: Whether to attempt automatic fixes

        Returns:
            ExecutionResult with success status and details
        """
        start_time = datetime.utcnow()
        validation_history = []
        current_plan = input_data.copy()
        previous_issues = []

        for iteration in range(self.max_iterations):
            context = ValidationContext(
                action_name=action_name,
                plan=current_plan,
                risk_level=self.risk_level,
                operator_id=self.operator_id,
                iteration=iteration,
                previous_issues=previous_issues
            )

            response = self.checker.check(context)

            validation_history.append({
                "iteration": iteration,
                "result": response.result.value,
                "message": response.message,
                "issues": response.issues,
                "suggestions": response.suggestions,
                "risk_flags": response.risk_flags
            })

            if response.result == CheckResult.APPROVED:
                try:
                    result = execute_fn(current_plan)
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                    exec_result = ExecutionResult(
                        success=True,
                        action_name=action_name,
                        result=result,
                        iterations_required=iteration + 1,
                        validation_history=validation_history,
                        final_plan=current_plan,
                        execution_time_ms=execution_time
                    )
                    self._audit_log(exec_result)
                    return exec_result

                except Exception as e:
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    exec_result = ExecutionResult(
                        success=False,
                        action_name=action_name,
                        error=f"Execution failed: {str(e)}",
                        iterations_required=iteration + 1,
                        validation_history=validation_history,
                        final_plan=current_plan,
                        execution_time_ms=execution_time
                    )
                    self._audit_log(exec_result)
                    return exec_result

            elif response.result == CheckResult.REJECTED:
                if auto_fix and response.modified_plan:
                    current_plan = response.modified_plan
                    previous_issues = response.issues
                    continue
                else:
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    exec_result = ExecutionResult(
                        success=False,
                        action_name=action_name,
                        error=f"Validation rejected: {'; '.join(response.issues)}",
                        iterations_required=iteration + 1,
                        validation_history=validation_history,
                        final_plan=current_plan,
                        execution_time_ms=execution_time
                    )
                    self._audit_log(exec_result)
                    return exec_result

            elif response.result == CheckResult.ESCALATE:
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                exec_result = ExecutionResult(
                    success=False,
                    action_name=action_name,
                    error=f"Escalated for review: {response.message}. Risk flags: {response.risk_flags}",
                    iterations_required=iteration + 1,
                    validation_history=validation_history,
                    final_plan=current_plan,
                    execution_time_ms=execution_time
                )
                self._audit_log(exec_result)
                return exec_result

            elif response.result == CheckResult.NEEDS_INFO:
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                exec_result = ExecutionResult(
                    success=False,
                    action_name=action_name,
                    error=f"Additional information required: {response.message}",
                    iterations_required=iteration + 1,
                    validation_history=validation_history,
                    final_plan=current_plan,
                    execution_time_ms=execution_time
                )
                self._audit_log(exec_result)
                return exec_result

        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        exec_result = ExecutionResult(
            success=False,
            action_name=action_name,
            error=f"Max iterations ({self.max_iterations}) exceeded",
            iterations_required=self.max_iterations,
            validation_history=validation_history,
            final_plan=current_plan,
            execution_time_ms=execution_time
        )
        self._audit_log(exec_result)
        return exec_result

    def _audit_log(self, result: ExecutionResult) -> None:
        """Log execution result to audit trail."""
        try:
            log_dir = Path(self.audit_log_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)

            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "operator_id": self.operator_id,
                "risk_level": self.risk_level.value,
                **asdict(result)
            }

            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(entry, default=str) + "\n")

        except Exception as e:
            logger.warning(f"Failed to write audit log: {e}")

    @staticmethod
    def protected(
        checker: BaseChecker,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        action_name: Optional[str] = None
    ):
        """Decorator to protect a function with maker/checker validation."""
        def decorator(fn: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                mc = MakerChecker(checker=checker, risk_level=risk_level)
                name = action_name or fn.__name__

                input_data = kwargs.copy()
                if args:
                    import inspect
                    sig = inspect.signature(fn)
                    params = list(sig.parameters.keys())
                    for i, arg in enumerate(args):
                        if i < len(params):
                            input_data[params[i]] = arg

                return mc.execute(
                    action_name=name,
                    input_data=input_data,
                    execute_fn=lambda plan: fn(**plan)
                )
            return wrapper
        return decorator
