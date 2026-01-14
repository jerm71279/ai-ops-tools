"""
Unit tests for CustomerStatusSync.

Tests the refactored sync using BaseSyncClient.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from customer_status_sync_v2 import (
    CustomerStatusSync,
    fetch_unifi_sites,
    fetch_ninjaone_data,
    determine_stack_type,
)
from services.health_score import HealthStatus
from core.errors import DataSourceError


class TestDetermineStackType:
    """Tests for stack type detection."""
    
    def test_default_ubiquiti(self):
        """Empty site should default to Ubiquiti."""
        site = {}
        stack = determine_stack_type(site)
        assert stack == ["Ubiquiti"]
    
    def test_with_mikrotik(self):
        """Should include MikroTik when present."""
        site = {"has_mikrotik": True}
        stack = determine_stack_type(site)
        assert "Ubiquiti" in stack
        assert "MikroTik" in stack
    
    def test_with_sonicwall(self):
        """Should include SonicWall when present."""
        site = {"has_sonicwall": True}
        stack = determine_stack_type(site)
        assert "SonicWall" in stack
    
    def test_with_azure(self):
        """Should include Azure when present."""
        site = {"has_azure": True}
        stack = determine_stack_type(site)
        assert "Azure" in stack
    
    def test_full_stack(self):
        """Should include all components when all present."""
        site = {
            "has_mikrotik": True,
            "has_sonicwall": True,
            "has_azure": True,
        }
        stack = determine_stack_type(site)
        assert len(stack) == 4
        assert "Ubiquiti" in stack
        assert "MikroTik" in stack
        assert "SonicWall" in stack
        assert "Azure" in stack


class TestCustomerStatusSyncInit:
    """Tests for CustomerStatusSync initialization."""
    
    def test_inherits_from_base(self, config_file):
        """Should inherit from BaseSyncClient."""
        from core.base_sync import BaseSyncClient
        
        syncer = CustomerStatusSync(str(config_file), dry_run=True)
        assert isinstance(syncer, BaseSyncClient)
    
    def test_primary_database(self, config_file):
        """Should have customer_status as primary database."""
        syncer = CustomerStatusSync(str(config_file), dry_run=True)
        assert syncer.primary_database == "customer_status"
    
    def test_has_health_calculator(self, config_file):
        """Should initialize health calculator."""
        syncer = CustomerStatusSync(str(config_file), dry_run=True)
        assert syncer.health_calculator is not None
    
    def test_dry_run_mode(self, config_file):
        """Dry run should not initialize client."""
        syncer = CustomerStatusSync(str(config_file), dry_run=True)
        assert syncer.dry_run is True
        assert syncer._client is None


class TestBuildProperties:
    """Tests for building Notion page properties."""
    
    @pytest.fixture
    def syncer(self, config_file):
        return CustomerStatusSync(str(config_file), dry_run=True)
    
    def test_healthy_site_properties(self, syncer, sample_site_data):
        """Should build properties for healthy site."""
        ninjaone_data = {
            "open_tickets": 0,
            "active_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "backup_status": "success"
        }
        
        properties, health_result = syncer.build_properties(
            sample_site_data, 
            ninjaone_data
        )
        
        # Check properties exist
        assert "Site Name" in properties
        assert "Health Score" in properties
        assert "Deployment Status" in properties
        
        # Check health result
        assert health_result.score >= 80
        assert health_result.status == HealthStatus.HEALTHY
    
    def test_unhealthy_site_properties(self, syncer):
        """Should build properties for unhealthy site."""
        site_data = {
            "name": "Problem Site",
            "site_id": "site_002",
            "devices_online": 3,
            "devices_total": 10,
            "wifi_clients": 20,
            "signal_warnings": 10,
        }
        ninjaone_data = {
            "open_tickets": 5,
            "critical_alerts": 2,
            "warning_alerts": 3,
            "backup_status": "failed"
        }
        
        properties, health_result = syncer.build_properties(site_data, ninjaone_data)
        
        assert health_result.score < 50
        assert health_result.status == HealthStatus.CRITICAL
        assert health_result.requires_review
    
    def test_status_mapping(self, syncer):
        """Should map health status to deployment status correctly."""
        # Healthy = active
        site_data = {"name": "Test", "devices_online": 10, "devices_total": 10}
        ninjaone_data = {"backup_status": "success"}
        props, result = syncer.build_properties(site_data, ninjaone_data)
        assert props["Deployment Status"]["select"]["name"] == "active"
        
        # Critical = needs attention
        site_data = {"name": "Test", "devices_online": 0, "devices_total": 10}
        ninjaone_data = {"backup_status": "failed", "critical_alerts": 5}
        props, result = syncer.build_properties(site_data, ninjaone_data)
        assert props["Deployment Status"]["select"]["name"] == "needs attention"


class TestSyncSite:
    """Tests for syncing individual sites."""
    
    @pytest.fixture
    def syncer(self, config_file):
        return CustomerStatusSync(str(config_file), dry_run=True)
    
    def test_dry_run_returns_preview(self, syncer, sample_site_data):
        """Dry run should return preview without writing."""
        result = syncer.sync_site(sample_site_data)
        
        assert result["status"] == "dry_run"
        assert result["site"] == sample_site_data["name"]
        assert "health_score" in result
    
    def test_logs_review_required(self, syncer, caplog):
        """Should log when site requires review."""
        import logging
        caplog.set_level(logging.WARNING)
        
        unhealthy_site = {
            "name": "Unhealthy Site",
            "site_id": "site_bad",
            "devices_online": 0,
            "devices_total": 10,
        }
        
        # Mock ninjaone to return bad data
        with patch('customer_status_sync_v2.fetch_ninjaone_data') as mock:
            mock.return_value = {"backup_status": "failed", "critical_alerts": 5}
            result = syncer.sync_site(unhealthy_site)
        
        assert result["requires_review"] is True
        assert "requires review" in caplog.text.lower()


class TestSyncAll:
    """Tests for syncing all sites."""
    
    @pytest.fixture
    def syncer(self, config_file):
        return CustomerStatusSync(str(config_file), dry_run=True)
    
    def test_sync_returns_results(self, syncer):
        """Sync should return list of results."""
        results = syncer.sync()
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert all("site" in r for r in results)
        assert all("status" in r for r in results)
    
    def test_filter_by_site_name(self, syncer):
        """Should filter sites by name."""
        # Stub data generates 98 sites with multiple Acme Corp variations
        results = syncer.sync(filter_site="Acme")
        assert len(results) >= 1  # Multiple Acme sites in stub data
        assert all("Acme" in r["site"] for r in results)

        results = syncer.sync(filter_site="NonExistent")
        assert len(results) == 0
    
    def test_bulk_operation_warning(self, syncer, caplog):
        """Should warn on bulk operations."""
        import logging
        caplog.set_level(logging.WARNING)
        
        # Mock to return many sites
        many_sites = [{"name": f"Site {i}", "site_id": f"s{i}"} for i in range(15)]
        
        with patch('customer_status_sync_v2.fetch_unifi_sites') as mock:
            mock.return_value = many_sites
            syncer.sync()
        
        # Should have logged bulk warning
        assert "bulk" in caplog.text.lower() or "threshold" in caplog.text.lower()


class TestGenerateReport:
    """Tests for report generation."""
    
    @pytest.fixture
    def syncer(self, config_file):
        return CustomerStatusSync(str(config_file), dry_run=True)
    
    def test_report_includes_summary(self, syncer):
        """Report should include summary statistics."""
        results = [
            {"site": "Site A", "status": "success", "action": "created", "health_score": 95},
            {"site": "Site B", "status": "success", "action": "updated", "health_score": 75},
            {"site": "Site C", "status": "error", "error": "API error"},
        ]
        
        report = syncer.generate_report(results)
        
        assert "Total Sites: 3" in report
        assert "Successful: 2" in report
        assert "Failed: 1" in report
        assert "Created: 1" in report
        assert "Updated: 1" in report
    
    def test_report_includes_health_average(self, syncer):
        """Report should include average health score."""
        results = [
            {"site": "Site A", "status": "success", "health_score": 100},
            {"site": "Site B", "status": "success", "health_score": 80},
        ]
        
        report = syncer.generate_report(results)
        
        assert "Average Score: 90.0" in report
    
    def test_report_highlights_review_needed(self, syncer):
        """Report should highlight sites needing review."""
        results = [
            {"site": "Good Site", "status": "success", "health_score": 95, "requires_review": False},
            {"site": "Bad Site", "status": "success", "health_score": 45, "requires_review": True},
        ]
        
        report = syncer.generate_report(results)
        
        assert "SITES REQUIRING REVIEW" in report
        assert "Bad Site" in report


class TestDataSourceErrors:
    """Tests for data source error handling."""
    
    @pytest.fixture
    def syncer(self, config_file):
        return CustomerStatusSync(str(config_file), dry_run=True)
    
    def test_ninjaone_error_wrapped(self, syncer):
        """NinjaOne errors should be wrapped in DataSourceError."""
        site_data = {"name": "Test Site", "site_id": "test_001"}
        
        with patch('customer_status_sync_v2.fetch_ninjaone_data') as mock:
            mock.side_effect = ConnectionError("Network timeout")
            
            with pytest.raises(DataSourceError) as exc_info:
                syncer.sync_site(site_data)
            
            assert "NinjaOne" in str(exc_info.value)
    
    def test_unifi_error_wrapped(self, syncer):
        """UniFi errors should be wrapped in DataSourceError."""
        with patch('customer_status_sync_v2.fetch_unifi_sites') as mock:
            mock.side_effect = ConnectionError("API unreachable")
            
            with pytest.raises(DataSourceError) as exc_info:
                syncer.sync()
            
            assert "UniFi" in str(exc_info.value)
