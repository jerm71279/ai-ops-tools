"""
Real UniFi data source implementation using MCP server patterns.

Connects to UniFi Site Manager API (api.ui.com) using official API key.

SECURITY: Credentials are read from environment variables only.
No file-based credential storage to prevent plaintext exposure.

Based on OberaConnect MCP server implementation.
"""

import os
import httpx
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from data_sources.interface import (
    UniFiDataSource,
    UniFiSite,
    UniFiDevice,
    DeviceStatus,
)


# Configure logging
logger = logging.getLogger(__name__)


class UniFiAPIError(Exception):
    """Custom exception for UniFi API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MCPUniFiDataSource(UniFiDataSource):
    """
    Real UniFi data source using MCP server patterns.

    SECURITY: Uses environment variables for credentials only.
    - UNIFI_API_KEY: Official UniFi API key (required)

    Example:
        # Set environment variable first
        export UNIFI_API_KEY="your-api-key-here"

        from data_sources.unifi_mcp import MCPUniFiDataSource
        from data_sources import get_factory

        factory = get_factory()
        factory.register_unifi(MCPUniFiDataSource())

        unifi = factory.get_unifi()
        sites = unifi.fetch_sites()
    """

    API_URL = "https://api.ui.com/v1/sites"

    # Rate limiting settings
    MAX_REQUESTS_PER_MINUTE = 60
    MIN_REQUEST_INTERVAL = 1.0  # seconds between requests

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        cache_ttl_minutes: int = 5,
    ):
        """
        Initialize UniFi data source.

        Args:
            api_key: UniFi API key. If not provided, reads from UNIFI_API_KEY env var
            timeout: HTTP request timeout in seconds (must be positive)
            cache_ttl_minutes: How long to cache site data (1-60 minutes)

        Raises:
            ValueError: If timeout or cache_ttl_minutes are invalid
        """
        # Validate inputs
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if not 1 <= cache_ttl_minutes <= 60:
            raise ValueError("cache_ttl_minutes must be between 1 and 60")

        self._api_key = api_key or os.getenv("UNIFI_API_KEY")
        self._timeout = timeout
        self._cache_ttl = timedelta(minutes=cache_ttl_minutes)

        # Cache
        self._sites_cache: Optional[List[Dict]] = None
        self._cache_time: Optional[datetime] = None
        self._normalized_sites: Optional[List[UniFiSite]] = None

        # Rate limiting
        self._last_request_time: Optional[datetime] = None

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers using API key from environment."""
        if not self._api_key:
            raise UniFiAPIError(
                "UNIFI_API_KEY environment variable not set. "
                "Set it with: export UNIFI_API_KEY='your-key'"
            )

        return {
            "X-API-KEY": self._api_key,
            "Accept": "application/json",
            "User-Agent": "OberaConnect-NotionDashboards/1.0",
        }

    def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        if self._last_request_time:
            elapsed = (datetime.utcnow() - self._last_request_time).total_seconds()
            if elapsed < self.MIN_REQUEST_INTERVAL:
                import time
                time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._sites_cache is None or self._cache_time is None:
            return False
        return datetime.utcnow() - self._cache_time < self._cache_ttl

    def _fetch_raw_sites(self) -> List[Dict[str, Any]]:
        """Fetch raw site data from API with rate limiting and error handling."""
        self._rate_limit()

        headers = self._get_headers()

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(self.API_URL, headers=headers)
                self._last_request_time = datetime.utcnow()

                # Handle specific HTTP errors
                if response.status_code == 401:
                    raise UniFiAPIError("Invalid API key", status_code=401)
                elif response.status_code == 403:
                    raise UniFiAPIError("API key lacks required permissions", status_code=403)
                elif response.status_code == 429:
                    raise UniFiAPIError("Rate limit exceeded", status_code=429)
                elif response.status_code >= 500:
                    raise UniFiAPIError(f"UniFi API server error", status_code=response.status_code)

                response.raise_for_status()
                result = response.json()

                # Handle both {data: [...]} and direct array response
                if isinstance(result, dict):
                    return result.get("data", [])
                return result

        except httpx.TimeoutException:
            raise UniFiAPIError("Request timed out", status_code=None)
        except httpx.ConnectError:
            raise UniFiAPIError("Failed to connect to UniFi API", status_code=None)

    def _normalize_site(self, raw: Dict[str, Any]) -> UniFiSite:
        """Convert raw API response to UniFiSite model."""
        meta = raw.get('meta', {})
        stats = raw.get('statistics', {})
        counts = stats.get('counts', {})
        percentages = stats.get('percentages', {})

        # Extract WAN info - cloudaccess uses statistics.wans dict
        wans = stats.get('wans', {})
        wan_ip = ''
        isp = ''
        uptime_seconds = 0

        if wans:
            for wan_name, wan_data in wans.items():
                wan_ip = wan_data.get('externalIp', '')
                isp_info = wan_data.get('ispInfo', {})
                isp = isp_info.get('name') or isp_info.get('organization', '')
                uptime = wan_data.get('wanUptime', 100.0) or 100.0
                uptime_seconds = int(uptime * 86400 / 100)  # Convert percentage to seconds
                break
        else:
            # Legacy format
            isp_info = raw.get('ispInfo', {})
            wan_info = raw.get('wan', {})
            wan_ip = wan_info.get('externalIp', '')
            isp = isp_info.get('name') or isp_info.get('organization', '')

        # Name: cloudaccess uses meta.desc, legacy uses desc
        name = meta.get('desc') or meta.get('name') or raw.get('desc') or raw.get('name', 'Unknown')

        # Extract state from name if present (e.g., "Acme Corp - Alabama")
        state = ""
        if " - " in name:
            parts = name.split(" - ")
            if len(parts) > 1:
                state = parts[-1]

        devices_total = counts.get('totalDevice', 0) or 0
        devices_offline = counts.get('offlineDevice', 0) or 0

        return UniFiSite(
            site_id=raw.get('siteId') or raw.get('_id') or raw.get('id', ''),
            name=name,
            state=state,
            devices_online=devices_total - devices_offline,
            devices_offline=devices_offline,
            devices_total=devices_total,
            wifi_clients=counts.get('wifiClient', 0) or 0,
            wifi_clients_weak_signal=0,  # Not available from this API
            wan_ip=wan_ip,
            isp=isp,
            uptime_seconds=uptime_seconds,
            last_seen=datetime.now(timezone.utc),
            has_mikrotik=False,  # Not available from UniFi API
            has_sonicwall=False,
            has_azure=False,
        )

    def fetch_sites(self) -> List[UniFiSite]:
        """
        Fetch all customer sites from UniFi Site Manager.

        Returns:
            List of UniFiSite objects
        """
        if self._is_cache_valid() and self._normalized_sites:
            return self._normalized_sites.copy()

        raw_sites = self._fetch_raw_sites()
        self._sites_cache = raw_sites
        self._cache_time = datetime.utcnow()
        self._normalized_sites = [self._normalize_site(raw) for raw in raw_sites]

        return self._normalized_sites.copy()

    def fetch_site(self, site_id: str) -> Optional[UniFiSite]:
        """
        Fetch a specific site by ID.

        Args:
            site_id: Site identifier

        Returns:
            UniFiSite or None if not found
        """
        sites = self.fetch_sites()
        for site in sites:
            if site.site_id == site_id:
                return site
        return None

    def fetch_devices(self, site_id: str) -> List[UniFiDevice]:
        """
        Fetch all devices for a site.

        Note: The Site Manager API doesn't provide device-level details.
        This returns a summary based on site statistics.

        Args:
            site_id: Site identifier

        Returns:
            List of UniFiDevice objects (summary only)
        """
        site = self.fetch_site(site_id)
        if not site:
            return []

        # Site Manager API doesn't provide individual device details
        # Return summary devices based on counts
        devices = []

        # Create placeholder devices based on site statistics
        # In production, you'd call the site-specific device endpoint
        for i in range(site.devices_total):
            status = DeviceStatus.ONLINE if i >= site.devices_offline else DeviceStatus.OFFLINE
            devices.append(UniFiDevice(
                device_id=f"{site_id}_device_{i:03d}",
                name=f"Device {i + 1}",
                mac_address="",
                device_type="unknown",
                status=status,
                site_id=site_id,
                last_seen=site.last_seen if status == DeviceStatus.ONLINE else None,
            ))

        return devices

    def fetch_device(self, site_id: str, device_id: str) -> Optional[UniFiDevice]:
        """
        Fetch a specific device.

        Args:
            site_id: Site identifier
            device_id: Device identifier

        Returns:
            UniFiDevice or None if not found
        """
        devices = self.fetch_devices(site_id)
        for device in devices:
            if device.device_id == device_id:
                return device
        return None

    def get_connection_status(self) -> Dict[str, Any]:
        """
        Check API connection status.

        Returns:
            Dict with connection status information
        """
        if self._api_key:
            return {
                "configured": True,
                "auth_method": "environment_variable",
                "message": "API key configured via UNIFI_API_KEY (no expiration)",
                "endpoint": self.API_URL,
            }

        return {
            "configured": False,
            "message": "UNIFI_API_KEY environment variable not set",
        }
