"""
Unit tests for ConfigChangeSync.

Tests the refactored config change sync using BaseSyncClient.
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from config_change_sync_v2 import (
    ConfigChangeSync,
    ConfigChange,
    ToolInfo,
    ToolCategory,
    RiskLevel,
    ChangeAction,
    TOOLS,
)
from core.errors import ValidationError


class TestToolInfo:
    """Tests for ToolInfo dataclass."""
    
    def test_known_tool_lookup(self):
        """Should return info for known tools."""
        info = ToolInfo.get("mikrotik-config-builder")
        assert info.vendor == "MikroTik"
        assert info.category == ToolCategory.NETWORK
    
    def test_unknown_tool_fallback(self):
        """Should return fallback for unknown tools."""
        info = ToolInfo.get("unknown-tool")
        assert info.vendor == "Unknown"
        assert info.category == ToolCategory.OTHER
        assert info.default_risk == RiskLevel.MEDIUM
    
    def test_sonicwall_higher_risk(self):
        """SonicWall tools should default to higher risk."""
        info = ToolInfo.get("sonicwall-scripts")
        assert info.default_risk == RiskLevel.HIGH


class TestConfigChange:
    """Tests for ConfigChange dataclass."""
    
    def test_basic_creation(self):
        """Should create change with required fields."""
        change = ConfigChange(
            tool="mikrotik-config-builder",
            site="Acme Corp",
            action=ChangeAction.DEPLOY,
            summary="Updated VPN config"
        )
        
        assert change.tool == "mikrotik-config-builder"
        assert change.site == "Acme Corp"
        assert change.action == ChangeAction.DEPLOY
        assert change.summary == "Updated VPN config"
    
    def test_auto_timestamp(self):
        """Should auto-populate timestamp."""
        change = ConfigChange(
            tool="manual",
            site="Test Site",
            action=ChangeAction.UPDATE,
            summary="Test change"
        )
        
        assert change.timestamp is not None
        assert isinstance(change.timestamp, datetime)
    
    def test_auto_engineer(self):
        """Should auto-populate engineer from environment."""
        with patch.dict(os.environ, {"USER": "testuser"}):
            change = ConfigChange(
                tool="manual",
                site="Test Site",
                action=ChangeAction.UPDATE,
                summary="Test change"
            )
            # May be testuser or OBERA_ENGINEER if set
            assert change.engineer is not None
    
    def test_change_id_format(self):
        """Change ID should follow expected format."""
        change = ConfigChange(
            tool="manual",
            site="Acme Corp",
            action=ChangeAction.UPDATE,
            summary="Test"
        )
        
        # Format: SiteName-YYYYMMDD-HHMMSS
        assert change.change_id.startswith("Acme-Corp")
        assert len(change.change_id.split("-")) >= 3
    
    def test_summary_truncation(self):
        """Long summaries should be truncated."""
        long_summary = "x" * 3000
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.UPDATE,
            summary=long_summary
        )
        
        assert len(change.summary) <= 2000
        assert change.summary.endswith("...")
    
    def test_empty_site_raises(self):
        """Empty site should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ConfigChange(
                tool="manual",
                site="",
                action=ChangeAction.UPDATE,
                summary="Test"
            )
        assert "site" in str(exc_info.value).lower()
    
    def test_empty_summary_raises(self):
        """Empty summary should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ConfigChange(
                tool="manual",
                site="Test Site",
                action=ChangeAction.UPDATE,
                summary=""
            )
        assert "summary" in str(exc_info.value).lower()


class TestRiskAssessment:
    """Tests for automatic risk assessment."""
    
    def test_delete_action_high_risk(self):
        """Delete actions should be high risk."""
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.DELETE,
            summary="Remove old config"
        )
        
        assert change.assessed_risk == RiskLevel.HIGH
    
    def test_rollback_action_high_risk(self):
        """Rollback actions should be high risk."""
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.ROLLBACK,
            summary="Revert changes"
        )
        
        assert change.assessed_risk == RiskLevel.HIGH
    
    def test_firewall_keyword_high_risk(self):
        """Summary containing 'firewall' should be high risk."""
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.UPDATE,
            summary="Updated firewall rules"
        )
        
        assert change.assessed_risk == RiskLevel.HIGH
    
    def test_vpn_keyword_high_risk(self):
        """Summary containing 'vpn' should be high risk."""
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.UPDATE,
            summary="Added new VPN tunnel"
        )
        
        assert change.assessed_risk == RiskLevel.HIGH
    
    def test_tool_default_risk(self):
        """Should fall back to tool's default risk."""
        change = ConfigChange(
            tool="network-troubleshooter",
            site="Test",
            action=ChangeAction.ASSESSMENT,
            summary="Network scan completed"
        )
        
        # network-troubleshooter defaults to LOW
        assert change.assessed_risk == RiskLevel.LOW
    
    def test_explicit_risk_override(self):
        """Explicit risk level should override auto-assessment."""
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.DELETE,  # Would be HIGH
            summary="Delete firewall rule",  # Would be HIGH
            risk_level=RiskLevel.LOW  # Override to LOW
        )
        
        assert change.assessed_risk == RiskLevel.LOW
    
    def test_requires_rollback_high(self):
        """High risk changes should require rollback plan."""
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.DELETE,
            summary="Remove config"
        )
        
        assert change.requires_rollback_plan is True
    
    def test_requires_rollback_critical(self):
        """Critical risk changes should require rollback plan."""
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.UPDATE,
            summary="Test",
            risk_level=RiskLevel.CRITICAL
        )
        
        assert change.requires_rollback_plan is True
    
    def test_no_rollback_required_medium(self):
        """Medium risk changes should not require rollback plan."""
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.UPDATE,
            summary="Basic update",
            risk_level=RiskLevel.MEDIUM
        )
        
        assert change.requires_rollback_plan is False


