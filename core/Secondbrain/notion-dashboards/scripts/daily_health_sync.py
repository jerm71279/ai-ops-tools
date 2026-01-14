#!/usr/bin/env python3
"""
Daily Health Summary Sync - Push daily site snapshots to Notion

Purpose:
    Creates daily health snapshot entries for each customer site,
    building historical data for trend analysis and reporting.

Usage:
    python daily_health_sync.py --config config.json
    python daily_health_sync.py --config config.json --dry-run
    
    # Typically run via cron at 6 AM:
    # 0 6 * * * /path/to/venv/bin/python /path/to/daily_health_sync.py --config /path/to/config.json

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
from typing import Dict, List, Optional, Tuple

from notion_client_wrapper import NotionWrapper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# UniFi Best Practices Constants
# =============================================================================

WIFI_SIGNAL_THRESHOLD = -65  # dBm minimum acceptable signal
RESERVED_VLANS = [1, 4095]   # VLANs that should not be used


# =============================================================================
# Data Collection - Replace stubs with actual API integrations
# =============================================================================

def fetch_unifi_site_health(site_id: str) -> Dict:
    """
    Fetch health metrics from UniFi Site Manager API.
    
    TODO: Replace with actual UniFi API integration
    """
    return {
        "site_id": site_id,
        "devices_online": 10,
        "devices_offline": 1,
        "devices_total": 11,
        "wifi_clients": 42,
        "clients_below_threshold": 3,
    }


def fetch_ninjaone_alerts(site_name: str) -> Dict:
    """Fetch active alerts from NinjaOne RMM."""
    return {
        "active_alerts": 2,
        "critical_alerts": 0,
        "warning_alerts": 2,
        "alert_summary": ["High CPU on server01", "Disk space warning on NAS"]
    }


def fetch_backup_status(site_name: str) -> str:
    """Fetch backup status. Returns: success, partial, failed, unknown"""
    return "success"


def check_config_drift(site_id: str) -> Tuple[bool, List[str]]:
    """
    Check for configuration drift against baseline rules.
    
    OberaConnect validation rules:
    - Open SSIDs must be blocked
    - VLAN 1 and 4095 are reserved
    - Permit-any firewall rules blocked
    """
    violations = []
    # Placeholder - implement actual config checks
    return (len(violations) > 0, violations)


# =============================================================================
# Health Score Calculation
# =============================================================================

def calculate_health_score(
    unifi_data: Dict,
    ninjaone_data: Dict,
    backup_status: str,
    config_drift: bool
) -> int:
    """
    Calculate comprehensive health score (0-100).
    
    Scoring: Device availability (30), WiFi quality (20), 
    Alerts (20), Backup (15), Config compliance (15)
    """
    score = 100
    
    # Device availability (30 points)
    total = unifi_data.get("devices_total", 0)
    if total > 0:
        availability = unifi_data.get("devices_online", 0) / total
        score -= int((1 - availability) * 30)
    
    # WiFi signal quality (20 points)
    weak_clients = unifi_data.get("clients_below_threshold", 0)
    total_clients = unifi_data.get("wifi_clients", 0)
    if total_clients > 0:
        weak_ratio = weak_clients / total_clients
        score -= int(weak_ratio * 20)
    
    # Active alerts (20 points)
    critical = ninjaone_data.get("critical_alerts", 0)
    warning = ninjaone_data.get("warning_alerts", 0)
    score -= min(critical * 10 + warning * 2, 20)
    
    # Backup status (15 points)
    backup_penalties = {"success": 0, "partial": 7, "failed": 15, "unknown": 5}
    score -= backup_penalties.get(backup_status, 5)
    
    # Config compliance (15 points)
    if config_drift:
        score -= 15
    
    return max(0, min(100, score))


# =============================================================================
# Notion Sync Operations
# =============================================================================

class DailyHealthSync:
    """Create daily health snapshot entries in Notion."""
    
    def __init__(self, config_path: str, dry_run: bool = False):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.dry_run = dry_run
        
        if not dry_run:
            self.client = NotionWrapper(token=self.config.get("notion_token"))
        else:
            self.client = None
        
        self.health_db_id = self.config["databases"]["daily_health"]
        self.customer_db_id = self.config["databases"]["customer_status"]
        self._customer_cache = {}
    
    def _get_customer_page_id(self, site_name: str) -> Optional[str]:
        """Get Notion page ID for customer site."""
        if self.dry_run:
            return None
        
        if site_name not in self._customer_cache:
            page = self.client.find_page_by_title(self.customer_db_id, site_name)
            self._customer_cache[site_name] = page["id"] if page else None
        return self._customer_cache[site_name]
    
    def build_properties(
        self,
        date: str,
        site_name: str,
        unifi_data: Dict,
        ninjaone_data: Dict,
        backup_status: str,
        config_drift: bool,
        drift_violations: List[str]
    ) -> Dict:
        """Build Notion page properties for health snapshot."""
        
        health_score = calculate_health_score(
            unifi_data, ninjaone_data, backup_status, config_drift
        )
        
        total = unifi_data.get("devices_total", 0)
        online = unifi_data.get("devices_online", 0)
        availability = (online / total * 100) if total > 0 else 0
        
        # Alert summary (top 3)
        alerts = ninjaone_data.get("alert_summary", [])[:3]
        alert_text = "; ".join(alerts) if alerts else "No active alerts"
        
        properties = {
            "Date": NotionWrapper.prop_title(date),
            "Devices Online": NotionWrapper.prop_number(online),
            "Devices Offline": NotionWrapper.prop_number(
                unifi_data.get("devices_offline", 0)
            ),
            "Devices Total": NotionWrapper.prop_number(total),
            "Availability Percentage": NotionWrapper.prop_number(round(availability, 1)),
            "WiFi Clients": NotionWrapper.prop_number(
                unifi_data.get("wifi_clients", 0)
            ),
            "Signal Warnings": NotionWrapper.prop_number(
                unifi_data.get("clients_below_threshold", 0)
            ),
            "Active Alerts": NotionWrapper.prop_number(
                ninjaone_data.get("active_alerts", 0)
            ),
            "Alert Summary": NotionWrapper.prop_rich_text(alert_text),
            "Config Drift Detected": NotionWrapper.prop_checkbox(config_drift),
            "Backup Status": NotionWrapper.prop_select(backup_status),
            "Health Score": NotionWrapper.prop_number(health_score),
        }
        
        # Add relation to customer if exists
        customer_page_id = self._get_customer_page_id(site_name)
        if customer_page_id:
            properties["Site"] = NotionWrapper.prop_relation([customer_page_id])
        
        # Add notes for drift violations
        if drift_violations:
            properties["Notes"] = NotionWrapper.prop_rich_text(
                "Config drift: " + "; ".join(drift_violations)
            )
        
        return properties
    
    def sync_site_health(self, site_id: str, site_name: str) -> Dict:
        """Create daily health snapshot for a single site."""
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logger.info(f"Creating health snapshot for {site_name} ({date})")
        
        # Collect data
        unifi_data = fetch_unifi_site_health(site_id)
        ninjaone_data = fetch_ninjaone_alerts(site_name)
        backup_status = fetch_backup_status(site_name)
        config_drift, drift_violations = check_config_drift(site_id)
        
        # Build properties
        properties = self.build_properties(
            date=date,
            site_name=site_name,
            unifi_data=unifi_data,
            ninjaone_data=ninjaone_data,
            backup_status=backup_status,
            config_drift=config_drift,
            drift_violations=drift_violations
        )
        
        # Calculate for maker/checker
        health_score = calculate_health_score(
            unifi_data, ninjaone_data, backup_status, config_drift
        )
        
        requires_review = (
            health_score < 70 or
            ninjaone_data.get("critical_alerts", 0) > 0 or
            config_drift
        )
        
        if requires_review:
            logger.warning(f"Site {site_name} flagged for review (score: {health_score})")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create snapshot for {site_name}")
            return {
                "status": "dry_run",
                "site": site_name,
                "health_score": health_score,
                "requires_review": requires_review
            }
        
        # Create snapshot entry
        result = self.client.create_page(self.health_db_id, properties)
        logger.info(f"Created health snapshot for {site_name} (score: {health_score})")
        
        return {
            "status": "success",
            "site": site_name,
            "health_score": health_score,
            "requires_review": requires_review,
            "page_id": result["id"]
        }
    
    def sync_all_sites(self) -> List[Dict]:
        """Create health snapshots for all customer sites."""
        results = []
        
        if self.dry_run:
            # Use placeholder data for dry run
            customers = [{"name": "Test Site", "site_id": "test_001"}]
        else:
            # Get all customer sites from the customer status database
            customer_pages = self.client.query_database(self.customer_db_id)
            customers = [
                {
                    "name": self.client.extract_title(p),
                    "site_id": self.client.extract_property(p, "Customer ID") or ""
                }
                for p in customer_pages
            ]
        
        logger.info(f"Found {len(customers)} customer sites")
        
        for customer in customers:
            try:
                result = self.sync_site_health(customer["site_id"], customer["name"])
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to sync {customer['name']}: {e}")
                results.append({
                    "status": "error",
                    "site": customer["name"],
                    "error": str(e)
                })
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate daily sync summary report."""
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "error"]
        review_needed = [r for r in results if r.get("requires_review")]
        
        avg_health = 0
        if successful:
            avg_health = sum(r["health_score"] for r in successful) / len(successful)
        
        report = f"""
Daily Health Sync Report - {date}
{'=' * 40}
Timestamp: {datetime.now().isoformat()}
Total Sites: {len(results)}
Successful: {len(successful)}
Failed: {len(failed)}
Average Health Score: {avg_health:.1f}
"""
        
        if review_needed:
            report += f"""
⚠️  SITES REQUIRING REVIEW ({len(review_needed)})
{'-' * 40}
"""
            for r in review_needed:
                report += f"  • {r['site']}: Health Score {r.get('health_score', 'N/A')}\n"
        
        if failed:
            report += f"""
❌ FAILED SYNCS ({len(failed)})
{'-' * 40}
"""
            for r in failed:
                report += f"  • {r['site']}: {r.get('error', 'Unknown error')}\n"
        
        return report


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Create daily health snapshots in Notion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config config.json
  %(prog)s --config config.json --dry-run
        """
    )
    
    parser.add_argument('--config', '-c', required=True, help='Config JSON path')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Debug logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not Path(args.config).exists():
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)
    
    try:
        syncer = DailyHealthSync(args.config, dry_run=args.dry_run)
        results = syncer.sync_all_sites()
        report = syncer.generate_report(results)
        print(report)
        
        if any(r["status"] == "error" for r in results):
            sys.exit(1)
        if any(r.get("requires_review") for r in results):
            sys.exit(2)  # Warning exit code
            
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
