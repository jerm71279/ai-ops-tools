"""
NinjaOne RMM API Client

Client for NinjaOne API integration.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


logger = logging.getLogger(__name__)


class NinjaOneAPIError(Exception):
    """Exception raised for NinjaOne API errors."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class NinjaOneConfig:
    """Configuration for NinjaOne API client."""
    client_id: str = ""
    client_secret: str = ""
    base_url: str = "https://us2.ninjarmm.com"
    timeout: int = 30
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> 'NinjaOneConfig':
        return cls(
            client_id=os.getenv('NINJAONE_CLIENT_ID', ''),
            client_secret=os.getenv('NINJAONE_CLIENT_SECRET', ''),
            base_url=os.getenv('NINJAONE_BASE_URL', 'https://api.ninjarmm.com'),
            timeout=int(os.getenv('NINJAONE_TIMEOUT', '30')),
            # Default to True; only disable for local dev with self-signed certs
            verify_ssl=os.getenv('NINJAONE_VERIFY_SSL', 'true').lower() != 'false'
        )


@dataclass
class NinjaOneAlert:
    """Represents a NinjaOne alert."""
    id: str
    severity: str  # CRITICAL, MAJOR, MODERATE, MINOR
    message: str
    device_id: str
    device_name: str
    org_id: str
    org_name: str
    created_at: datetime
    source: str = "NinjaOne"
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'severity': self.severity,
            'message': self.message,
            'deviceId': self.device_id,
            'deviceName': self.device_name,
            'orgId': self.org_id,
            'orgName': self.org_name,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'source': self.source,
            'acknowledged': self.acknowledged
        }


@dataclass
class NinjaOneDevice:
    """Represents a NinjaOne managed device."""
    id: str
    name: str
    org_id: str
    org_name: str
    status: str  # ONLINE, OFFLINE, UNKNOWN
    os: str
    last_contact: Optional[datetime] = None
    ip_address: Optional[str] = None
    
    @property
    def is_online(self) -> bool:
        return self.status.upper() == "ONLINE"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'orgId': self.org_id,
            'orgName': self.org_name,
            'status': self.status,
            'os': self.os,
            'lastContact': self.last_contact.isoformat() if self.last_contact else None,
            'ipAddress': self.ip_address,
            'isOnline': self.is_online
        }


@dataclass
class NinjaOneOrg:
    """Represents a NinjaOne organization (customer)."""
    id: str
    name: str
    device_count: int = 0
    alert_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'deviceCount': self.device_count,
            'alertCount': self.alert_count
        }


