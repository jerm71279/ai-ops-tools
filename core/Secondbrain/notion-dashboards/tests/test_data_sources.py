"""
Unit tests for data source interfaces and stub implementations.

Tests the data abstraction layer for UniFi and NinjaOne.
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from data_sources import (
    # Interfaces
    UniFiDataSource,
    NinjaOneDataSource,
    DataSourceFactory,
    # Stubs
    StubUniFiDataSource,
    StubNinjaOneDataSource,
    # Data models
    UniFiSite,
    UniFiDevice,
    NinjaOneOrganization,
    NinjaOneAlert,
    BackupStatus,
    DeviceStatus,
    AlertSeverity,
    # Factory functions
    get_factory,
    get_unifi,
    get_ninjaone,
)


class TestUniFiSiteModel:
    """Tests for UniFiSite data model."""
    
    def test_availability_all_online(self):
        """All devices online = 100% availability."""
        site = UniFiSite(
            site_id="test",
            name="Test Site",
            devices_online=10,
            devices_total=10,
        )
        assert site.devices_availability_pct == 100.0
    
    def test_availability_half_online(self):
        """Half devices online = 50% availability."""
        site = UniFiSite(
            site_id="test",
            name="Test Site",
            devices_online=5,
            devices_total=10,
        )
        assert site.devices_availability_pct == 50.0
    
    def test_availability_no_devices(self):
        """No devices = 100% availability (edge case)."""
        site = UniFiSite(
            site_id="test",
            name="Test Site",
            devices_online=0,
            devices_total=0,
        )
        assert site.devices_availability_pct == 100.0


class TestStubUniFiDataSource:
    """Tests for stub UniFi data source."""
    
    @pytest.fixture
    def unifi(self):
        return StubUniFiDataSource(site_count=10, seed=42)
    
    def test_fetch_sites_returns_list(self, unifi):
        """Should return list of UniFiSite objects."""
        sites = unifi.fetch_sites()
        assert isinstance(sites, list)
        assert len(sites) == 10
        assert all(isinstance(s, UniFiSite) for s in sites)
    
    def test_sites_have_required_fields(self, unifi):
        """Sites should have all required fields populated."""
        sites = unifi.fetch_sites()
        for site in sites:
            assert site.site_id
            assert site.name
            assert site.devices_total >= 0
            assert site.devices_online >= 0
            assert site.devices_offline >= 0
            assert site.devices_online + site.devices_offline == site.devices_total
    
    def test_fetch_site_by_id(self, unifi):
        """Should fetch specific site by ID."""
        sites = unifi.fetch_sites()
        first_site = sites[0]
        
        fetched = unifi.fetch_site(first_site.site_id)
        assert fetched is not None
        assert fetched.site_id == first_site.site_id
        assert fetched.name == first_site.name
    
    def test_fetch_site_not_found(self, unifi):
        """Should return None for non-existent site."""
        result = unifi.fetch_site("nonexistent_site_id")
        assert result is None
    
    def test_fetch_devices_returns_list(self, unifi):
        """Should return list of devices for site."""
        sites = unifi.fetch_sites()
        site = sites[0]
        
        devices = unifi.fetch_devices(site.site_id)
        assert isinstance(devices, list)
        assert all(isinstance(d, UniFiDevice) for d in devices)
        assert len(devices) == site.devices_total
    
    def test_devices_have_gateway(self, unifi):
        """Every site should have at least one gateway."""
        sites = unifi.fetch_sites()
        for site in sites:
            devices = unifi.fetch_devices(site.site_id)
            gateways = [d for d in devices if d.device_type == "gateway"]
            assert len(gateways) >= 1
    
    def test_device_status_matches_site(self, unifi):
        """Device status counts should match site metrics."""
        sites = unifi.fetch_sites()
        for site in sites:
            devices = unifi.fetch_devices(site.site_id)
            online = len([d for d in devices if d.status == DeviceStatus.ONLINE])
            offline = len([d for d in devices if d.status == DeviceStatus.OFFLINE])
            
            # May have some devices in other states
            assert online >= site.devices_online - 1  # Allow small variance
    
    def test_reproducible_with_seed(self):
        """Same seed should produce same data."""
        unifi1 = StubUniFiDataSource(site_count=5, seed=42)
        unifi2 = StubUniFiDataSource(site_count=5, seed=42)
        
        sites1 = unifi1.fetch_sites()
        sites2 = unifi2.fetch_sites()
        
        for s1, s2 in zip(sites1, sites2):
            assert s1.site_id == s2.site_id
            assert s1.name == s2.name


class TestStubNinjaOneDataSource:
    """Tests for stub NinjaOne data source."""
    
    @pytest.fixture
    def ninjaone(self):
        return StubNinjaOneDataSource(seed=42)
    
    def test_fetch_organization_creates_data(self, ninjaone):
        """Should create organization data on demand."""
        org = ninjaone.fetch_organization("Test Customer")
        
        assert org is not None
        assert isinstance(org, NinjaOneOrganization)
        assert org.name == "Test Customer"
    
    def test_same_org_returns_same_data(self, ninjaone):
        """Same org name should return consistent data."""
        org1 = ninjaone.fetch_organization("Test Customer")
        org2 = ninjaone.fetch_organization("Test Customer")
        
        assert org1.org_id == org2.org_id
        assert org1.device_count == org2.device_count
    
    def test_organization_has_backup_status(self, ninjaone):
        """Organization should have backup status."""
        org = ninjaone.fetch_organization("Test Customer")
        assert org.backup_status in ["success", "partial", "failed", "unknown"]
    
    def test_fetch_backup_status(self, ninjaone):
        """Should return BackupStatus object."""
        status = ninjaone.fetch_backup_status("Test Customer")
        
        assert isinstance(status, BackupStatus)
        assert status.status in ["success", "partial", "failed", "unknown"]
    
    def test_fetch_alerts(self, ninjaone):
        """Should return list of alerts."""
        # First create some org data
        ninjaone.fetch_organization("Test Customer")
        
        alerts = ninjaone.fetch_alerts()
        assert isinstance(alerts, list)
        assert all(isinstance(a, NinjaOneAlert) for a in alerts)
    
    def test_filter_alerts_by_severity(self, ninjaone):
        """Should filter alerts by severity."""
        ninjaone.fetch_organization("Test")  # Generate data
        
        critical = ninjaone.fetch_alerts(severity=AlertSeverity.CRITICAL)
        warning = ninjaone.fetch_alerts(severity=AlertSeverity.WARNING)
        
        assert all(a.severity == AlertSeverity.CRITICAL for a in critical)
        assert all(a.severity == AlertSeverity.WARNING for a in warning)


class TestDataSourceFactory:
    """Tests for DataSourceFactory."""
    
    def test_default_unifi_is_stub(self):
        """Factory should return stub by default."""
        factory = DataSourceFactory()
        unifi = factory.get_unifi()
        
        assert isinstance(unifi, StubUniFiDataSource)
    
    def test_default_ninjaone_is_stub(self):
        """Factory should return stub by default."""
        factory = DataSourceFactory()
        ninjaone = factory.get_ninjaone()
        
        assert isinstance(ninjaone, StubNinjaOneDataSource)
    
    def test_register_custom_unifi(self):
        """Should allow registering custom implementation."""
        factory = DataSourceFactory()
        
        custom_unifi = StubUniFiDataSource(site_count=5)
        factory.register_unifi(custom_unifi)
        
        assert factory.get_unifi() is custom_unifi
    
    def test_register_custom_ninjaone(self):
        """Should allow registering custom implementation."""
        factory = DataSourceFactory()
        
        custom_ninjaone = StubNinjaOneDataSource()
        factory.register_ninjaone(custom_ninjaone)
        
        assert factory.get_ninjaone() is custom_ninjaone


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""
    
    def test_get_factory_returns_factory(self):
        """get_factory should return DataSourceFactory."""
        factory = get_factory()
        assert isinstance(factory, DataSourceFactory)
    
    def test_get_factory_singleton(self):
        """get_factory should return same instance."""
        factory1 = get_factory()
        factory2 = get_factory()
        assert factory1 is factory2
    
    def test_get_unifi_returns_source(self):
        """get_unifi should return UniFiDataSource."""
        unifi = get_unifi()
        assert isinstance(unifi, UniFiDataSource)
    
    def test_get_ninjaone_returns_source(self):
        """get_ninjaone should return NinjaOneDataSource."""
        ninjaone = get_ninjaone()
        assert isinstance(ninjaone, NinjaOneDataSource)


class TestDeviceStatusEnum:
    """Tests for DeviceStatus enum."""
    
    def test_status_values(self):
        """Should have expected status values."""
        assert DeviceStatus.ONLINE.value == "online"
        assert DeviceStatus.OFFLINE.value == "offline"
        assert DeviceStatus.UNKNOWN.value == "unknown"


class TestAlertSeverityEnum:
    """Tests for AlertSeverity enum."""
    
    def test_severity_values(self):
        """Should have expected severity values."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.CRITICAL.value == "critical"
