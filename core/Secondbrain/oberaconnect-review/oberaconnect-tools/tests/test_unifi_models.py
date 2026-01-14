"""
Tests for UniFi data models.

Tests:
- UniFiDevice properties and serialization
- UniFiSite health score calculation
- FleetSummary aggregation
"""

import pytest
from datetime import datetime


class TestUniFiDevice:
    """Tests for UniFiDevice model."""

    def test_device_creation(self, sample_device_data):
        """Test basic device creation."""
        from unifi.models import UniFiDevice

        device = UniFiDevice(
            mac=sample_device_data['mac'],
            name=sample_device_data['name'],
            type=sample_device_data['type'],
            model=sample_device_data['model'],
            status=sample_device_data['status'],
            ip=sample_device_data['ip'],
            uptime=sample_device_data['uptime']
        )

        assert device.mac == '00:1A:2B:3C:4D:5E'
        assert device.name == 'Test-AP-01'
        assert device.type == 'uap'

    def test_device_is_online(self):
        """Test is_online property."""
        from unifi.models import UniFiDevice

        online_device = UniFiDevice(
            mac='00:00:00:00:00:01',
            name='Online-AP',
            type='uap',
            model='U6-LR',
            status='online'
        )

        offline_device = UniFiDevice(
            mac='00:00:00:00:00:02',
            name='Offline-AP',
            type='uap',
            model='U6-LR',
            status='offline'
        )

        assert online_device.is_online is True
        assert offline_device.is_online is False

    def test_device_type_detection(self):
        """Test device type detection properties."""
        from unifi.models import UniFiDevice

        ap = UniFiDevice(mac='a', name='AP', type='uap', model='U6', status='online')
        switch = UniFiDevice(mac='b', name='Switch', type='usw', model='USW-48', status='online')
        gateway = UniFiDevice(mac='c', name='UDM', type='udm', model='UDM-Pro', status='online')

        assert ap.is_ap is True
        assert ap.is_switch is False
        assert ap.is_gateway is False

        assert switch.is_switch is True
        assert switch.is_ap is False

        assert gateway.is_gateway is True
        assert gateway.is_switch is False

    def test_uptime_calculations(self):
        """Test uptime conversions."""
        from unifi.models import UniFiDevice

        device = UniFiDevice(
            mac='00:00:00:00:00:01',
            name='Test',
            type='uap',
            model='U6',
            status='online',
            uptime=172800  # 2 days in seconds
        )

        assert device.uptime_hours == 48.0
        assert device.uptime_days == 2.0

    def test_device_to_dict(self, sample_device_data):
        """Test device serialization."""
        from unifi.models import UniFiDevice

        device = UniFiDevice(
            mac=sample_device_data['mac'],
            name=sample_device_data['name'],
            type=sample_device_data['type'],
            model=sample_device_data['model'],
            status=sample_device_data['status'],
            uptime=sample_device_data['uptime'],
            clients=sample_device_data['clients']
        )

        result = device.to_dict()

        assert result['mac'] == '00:1A:2B:3C:4D:5E'
        assert result['is_online'] is True
        assert result['uptime_hours'] == 24.0
        assert result['clients'] == 25


