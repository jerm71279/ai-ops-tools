"""
Tests for Maker/Checker Validation Framework.

Tests:
- Bulk operation validation
- Rollback plan requirements
- Risk level classification
- Validation result aggregation
"""

import pytest


class TestValidationContext:
    """Tests for ValidationContext."""

    def test_site_count(self, small_operation_context):
        """Test site count property."""
        assert small_operation_context.site_count == 2

    def test_is_bulk_operation_false(self, small_operation_context):
        """Test bulk operation detection for small operations."""
        assert small_operation_context.is_bulk_operation is False

    def test_is_bulk_operation_true(self, bulk_operation_context):
        """Test bulk operation detection for large operations."""
        assert bulk_operation_context.is_bulk_operation is True
        assert bulk_operation_context.site_count == 15


class TestBulkOperationChecker:
    """Tests for BulkOperationChecker."""

    def test_small_operation_approved(self, small_operation_context):
        """Test that small operations are approved without confirmation."""
        from common.maker_checker import BulkOperationChecker, CheckResult

        checker = BulkOperationChecker()
        response = checker.validate(small_operation_context)

        assert response.result == CheckResult.APPROVED
        assert response.passed is True

    def test_bulk_operation_requires_confirmation(self, bulk_operation_context):
        """Test that bulk operations require confirmation."""
        from common.maker_checker import BulkOperationChecker, CheckResult

        checker = BulkOperationChecker()
        response = checker.validate(bulk_operation_context)

        assert response.result == CheckResult.ESCALATE
        assert 'BULK_OPERATION' in response.risk_flags
        assert len(response.issues) > 0

    def test_bulk_operation_with_confirmation(self):
        """Test bulk operation passes with confirmation and rollback."""
        from common.maker_checker import (
            BulkOperationChecker,
            ValidationContext,
            CheckResult
        )

        ctx = ValidationContext(
            action_name='config_push',
            target_sites=[f'site-{i}' for i in range(15)],
            plan={
                'bulk_confirmed': True,
                'rollback_plan': 'Restore all configs from backup'
            }
        )

        checker = BulkOperationChecker()
        response = checker.validate(ctx)

        assert response.result == CheckResult.APPROVED


class TestRollbackPlanChecker:
    """Tests for RollbackPlanChecker."""

    def test_non_critical_action_approved(self, small_operation_context):
        """Test that non-critical actions don't require rollback plans."""
        from common.maker_checker import RollbackPlanChecker, CheckResult

        checker = RollbackPlanChecker()
        response = checker.validate(small_operation_context)

        assert response.result == CheckResult.APPROVED

    def test_critical_action_requires_rollback(self):
        """Test that critical actions require rollback plans."""
        from common.maker_checker import (
            RollbackPlanChecker,
            ValidationContext,
            CheckResult
        )

        ctx = ValidationContext(
            action_name='firmware_upgrade',
            target_sites=['site-001'],
            plan={}  # No rollback plan
        )

        checker = RollbackPlanChecker()
        response = checker.validate(ctx)

        assert response.result == CheckResult.ESCALATE
        assert 'MISSING_ROLLBACK_PLAN' in response.risk_flags

    def test_critical_action_with_rollback_plan(self, critical_operation_context):
        """Test that critical action with rollback plan is approved."""
        from common.maker_checker import RollbackPlanChecker, CheckResult

        checker = RollbackPlanChecker()
        response = checker.validate(critical_operation_context)

        assert response.result == CheckResult.APPROVED

    def test_brief_rollback_plan_needs_review(self):
        """Test that very brief rollback plans need review."""
        from common.maker_checker import (
            RollbackPlanChecker,
            ValidationContext,
            CheckResult
        )

        ctx = ValidationContext(
            action_name='vlan_change',
            target_sites=['site-001'],
            plan={'rollback_plan': 'Undo it'}  # Too brief
        )

        checker = RollbackPlanChecker()
        response = checker.validate(ctx)

        assert response.result == CheckResult.NEEDS_REVIEW

    def test_critical_actions_list(self):
        """Test that all expected critical actions are recognized."""
        from common.maker_checker import (
            RollbackPlanChecker,
            ValidationContext,
            CheckResult
        )

        critical_actions = [
            'firmware_upgrade',
            'factory_reset',
            'config_push',
            'vlan_change',
            'firewall_rule_change',
            'ssid_modify'
        ]

        checker = RollbackPlanChecker()

        for action in critical_actions:
            ctx = ValidationContext(action_name=action, target_sites=['site-001'])
            response = checker.validate(ctx)
            assert response.result == CheckResult.ESCALATE, f"{action} should require rollback"


