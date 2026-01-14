"""
UniFi Site Manager API Client

Handles authentication and API calls to unifi.ui.com Site Manager.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

import requests

from .models import UniFiSite, UniFiDevice, FleetSummary


logger = logging.getLogger(__name__)


class UniFiAPIError(Exception):
    """Exception raised for API errors."""
    
    def __init__(self, message: str, status_code: int = None, response: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


@dataclass
class UniFiAPIConfig:
    """Configuration for UniFi API client."""
    api_key: str = ""  # Official API key (X-API-KEY header)
    base_url: str = "https://api.ui.com/v1"
    timeout: int = 30
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> 'UniFiAPIConfig':
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv('UNIFI_API_KEY', ''),
            base_url=os.getenv('UNIFI_API_BASE_URL', 'https://api.ui.com/v1'),
            timeout=int(os.getenv('UNIFI_API_TIMEOUT', '30')),
            # Default to True; only disable for local dev with self-signed certs
            verify_ssl=os.getenv('UNIFI_VERIFY_SSL', 'true').lower() != 'false'
        )


class UniFiClient:
    """
    Client for UniFi Site Manager API.
    
    Provides methods for querying and managing UniFi sites.
    """
    
    def __init__(self, config: Optional[UniFiAPIConfig] = None):
        """
        Initialize the client.
        
        Args:
            config: API configuration. If None, loads from environment.
        """
        self.config = config or UniFiAPIConfig.from_env()
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Configure the requests session with authentication."""
        if self.config.api_key:
            self.session.headers.update({
                'X-API-KEY': self.config.api_key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Dict = None, 
        data: Dict = None
    ) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body
            
        Returns:
            Parsed JSON response
            
        Raises:
            UniFiAPIError: On API errors
        """
        url = f"{self.config.base_url}{endpoint}"
        
        logger.debug(f"API request: {method} {url}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            if response.status_code >= 400:
                logger.error(f"API error: {response.status_code} - {response.text}")
                raise UniFiAPIError(
                    f"API request failed: {response.status_code}",
                    status_code=response.status_code,
                    response=response.text
                )
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise UniFiAPIError("API request timed out")
        except requests.exceptions.ConnectionError as e:
            raise UniFiAPIError(f"Connection error: {e}")
        except json.JSONDecodeError:
            raise UniFiAPIError("Invalid JSON response")
    
    def get_sites(self) -> List[UniFiSite]:
        """
        Get all sites from Site Manager.

        Returns:
            List of UniFiSite objects
        """
        response = self._request('GET', '/sites')
        
        sites = []
        for item in response.get('data', []):
            try:
                site = UniFiSite.from_api_response(item)
                sites.append(site)
            except Exception as e:
                logger.warning(f"Failed to parse site: {e}")
                continue
        
        logger.info(f"Loaded {len(sites)} sites from API")
        return sites
    
    def get_site(self, site_id: str) -> Optional[UniFiSite]:
        """
        Get a specific site by ID.
        
        Args:
            site_id: The site/host ID
            
        Returns:
            UniFiSite object or None if not found
        """
        response = self._request('GET', f'/ea/hosts/{site_id}')
        
        if 'data' in response:
            return UniFiSite.from_api_response(response['data'])
        
        return None
    
    def get_site_devices(self, site_id: str) -> List[UniFiDevice]:
        """
        Get all devices for a specific site.
        
        Args:
            site_id: The site/host ID
            
        Returns:
            List of UniFiDevice objects
        """
        response = self._request('GET', f'/ea/hosts/{site_id}/devices')
        
        devices = []
        for item in response.get('data', []):
            try:
                device = UniFiDevice(
                    mac=item.get('mac', ''),
                    name=item.get('name', item.get('model', 'Unknown')),
                    type=item.get('type', 'unknown'),
                    model=item.get('model', 'Unknown'),
                    status=item.get('status', 'unknown'),
                    ip=item.get('ip'),
                    firmware=item.get('version'),
                    uptime=item.get('uptime', 0),
                    clients=item.get('numSta', 0)
                )
                devices.append(device)
            except Exception as e:
                logger.warning(f"Failed to parse device: {e}")
                continue
        
        return devices
    
    def get_fleet_summary(self) -> FleetSummary:
        """
        Get summary statistics for the entire fleet.
        
        Returns:
            FleetSummary object
        """
        sites = self.get_sites()
        return FleetSummary.from_sites(sites)
    
    def test_connection(self) -> bool:
        """
        Test API connectivity.
        
        Returns:
            True if connection successful
        """
        try:
            self._request('GET', '/ea/hosts?limit=1')
            return True
        except UniFiAPIError:
            return False


# Demo data for testing without API credentials
DEMO_SITES = [
    {
        "hostId": "demo-site-001",
        "siteName": "Setco Industries",
        "meta": {"desc": "Setco Industries", "timezone": "America/Chicago"},
        "statistics": {
            "counts": {
                "totalDevice": 8,
                "offlineDevice": 0,
                "totalClient": 45,
                "uap": 4,
                "usw": 3,
                "ugw": 1
            }
        },
        "wan": {"isp": "Verizon", "ip": "203.0.113.10"},
        "status": "online"
    },
    {
        "hostId": "demo-site-002",
        "siteName": "Hoods Discount Home",
        "meta": {"desc": "Hoods Discount Home", "timezone": "America/Chicago"},
        "statistics": {
            "counts": {
                "totalDevice": 12,
                "offlineDevice": 2,
                "totalClient": 87,
                "uap": 6,
                "usw": 4,
                "ugw": 2
            }
        },
        "wan": {"isp": "Lumen", "ip": "203.0.113.20"},
        "status": "online"
    },
    {
        "hostId": "demo-site-003",
        "siteName": "Kinder Academy Main",
        "meta": {"desc": "Kinder Academy Main", "timezone": "America/Chicago"},
        "statistics": {
            "counts": {
                "totalDevice": 6,
                "offlineDevice": 1,
                "totalClient": 32,
                "uap": 3,
                "usw": 2,
                "ugw": 1
            }
        },
        "wan": {"isp": "AT&T", "ip": "203.0.113.30"},
        "status": "online"
    },
    {
        "hostId": "demo-site-004",
        "siteName": "Celebration Church",
        "meta": {"desc": "Celebration Church", "timezone": "America/Chicago"},
        "statistics": {
            "counts": {
                "totalDevice": 15,
                "offlineDevice": 0,
                "totalClient": 156,
                "uap": 8,
                "usw": 5,
                "ugw": 2
            }
        },
        "wan": {"isp": "Spectrum", "ip": "203.0.113.40"},
        "status": "online"
    },
    {
        "hostId": "demo-site-005",
        "siteName": "Gulf Shores Medical",
        "meta": {"desc": "Gulf Shores Medical", "timezone": "America/Chicago"},
        "statistics": {
            "counts": {
                "totalDevice": 10,
                "offlineDevice": 3,
                "totalClient": 28,
                "uap": 5,
                "usw": 4,
                "ugw": 1
            }
        },
        "wan": {"isp": "Comcast", "ip": "203.0.113.50"},
        "status": "degraded"
    },
    {
        "hostId": "demo-site-006",
        "siteName": "Mobile Bay Construction",
        "meta": {"desc": "Mobile Bay Construction", "timezone": "America/Chicago"},
        "statistics": {
            "counts": {
                "totalDevice": 5,
                "offlineDevice": 0,
                "totalClient": 18,
                "uap": 2,
                "usw": 2,
                "ugw": 1
            }
        },
        "wan": {"isp": "Verizon", "ip": "203.0.113.60"},
        "status": "online"
    },
    {
        "hostId": "demo-site-007",
        "siteName": "Fairhope Dental",
        "meta": {"desc": "Fairhope Dental", "timezone": "America/Chicago"},
        "statistics": {
            "counts": {
                "totalDevice": 4,
                "offlineDevice": 0,
                "totalClient": 12,
                "uap": 2,
                "usw": 1,
                "ugw": 1
            }
        },
        "wan": {"isp": "AT&T", "ip": "203.0.113.70"},
        "status": "online"
    },
    {
        "hostId": "demo-site-008",
        "siteName": "Daphne Auto Group",
        "meta": {"desc": "Daphne Auto Group", "timezone": "America/Chicago"},
        "statistics": {
            "counts": {
                "totalDevice": 20,
                "offlineDevice": 1,
                "totalClient": 95,
                "uap": 10,
                "usw": 7,
                "ugw": 3
            }
        },
        "wan": {"isp": "Lumen", "ip": "203.0.113.80"},
        "status": "online"
    }
]


class DemoUniFiClient:
    """
    Demo client that returns fake data for testing.
    
    No API credentials required.
    """
    
    def __init__(self):
        self._sites = [UniFiSite.from_api_response(s) for s in DEMO_SITES]
    
    def get_sites(self) -> List[UniFiSite]:
        return self._sites.copy()
    
    def get_site(self, site_id: str) -> Optional[UniFiSite]:
        for site in self._sites:
            if site.id == site_id:
                return site
        return None
    
    def get_fleet_summary(self) -> FleetSummary:
        return FleetSummary.from_sites(self._sites)
    
    def test_connection(self) -> bool:
        return True


def get_client(demo: bool = False) -> UniFiClient:
    """
    Factory function to get appropriate client.
    
    Args:
        demo: If True, return demo client
        
    Returns:
        UniFiClient or DemoUniFiClient
    """
    if demo:
        return DemoUniFiClient()
    return UniFiClient()


__all__ = [
    'UniFiAPIError',
    'UniFiAPIConfig',
    'UniFiClient',
    'DemoUniFiClient',
    'get_client'
]
