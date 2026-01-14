#!/usr/bin/env python3
"""
Device Issues Sync - Pull NinjaOne alerts to Notion for triage and maintenance

Purpose:
    Syncs active NinjaOne alerts to a Notion database for visibility,
    triage, and scheduling maintenance actions.

Usage:
    python device_issues_sync.py --config config.json
    python device_issues_sync.py --config config.json --dry-run

    # Typically run via cron every 2 hours:
    # 0 */2 * * * /path/to/venv/bin/python /path/to/device_issues_sync.py --config /path/to/config.json

Requirements:
    pip install notion-client httpx --break-system-packages

Author: OberaConnect
Created: 2026
"""

import argparse
import sys
import os
import json
import httpx
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import from core modules
from core import (
    BaseSyncClient,
    get_logger,
    enable_debug,
    NotionSyncError,
    DataSourceError,
)

# Import NotionWrapper for static property builders
from notion_client_wrapper import NotionWrapper

# Setup logging
logger = get_logger(__name__)


# =============================================================================
# Issue Type Classification
# =============================================================================

def classify_alert(alert: Dict) -> Tuple[str, str]:
    """
    Classify an alert into issue type and severity.

    Args:
        alert: Raw NinjaOne alert dictionary

    Returns:
        Tuple of (issue_type, severity)
    """
    source_type = alert.get("sourceType", "").upper()
    message = alert.get("message", "").lower()
    condition = alert.get("conditionName", "").lower()

    # Classify by source type
    if "DISK_FREE_SPACE" in source_type:
        issue_type = "disk_space"
    elif "DISK_IO" in source_type:
        issue_type = "disk_io"
    elif "MEMORY" in source_type:
        issue_type = "memory"
    elif "CPU" in source_type:
        issue_type = "cpu"
    elif "SERVICE" in source_type or "service" in message:
        issue_type = "service_down"
    elif "backup" in message or "backup" in condition:
        issue_type = "backup_failed"
    elif "offline" in message:
        issue_type = "offline"
    else:
        issue_type = "other"

    # Determine severity from alert data or thresholds
    data = alert.get("data", {}).get("message", {}).get("params", {})
    threshold = data.get("threshold", "")

    # Critical: disk <10%, memory >95%, any offline
    # Warning: disk 10-20%, memory 85-95%
    if issue_type == "disk_space":
        try:
            thresh = int(threshold)
            severity = "critical" if thresh <= 10 else "warning"
        except (ValueError, TypeError):
            severity = "warning"
    elif issue_type == "memory":
        try:
            thresh = int(threshold)
            severity = "critical" if thresh >= 95 else "warning"
        except (ValueError, TypeError):
            severity = "warning"
    elif issue_type == "offline":
        severity = "critical"
    elif issue_type == "backup_failed":
        severity = "critical"
    else:
        severity = "warning"

    return issue_type, severity


def suggest_action(issue_type: str) -> str:
    """
    Suggest a maintenance action based on issue type.

    Args:
        issue_type: Classified issue type

    Returns:
        Suggested action string
    """
    actions = {
        "disk_space": "disk_cleanup",
        "memory": "restart_service",
        "disk_io": "manual",
        "cpu": "manual",
        "service_down": "restart_service",
        "backup_failed": "manual",
        "offline": "manual",
    }
    return actions.get(issue_type, "manual")


# =============================================================================
# NinjaOne MCP Client
# =============================================================================

class NinjaOneMCPClient:
    """
    Client for NinjaOne API using MCP server patterns.

    Uses OAuth client credentials for authentication.
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
        region: str = "us2",
    ):
        self._client_id = client_id or os.getenv("NINJAONE_CLIENT_ID")
        self._client_secret = client_secret or os.getenv("NINJAONE_CLIENT_SECRET")
        self._region = region.lower()
        # Allow NINJAONE_BASE_URL to override region mapping
        self._base_url = os.getenv("NINJAONE_BASE_URL") or self.REGIONS.get(self._region, self.REGIONS["us2"])
        self._api_url = f"{self._base_url}/api/v2"

        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    def is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    def _get_token(self) -> str:
        """Get or refresh OAuth token."""
        if self._access_token and self._token_expires:
            if datetime.now(timezone.utc) < self._token_expires - timedelta(minutes=5):
                return self._access_token

        if not self.is_configured():
            raise ValueError("NinjaOne not configured. Set NINJAONE_CLIENT_ID and NINJAONE_CLIENT_SECRET.")

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self._base_url}/oauth/token",
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
        self._token_expires = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        return self._access_token

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make authenticated API request."""
        token = self._get_token()
        url = f"{self._api_url}{endpoint}"

        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method=method,
                url=url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                params=params,
            )
            response.raise_for_status()

            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

    def get_organizations(self) -> List[Dict]:
        """Fetch all organizations."""
        return self._request("GET", "/organizations")

    def get_alerts(self, status: str = "ACTIVE", page_size: int = 200) -> List[Dict]:
        """Fetch alerts."""
        return self._request("GET", "/alerts", params={
            "status": status,
            "pageSize": page_size
        })

    def get_device(self, device_id: int) -> Optional[Dict]:
        """Fetch a single device by ID."""
        try:
            return self._request("GET", f"/devices/{device_id}")
        except httpx.HTTPStatusError:
            return None

    def get_all_devices(self, page_size: int = 1000) -> List[Dict]:
        """Fetch all devices (increased page size to cover full fleet)."""
        return self._request("GET", "/devices-detailed", params={"pageSize": page_size})