class TestMakerCheckerValidator:
    """Tests for the main validator orchestrator."""

    def test_default_checkers_registered(self):
        """Test that default checkers are registered."""
        from common.maker_checker import MakerCheckerValidator

        validator = MakerCheckerValidator()

        assert len(validator.checkers) >= 2
        checker_names = [c.name for c in validator.checkers]
        assert 'bulk_operation_checker' in checker_names
        assert 'rollback_plan_checker' in checker_names

    def test_validation_combines_results(self, bulk_operation_context):
        """Test that validation combines all checker results."""
        from common.maker_checker import MakerCheckerValidator, CheckResult

        validator = MakerCheckerValidator()
        result = validator.validate(bulk_operation_context)

        assert result.overall_result == CheckResult.ESCALATE
        assert 'bulk_operation_checker' in result.checker_responses
        assert len(result.all_issues) > 0

    def test_can_proceed_property(self, small_operation_context):
        """Test can_proceed for passing validation."""
        from common.maker_checker import MakerCheckerValidator

        validator = MakerCheckerValidator()
        result = validator.validate(small_operation_context)

        assert result.can_proceed is True
        assert result.blocked is False

    def test_needs_approval_property(self, bulk_operation_context):
        """Test needs_approval for escalated validation."""
        from common.maker_checker import MakerCheckerValidator

        validator = MakerCheckerValidator()
        result = validator.validate(bulk_operation_context)

        assert result.needs_approval is True
        assert result.can_proceed is False

    def test_custom_checker_registration(self, small_operation_context):
        """Test registering custom checkers."""
        from common.maker_checker import (
            MakerCheckerValidator,
            BaseChecker,
            CheckerResponse,
            CheckResult,
            ValidationContext,
            RiskLevel
        )

        class TestChecker(BaseChecker):
            name = "test_checker"
            description = "Test checker"
            risk_level = RiskLevel.LOW

            def validate(self, ctx: ValidationContext) -> CheckerResponse:
                return CheckerResponse(
                    result=CheckResult.APPROVED,
                    message="Test passed"
                )

        validator = MakerCheckerValidator()
        validator.register(TestChecker())

        result = validator.validate(small_operation_context)

        assert 'test_checker' in result.checker_responses


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_summary_output(self, bulk_operation_context):
        """Test human-readable summary generation."""
        from common.maker_checker import MakerCheckerValidator

        validator = MakerCheckerValidator()
        result = validator.validate(bulk_operation_context)

        summary = result.summary()

        assert 'ESCALATE' in summary
        assert 'Issues:' in summary
        assert 'Suggestions:' in summary


class TestValidateOperationConvenience:
    """Tests for the validate_operation convenience function."""

    def test_basic_validation(self):
        """Test basic validation with convenience function."""
        from common.maker_checker import validate_operation

        result = validate_operation(
            action='config_check',
            sites=['site-001']
        )

        assert result.can_proceed is True

    def test_bulk_validation(self):
        """Test bulk operation with convenience function."""
        from common.maker_checker import validate_operation

        result = validate_operation(
            action='firmware_upgrade',
            sites=[f'site-{i}' for i in range(20)],
            plan={}
        )

        assert result.needs_approval is True
        assert 'BULK_OPERATION' in result.all_risk_flags

    def test_with_rollback_plan(self):
        """Test operation with proper rollback plan."""
        from common.maker_checker import validate_operation

        result = validate_operation(
            action='firmware_upgrade',
            sites=['site-001'],
            plan={
                'firmware_version': '7.0.0',
                'rollback_plan': 'Restore from backup if upgrade fails. Contact support at x123.'
            }
        )

        assert result.can_proceed is True
