#!/usr/bin/env python3
"""
NinjaOne RMM API Client
=======================

Handles OAuth authentication and API calls to NinjaOne's RMM platform
for endpoint management across customer organizations.

Environment Variables:
    NINJAONE_CLIENT_ID: OAuth client ID (required)
    NINJAONE_CLIENT_SECRET: OAuth client secret (required)
    NINJAONE_REGION: Regional endpoint - us, eu, oc, ca (default: us)

Usage:
    from skills.ninjaone import NinjaOneClient

    client = NinjaOneClient()
    if not client.is_configured():
        raise EnvironmentError("Set NINJAONE_CLIENT_ID and NINJAONE_CLIENT_SECRET")

    # Get fleet summary
    summary = await client.get_fleet_summary()

    # Get critical alerts
    alerts = await client.get_critical_alerts()
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    httpx = None

logger = logging.getLogger(__name__)


class NinjaOneError(Exception):
    """Base exception for NinjaOne client errors."""
    pass


class NinjaOneConfigError(NinjaOneError):
    """Raised when client is not properly configured."""
    pass


class NinjaOneAPIError(NinjaOneError):
    """Raised when API returns an error."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class NinjaOneClient:
    """
    Client for NinjaOne RMM API.

    Supports regional endpoints and OAuth client_credentials flow.
    """

    # Regional endpoints
    REGIONS = {
        "us": "https://app.ninjarmm.com",
        "eu": "https://eu.ninjarmm.com",
        "oc": "https://oc.ninjarmm.com",
        "ca": "https://ca.ninjarmm.com"
    }

    # Rate limits (approximate - adjust based on your tier)
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        Initialize NinjaOne client.

        Args:
            client_id: OAuth client ID (or set NINJAONE_CLIENT_ID env var)
            client_secret: OAuth client secret (or set NINJAONE_CLIENT_SECRET env var)
            region: Regional endpoint - us, eu, oc, ca (or set NINJAONE_REGION)
        """
        if not HAS_HTTPX:
            raise ImportError("httpx is required. Install with: pip install httpx")

        self.client_id = client_id or os.getenv("NINJAONE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("NINJAONE_CLIENT_SECRET")
        self.region = (region or os.getenv("NINJAONE_REGION", "us")).lower()

        self.base_url = self.REGIONS.get(self.region, self.REGIONS["us"])
        self.api_url = f"{self.base_url}/api/v2"

        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    def is_configured(self) -> bool:
        """Check if client has required credentials."""
        return bool(self.client_id and self.client_secret)

    def require_configured(self) -> None:
        """
        Raise error if not configured.

        IMPORTANT: This replaces the silent demo-mode fallback.
        We fail loudly instead of silently using fake data.
        """
        if not self.is_configured():
            raise NinjaOneConfigError(
                "NinjaOne not configured. "
                "Set NINJAONE_CLIENT_ID and NINJAONE_CLIENT_SECRET environment variables. "
                "See skills/ninjaone/README.md for setup instructions."
            )

    def get_endpoint_summary(self) -> str:
        """Get summary of configured endpoint."""
        return f"{self.base_url} ({self.region.upper()})"

    async def _get_access_token(self) -> str:
        """Get or refresh OAuth access token."""
        # Check if current token is valid (with 5-minute buffer)
        if self._access_token and self._token_expires:
            if datetime.utcnow() < self._token_expires - timedelta(minutes=5):
                return self._access_token

        self.require_configured()

        # Request new token
        token_url = f"{self.base_url}/oauth/token"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "scope": "monitoring management"
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                raise NinjaOneAPIError(
                    f"OAuth token request failed: {e}",
                    status_code=e.response.status_code
                )
            except httpx.RequestError as e:
                raise NinjaOneAPIError(f"OAuth token request error: {e}")

        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        self._token_expires = datetime.utcnow() + timedelta(seconds=expires_in)

        logger.debug(f"NinjaOne token refreshed, expires in {expires_in}s")
        return self._access_token

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Any:
        """Make authenticated API request."""
        token = await self._get_access_token()

        url = f"{self.api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise NinjaOneAPIError(
                        f"Rate limited. Wait before retrying. Limit: ~{self.RATE_LIMIT_REQUESTS_PER_MINUTE}/min",
                        status_code=429
                    )
                raise NinjaOneAPIError(
                    f"API request failed: {e}",
                    status_code=e.response.status_code
                )
            except httpx.RequestError as e:
                raise NinjaOneAPIError(f"API request error: {e}")

            # Some endpoints return empty body
            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

    # =========================================================================
    # ORGANIZATIONS
    # =========================================================================

    async def get_organizations(self) -> List[Dict[str, Any]]:
        """Get all customer organizations."""
        return await self._request("GET", "/organizations")

    async def get_organization(self, org_id: int) -> Dict[str, Any]:
        """Get a specific organization by ID."""
        return await self._request("GET", f"/organizations/{org_id}")

    # =========================================================================
    # DEVICES
    # =========================================================================

    async def get_devices(
        self,
        org_id: Optional[int] = None,
        device_filter: Optional[str] = None,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get devices with optional filtering.

        Args:
            org_id: Filter to specific organization
            device_filter: NinjaOne device filter string (e.g., "status eq OFFLINE")
            page_size: Results per page (max 1000)

        Returns:
            List of device dictionaries
        """
        params = {"pageSize": min(page_size, 1000)}

        if device_filter:
            params["df"] = device_filter

        endpoint = "/devices-detailed" if not org_id else f"/organizations/{org_id}/devices-detailed"

        return await self._request("GET", endpoint, params=params)

    async def get_device(self, device_id: int) -> Dict[str, Any]:
        """Get a specific device by ID."""
        return await self._request("GET", f"/devices/{device_id}")

    async def get_offline_devices(self) -> List[Dict[str, Any]]:
        """Get all offline devices across all organizations."""
        return await self.get_devices(device_filter="status eq OFFLINE")

    async def get_device_count_by_org(self) -> Dict[int, Dict[str, Any]]:
        """
        Get device counts per organization.

        Returns:
            Dict mapping org_id to {name, total, online, offline}
        """
        orgs = await self.get_organizations()
        counts = {}

        for org in orgs:
            org_id = org.get("id")
            devices = await self.get_devices(org_id=org_id)

            online = sum(1 for d in devices if d.get("status") == "ONLINE")
            offline = sum(1 for d in devices if d.get("status") == "OFFLINE")

            counts[org_id] = {
                "name": org.get("name"),
                "total": len(devices),
                "online": online,
                "offline": offline
            }

        return counts

    # =========================================================================
    # ALERTS
    # =========================================================================

    async def get_alerts(
        self,
        org_id: Optional[int] = None,
        severity: Optional[str] = None,
        status: str = "ACTIVE",
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get alerts with optional filtering.

        Args:
            org_id: Filter to specific organization
            severity: NONE, MINOR, MODERATE, MAJOR, CRITICAL
            status: ACTIVE, RESOLVED, ALL
            page_size: Results per page

        Returns:
            List of alert dictionaries
        """
        params = {"pageSize": page_size}

        if severity:
            params["severity"] = severity.upper()
        if status != "ALL":
            params["status"] = status.upper()

        endpoint = "/alerts" if not org_id else f"/organizations/{org_id}/alerts"

        return await self._request("GET", endpoint, params=params)

    async def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get all critical alerts across all organizations."""
        return await self.get_alerts(severity="CRITICAL", status="ACTIVE")

    # =========================================================================
    # ACTIVITIES
    # =========================================================================

    async def get_activities(
        self,
        activity_type: Optional[str] = None,
        older_than: Optional[int] = None,
        newer_than: Optional[int] = None,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get activity log entries.

        Args:
            activity_type: Filter by activity type
            older_than: Activity ID to paginate from
            newer_than: Activity ID to paginate to
            page_size: Results per page

        Returns:
            List of activity dictionaries
        """
        params = {"pageSize": page_size}

        if activity_type:
            params["activityType"] = activity_type
        if older_than:
            params["olderThan"] = older_than
        if newer_than:
            params["newerThan"] = newer_than

        return await self._request("GET", "/activities", params=params)

    # =========================================================================
    # SCRIPTING
    # =========================================================================

    async def run_script(
        self,
        device_ids: List[int],
        script_id: int,
        parameters: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Run a script on specified devices.

        Args:
            device_ids: List of target device IDs
            script_id: ID of script to run
            parameters: Optional script parameters

        Returns:
            Job information dictionary
        """
        payload = {
            "targets": {
                "devices": device_ids
            },
            "scriptId": script_id
        }

        if parameters:
            payload["parameters"] = parameters

        return await self._request("POST", "/scripting/run", data=payload)

    # =========================================================================
    # PATCHING
    # =========================================================================

    async def get_patch_report(
        self,
        org_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get patch compliance report.

        Args:
            org_id: Filter to specific organization

        Returns:
            List of devices with patch status
        """
        endpoint = "/queries/os-patch-installs"
        params = {}

        if org_id:
            params["organizationId"] = org_id

        return await self._request("GET", endpoint, params=params)

    # =========================================================================
    # SUMMARY QUERIES
    # =========================================================================

    async def get_fleet_summary(self) -> Dict[str, Any]:
        """
        Get aggregated statistics across all organizations.

        Returns:
            Dictionary with total orgs, devices, alerts, health metrics
        """
        orgs = await self.get_organizations()
        devices = await self.get_devices()
        alerts = await self.get_alerts(status="ACTIVE")

        online = sum(1 for d in devices if d.get("status") == "ONLINE")
        offline = sum(1 for d in devices if d.get("status") == "OFFLINE")

        critical_alerts = sum(1 for a in alerts if a.get("severity") == "CRITICAL")
        major_alerts = sum(1 for a in alerts if a.get("severity") == "MAJOR")

        return {
            "total_organizations": len(orgs),
            "total_devices": len(devices),
            "online_devices": online,
            "offline_devices": offline,
            "online_percent": round(online / len(devices) * 100, 1) if devices else 0,
            "total_alerts": len(alerts),
            "critical_alerts": critical_alerts,
            "major_alerts": major_alerts,
            "device_types": self._count_device_types(devices),
            "os_distribution": self._count_os_distribution(devices)
        }

    def _count_device_types(self, devices: List[Dict]) -> Dict[str, int]:
        """Count devices by type."""
        types = {}
        for d in devices:
            dtype = d.get("nodeClass", "Unknown")
            types[dtype] = types.get(dtype, 0) + 1
        return types

    def _count_os_distribution(self, devices: List[Dict]) -> Dict[str, int]:
        """Count devices by OS."""
        os_dist = {}
        for d in devices:
            os_name = d.get("os", {}).get("name", "Unknown")
            os_dist[os_name] = os_dist.get(os_name, 0) + 1
        return os_dist


# CLI for testing
if __name__ == "__main__":
    import asyncio
    import argparse

    parser = argparse.ArgumentParser(description="NinjaOne RMM Client")
    parser.add_argument("--summary", action="store_true", help="Get fleet summary")
    parser.add_argument("--alerts", action="store_true", help="Get critical alerts")
    parser.add_argument("--devices", action="store_true", help="Get all devices")
    args = parser.parse_args()

    async def main():
        client = NinjaOneClient()

        # IMPORTANT: No silent demo mode fallback - fail loudly
        if not client.is_configured():
            print("ERROR: NinjaOne not configured.")
            print("Set environment variables:")
            print("  export NINJAONE_CLIENT_ID=your_client_id")
            print("  export NINJAONE_CLIENT_SECRET=your_client_secret")
            print("  export NINJAONE_REGION=us  # or eu, oc, ca")
            return

        print(f"Endpoint: {client.get_endpoint_summary()}")

        if args.summary:
            summary = await client.get_fleet_summary()
            print(f"\nFleet Summary:")
            print(f"  Organizations: {summary['total_organizations']}")
            print(f"  Devices: {summary['total_devices']} ({summary['online_percent']}% online)")
            print(f"  Alerts: {summary['total_alerts']} ({summary['critical_alerts']} critical)")

        if args.alerts:
            alerts = await client.get_critical_alerts()
            print(f"\nCritical Alerts: {len(alerts)}")
            for a in alerts[:5]:
                print(f"  - {a.get('message', 'No message')}")

        if args.devices:
            devices = await client.get_devices()
            print(f"\nDevices: {len(devices)}")

    asyncio.run(main())