# =============================================================================
# Device Issues Sync Client
# =============================================================================

class DeviceIssuesSyncClient(BaseSyncClient):
    """
    Sync NinjaOne alerts to Notion Device Issues database.

    Features:
    - Pulls active alerts from NinjaOne
    - Classifies by issue type and severity
    - Creates/updates pages in Notion
    - Deduplicates by alert UID
    - Marks resolved issues when alerts clear
    """

    def __init__(self, config_path: str, dry_run: bool = False, verbose: bool = False):
        super().__init__(config_path, dry_run, verbose)

        # Initialize NinjaOne client
        # Config may have ${ENV_VAR} placeholders - always prefer env vars
        self._ninja = NinjaOneMCPClient(
            client_id=os.getenv("NINJAONE_CLIENT_ID"),
            client_secret=os.getenv("NINJAONE_CLIENT_SECRET"),
        )

        # Caches
        self._org_cache: Dict[int, str] = {}
        self._device_cache: Dict[int, Dict] = {}

    @property
    def primary_database(self) -> str:
        return "device_issues"

    def _get_org_name(self, org_id: int) -> str:
        """Get organization name from cache or API."""
        if not self._org_cache:
            orgs = self._ninja.get_organizations()
            self._org_cache = {o["id"]: o["name"] for o in orgs}
        return self._org_cache.get(org_id, f"Org {org_id}")

    def _get_existing_issues(self) -> Dict[str, Dict]:
        """
        Get existing issues from Notion, keyed by alert UID.

        Returns:
            Dict mapping alert_uid to page data
        """
        if self.dry_run:
            return {}

        db_id = self.config.databases.get(self.primary_database)
        if not db_id:
            self.logger.warning("device_issues database not configured")
            return {}

        existing = {}
        try:
            # Query for non-resolved issues
            pages = self._client.query_database(
                db_id,
                filter_obj={
                    "property": "Status",
                    "select": {
                        "does_not_equal": "resolved"
                    }
                }
            )

            for page in pages:
                props = page.get("properties", {})
                alert_uid = props.get("Alert UID", {}).get("rich_text", [])
                if alert_uid:
                    uid = alert_uid[0].get("plain_text", "")
                    if uid:
                        existing[uid] = {
                            "page_id": page["id"],
                            "status": props.get("Status", {}).get("select", {}).get("name", "new")
                        }
        except Exception as e:
            self.logger.warning(f"Failed to query existing issues: {e}")

        return existing

    def _build_properties(self, alert: Dict, device: Optional[Dict], org_name: str) -> Dict:
        """
        Build Notion page properties from alert data.

        Args:
            alert: NinjaOne alert dictionary
            device: Optional device details
            org_name: Organization name

        Returns:
            Dict of Notion properties
        """
        issue_type, severity = classify_alert(alert)
        suggested_action = suggest_action(issue_type)

        # Get device name
        device_name = "Unknown Device"
        if device:
            device_name = device.get("systemName") or device.get("dnsName") or f"Device {alert.get('deviceId')}"

        # Parse timestamps
        create_time = alert.get("createTime")
        if isinstance(create_time, (int, float)):
            created_dt = datetime.fromtimestamp(create_time, tz=timezone.utc)
        else:
            created_dt = datetime.now(timezone.utc)

        return {
            "Device Name": NotionWrapper.prop_title(device_name),
            "Organization": NotionWrapper.prop_rich_text(org_name),
            "Issue Type": NotionWrapper.prop_select(issue_type),
            "Severity": NotionWrapper.prop_select(severity),
            "Details": NotionWrapper.prop_rich_text(alert.get("message", "")[:2000]),
            "Status": NotionWrapper.prop_select("new"),
            "Device ID": NotionWrapper.prop_number(alert.get("deviceId")),
            "Scheduled Action": NotionWrapper.prop_select(suggested_action),
            "Alert UID": NotionWrapper.prop_rich_text(alert.get("uid", "")),
            "Created": NotionWrapper.prop_date(created_dt.strftime("%Y-%m-%d")),
            "Last Seen": NotionWrapper.prop_date(datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        }

    def sync(self) -> List[Dict]:
        """
        Sync NinjaOne alerts to Notion.

        Returns:
            List of sync results
        """
        self.logger.info("Starting device issues sync")

        # Check NinjaOne configuration
        if not self._ninja.is_configured():
            self.logger.error("NinjaOne not configured")
            return []

        # Get database ID
        db_id = self.config.databases.get(self.primary_database)
        if not db_id and not self.dry_run:
            self.logger.error("device_issues database not configured in config")
            return []

        results = []

        # Fetch active alerts
        self.logger.info("Fetching alerts from NinjaOne...")
        try:
            alerts = self._ninja.get_alerts(status="ACTIVE")
            self.logger.info(f"Found {len(alerts)} active alerts")
        except Exception as e:
            self.logger.error(f"Failed to fetch alerts: {e}")
            return []

        # Build device cache (one API call instead of N)
        self.logger.info("Fetching device inventory...")
        try:
            devices = self._ninja.get_all_devices()
            self._device_cache = {d["id"]: d for d in devices}
            self.logger.info(f"Cached {len(self._device_cache)} devices")
        except Exception as e:
            self.logger.warning(f"Failed to fetch devices (names will be Unknown): {e}")

        # Get existing issues for deduplication
        existing_issues = self._get_existing_issues()
        self.logger.info(f"Found {len(existing_issues)} existing issues in Notion")

        # Track which alerts we see (for marking resolved)
        seen_uids = set()

        # Process each alert
        for alert in alerts:
            alert_uid = alert.get("uid", "")
            if not alert_uid:
                continue

            seen_uids.add(alert_uid)
            device_id = alert.get("deviceId")

            # Get device from cache
            device = self._device_cache.get(device_id) if device_id else None

            # Get org ID from device (alerts don't include organizationId)
            org_id = device.get("organizationId") if device else None
            org_name = self._get_org_name(org_id) if org_id else "Unknown"

            # Build properties
            properties = self._build_properties(alert, device, org_name)

            issue_type, severity = classify_alert(alert)
            device_name = properties["Device Name"]["title"][0]["text"]["content"]

            # Check if already exists
            if alert_uid in existing_issues:
                # Update last seen date only
                if not self.dry_run:
                    try:
                        self._client.update_page(
                            existing_issues[alert_uid]["page_id"],
                            {"Last Seen": NotionWrapper.prop_date(datetime.now(timezone.utc).strftime("%Y-%m-%d"))}
                        )
                    except Exception as e:
                        self.logger.warning(f"Failed to update {device_name}: {e}")

                results.append({
                    "device": device_name,
                    "action": "updated",
                    "issue_type": issue_type,
                    "severity": severity,
                })
            else:
                # Create new issue
                if self.dry_run:
                    self.logger.info(f"[DRY RUN] Would create: {device_name} - {issue_type} ({severity})")
                else:
                    try:
                        self._client.create_page(db_id, properties)
                        self.logger.info(f"Created issue: {device_name} - {issue_type}")
                    except Exception as e:
                        self.logger.error(f"Failed to create issue for {device_name}: {e}")
                        continue

                results.append({
                    "device": device_name,
                    "action": "created",
                    "issue_type": issue_type,
                    "severity": severity,
                })

        # Mark resolved issues (alerts no longer active)
        resolved_count = 0
        for uid, issue_data in existing_issues.items():
            if uid not in seen_uids and issue_data["status"] != "resolved":
                if not self.dry_run:
                    try:
                        self._client.update_page(
                            issue_data["page_id"],
                            {"Status": NotionWrapper.prop_select("resolved")}
                        )
                        resolved_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to mark resolved: {e}")
                else:
                    self.logger.info(f"[DRY RUN] Would mark as resolved: {uid}")
                    resolved_count += 1

        if resolved_count:
            self.logger.info(f"Marked {resolved_count} issues as resolved")

        # Summary
        created = sum(1 for r in results if r["action"] == "created")
        updated = sum(1 for r in results if r["action"] == "updated")
        self.logger.info(f"Sync complete: {created} created, {updated} updated, {resolved_count} resolved")

        return results


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sync NinjaOne alerts to Notion Device Issues database"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to config.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to Notion"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        enable_debug()

    try:
        client = DeviceIssuesSyncClient(
            config_path=args.config,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        results = client.sync()

        # Print summary
        if args.dry_run:
            print("\n[DRY RUN] No changes made")

        print(f"\nProcessed {len(results)} alerts")

        # Exit with success
        sys.exit(0)

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
