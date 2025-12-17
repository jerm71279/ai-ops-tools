"""
Orchestration Validator
=======================

Integrates maker_checker validation framework into Layer 3 orchestration.
Validates requests before execution based on risk level.
"""

import os
import sys
from typing import Any, Callable, Dict, Optional, Tuple

# Add oberaconnect-ai-ops to path for imports
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from core.validation_framework import (
    MakerChecker,
    RiskLevel,
    CheckResult,
    BaseChecker,
    RuleBasedChecker,
    CompositeChecker,
    ValidationContext,
    CheckerResponse,
    ExecutionResult,
    rule_required_fields,
    rule_bulk_confirmation,
)

from ..core.base import AIRequest
from ..core.logging import get_logger

logger = get_logger("ai_os.layer3.validator")


# =============================================================================
# RISK CLASSIFICATION
# =============================================================================

# Keywords that indicate higher risk operations
HIGH_RISK_KEYWORDS = [
    "delete", "remove", "destroy", "terminate", "shutdown",
    "firewall", "security", "credentials", "password", "secret",
    "production", "prod", "live", "customer",
    "all devices", "all sites", "bulk", "mass",
]

CRITICAL_RISK_KEYWORDS = [
    "wipe", "format", "reset factory", "nuke",
    "delete all", "remove all", "destroy all",
    "root", "admin", "sudo",
]

MEDIUM_RISK_KEYWORDS = [
    "update", "modify", "change", "configure", "edit",
    "restart", "reboot", "deploy",
]


def classify_risk(request: AIRequest) -> RiskLevel:
    """
    Classify risk level based on request content and metadata.

    Returns:
        RiskLevel: NONE, LOW, MEDIUM, HIGH, or CRITICAL
    """
    content_lower = request.content.lower()

    # Check for critical risk keywords
    for keyword in CRITICAL_RISK_KEYWORDS:
        if keyword in content_lower:
            logger.warning(f"CRITICAL risk keyword detected: {keyword}")
            return RiskLevel.CRITICAL

    # Check for high risk keywords
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in content_lower:
            logger.info(f"HIGH risk keyword detected: {keyword}")
            return RiskLevel.HIGH

    # Check for medium risk keywords
    for keyword in MEDIUM_RISK_KEYWORDS:
        if keyword in content_lower:
            return RiskLevel.MEDIUM

    # Check request type
    request_type = request.request_type or ""
    if request_type in ["action", "execute", "command"]:
        return RiskLevel.MEDIUM

    # Check complexity from classification
    classification = request.classification or {}
    complexity = classification.get("complexity", "simple")
    if complexity == "complex":
        return RiskLevel.MEDIUM

    # Default: read-only operations are LOW risk
    if any(word in content_lower for word in ["list", "show", "get", "query", "search", "find", "status"]):
        return RiskLevel.LOW

    return RiskLevel.NONE


# =============================================================================
# SECONDBRAIN CHECKER
# =============================================================================

class SecondbrainChecker(BaseChecker):
    """
    Checker for Secondbrain AI operations.

    Validates:
    - Request has valid content
    - Risk level is appropriate for automatic execution
    - Bulk operations are confirmed
    - Critical operations have required context
    """

    def __init__(self, auto_approve_level: RiskLevel = RiskLevel.MEDIUM):
        """
        Initialize checker.

        Args:
            auto_approve_level: Maximum risk level to auto-approve.
                               Anything higher requires escalation.
        """
        self.auto_approve_level = auto_approve_level
        self._risk_order = [
            RiskLevel.NONE,
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.CRITICAL
        ]

    def check(self, context: ValidationContext) -> CheckerResponse:
        """Validate the request."""
        issues = []
        suggestions = []
        risk_flags = []

        plan = context.plan or {}

        # Check 1: Content must exist
        content = plan.get("content", "")
        if not content or len(content.strip()) < 3:
            issues.append("Request content is empty or too short")

        # Check 2: Risk level assessment
        current_risk_idx = self._risk_order.index(context.risk_level)
        auto_approve_idx = self._risk_order.index(self.auto_approve_level)

        if current_risk_idx > auto_approve_idx:
            risk_flags.append(f"Risk level {context.risk_level.value} exceeds auto-approve threshold ({self.auto_approve_level.value})")

        # Check 3: Critical operations need confirmation
        if context.risk_level == RiskLevel.CRITICAL:
            if not plan.get("confirmed"):
                issues.append("CRITICAL operations require explicit confirmation (confirmed=True)")
                suggestions.append("Add 'confirmed: true' to the request context")

        # Check 4: HIGH operations need rollback plan for workflows
        if context.risk_level == RiskLevel.HIGH:
            if plan.get("type") == "workflow" and not plan.get("rollback_plan"):
                suggestions.append("Consider adding rollback_plan for HIGH risk workflows")
                risk_flags.append("HIGH risk workflow without rollback plan")

        # Check 5: Bulk operations
        targets = plan.get("targets", [])
        if isinstance(targets, list) and len(targets) > 10:
            if not plan.get("bulk_confirmed"):
                issues.append(f"Bulk operation ({len(targets)} targets) requires bulk_confirmed=True")

        # Determine result
        if issues:
            return CheckerResponse(
                result=CheckResult.REJECTED,
                message="Validation failed",
                issues=issues,
                suggestions=suggestions,
                risk_flags=risk_flags
            )

        if risk_flags and context.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return CheckerResponse(
                result=CheckResult.ESCALATE,
                message="Operation requires human review",
                issues=[],
                suggestions=suggestions,
                risk_flags=risk_flags
            )

        return CheckerResponse(
            result=CheckResult.APPROVED,
            message="Validation passed",
            suggestions=suggestions,
            risk_flags=risk_flags
        )

    def get_name(self) -> str:
        return "SecondbrainChecker"


