"""
Maker/Checker Validation Framework

A reusable pattern for validating operations before execution, with support for:
- Risk levels (LOW, MEDIUM, HIGH, CRITICAL)
- Automatic escalation based on scope
- Rollback plan requirements
- Extensible checker system

Based on OberaConnect best practices:
- Bulk operations (>10 sites) require confirmation
- HIGH/CRITICAL operations require rollback_plan
- All validation rules are declarative and composable
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
import re


class RiskLevel(Enum):
    """Risk classification for operations."""
    LOW = auto()      # Read-only, no customer impact
    MEDIUM = auto()   # Single-site changes, reversible
    HIGH = auto()     # Multi-site changes, needs approval
    CRITICAL = auto() # Infrastructure-wide, needs rollback plan


class CheckResult(Enum):
    """Result of a validation check."""
    APPROVED = auto()     # Safe to proceed
    NEEDS_REVIEW = auto() # Requires human review
    ESCALATE = auto()     # Needs higher approval
    REJECTED = auto()     # Cannot proceed


@dataclass
class ValidationContext:
    """Context passed to all checkers."""
    action_name: str
    target_sites: List[str] = field(default_factory=list)
    target_devices: List[str] = field(default_factory=list)
    plan: Dict[str, Any] = field(default_factory=dict)
    user: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def site_count(self) -> int:
        return len(self.target_sites)
    
    @property
    def device_count(self) -> int:
        return len(self.target_devices)
    
    @property
    def is_bulk_operation(self) -> bool:
        """OberaConnect rule: >10 sites = bulk operation."""
        return self.site_count > 10


@dataclass
class CheckerResponse:
    """Response from a validation checker."""
    result: CheckResult
    message: str
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def passed(self) -> bool:
        return self.result in (CheckResult.APPROVED, CheckResult.NEEDS_REVIEW)
    
    @property
    def blocked(self) -> bool:
        return self.result == CheckResult.REJECTED


class BaseChecker(ABC):
    """Abstract base class for all validation checkers."""
    
    name: str = "base_checker"
    description: str = "Base validation checker"
    risk_level: RiskLevel = RiskLevel.LOW
    
    @abstractmethod
    def validate(self, ctx: ValidationContext) -> CheckerResponse:
        """Run validation and return response."""
        pass


class BulkOperationChecker(BaseChecker):
    """
    Validates bulk operations per OberaConnect rules.
    
    >10 sites requires explicit confirmation.
    """
    
    name = "bulk_operation_checker"
    description = "Validates bulk operations across multiple sites"
    risk_level = RiskLevel.HIGH
    
    def validate(self, ctx: ValidationContext) -> CheckerResponse:
        if not ctx.is_bulk_operation:
            return CheckerResponse(
                result=CheckResult.APPROVED,
                message=f"Single/small operation: {ctx.site_count} site(s)"
            )
        
        issues = []
        suggestions = []
        
        # Check for confirmation flag
        if not ctx.plan.get('bulk_confirmed'):
            issues.append(f"Bulk operation affecting {ctx.site_count} sites requires confirmation")
            suggestions.append("Set bulk_confirmed=true in plan to proceed")
        
        # Check for rollback plan
        if not ctx.plan.get('rollback_plan'):
            issues.append("Bulk operations require a rollback plan")
            suggestions.append("Include rollback_plan in operation plan")
        
        if issues:
            return CheckerResponse(
                result=CheckResult.ESCALATE,
                message=f"Bulk operation needs confirmation ({ctx.site_count} sites)",
                issues=issues,
                suggestions=suggestions,
                risk_flags=["BULK_OPERATION"]
            )
        
        return CheckerResponse(
            result=CheckResult.APPROVED,
            message=f"Bulk operation confirmed for {ctx.site_count} sites",
            data={"site_count": ctx.site_count}
        )


class RollbackPlanChecker(BaseChecker):
    """
    Validates HIGH/CRITICAL operations have rollback plans.
    """
    
    name = "rollback_plan_checker"
    description = "Ensures high-risk operations have rollback plans"
    risk_level = RiskLevel.HIGH
    
    # Operations that always require rollback plans
    CRITICAL_ACTIONS = {
        'firmware_upgrade', 'factory_reset', 'config_push',
        'vlan_change', 'firewall_rule_change', 'ssid_modify'
    }
    
    def validate(self, ctx: ValidationContext) -> CheckerResponse:
        action_lower = ctx.action_name.lower().replace(' ', '_')
        
        # Check if this is a critical action
        is_critical = any(crit in action_lower for crit in self.CRITICAL_ACTIONS)
        
        if not is_critical:
            return CheckerResponse(
                result=CheckResult.APPROVED,
                message="Action does not require rollback plan"
            )
        
        rollback_plan = ctx.plan.get('rollback_plan', '')
        
        if not rollback_plan:
            return CheckerResponse(
                result=CheckResult.ESCALATE,
                message=f"Critical action '{ctx.action_name}' requires rollback plan",
                issues=["No rollback plan provided"],
                suggestions=[
                    "Include rollback_plan with specific recovery steps",
                    "Example: 'Restore from backup taken at {timestamp}'"
                ],
                risk_flags=["MISSING_ROLLBACK_PLAN"]
            )
        
        # Validate rollback plan quality
        if len(rollback_plan) < 20:
            return CheckerResponse(
                result=CheckResult.NEEDS_REVIEW,
                message="Rollback plan may be insufficient",
                issues=["Rollback plan appears too brief"],
                suggestions=["Include specific recovery steps and timeframes"]
            )
        
        return CheckerResponse(
            result=CheckResult.APPROVED,
            message="Rollback plan provided",
            data={"rollback_plan": rollback_plan}
        )


@dataclass
class ValidationResult:
    """Combined result from all checkers."""
    overall_result: CheckResult
    risk_level: RiskLevel
    checker_responses: Dict[str, CheckerResponse]
    all_issues: List[str]
    all_suggestions: List[str]
    all_risk_flags: List[str]
    
    @property
    def can_proceed(self) -> bool:
        return self.overall_result in (CheckResult.APPROVED, CheckResult.NEEDS_REVIEW)
    
    @property
    def needs_approval(self) -> bool:
        return self.overall_result == CheckResult.ESCALATE
    
    @property
    def blocked(self) -> bool:
        return self.overall_result == CheckResult.REJECTED
    
    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Validation Result: {self.overall_result.name}",
            f"Risk Level: {self.risk_level.name}",
            ""
        ]
        
        if self.all_issues:
            lines.append("Issues:")
            for issue in self.all_issues:
                lines.append(f"  ❌ {issue}")
            lines.append("")
        
        if self.all_suggestions:
            lines.append("Suggestions:")
            for suggestion in self.all_suggestions:
                lines.append(f"  💡 {suggestion}")
            lines.append("")
        
        if self.all_risk_flags:
            lines.append(f"Risk Flags: {', '.join(self.all_risk_flags)}")
        
        return '\n'.join(lines)


class MakerCheckerValidator:
    """
    Main validation orchestrator.
    
    Runs all registered checkers and combines results.
    """
    
    def __init__(self):
        self.checkers: List[BaseChecker] = []
        
        # Register default checkers
        self.register(BulkOperationChecker())
        self.register(RollbackPlanChecker())
    
    def register(self, checker: BaseChecker):
        """Register a validation checker."""
        self.checkers.append(checker)
        return self
    
    def validate(self, ctx: ValidationContext) -> ValidationResult:
        """Run all checkers and return combined result."""
        responses: Dict[str, CheckerResponse] = {}
        all_issues: List[str] = []
        all_suggestions: List[str] = []
        all_risk_flags: List[str] = []
        max_risk = RiskLevel.LOW
        worst_result = CheckResult.APPROVED
        
        for checker in self.checkers:
            response = checker.validate(ctx)
            responses[checker.name] = response
            
            all_issues.extend(response.issues)
            all_suggestions.extend(response.suggestions)
            all_risk_flags.extend(response.risk_flags)
            
            # Track highest risk level
            if checker.risk_level.value > max_risk.value:
                max_risk = checker.risk_level
            
            # Track worst result
            if response.result.value > worst_result.value:
                worst_result = response.result
        
        return ValidationResult(
            overall_result=worst_result,
            risk_level=max_risk,
            checker_responses=responses,
            all_issues=all_issues,
            all_suggestions=list(set(all_suggestions)),  # Dedupe
            all_risk_flags=list(set(all_risk_flags))
        )


# Convenience function for quick validation
def validate_operation(
    action: str,
    sites: Optional[List[str]] = None,
    devices: Optional[List[str]] = None,
    plan: Optional[Dict[str, Any]] = None,
    extra_checkers: Optional[List[BaseChecker]] = None
) -> ValidationResult:
    """
    Quick validation of an operation.
    
    Args:
        action: Name of the action being performed
        sites: List of target site IDs
        devices: List of target device MACs
        plan: Operation plan with parameters
        extra_checkers: Additional checkers to run
    
    Returns:
        ValidationResult with combined checker responses
    
    Example:
        result = validate_operation(
            action="firmware_upgrade",
            sites=["site-001", "site-002"],
            plan={
                "firmware_version": "7.0.0",
                "rollback_plan": "Restore from backup if upgrade fails"
            }
        )
        if result.can_proceed:
            execute_upgrade()
    """
    ctx = ValidationContext(
        action_name=action,
        target_sites=sites or [],
        target_devices=devices or [],
        plan=plan or {}
    )
    
    validator = MakerCheckerValidator()
    
    if extra_checkers:
        for checker in extra_checkers:
            validator.register(checker)
    
    return validator.validate(ctx)


# Export all public classes and functions
__all__ = [
    'RiskLevel',
    'CheckResult',
    'ValidationContext',
    'CheckerResponse',
    'BaseChecker',
    'BulkOperationChecker',
    'RollbackPlanChecker',
    'ValidationResult',
    'MakerCheckerValidator',
    'validate_operation'
]
