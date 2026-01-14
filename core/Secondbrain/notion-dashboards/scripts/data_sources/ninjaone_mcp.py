"""
Real NinjaOne data source implementation using MCP server patterns.

Connects to NinjaOne RMM API using OAuth client credentials.

Based on OberaConnect MCP server implementation.
"""

import os
import httpx
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from data_sources.interface import (
    NinjaOneDataSource,
    NinjaOneOrganization,
    NinjaOneAlert,
    BackupStatus,
    AlertSeverity,
)


class MCPNinjaOneDataSource(NinjaOneDataSource):
    """
    Real NinjaOne data source using MCP server patterns.

    Connects to NinjaOne RMM API using OAuth client credentials.
    Requires:
    - NINJAONE_CLIENT_ID
    - NINJAONE_CLIENT_SECRET
    - NINJAONE_REGION (default: us2)

    Example:
        from data_sources.ninjaone_mcp import MCPNinjaOneDataSource
        from data_sources import get_factory

        factory = get_factory()
        factory.register_ninjaone(MCPNinjaOneDataSource())

        ninja = factory.get_ninjaone()
        orgs = ninja.fetch_organizations()
    """

    REGIONS = {
        "us": "https://app.ninjarmm.com",
        "us2": "https://us2.ninjarmm.com",
        "us3": "https://us3.ninjarmm.com",
        "eu": "https://eu.ninjarmm.com",
        "oc": "https://oc.ninjarmm.com",
        "ca": "https://ca.ninjarmm.com"
    }

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        region: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize NinjaOne data source.

        Args:
            client_id: OAuth client ID. If not provided, reads from NINJAONE_CLIENT_ID
            client_secret: OAuth client secret. If not provided, reads from NINJAONE_CLIENT_SECRET
            region: Datacenter region. If not provided, reads from NINJAONE_REGION (default: us2)
            timeout: HTTP request timeout in seconds
        """
        self._client_id = client_id or os.getenv("NINJAONE_CLIENT_ID")
        self._client_secret = client_secret or os.getenv("NINJAONE_CLIENT_SECRET")
        self._region = (region or os.getenv("NINJAONE_REGION", "us2")).lower()
        self._timeout = timeout

        # Allow direct base URL override
        self._base_url = os.getenv("NINJAONE_BASE_URL") or self.REGIONS.get(
            self._region, self.REGIONS["us2"]
        )
        self._api_url = f"{self._base_url}/api/v2"

        # OAuth token cache
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

        # Data cache
        self._orgs_cache: Optional[List[Dict]] = None
        self._devices_cache: Optional[List[Dict]] = None
        self._alerts_cache: Optional[List[Dict]] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)

    def is_configured(self) -> bool:
        """Check if credentials are configured."""
        return bool(self._client_id and self._client_secret)

    def _get_access_token(self) -> str:
        """Get or refresh OAuth access token (synchronous)."""
        # Check if current token is valid
        if self._access_token and self._token_expires:
            if datetime.utcnow() < self._token_expires - timedelta(minutes=5):
                return self._access_token

        if not self.is_configured():
            raise ValueError(
                "NinjaOne not configured. Set NINJAONE_CLIENT_ID and NINJAONE_CLIENT_SECRET."
            )

        # Request new token
        token_url = f"{self._base_url}/oauth/token"

        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "scope": "monitoring management"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            data = response.json()

        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        self._token_expires = datetime.utcnow() + timedelta(seconds=expires_in)

        return self._access_token

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
    ) -> Any:
        """Make authenticated API request."""
        token = self._get_access_token()

        url = f"{self._api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        with httpx.Client(timeout=self._timeout) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
            )
            response.raise_for_status()

            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache_time is None:
            return False
        return datetime.utcnow() - self._cache_time < self._cache_ttl

    def _fetch_raw_organizations(self) -> List[Dict]:
        """Fetch raw organization data."""
        return self._request("GET", "/organizations")

    def _fetch_raw_devices(self, org_id: Optional[int] = None) -> List[Dict]:
        """Fetch raw device data."""
        if org_id:
            return self._request("GET", f"/organizations/{org_id}/devices-detailed")
        return self._request("GET", "/devices-detailed")

    def _fetch_raw_alerts(
        self,
        org_id: Optional[int] = None,
        severity: Optional[str] = None,
        status: str = "ACTIVE"
    ) -> List[Dict]:
        """Fetch raw alert data."""
        params = {"pageSize": 200}

        if severity:
            params["severity"] = severity.upper()
        if status != "ALL":
            params["status"] = status.upper()

        if org_id:
            return self._request("GET", f"/organizations/{org_id}/alerts", params=params)
        return self._request("GET", "/alerts", params=params)

    def _normalize_organization(
        self,
        raw_org: Dict,
        devices: List[Dict],
        alerts: List[Dict]
    ) -> NinjaOneOrganization:
        """Convert raw API data to NinjaOneOrganization model."""
        org_id = raw_org.get("id")
        org_name = raw_org.get("name", "Unknown")

        # Filter devices for this org
        org_devices = [d for d in devices if d.get("organizationId") == org_id]
        org_alerts = [a for a in alerts if a.get("organizationId") == org_id]

        online = sum(1 for d in org_devices if d.get("status") == "ONLINE")
        offline = sum(1 for d in org_devices if d.get("status") == "OFFLINE")

        critical = sum(1 for a in org_alerts if a.get("severity") == "CRITICAL")
        warning = sum(1 for a in org_alerts if a.get("severity") in ("MAJOR", "MODERATE", "MINOR"))
        info = sum(1 for a in org_alerts if a.get("severity") in ("INFO", "NONE"))

        # Backup status - infer from alerts
        backup_alerts = [a for a in org_alerts if "backup" in a.get("message", "").lower()]
        if any(a.get("severity") == "CRITICAL" for a in backup_alerts):
            backup_status = "failed"
        elif backup_alerts:
            backup_status = "partial"
        else:
            backup_status = "success"

        # Alert summary
        alert_summary = [a.get("message", "") for a in org_alerts[:5]]

        return NinjaOneOrganization(
            org_id=str(org_id),
            name=org_name,
            device_count=len(org_devices),
            online_devices=online,
            offline_devices=offline,
            open_tickets=0,  # Not available from alerts API
            alerts_critical=critical,
            alerts_warning=warning,
            alerts_info=info,
            backup_status=backup_status,
            last_backup=datetime.now(timezone.utc) - timedelta(hours=1),  # Placeholder
            alert_summary=alert_summary,
        )

    def fetch_organization(self, org_name: str) -> Optional[NinjaOneOrganization]:
        """
        Fetch organization data by name.

        Args:
            org_name: Organization/customer name (partial match supported)

        Returns:
            NinjaOneOrganization or None if not found
        """
        orgs = self.fetch_organizations()
        org_name_lower = org_name.lower()

        for org in orgs:
            if org_name_lower in org.name.lower():
                return org

        return None

    def fetch_organizations(self) -> List[NinjaOneOrganization]:
        """
        Fetch all organizations.

        Returns:
            List of NinjaOneOrganization objects
        """
        # Use cache if valid
        if self._is_cache_valid() and self._orgs_cache is not None:
            return self._normalize_all_orgs()

        # Fetch fresh data
        self._orgs_cache = self._fetch_raw_organizations()
        self._devices_cache = self._fetch_raw_devices()
        self._alerts_cache = self._fetch_raw_alerts()
        self._cache_time = datetime.utcnow()

        return self._normalize_all_orgs()

    def _normalize_all_orgs(self) -> List[NinjaOneOrganization]:
        """Normalize all cached organizations."""
        if not self._orgs_cache:
            return []

        return [
            self._normalize_organization(
                org,
                self._devices_cache or [],
                self._alerts_cache or []
            )
            for org in self._orgs_cache
        ]

    def fetch_alerts(
        self,
        org_name: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
        active_only: bool = True
    ) -> List[NinjaOneAlert]:
        """
        Fetch alerts with optional filtering.

        Args:
            org_name: Filter by organization name
            severity: Filter by severity level
            active_only: Only return active (unresolved) alerts

        Returns:
            List of NinjaOneAlert objects
        """
        status = "ACTIVE" if active_only else "ALL"
        severity_str = severity.value.upper() if severity else None

        # Map our AlertSeverity to NinjaOne severity
        severity_map = {
            "INFO": "NONE",
            "WARNING": "MINOR",  # Also includes MODERATE, MAJOR
            "CRITICAL": "CRITICAL",
        }
        if severity_str and severity_str in severity_map:
            severity_str = severity_map[severity_str]

        raw_alerts = self._fetch_raw_alerts(severity=severity_str, status=status)

        # Filter by org name if provided
        if org_name:
            org_name_lower = org_name.lower()
            raw_alerts = [
                a for a in raw_alerts
                if org_name_lower in a.get("organization", {}).get("name", "").lower()
            ]

        # Convert to NinjaOneAlert objects
        alerts = []
        for raw in raw_alerts:
            sev_str = raw.get("severity", "INFO")
            if sev_str in ("CRITICAL",):
                sev = AlertSeverity.CRITICAL
            elif sev_str in ("MAJOR", "MODERATE", "MINOR"):
                sev = AlertSeverity.WARNING
            else:
                sev = AlertSeverity.INFO

            created_str = raw.get("createTime")
            created_at = None
            if created_str:
                try:
                    created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                except ValueError:
                    pass

            alerts.append(NinjaOneAlert(
                alert_id=str(raw.get("id", "")),
                device_id=str(raw.get("deviceId", "")),
                device_name=raw.get("device", {}).get("systemName", "Unknown"),
                severity=sev,
                message=raw.get("message", ""),
                category=raw.get("type", ""),
                created_at=created_at,
                is_active=raw.get("status") == "ACTIVE",
                is_acknowledged=raw.get("acknowledged", False),
            ))

        return alerts

    def fetch_backup_status(self, org_name: str) -> BackupStatus:
        """
        Fetch backup status for an organization.

        Args:
            org_name: Organization name

        Returns:
            BackupStatus object
        """
        org = self.fetch_organization(org_name)
        if not org:
            return BackupStatus(status="unknown")

        # Derive backup status from alerts
        alerts = self.fetch_alerts(org_name=org_name, active_only=True)
        backup_alerts = [a for a in alerts if "backup" in a.message.lower()]

        if any(a.severity == AlertSeverity.CRITICAL for a in backup_alerts):
            status = "failed"
            failed_jobs = [a.message for a in backup_alerts if a.severity == AlertSeverity.CRITICAL]
        elif backup_alerts:
            status = "partial"
            failed_jobs = [a.message for a in backup_alerts]
        else:
            status = "success"
            failed_jobs = []

        return BackupStatus(
            status=status,
            last_successful=datetime.now(timezone.utc) - timedelta(hours=1) if status == "success" else None,
            last_attempted=datetime.now(timezone.utc),
            protected_devices=org.device_count,
            total_devices=org.device_count,
            failed_jobs=failed_jobs,
        )

    def get_connection_status(self) -> Dict[str, Any]:
        """
        Check API connection status.

        Returns:
            Dict with connection status information
        """
        if not self.is_configured():
            return {
                "configured": False,
                "message": "Credentials not configured. Set NINJAONE_CLIENT_ID and NINJAONE_CLIENT_SECRET.",
            }

        # Try to get a token to verify credentials
        try:
            self._get_access_token()
            return {
                "configured": True,
                "authenticated": True,
                "region": self._region,
                "endpoint": self._base_url,
                "message": f"Connected to {self._region.upper()} datacenter",
            }
        except Exception as e:
            return {
                "configured": True,
                "authenticated": False,
                "error": str(e),
                "message": f"Authentication failed: {str(e)}",
            }
