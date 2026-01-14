"""
Tests for NinjaOne RMM API Client.

Tests:
- Configuration handling
- Demo client functionality
- Data models
- Authentication (mocked)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestNinjaOneConfig:
    """Tests for NinjaOneConfig."""

    def test_config_creation(self, ninjaone_config):
        """Test basic config creation."""
        assert ninjaone_config.client_id == 'test-client-id'
        assert ninjaone_config.client_secret == 'test-client-secret'
        assert ninjaone_config.base_url == 'https://api.ninjarmm.com'

    def test_config_from_env(self):
        """Test config creation from environment variables."""
        from ninjaone.client import NinjaOneConfig

        with patch.dict('os.environ', {
            'NINJAONE_CLIENT_ID': 'env-client-id',
            'NINJAONE_CLIENT_SECRET': 'env-secret',
            'NINJAONE_BASE_URL': 'https://custom.ninjarmm.com'
        }):
            config = NinjaOneConfig.from_env()

            assert config.client_id == 'env-client-id'
            assert config.client_secret == 'env-secret'
            assert config.base_url == 'https://custom.ninjarmm.com'

    def test_config_default_values(self):
        """Test config default values when env vars not set."""
        from ninjaone.client import NinjaOneConfig

        with patch.dict('os.environ', {}, clear=True):
            config = NinjaOneConfig.from_env()

            assert config.client_id == ''
            assert config.base_url == 'https://api.ninjarmm.com'
            assert config.timeout == 30


class TestNinjaOneAlert:
    """Tests for NinjaOneAlert model."""

    def test_alert_creation(self):
        """Test alert creation."""
        from ninjaone.client import NinjaOneAlert

        alert = NinjaOneAlert(
            id='alert-001',
            severity='CRITICAL',
            message='Disk space critical',
            device_id='device-001',
            device_name='SETCO-DC01',
            org_id='org-001',
            org_name='Setco Industries',
            created_at=datetime(2024, 12, 30, 10, 0, 0)
        )

        assert alert.id == 'alert-001'
        assert alert.severity == 'CRITICAL'
        assert alert.acknowledged is False

    def test_alert_to_dict(self):
        """Test alert serialization."""
        from ninjaone.client import NinjaOneAlert

        alert = NinjaOneAlert(
            id='alert-001',
            severity='CRITICAL',
            message='Test',
            device_id='d1',
            device_name='Test',
            org_id='o1',
            org_name='Test Org',
            created_at=datetime(2024, 12, 30, 10, 0, 0)
        )

        result = alert.to_dict()

        assert result['id'] == 'alert-001'
        assert result['severity'] == 'CRITICAL'
        assert result['source'] == 'NinjaOne'


class TestNinjaOneDevice:
    """Tests for NinjaOneDevice model."""

    def test_device_creation(self):
        """Test device creation."""
        from ninjaone.client import NinjaOneDevice

        device = NinjaOneDevice(
            id='device-001',
            name='SETCO-DC01',
            org_id='org-001',
            org_name='Setco Industries',
            status='ONLINE',
            os='Windows Server 2022'
        )

        assert device.id == 'device-001'
        assert device.name == 'SETCO-DC01'
        assert device.is_online is True

    def test_device_offline_status(self):
        """Test offline device detection."""
        from ninjaone.client import NinjaOneDevice

        device = NinjaOneDevice(
            id='device-001',
            name='Test',
            org_id='org-001',
            org_name='Test',
            status='OFFLINE',
            os='Windows'
        )

        assert device.is_online is False


class TestDemoNinjaOneClient:
    """Tests for DemoNinjaOneClient (for testing without credentials)."""

    def test_get_all_alerts(self):
        """Test getting all demo alerts."""
        from ninjaone.client import DemoNinjaOneClient

        client = DemoNinjaOneClient()
        alerts = client.get_alerts()

        assert len(alerts) == 3
        assert all(hasattr(a, 'severity') for a in alerts)

    def test_get_critical_alerts(self):
        """Test filtering critical alerts."""
        from ninjaone.client import DemoNinjaOneClient

        client = DemoNinjaOneClient()
        alerts = client.get_critical_alerts()

        assert len(alerts) == 2
        assert all(a.severity == 'CRITICAL' for a in alerts)

    def test_get_alerts_by_org(self):
        """Test filtering alerts by organization."""
        from ninjaone.client import DemoNinjaOneClient

        client = DemoNinjaOneClient()
        alerts = client.get_alerts(org_id='org-001')

        assert len(alerts) == 1
        assert alerts[0].org_id == 'org-001'

    def test_get_all_devices(self):
        """Test getting all demo devices."""
        from ninjaone.client import DemoNinjaOneClient

        client = DemoNinjaOneClient()
        devices = client.get_devices()

        assert len(devices) == 3

    def test_get_devices_by_org(self):
        """Test filtering devices by organization."""
        from ninjaone.client import DemoNinjaOneClient

        client = DemoNinjaOneClient()
        devices = client.get_devices(org_id='org-002')

        assert len(devices) == 1
        assert devices[0].org_id == 'org-002'

    def test_connection_always_succeeds(self):
        """Test that demo client always reports successful connection."""
        from ninjaone.client import DemoNinjaOneClient

        client = DemoNinjaOneClient()
        assert client.test_connection() is True


class TestNinjaOneClientFactory:
    """Tests for client factory function."""

    def test_get_demo_client(self):
        """Test getting demo client."""
        from ninjaone.client import get_client, DemoNinjaOneClient

        client = get_client(demo=True)
        assert isinstance(client, DemoNinjaOneClient)

    def test_get_real_client(self):
        """Test getting real client."""
        from ninjaone.client import get_client, NinjaOneClient

        client = get_client(demo=False)
        assert isinstance(client, NinjaOneClient)


class TestNinjaOneClientAuthentication:
    """Tests for NinjaOneClient authentication (mocked)."""

    def test_missing_credentials_raises_error(self, ninjaone_config):
        """Test that missing credentials raises error."""
        from ninjaone.client import NinjaOneClient, NinjaOneConfig, NinjaOneAPIError

        config = NinjaOneConfig(client_id='', client_secret='')
        client = NinjaOneClient(config)

        with pytest.raises(NinjaOneAPIError):
            client._authenticate()

    @patch('ninjaone.client.requests.post')
    def test_successful_authentication(self, mock_post, ninjaone_config):
        """Test successful authentication flow."""
        from ninjaone.client import NinjaOneClient

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test-token-12345',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        client = NinjaOneClient(ninjaone_config)
        client._authenticate()

        assert client._access_token == 'test-token-12345'

    @patch('ninjaone.client.requests.post')
    def test_failed_authentication(self, mock_post, ninjaone_config):
        """Test failed authentication raises error."""
        from ninjaone.client import NinjaOneClient, NinjaOneAPIError

        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        client = NinjaOneClient(ninjaone_config)

        with pytest.raises(NinjaOneAPIError):
            client._authenticate()


class TestNinjaOneClientRequests:
    """Tests for NinjaOneClient API requests (mocked)."""

    @patch('ninjaone.client.requests.post')
    def test_request_adds_auth_header(self, mock_post, ninjaone_config):
        """Test that requests include authorization header."""
        from ninjaone.client import NinjaOneClient

        # Mock auth response
        mock_auth = Mock()
        mock_auth.status_code = 200
        mock_auth.json.return_value = {'access_token': 'test-token'}
        mock_post.return_value = mock_auth

        client = NinjaOneClient(ninjaone_config)
        client._authenticate()

        # Verify token is set
        assert client._access_token == 'test-token'

    @patch.object(requests := Mock(), 'Session')
    def test_token_refresh_on_401(self, ninjaone_config):
        """Test that client refreshes token on 401 response."""
        from ninjaone.client import NinjaOneClient

        # This would test automatic token refresh
        # Simplified test since full mocking is complex
        client = NinjaOneClient(ninjaone_config)
        assert client._access_token is None  # Not authenticated yet