# =============================================================================
# ORCHESTRATION VALIDATOR
# =============================================================================

class OrchestrationValidator:
    """
    Validates requests before orchestration execution.

    Usage:
        validator = OrchestrationValidator()
        is_approved, message = validator.validate(request)
        if not is_approved:
            return AIResponse.error_response(error=message)
    """

    def __init__(
        self,
        auto_approve_level: RiskLevel = RiskLevel.MEDIUM,
        audit_log_path: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Initialize validator.

        Args:
            auto_approve_level: Maximum risk level to auto-approve
            audit_log_path: Path for audit log (default: logs/orchestration/audit.jsonl)
            enabled: Whether validation is enabled
        """
        self.enabled = enabled
        self.auto_approve_level = auto_approve_level

        # Set up audit log path
        if audit_log_path:
            self.audit_log_path = audit_log_path
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            self.audit_log_path = os.path.join(base_dir, "logs", "orchestration", "audit.jsonl")

        # Create checker
        self.checker = SecondbrainChecker(auto_approve_level=auto_approve_level)

        logger.info(f"OrchestrationValidator initialized (enabled={enabled}, auto_approve={auto_approve_level.value})")

    def validate(self, request: AIRequest, strategy: Dict[str, Any] = None) -> Tuple[bool, str, Optional[ExecutionResult]]:
        """
        Validate a request before execution.

        Args:
            request: The AIRequest to validate
            strategy: Execution strategy (from _determine_strategy)

        Returns:
            Tuple of (approved: bool, message: str, result: ExecutionResult or None)
        """
        if not self.enabled:
            return True, "Validation disabled", None

        # Classify risk
        risk_level = classify_risk(request)

        # Build plan from request
        plan = {
            "content": request.content,
            "request_id": request.request_id,
            "request_type": request.request_type,
            "source": request.source,
            "target_agent": request.target_agent,
            "type": strategy.get("type") if strategy else "single",
            "confirmed": request.context.get("confirmed", False),
            "bulk_confirmed": request.context.get("bulk_confirmed", False),
            "rollback_plan": request.context.get("rollback_plan"),
            "targets": request.context.get("targets", []),
        }

        # Create MakerChecker instance
        mc = MakerChecker(
            checker=self.checker,
            risk_level=risk_level,
            max_iterations=1,  # No auto-fix for orchestration
            audit_log_path=self.audit_log_path,
            operator_id=request.source or "unknown"
        )

        # Execute validation (execute_fn just returns the plan - we don't actually execute here)
        result = mc.execute(
            action_name=f"orchestrate:{request.request_id[:8]}",
            input_data=plan,
            execute_fn=lambda p: p,  # Dummy - just validate
            auto_fix=False
        )

        if result.success:
            logger.info(f"Request {request.request_id[:8]} approved (risk={risk_level.value})")
            return True, "Approved", result
        else:
            logger.warning(f"Request {request.request_id[:8]} rejected: {result.error}")
            return False, result.error, result

    def set_auto_approve_level(self, level: RiskLevel):
        """Update auto-approve threshold."""
        self.auto_approve_level = level
        self.checker = SecondbrainChecker(auto_approve_level=level)
        logger.info(f"Auto-approve level updated to {level.value}")


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_validator(
    enabled: bool = True,
    auto_approve_level: str = "medium"
) -> OrchestrationValidator:
    """
    Factory function to create validator from config.

    Args:
        enabled: Whether validation is enabled
        auto_approve_level: "none", "low", "medium", "high", or "critical"

    Returns:
        OrchestrationValidator instance
    """
    level_map = {
        "none": RiskLevel.NONE,
        "low": RiskLevel.LOW,
        "medium": RiskLevel.MEDIUM,
        "high": RiskLevel.HIGH,
        "critical": RiskLevel.CRITICAL,
    }

    level = level_map.get(auto_approve_level.lower(), RiskLevel.MEDIUM)

    return OrchestrationValidator(
        auto_approve_level=level,
        enabled=enabled
    )
