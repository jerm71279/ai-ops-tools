"""
Pytest configuration and shared fixtures.
"""

import pytest
from typing import List
from datetime import datetime


# UniFi fixtures
@pytest.fixture
def sample_device_data():
    """Sample UniFi device data from API."""
    return {
        'mac': '00:1A:2B:3C:4D:5E',
        'name': 'Test-AP-01',
        'type': 'uap',
        'model': 'U6-LR',
        'status': 'online',
        'ip': '192.168.1.100',
        'firmware': '6.6.55',
        'uptime': 86400,
        'clients': 25
    }


@pytest.fixture
def sample_site_api_response():
    """Sample UniFi Site Manager API response."""
    return {
        'hostId': 'site-001',
        'siteName': 'Test Site',
        'meta': {
            'desc': 'Test Office',
            'timezone': 'America/Chicago',
            'address': '123 Test St'
        },
        'statistics': {
            'counts': {
                'totalDevice': 10,
                'offlineDevice': 2,
                'totalClient': 50,
                'uap': 5,
                'usw': 3,
                'ugw': 1,
                'udm': 1
            }
        },
        'wan': {
            'isp': 'Verizon',
            'ip': '203.0.113.1'
        },
        'status': 'online'
    }


@pytest.fixture
def sample_sites():
    """List of sample UniFi sites for testing analyzer."""
    from unifi.models import UniFiSite

    return [
        UniFiSite(
            id='site-001',
            name='Setco Industries',
            total_devices=10,
            offline_devices=0,
            total_clients=150,
            ap_count=5,
            switch_count=3,
            gateway_count=2,
            isp='Verizon',
            health_score=95
        ),
        UniFiSite(
            id='site-002',
            name='Hoods Discount',
            total_devices=8,
            offline_devices=2,
            total_clients=80,
            ap_count=4,
            switch_count=2,
            gateway_count=2,
            isp='AT&T',
            health_score=75
        ),
        UniFiSite(
            id='site-003',
            name='Kinder Academy',
            total_devices=5,
            offline_devices=0,
            total_clients=30,
            ap_count=3,
            switch_count=1,
            gateway_count=1,
            isp='Comcast',
            health_score=100
        ),
        UniFiSite(
            id='site-004',
            name='Gulf Shores Office',
            total_devices=12,
            offline_devices=4,
            total_clients=200,
            ap_count=6,
            switch_count=4,
            gateway_count=2,
            isp='Verizon',
            health_score=60
        ),
    ]


# NinjaOne fixtures
@pytest.fixture
def ninjaone_config():
    """NinjaOne configuration for testing."""
    from ninjaone.client import NinjaOneConfig
    return NinjaOneConfig(
        client_id='test-client-id',
        client_secret='test-client-secret',
        base_url='https://api.ninjarmm.com'
    )


# Maker/Checker fixtures
@pytest.fixture
def small_operation_context():
    """Context for a small operation (< 10 sites)."""
    from common.maker_checker import ValidationContext
    return ValidationContext(
        action_name='config_check',
        target_sites=['site-001', 'site-002'],
        user='test-user'
    )


@pytest.fixture
def bulk_operation_context():
    """Context for a bulk operation (> 10 sites)."""
    from common.maker_checker import ValidationContext
    return ValidationContext(
        action_name='firmware_upgrade',
        target_sites=[f'site-{i:03d}' for i in range(1, 16)],
        user='test-user'
    )


@pytest.fixture
def critical_operation_context():
    """Context for a critical operation requiring rollback plan."""
    from common.maker_checker import ValidationContext
    return ValidationContext(
        action_name='factory_reset',
        target_sites=['site-001'],
        plan={
            'rollback_plan': 'Restore from backup taken at 2024-12-30T10:00:00Z'
        },
        user='test-user'
    )
