#!/usr/bin/env python3
"""
Customer Status Board Sync - Push site data to Notion dashboard

Purpose:
    Syncs customer site data from UniFi Site Manager and NinjaOne
    to a Notion database for cross-team visibility.

Usage:
    python customer_status_sync.py --config config.json
    python customer_status_sync.py --config config.json --dry-run
    python customer_status_sync.py --config config.json --site "Acme Corp"

Requirements:
    pip install notion-client --break-system-packages

Author: OberaConnect
Created: 2025
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from notion_client_wrapper import NotionWrapper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Data Collection Stubs - Replace with actual API integrations
# =============================================================================

def fetch_unifi_sites() -> List[Dict]:
    """
    Fetch site data from UniFi Site Manager API.
    
    Returns:
        List of site dictionaries with device counts and status
    
    TODO: Replace with actual UniFi API integration
    Reference: https://developer.ui.com for API docs
    """
    # Placeholder - integrate with UniFi Site Manager API
    return [
        {
            "site_id": "site_001",
            "name": "Acme Corp - Main Office",
            "state": "Alabama",
            "devices_online": 12,
            "devices_offline": 0,
            "devices_total": 12,
            "wifi_clients": 45,
            "signal_warnings": 2,
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "has_mikrotik": False,
            "has_sonicwall": False,
            "has_azure": True,
            "contract_renewal": "2025-12-31",
            "primary_contact": "John Smith"
        }
    ]


def fetch_ninjaone_data(site_name: str) -> Dict:
    """
    Fetch monitoring data from NinjaOne RMM.
    
    Args:
        site_name: Customer site name to match
    
    Returns:
        Dictionary with tickets, alerts, backup status
    
    TODO: Replace with actual NinjaOne API integration
    """
    return {
        "open_tickets": 0,
        "active_alerts": 0,
        "backup_status": "success"
    }


def calculate_health_score(site_data: Dict, ninjaone_data: Dict) -> int:
    """
    Calculate health score (0-100) based on site metrics.
    
    Scoring factors:
    - Device availability: 40 points
    - WiFi signal quality: 20 points
    - Open tickets: 20 points
    - Backup status: 20 points
    """
    score = 100
    
    # Device availability (40 points)
    total = site_data.get("devices_total", 0)
    if total > 0:
        availability = site_data["devices_online"] / total
        score -= int((1 - availability) * 40)
    
    # WiFi signal warnings (20 points) - signals below -65dBm threshold
    signal_warnings = site_data.get("signal_warnings", 0)
    if signal_warnings > 0:
        score -= min(signal_warnings * 2, 20)
    
    # Open tickets (20 points)
    tickets = ninjaone_data.get("open_tickets", 0)
    if tickets > 0:
        score -= min(tickets * 4, 20)
    
    # Backup status (20 points)
    backup = ninjaone_data.get("backup_status", "unknown")
    backup_penalties = {"success": 0, "partial": 10, "failed": 20, "unknown": 5}
    score -= backup_penalties.get(backup, 5)
    
    return max(0, score)


def determine_stack_type(site_data: Dict) -> List[str]:
    """Determine technology stack from device inventory."""
    stack = ["Ubiquiti"]  # Default for new deployments
    
    if site_data.get("has_mikrotik"):
        stack.append("MikroTik")
    if site_data.get("has_sonicwall"):
        stack.append("SonicWall")
    if site_data.get("has_azure"):
        stack.append("Azure")
    
    return stack


# =============================================================================
# Notion Sync Operations
# =============================================================================

class CustomerStatusSync:
    """Sync customer site data to Notion database."""
    
    def __init__(self, config_path: str, dry_run: bool = False):
        """
        Initialize sync with configuration.
        
        Args:
            config_path: Path to config JSON with Notion credentials and DB IDs
            dry_run: If True, don't actually write to Notion
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.dry_run = dry_run
        
        if not dry_run:
            self.client = NotionWrapper(token=self.config.get("notion_token"))
        else:
            self.client = None
        
        self.db_id = self.config["databases"]["customer_status"]
    
    def build_properties(self, site_data: Dict, ninjaone_data: Dict) -> Dict:
        """Build Notion page properties from collected data."""
        health_score = calculate_health_score(site_data, ninjaone_data)
        stack = determine_stack_type(site_data)
        
        # Determine deployment status based on health
        if health_score >= 80:
            status = "active"
        elif health_score >= 50:
            status = "maintenance"
        else:
            status = "needs attention"
        
        properties = {
            "Site Name": NotionWrapper.prop_title(site_data["name"]),
            "Customer ID": NotionWrapper.prop_rich_text(site_data.get("site_id", "")),
            "State": NotionWrapper.prop_select(site_data.get("state", "Alabama")),
            "Device Count": NotionWrapper.prop_number(site_data.get("devices_total", 0)),
            "Stack Type": NotionWrapper.prop_multi_select(stack),
            "Deployment Status": NotionWrapper.prop_select(status),
            "Health Score": NotionWrapper.prop_number(health_score),
            "Last Health Check": NotionWrapper.prop_date(
                datetime.now(timezone.utc).strftime("%Y-%m-%d")
            ),
            "Open Tickets": NotionWrapper.prop_number(ninjaone_data.get("open_tickets", 0)),
        }
        
        # Optional fields
        if site_data.get("contract_renewal"):
            properties["Contract Renewal"] = NotionWrapper.prop_date(
                site_data["contract_renewal"]
            )
        
        if site_data.get("primary_contact"):
            properties["Primary Contact"] = NotionWrapper.prop_rich_text(
                site_data["primary_contact"]
            )
        
        return properties
    
    def sync_site(self, site_data: Dict) -> Dict:
        """
        Sync a single site to Notion.
        
        Creates new page or updates existing based on site name match.
        """
        site_name = site_data["name"]
        logger.info(f"Syncing site: {site_name}")
        
        # Fetch additional data
        ninjaone_data = fetch_ninjaone_data(site_name)
        
        # Build properties
        properties = self.build_properties(site_data, ninjaone_data)
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would sync: {site_name}")
            logger.debug(f"Properties: {json.dumps(properties, indent=2, default=str)}")
            return {"status": "dry_run", "site": site_name}
        
        # Upsert - update if exists, create if not
        result, action = self.client.upsert_page(
            self.db_id,
            site_name,
            properties
        )
        
        logger.info(f"{action.capitalize()} page for: {site_name}")
        return {"status": "success", "action": action, "page": result}
    
    def sync_all(self, filter_site: Optional[str] = None) -> List[Dict]:
        """
        Sync all sites (or filtered site) to Notion.
        
        Args:
            filter_site: Optional site name to sync only that site
        
        Returns:
            List of sync results
        """
        results = []
        
        # Fetch site data from UniFi
        sites = fetch_unifi_sites()
        logger.info(f"Found {len(sites)} sites from UniFi")
        
        # Filter if specified
        if filter_site:
            sites = [s for s in sites if filter_site.lower() in s["name"].lower()]
            logger.info(f"Filtered to {len(sites)} sites matching '{filter_site}'")
        
        # Maker/checker: warn if bulk operation
        if len(sites) > 10 and not self.dry_run:
            logger.warning(f"Bulk operation: {len(sites)} sites. Consider --dry-run first.")
        
        # Sync each site
        for site in sites:
            try:
                result = self.sync_site(site)
                results.append({
                    "site": site["name"],
                    "status": result.get("status", "success"),
                    "action": result.get("action"),
                    "result": result
                })
            except Exception as e:
                logger.error(f"Failed to sync {site['name']}: {e}")
                results.append({
                    "site": site["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate sync summary report."""
        successful = len([r for r in results if r["status"] == "success"])
        created = len([r for r in results if r.get("action") == "created"])
        updated = len([r for r in results if r.get("action") == "updated"])
        failed = len([r for r in results if r["status"] == "error"])
        dry_run = len([r for r in results if r["status"] == "dry_run"])
        
        report = f"""
Customer Status Sync Report
{'=' * 40}
Timestamp: {datetime.now().isoformat()}
Total Sites: {len(results)}
Successful: {successful} (Created: {created}, Updated: {updated})
Failed: {failed}
Dry Run: {dry_run}

Details:
"""
        for r in results:
            if r["status"] == "success":
                icon = "✓"
                detail = r.get("action", "synced")
            elif r["status"] == "error":
                icon = "✗"
                detail = "error"
            else:
                icon = "○"
                detail = "dry run"
            
            report += f"  {icon} {r['site']}: {detail}\n"
            if r.get("error"):
                report += f"      Error: {r['error']}\n"
        
        return report


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sync customer site data to Notion dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config config.json
  %(prog)s --config config.json --dry-run
  %(prog)s --config config.json --site "Acme Corp"
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        required=True,
        help='Path to configuration JSON file'
    )
    
    parser.add_argument(
        '--site', '-s',
        help='Sync only sites matching this name'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing to Notion'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not Path(args.config).exists():
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)
    
    try:
        syncer = CustomerStatusSync(args.config, dry_run=args.dry_run)
        results = syncer.sync_all(filter_site=args.site)
        report = syncer.generate_report(results)
        print(report)
        
        # Exit with error if any failures
        if any(r["status"] == "error" for r in results):
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
