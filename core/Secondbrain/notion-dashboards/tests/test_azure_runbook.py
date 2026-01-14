"""
Unit tests for Azure Pipeline Manager and Runbook Manager.

Tests the refactored versions using BaseSyncClient.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from azure_pipeline_sync_v2 import (
    AzurePipelineManager,
    AzureService,
    AzureCategory,
    PipelineStage,
    TestStatus,
    StageGateResult,
)

from runbook_manager_v2 import (
    RunbookManager,
    Runbook,
    RunbookCategory,
    Vendor,
    DocumentType,
    ComplexityLevel,
    AutomationStatus,
)

from core.errors import ValidationError, MakerCheckerError


# =============================================================================
# Azure Pipeline Manager Tests
# =============================================================================

class TestAzureCategory:
    """Tests for AzureCategory enum."""
    
    def test_all_categories_exist(self):
        """Should have all 15 categories."""
        expected = [
            "Compute", "Networking", "Storage", "Databases", "Identity",
            "Security", "Management", "DevOps", "AI/ML", "Analytics",
            "Integration", "IoT", "Migration", "Backup", "Monitoring"
        ]
        values = AzureCategory.values()
        for cat in expected:
            assert cat in values
    
    def test_values_method(self):
        """values() should return list of strings."""
        values = AzureCategory.values()
        assert isinstance(values, list)
        assert all(isinstance(v, str) for v in values)


class TestPipelineStage:
    """Tests for PipelineStage enum."""
    
    def test_stage_values(self):
        """Should have expected stages."""
        stages = PipelineStage.values()
        assert "backlog" in stages
        assert "lab testing" in stages
        assert "production validation" in stages
        assert "customer ready" in stages
        assert "deprecated" in stages
    
    def test_next_stage_backlog(self):
        """Backlog should advance to lab testing."""
        stage = PipelineStage.BACKLOG
        assert stage.next_stage() == PipelineStage.LAB_TESTING
    
    def test_next_stage_lab(self):
        """Lab testing should advance to production validation."""
        stage = PipelineStage.LAB_TESTING
        assert stage.next_stage() == PipelineStage.PRODUCTION_VALIDATION
    
    def test_next_stage_production(self):
        """Production validation should advance to customer ready."""
        stage = PipelineStage.PRODUCTION_VALIDATION
        assert stage.next_stage() == PipelineStage.CUSTOMER_READY
    
    def test_next_stage_customer_ready(self):
        """Customer ready has no next stage."""
        stage = PipelineStage.CUSTOMER_READY
        assert stage.next_stage() is None
    
    def test_next_stage_deprecated(self):
        """Deprecated has no next stage."""
        stage = PipelineStage.DEPRECATED
        assert stage.next_stage() is None


class TestAzureService:
    """Tests for AzureService dataclass."""
    
    def test_basic_creation(self):
        """Should create service with required fields."""
        service = AzureService(
            name="Azure VPN",
            category=AzureCategory.NETWORKING
        )
        
        assert service.name == "Azure VPN"
        assert service.category == AzureCategory.NETWORKING
        assert service.stage == PipelineStage.BACKLOG
    
    def test_empty_name_raises(self):
        """Empty name should raise ValidationError."""
        with pytest.raises(ValidationError):
            AzureService(name="", category=AzureCategory.COMPUTE)
    
    def test_string_category_conversion(self):
        """Should convert string category to enum."""
        service = AzureService(
            name="Test Service",
            category="Networking"  # String instead of enum
        )
        assert service.category == AzureCategory.NETWORKING
    
    def test_invalid_category_raises(self):
        """Invalid category string should raise ValidationError."""
        with pytest.raises(ValidationError):
            AzureService(name="Test", category="InvalidCategory")


class TestStageGateValidation:
    """Tests for stage gate validation logic."""
    
    def test_backlog_can_advance(self):
        """Backlog should always be able to advance."""
        service = AzureService(
            name="Test",
            category=AzureCategory.COMPUTE,
            stage=PipelineStage.BACKLOG
        )
        result = service.check_stage_gate()
        
        assert result.can_advance is True
        assert result.next_stage == PipelineStage.LAB_TESTING
        assert len(result.blockers) == 0
    
    def test_lab_to_production_requires_passed(self):
        """Lab to production requires lab status passed."""
        service = AzureService(
            name="Test",
            category=AzureCategory.COMPUTE,
            stage=PipelineStage.LAB_TESTING,
            lab_status=TestStatus.IN_PROGRESS  # Not passed
        )
        result = service.check_stage_gate()
        
        assert result.can_advance is False
        assert "Lab testing must pass" in result.blockers[0]
    
    def test_lab_to_production_allowed_when_passed(self):
        """Lab to production allowed when lab passed."""
        service = AzureService(
            name="Test",
            category=AzureCategory.COMPUTE,
            stage=PipelineStage.LAB_TESTING,
            lab_status=TestStatus.PASSED
        )
        result = service.check_stage_gate()
        
        assert result.can_advance is True
        assert result.next_stage == PipelineStage.PRODUCTION_VALIDATION
    
    def test_production_to_customer_requires_both(self):
        """Customer ready requires prod passed AND security review."""
        service = AzureService(
            name="Test",
            category=AzureCategory.COMPUTE,
            stage=PipelineStage.PRODUCTION_VALIDATION,
            prod_status=TestStatus.IN_PROGRESS,
            security_review=False
        )
        result = service.check_stage_gate()
        
        assert result.can_advance is False
        assert len(result.blockers) == 2
    
    def test_production_to_customer_allowed(self):
        """Customer ready allowed when all requirements met."""
        service = AzureService(
            name="Test",
            category=AzureCategory.COMPUTE,
            stage=PipelineStage.PRODUCTION_VALIDATION,
            prod_status=TestStatus.PASSED,
            security_review=True
        )
        result = service.check_stage_gate()
        
        assert result.can_advance is True
        assert result.next_stage == PipelineStage.CUSTOMER_READY


class TestAzurePipelineManagerInit:
    """Tests for AzurePipelineManager initialization."""
    
    def test_inherits_from_base(self, config_file):
        """Should inherit from BaseSyncClient."""
        from core.base_sync import BaseSyncClient
        
        manager = AzurePipelineManager(str(config_file), dry_run=True)
        assert isinstance(manager, BaseSyncClient)
    
    def test_primary_database(self, config_file):
        """Should have azure_pipeline as primary database."""
        manager = AzurePipelineManager(str(config_file), dry_run=True)
        assert manager.primary_database == "azure_pipeline"


class TestAzurePipelineManagerOperations:
    """Tests for AzurePipelineManager operations."""
    
    @pytest.fixture
    def manager(self, config_file):
        return AzurePipelineManager(str(config_file), dry_run=True)
    
    def test_list_dry_run(self, manager):
        """Dry run list should return empty."""
        result = manager.list_services()
        assert result == []
    
    def test_add_dry_run(self, manager):
        """Dry run add should return preview."""
        service = AzureService(
            name="Azure VPN Gateway",
            category=AzureCategory.NETWORKING
        )
        result = manager.add_service(service)
        
        assert result["status"] == "dry_run"
        assert result["name"] == "Azure VPN Gateway"
    
    def test_advance_dry_run(self, manager):
        """Dry run advance should return preview."""
        result = manager.advance_stage("Test Service")
        
        assert result["status"] == "dry_run"
    
    def test_build_properties(self, manager):
        """Should build correct Notion properties."""
        service = AzureService(
            name="Azure SQL",
            category=AzureCategory.DATABASES,
            stage=PipelineStage.LAB_TESTING,
            owner="Maverick",
            customer_requests=5
        )
        
        props = manager.build_properties(service)
        
        assert "Service Name" in props
        assert "Category" in props
        assert "Pipeline Stage" in props
        assert "Owner" in props
        assert "Customer Requests" in props


# =============================================================================
# Runbook Manager Tests
# =============================================================================

class TestComplexityLevel:
    """Tests for ComplexityLevel enum."""
    
    def test_review_intervals(self):
        """Should have correct review intervals."""
        assert ComplexityLevel.BASIC.review_interval_days == 180
        assert ComplexityLevel.INTERMEDIATE.review_interval_days == 90
        assert ComplexityLevel.ADVANCED.review_interval_days == 60


class TestRunbook:
    """Tests for Runbook dataclass."""
    
    def test_basic_creation(self):
        """Should create runbook with required fields."""
        runbook = Runbook(
            title="VPN Setup Guide",
            category=RunbookCategory.NETWORK,
            doc_type=DocumentType.RUNBOOK
        )
        
        assert runbook.title == "VPN Setup Guide"
        assert runbook.category == RunbookCategory.NETWORK
        assert runbook.automation_status == AutomationStatus.MANUAL
    
    def test_empty_title_raises(self):
        """Empty title should raise ValidationError."""
        with pytest.raises(ValidationError):
            Runbook(
                title="",
                category=RunbookCategory.NETWORK,
                doc_type=DocumentType.SOP
            )
    
    def test_auto_review_dates(self):
        """Should auto-calculate review dates."""
        runbook = Runbook(
            title="Test",
            category=RunbookCategory.SECURITY,
            doc_type=DocumentType.SOP,
            complexity=ComplexityLevel.BASIC
        )
        
        assert runbook.last_review_date is not None
        assert runbook.next_review_due is not None
        # Basic complexity = 180 days
        expected_next = runbook.last_review_date + timedelta(days=180)
        assert runbook.next_review_due.date() == expected_next.date()
    
    def test_days_until_review(self):
        """Should calculate days until review."""
        runbook = Runbook(
            title="Test",
            category=RunbookCategory.NETWORK,
            doc_type=DocumentType.RUNBOOK,
            complexity=ComplexityLevel.INTERMEDIATE  # 90 days
        )
        
        # Should be approximately 90 days (±1 for timing)
        assert 89 <= runbook.days_until_review <= 90
    
    def test_is_overdue(self):
        """Should detect overdue runbooks."""
        past_date = datetime.now(timezone.utc) - timedelta(days=100)
        runbook = Runbook(
            title="Test",
            category=RunbookCategory.NETWORK,
            doc_type=DocumentType.RUNBOOK,
            last_review_date=past_date,
            next_review_due=past_date  # Already past
        )
        
        assert runbook.is_overdue is True
    
    def test_is_automation_candidate_basic_manual(self):
        """Manual + basic = candidate."""
        runbook = Runbook(
            title="Test",
            category=RunbookCategory.NETWORK,
            doc_type=DocumentType.RUNBOOK,
            complexity=ComplexityLevel.BASIC,
            automation_status=AutomationStatus.MANUAL
        )
        assert runbook.is_automation_candidate is True
    
    def test_is_automation_candidate_automated(self):
        """Already automated = not candidate."""
        runbook = Runbook(
            title="Test",
            category=RunbookCategory.NETWORK,
            doc_type=DocumentType.RUNBOOK,
            complexity=ComplexityLevel.BASIC,
            automation_status=AutomationStatus.FULLY_AUTOMATED
        )
        assert runbook.is_automation_candidate is False
    
    def test_is_automation_candidate_advanced(self):
        """Advanced complexity = not candidate."""
        runbook = Runbook(
            title="Test",
            category=RunbookCategory.NETWORK,
            doc_type=DocumentType.RUNBOOK,
            complexity=ComplexityLevel.ADVANCED,
            automation_status=AutomationStatus.MANUAL
        )
        assert runbook.is_automation_candidate is False


class TestRunbookManagerInit:
    """Tests for RunbookManager initialization."""
    
    def test_inherits_from_base(self, config_file):
        """Should inherit from BaseSyncClient."""
        from core.base_sync import BaseSyncClient
        
        manager = RunbookManager(str(config_file), dry_run=True)
        assert isinstance(manager, BaseSyncClient)
    
    def test_primary_database(self, config_file):
        """Should have runbook_library as primary database."""
        manager = RunbookManager(str(config_file), dry_run=True)
        assert manager.primary_database == "runbook_library"


class TestRunbookManagerOperations:
    """Tests for RunbookManager operations."""
    
    @pytest.fixture
    def manager(self, config_file):
        return RunbookManager(str(config_file), dry_run=True)
    
    def test_list_dry_run(self, manager):
        """Dry run list should return empty."""
        result = manager.list_runbooks()
        assert result == []
    
    def test_add_dry_run(self, manager):
        """Dry run add should return preview."""
        runbook = Runbook(
            title="Test Runbook",
            category=RunbookCategory.NETWORK,
            doc_type=DocumentType.RUNBOOK
        )
        result = manager.add_runbook(runbook)
        
        assert result["status"] == "dry_run"
        assert result["title"] == "Test Runbook"
    
    def test_review_due_dry_run(self, manager):
        """Dry run review-due should return empty."""
        result = manager.get_review_due()
        assert result == []
    
    def test_candidates_dry_run(self, manager):
        """Dry run candidates should return empty."""
        result = manager.get_automation_candidates()
        assert result == []
    
    def test_build_properties(self, manager):
        """Should build correct Notion properties."""
        runbook = Runbook(
            title="VPN Troubleshooting",
            category=RunbookCategory.NETWORK,
            doc_type=DocumentType.TROUBLESHOOTING,
            vendors=["Ubiquiti", "MikroTik"],
            complexity=ComplexityLevel.ADVANCED,
            owner="Maverick"
        )
        
        props = manager.build_properties(runbook)
        
        assert "Title" in props
        assert "Category" in props
        assert "Document Type" in props
        assert "Vendor" in props
        assert "Complexity" in props
        assert "Owner" in props


class TestEnumValues:
    """Tests for all enum value methods."""
    
    def test_runbook_category_values(self):
        """RunbookCategory.values() should return list."""
        values = RunbookCategory.values()
        assert "network" in values
        assert "security" in values
        assert "cloud" in values
    
    def test_vendor_values(self):
        """Vendor.values() should return list."""
        values = Vendor.values()
        assert "Ubiquiti" in values
        assert "MikroTik" in values
        assert "Azure" in values
    
    def test_document_type_values(self):
        """DocumentType.values() should return list."""
        values = DocumentType.values()
        assert "SOP" in values
        assert "runbook" in values
    
    def test_automation_status_values(self):
        """AutomationStatus.values() should return list."""
        values = AutomationStatus.values()
        assert "manual" in values
        assert "fully automated" in values
        assert "deprecated" in values
    
    def test_test_status_values(self):
        """TestStatus.values() should return list."""
        values = TestStatus.values()
        assert "not started" in values
        assert "passed" in values
        assert "failed" in values