class NinjaOneClient:
    """
    Client for NinjaOne RMM API.

    Provides methods for querying alerts, devices, and organizations.
    """

    # Buffer time before expiration to refresh token (5 minutes)
    TOKEN_REFRESH_BUFFER = timedelta(minutes=5)

    def __init__(self, config: Optional[NinjaOneConfig] = None):
        self.config = config or NinjaOneConfig.from_env()
        self.session = requests.Session()
        self.session.verify = self.config.verify_ssl
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    def _is_token_expired(self) -> bool:
        """Check if token needs refresh (expired or expiring soon)."""
        if not self._access_token or not self._token_expires:
            return True
        # Refresh 5 minutes before actual expiry to avoid mid-request failures
        return datetime.now() >= (self._token_expires - self.TOKEN_REFRESH_BUFFER)

    def _authenticate(self):
        """Get OAuth access token."""
        if not self.config.client_id or not self.config.client_secret:
            raise NinjaOneAPIError("Missing client credentials")

        logger.info("Authenticating with NinjaOne API...")

        response = requests.post(
            f"{self.config.base_url}/oauth/token",
            data={
                'grant_type': 'client_credentials',
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'scope': 'monitoring management'
            },
            timeout=self.config.timeout,
            verify=self.config.verify_ssl
        )

        if response.status_code != 200:
            raise NinjaOneAPIError(f"Authentication failed: {response.status_code}")

        data = response.json()
        self._access_token = data['access_token']

        # Calculate actual expiration time from response (default 3600 seconds = 1 hour)
        expires_in = data.get('expires_in', 3600)
        self._token_expires = datetime.now() + timedelta(seconds=expires_in)

        logger.info(f"NinjaOne token acquired, expires at {self._token_expires.isoformat()}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError,
                                       requests.exceptions.Timeout))
    )
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request with retry logic."""
        # Proactively refresh token if expired or expiring soon
        if self._is_token_expired():
            self._authenticate()

        headers = {
            'Authorization': f'Bearer {self._access_token}',
            'Accept': 'application/json'
        }

        response = self.session.request(
            method=method,
            url=f"{self.config.base_url}{endpoint}",
            headers=headers,
            timeout=self.config.timeout,
            **kwargs
        )

        if response.status_code == 401:
            # Token rejected (possibly invalidated server-side), force re-authenticate
            logger.warning("Token rejected, re-authenticating...")
            self._access_token = None  # Force refresh
            self._authenticate()
            headers['Authorization'] = f'Bearer {self._access_token}'
            response = self.session.request(
                method=method,
                url=f"{self.config.base_url}{endpoint}",
                headers=headers,
                timeout=self.config.timeout,
                **kwargs
            )

        if response.status_code == 429:
            # Rate limited - let tenacity handle retry
            raise NinjaOneAPIError("Rate limited", status_code=429)

        if response.status_code >= 400:
            raise NinjaOneAPIError(
                f"API error: {response.status_code}",
                status_code=response.status_code
            )

        return response.json()
    
    def get_alerts(
        self, 
        severity: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> List[NinjaOneAlert]:
        """
        Get alerts from NinjaOne.
        
        Args:
            severity: Filter by severity (CRITICAL, MAJOR, MODERATE, MINOR)
            org_id: Filter by organization ID
        """
        params = {}
        if severity:
            params['severity'] = severity
        if org_id:
            params['organizationId'] = org_id
        
        data = self._request('GET', '/v2/alerts', params=params)
        
        alerts = []
        # NinjaOne API returns list directly, not wrapped in {'alerts': [...]}
        items = data if isinstance(data, list) else data.get('alerts', [])
        for item in items:
            try:
                alert = NinjaOneAlert(
                    id=str(item.get('id', '')),
                    severity=item.get('severity', 'UNKNOWN'),
                    message=item.get('message', ''),
                    device_id=str(item.get('deviceId', '')),
                    device_name=item.get('deviceName', ''),
                    org_id=str(item.get('organizationId', '')),
                    org_name=item.get('organizationName', ''),
                    created_at=datetime.fromisoformat(item['createTime'].replace('Z', '+00:00')) 
                               if item.get('createTime') else None,
                    acknowledged=item.get('acknowledged', False)
                )
                alerts.append(alert)
            except Exception as e:
                logger.warning(f"Failed to parse alert: {e}")
        
        return alerts
    
    def get_devices(self, org_id: Optional[str] = None) -> List[NinjaOneDevice]:
        """Get managed devices."""
        params = {}
        if org_id:
            params['organizationId'] = org_id
        
        data = self._request('GET', '/v2/devices', params=params)
        
        devices = []
        # NinjaOne API returns list directly, not wrapped in {'devices': [...]}
        items = data if isinstance(data, list) else data.get('devices', [])
        for item in items:
            try:
                device = NinjaOneDevice(
                    id=str(item.get('id', '')),
                    name=item.get('systemName', item.get('dnsName', 'Unknown')),
                    org_id=str(item.get('organizationId', '')),
                    org_name=item.get('organizationName', ''),
                    status=item.get('nodeStatus', 'UNKNOWN'),
                    os=item.get('os', {}).get('name', 'Unknown'),
                    ip_address=item.get('ipAddress')
                )
                devices.append(device)
            except Exception as e:
                logger.warning(f"Failed to parse device: {e}")
        
        return devices
    
    def get_organizations(self) -> List[NinjaOneOrg]:
        """Get all organizations (customers)."""
        data = self._request('GET', '/v2/organizations')
        
        orgs = []
        for item in data if isinstance(data, list) else data.get('organizations', []):
            try:
                org = NinjaOneOrg(
                    id=str(item.get('id', '')),
                    name=item.get('name', 'Unknown'),
                    device_count=item.get('deviceCount', 0),
                    alert_count=item.get('alertCount', 0)
                )
                orgs.append(org)
            except Exception as e:
                logger.warning(f"Failed to parse org: {e}")
        
        return orgs
    
    def get_critical_alerts(self) -> List[NinjaOneAlert]:
        """Get only critical severity alerts."""
        return self.get_alerts(severity='CRITICAL')

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert by ID."""
        try:
            self._request('POST', f'/v2/alert/{alert_id}/acknowledge')
            logger.info(f"Alert {alert_id} acknowledged")
            return True
        except NinjaOneAPIError as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False

    def reset_alert(self, alert_id: str) -> bool:
        """Reset/clear an alert by ID."""
        try:
            self._request('POST', f'/v2/alert/{alert_id}/reset')
            logger.info(f"Alert {alert_id} reset")
            return True
        except NinjaOneAPIError as e:
            logger.error(f"Failed to reset alert {alert_id}: {e}")
            return False

    def reset_device_alerts(self, device_id: str) -> bool:
        """Reset all alerts for a device."""
        try:
            self._request('POST', f'/v2/device/{device_id}/alerts/reset')
            logger.info(f"All alerts reset for device {device_id}")
            return True
        except NinjaOneAPIError as e:
            logger.error(f"Failed to reset alerts for device {device_id}: {e}")
            return False

    def test_connection(self) -> bool:
        """Test API connectivity."""
        try:
            self._authenticate()
            return True
        except NinjaOneAPIError:
            return False