class TestConfigChangeSyncInit:
    """Tests for ConfigChangeSync initialization."""
    
    def test_inherits_from_base(self, config_file):
        """Should inherit from BaseSyncClient."""
        from core.base_sync import BaseSyncClient
        
        sync = ConfigChangeSync(str(config_file), dry_run=True)
        assert isinstance(sync, BaseSyncClient)
    
    def test_primary_database(self, config_file):
        """Should have config_changes as primary database."""
        sync = ConfigChangeSync(str(config_file), dry_run=True)
        assert sync.primary_database == "config_changes"


class TestLogChange:
    """Tests for logging changes."""
    
    @pytest.fixture
    def sync(self, config_file):
        return ConfigChangeSync(str(config_file), dry_run=True)
    
    def test_dry_run_returns_preview(self, sync):
        """Dry run should return preview without writing."""
        change = ConfigChange(
            tool="mikrotik-config-builder",
            site="Acme Corp",
            action=ChangeAction.DEPLOY,
            summary="Test deployment"
        )
        
        result = sync.log_change(change)
        
        assert result["status"] == "dry_run"
        assert "change_id" in result
        assert "risk_level" in result
    
    def test_builds_correct_properties(self, sync):
        """Should build all required properties."""
        change = ConfigChange(
            tool="sonicwall-scripts",
            site="Test Site",
            action=ChangeAction.UPDATE,
            summary="Updated access rules",
            details="Added rule for new subnet",
            ticket_id="INC001234",
            rollback_plan="Remove rule and restart service"
        )
        
        properties = sync.build_properties(change)
        
        assert "Change ID" in properties
        assert "Site Name" in properties
        assert "Tool" in properties
        assert "Vendor" in properties
        assert "Category" in properties
        assert "Action" in properties
        assert "Summary" in properties
        assert "Risk Level" in properties
        assert "Details" in properties
        assert "Ticket ID" in properties
        assert "Rollback Plan" in properties
    
    def test_logs_warning_high_risk_no_rollback(self, sync, caplog):
        """Should log warning for high risk without rollback."""
        import logging
        caplog.set_level(logging.WARNING)
        
        change = ConfigChange(
            tool="manual",
            site="Test",
            action=ChangeAction.DELETE,
            summary="Delete firewall rule",
            # No rollback_plan
        )
        
        sync.log_change(change)
        
        assert "rollback" in caplog.text.lower() or "high" in caplog.text.lower()


class TestGetRecentChanges:
    """Tests for querying recent changes."""
    
    @pytest.fixture
    def sync(self, config_file):
        return ConfigChangeSync(str(config_file), dry_run=True)
    
    def test_dry_run_returns_empty(self, sync):
        """Dry run should return empty list."""
        changes = sync.get_recent_changes(days=7)
        assert changes == []


class TestGenerateReport:
    """Tests for report generation."""
    
    @pytest.fixture
    def sync(self, config_file):
        return ConfigChangeSync(str(config_file), dry_run=True)
    
    def test_no_changes_message(self, sync):
        """Should return message when no changes found."""
        # Dry run returns empty, so no changes
        report = sync.generate_report(days=7)
        assert "No changes found" in report


class TestEnums:
    """Tests for enum values."""
    
    def test_risk_levels(self):
        """Should have expected risk levels."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"
    
    def test_change_actions(self):
        """Should have expected actions."""
        actions = [a.value for a in ChangeAction]
        assert "deploy" in actions
        assert "update" in actions
        assert "rollback" in actions
        assert "delete" in actions
    
    def test_tool_categories(self):
        """Should have expected categories."""
        categories = [c.value for c in ToolCategory]
        assert "network" in categories
        assert "security" in categories
        assert "cloud" in categories


class TestToolRegistry:
    """Tests for tool registry."""
    
    def test_all_tools_have_info(self):
        """All registered tools should have complete info."""
        for name, info in TOOLS.items():
            assert info.name == name
            assert info.vendor
            assert info.category
            assert info.default_risk
    
    def test_known_tools_exist(self):
        """Expected tools should be registered."""
        expected = [
            "mikrotik-config-builder",
            "sonicwall-scripts",
            "unifi-deploy",
            "azure-automation",
            "network-troubleshooter",
            "manual",
        ]
        for tool in expected:
            assert tool in TOOLS