class TestUniFiSite:
    """Tests for UniFiSite model."""

    def test_site_from_api_response(self, sample_site_api_response):
        """Test site creation from API response."""
        from unifi.models import UniFiSite

        site = UniFiSite.from_api_response(sample_site_api_response)

        assert site.id == 'site-001'
        assert site.name == 'Test Office'
        assert site.total_devices == 10
        assert site.offline_devices == 2
        assert site.total_clients == 50
        assert site.isp == 'Verizon'

    def test_health_status_healthy(self):
        """Test health status for healthy site."""
        from unifi.models import UniFiSite

        site = UniFiSite(id='1', name='Test', health_score=95)
        assert site.health_status == 'healthy'

        site.health_score = 90
        assert site.health_status == 'healthy'

    def test_health_status_warning(self):
        """Test health status for warning site."""
        from unifi.models import UniFiSite

        site = UniFiSite(id='1', name='Test', health_score=75)
        assert site.health_status == 'warning'

        site.health_score = 70
        assert site.health_status == 'warning'

    def test_health_status_degraded(self):
        """Test health status for degraded site."""
        from unifi.models import UniFiSite

        site = UniFiSite(id='1', name='Test', health_score=60)
        assert site.health_status == 'degraded'

    def test_health_status_critical(self):
        """Test health status for critical site."""
        from unifi.models import UniFiSite

        site = UniFiSite(id='1', name='Test', health_score=40)
        assert site.health_status == 'critical'

    def test_health_score_calculation_offline_penalty(self):
        """Test health score penalty for offline devices."""
        from unifi.models import UniFiSite, UniFiDevice

        site = UniFiSite(
            id='1',
            name='Test',
            total_devices=10,
            offline_devices=5,  # 50% offline
            ap_count=5,
            gateway_count=1,
            devices=[
                UniFiDevice(mac='g', name='Gateway', type='udm', model='UDM', status='online')
            ]
        )

        score = site.calculate_health_score()
        # 50% offline = 20 point penalty (40% weight * 0.5)
        assert score == 80

    def test_health_score_calculation_overloaded_aps(self):
        """Test health score penalty for overloaded APs."""
        from unifi.models import UniFiSite, UniFiDevice

        site = UniFiSite(
            id='1',
            name='Test',
            total_devices=5,
            offline_devices=0,
            total_clients=250,
            ap_count=2,  # 125 clients per AP (overloaded)
            gateway_count=1,
            devices=[
                UniFiDevice(mac='g', name='Gateway', type='udm', model='UDM', status='online')
            ]
        )

        score = site.calculate_health_score()
        # (125 - 50) / 50 = 1.5, capped at 1.0 -> 20 point penalty
        assert score == 80

    def test_health_score_calculation_gateway_offline(self):
        """Test health score penalty for offline gateway."""
        from unifi.models import UniFiSite, UniFiDevice

        site = UniFiSite(
            id='1',
            name='Test',
            total_devices=5,
            offline_devices=1,
            gateway_count=1,
            devices=[
                UniFiDevice(mac='g', name='Gateway', type='udm', model='UDM', status='offline')
            ]
        )

        score = site.calculate_health_score()
        # Gateway offline = 40 point penalty + offline device penalty
        assert score <= 60

    def test_clients_per_ap(self):
        """Test clients per AP calculation."""
        from unifi.models import UniFiSite

        site = UniFiSite(id='1', name='Test', total_clients=100, ap_count=4)
        assert site.clients_per_ap == 25.0

        # No APs
        site_no_aps = UniFiSite(id='2', name='Test2', total_clients=100, ap_count=0)
        assert site_no_aps.clients_per_ap == 0.0

    def test_site_to_dict(self):
        """Test site serialization."""
        from unifi.models import UniFiSite

        site = UniFiSite(
            id='site-001',
            name='Test Site',
            total_devices=10,
            offline_devices=2,
            total_clients=50,
            isp='Verizon',
            health_score=85
        )

        result = site.to_dict()

        assert result['id'] == 'site-001'
        assert result['name'] == 'Test Site'
        assert result['totalDevices'] == 10
        assert result['offlineDevices'] == 2
        assert result['onlineDevices'] == 8
        assert result['healthScore'] == 85
        assert result['healthStatus'] == 'warning'


class TestFleetSummary:
    """Tests for FleetSummary model."""

    def test_fleet_summary_from_sites(self, sample_sites):
        """Test fleet summary calculation from sites."""
        from unifi.models import FleetSummary

        summary = FleetSummary.from_sites(sample_sites)

        assert summary.total_sites == 4
        assert summary.total_devices == 35  # 10+8+5+12
        assert summary.offline_devices == 6  # 0+2+0+4
        assert summary.total_clients == 460  # 150+80+30+200

    def test_fleet_health_categorization(self, sample_sites):
        """Test site health categorization."""
        from unifi.models import FleetSummary

        summary = FleetSummary.from_sites(sample_sites)

        # site-001: 95 (healthy), site-002: 75 (warning)
        # site-003: 100 (healthy), site-004: 60 (critical)
        assert summary.healthy_sites == 2
        assert summary.warning_sites == 1
        assert summary.critical_sites == 1

    def test_fleet_health_score(self, sample_sites):
        """Test overall fleet health percentage."""
        from unifi.models import FleetSummary

        summary = FleetSummary.from_sites(sample_sites)

        # 2 healthy out of 4 = 50%
        assert summary.fleet_health_score == 50

    def test_device_availability(self, sample_sites):
        """Test device availability calculation."""
        from unifi.models import FleetSummary

        summary = FleetSummary.from_sites(sample_sites)

        # 29 online out of 35 = 82.86%
        assert round(summary.device_availability, 1) == 82.9

    def test_isp_distribution(self, sample_sites):
        """Test ISP distribution tracking."""
        from unifi.models import FleetSummary

        summary = FleetSummary.from_sites(sample_sites)

        assert summary.sites_by_isp['Verizon'] == 2
        assert summary.sites_by_isp['AT&T'] == 1
        assert summary.sites_by_isp['Comcast'] == 1

    def test_empty_fleet_summary(self):
        """Test fleet summary with no sites."""
        from unifi.models import FleetSummary

        summary = FleetSummary.from_sites([])

        assert summary.total_sites == 0
        assert summary.fleet_health_score == 100
        assert summary.device_availability == 100.0