# Demo data for testing
DEMO_ALERTS = [
    {
        'id': 'alert-001',
        'severity': 'CRITICAL',
        'message': 'Disk space critical on C: drive (95% full)',
        'deviceId': 'device-001',
        'deviceName': 'SETCO-DC01',
        'organizationId': 'org-001',
        'organizationName': 'Setco Industries',
        'createTime': '2024-12-30T10:00:00Z'
    },
    {
        'id': 'alert-002',
        'severity': 'MAJOR',
        'message': 'Antivirus definitions out of date',
        'deviceId': 'device-002',
        'deviceName': 'HOODS-PC05',
        'organizationId': 'org-002',
        'organizationName': 'Hoods Discount Home',
        'createTime': '2024-12-30T09:30:00Z'
    },
    {
        'id': 'alert-003',
        'severity': 'CRITICAL',
        'message': 'Service stopped: Print Spooler',
        'deviceId': 'device-003',
        'deviceName': 'KINDER-PRINT01',
        'organizationId': 'org-003',
        'organizationName': 'Kinder Academy',
        'createTime': '2024-12-30T08:45:00Z'
    }
]

DEMO_DEVICES = [
    {'id': 'device-001', 'systemName': 'SETCO-DC01', 'organizationId': 'org-001', 
     'organizationName': 'Setco Industries', 'nodeStatus': 'ONLINE', 'os': {'name': 'Windows Server 2022'}},
    {'id': 'device-002', 'systemName': 'HOODS-PC05', 'organizationId': 'org-002',
     'organizationName': 'Hoods Discount Home', 'nodeStatus': 'OFFLINE', 'os': {'name': 'Windows 11'}},
    {'id': 'device-003', 'systemName': 'KINDER-PRINT01', 'organizationId': 'org-003',
     'organizationName': 'Kinder Academy', 'nodeStatus': 'ONLINE', 'os': {'name': 'Windows 10'}}
]


class DemoNinjaOneClient:
    """Demo client for testing without credentials."""
    
    def get_alerts(self, severity=None, org_id=None) -> List[NinjaOneAlert]:
        alerts = []
        for item in DEMO_ALERTS:
            if severity and item['severity'] != severity:
                continue
            if org_id and item['organizationId'] != org_id:
                continue
            alerts.append(NinjaOneAlert(
                id=item['id'],
                severity=item['severity'],
                message=item['message'],
                device_id=item['deviceId'],
                device_name=item['deviceName'],
                org_id=item['organizationId'],
                org_name=item['organizationName'],
                created_at=datetime.fromisoformat(item['createTime'].replace('Z', '+00:00'))
            ))
        return alerts
    
    def get_devices(self, org_id=None) -> List[NinjaOneDevice]:
        devices = []
        for item in DEMO_DEVICES:
            if org_id and item['organizationId'] != org_id:
                continue
            devices.append(NinjaOneDevice(
                id=item['id'],
                name=item['systemName'],
                org_id=item['organizationId'],
                org_name=item['organizationName'],
                status=item['nodeStatus'],
                os=item['os']['name']
            ))
        return devices
    
    def get_critical_alerts(self) -> List[NinjaOneAlert]:
        return self.get_alerts(severity='CRITICAL')
    
    def test_connection(self) -> bool:
        return True


def get_client(demo: bool = False):
    """Factory function to get appropriate client."""
    if demo:
        return DemoNinjaOneClient()
    return NinjaOneClient()


__all__ = [
    'NinjaOneAPIError',
    'NinjaOneConfig',
    'NinjaOneAlert',
    'NinjaOneDevice',
    'NinjaOneOrg',
    'NinjaOneClient',
    'DemoNinjaOneClient',
    'get_client'
]
