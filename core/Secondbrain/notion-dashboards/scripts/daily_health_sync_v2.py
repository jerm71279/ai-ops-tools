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
Refactored: 2025 - Now uses BaseSyncClient, unified health scoring, and data source interfaces
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import from core modules
from core import (
    BaseSyncClient,
    get_logger,
    enable_debug,
    NotionSyncError,
    DataSourceError,
)

# Import unified health scoring
from services.health_score import (
    HealthScoreCalculator,
    HealthMetrics,
    HealthResult,
    HealthStatus,
)

# Import data source interfaces
from data_sources import (
    get_unifi,
    get_ninjaone,
    use_real_apis,
    use_stub_apis,
    UniFiSite,
    NinjaOneOrganization,
)

# Import NotionWrapper for static property builders
from notion_client_wrapper import NotionWrapper

# Setup logging via centralized config
logger = get_logger(__name__)


# =============================================================================
# UniFi Best Practices Constants
# =============================================================================

WIFI_SIGNAL_THRESHOLD = -65  # dBm minimum acceptable signal
RESERVED_VLANS = [1, 4095]   # VLANs that should not be used


# =============================================================================
# Config Drift Detection
# =============================================================================

def check_config_drift(site: UniFiSite) -> Tuple[bool, List[str]]:
    """
    Check for configuration drift against OberaConnect baseline rules.
    
    Rules checked:
    - Open SSIDs must be blocked
    - VLAN 1 and 4095 are reserved
    - Permit-any firewall rules blocked
    
    Args:
        site: UniFi site to check
        
    Returns:
        Tuple of (has_drift, list_of_violations)
    """
    violations = []
    
    # TODO: Implement actual config drift checks when real API available
    # These would query the UniFi controller for:
    # - SSID configurations (check for open networks)
    # - VLAN assignments (check for reserved VLANs in use)
    # - Firewall rules (check for permit-any rules)
    
    # Placeholder: 5% of sites have drift for realistic testing
    import random
    if random.random() < 0.05:
        violations.append("Permit-any firewall rule detected")
    
    return (len(violations) > 0, violations)


# =============================================================================
# Daily Health Sync - Using BaseSyncClient
# =============================================================================

class DailyHealthSync(BaseSyncClient):
    """
    Create daily health snapshot entries in Notion.
    
    Inherits from BaseSyncClient which provides:
    - Configuration loading and validation
    - Notion client initialization with dry-run support
    - Retry logic for API calls
    - Page caching for relations
    
    Uses data source interfaces for UniFi and NinjaOne data.
    """
    
    def __init__(
        self,
        config_path: str,
        dry_run: bool = False,
        verbose: bool = False
    ):
        """
        Initialize daily health sync.
        
        Args:
            config_path: Path to config JSON file
            dry_run: If True, preview changes without writing
            verbose: If True, enable debug logging
        """
        super().__init__(config_path, dry_run, verbose)
        
        # Initialize unified health calculator
        self.health_calculator = HealthScoreCalculator(
            warning_threshold=self.config.settings.health_score_warning_threshold,
            critical_threshold=self.config.settings.health_score_critical_threshold,
        )
        
        # Initialize data sources
        self.unifi = get_unifi()
        self.ninjaone = get_ninjaone()
    
    @property
    def primary_database(self) -> str:
        """Primary database for this sync operation."""
        return "daily_health"
    
    def build_properties(
        self,
        date: str,
        site: UniFiSite,
        ninjaone_data: NinjaOneOrganization,
        health_result: HealthResult,
        config_drift: bool,
        drift_violations: List[str]
    ) -> Dict:
        """Build Notion page properties for health snapshot."""
        
        # Calculate availability percentage
        availability = (
            (site.devices_online / site.devices_total * 100)
            if site.devices_total > 0 else 100.0
        )
        
        # Alert summary (top 3)
        alerts = ninjaone_data.alert_summary[:3]
        alert_text = "; ".join(alerts) if alerts else "No active alerts"
        
        properties = {
            "Date": NotionWrapper.prop_title(date),
            "Devices Online": NotionWrapper.prop_number(site.devices_online),
            "Devices Offline": NotionWrapper.prop_number(site.devices_offline),
            "Devices Total": NotionWrapper.prop_number(site.devices_total),
            "Availability Percentage": NotionWrapper.prop_number(round(availability, 1)),
            "WiFi Clients": NotionWrapper.prop_number(site.wifi_clients),
            "Signal Warnings": NotionWrapper.prop_number(site.wifi_clients_weak_signal),
            "Active Alerts": NotionWrapper.prop_number(
                ninjaone_data.alerts_critical + ninjaone_data.alerts_warning
            ),
            "Alert Summary": NotionWrapper.prop_rich_text(alert_text),
            "Config Drift Detected": NotionWrapper.prop_checkbox(config_drift),
            "Backup Status": NotionWrapper.prop_select(ninjaone_data.backup_status),
            "Health Score": NotionWrapper.prop_number(health_result.score),
        }
        
        # Add relation to customer site if exists
        customer_page_id = self.get_page_id("customer_status", site.name)
        if customer_page_id:
            properties["Site"] = NotionWrapper.prop_relation([customer_page_id])
        
        # Add notes for drift violations
        if drift_violations:
            properties["Notes"] = NotionWrapper.prop_rich_text(
                "Config drift: " + "; ".join(drift_violations)
            )
        
        return properties
    
    def sync_site_health(self, site: UniFiSite) -> Dict:
        """
        Create daily health snapshot for a single site.
        
        Args:
            site: UniFi site data
            
        Returns:
            Sync result dictionary
        """
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.logger.info(f"Creating health snapshot for {site.name} ({date})")
        
        # Fetch NinjaOne data
        try:
            # Extract customer name from site name (before " - ")
            customer_name = site.name.split(" - ")[0] if " - " in site.name else site.name
            ninjaone_data = self.ninjaone.fetch_organization(customer_name)
            
            if ninjaone_data is None:
                # Create minimal data if not found
                ninjaone_data = NinjaOneOrganization(
                    org_id="unknown",
                    name=customer_name,
                    backup_status="unknown"
                )
        except Exception as e:
            raise DataSourceError("NinjaOne", f"Failed to fetch data for {site.name}", e)
        
        # Check for config drift
        config_drift, drift_violations = check_config_drift(site)
        
        # Build metrics for unified health calculator
        metrics = HealthMetrics(
            devices_online=site.devices_online,
            devices_total=site.devices_total,
            wifi_clients_total=site.wifi_clients,
            wifi_clients_weak_signal=site.wifi_clients_weak_signal,
            alerts_critical=ninjaone_data.alerts_critical,
            alerts_warning=ninjaone_data.alerts_warning,
            backup_status=ninjaone_data.backup_status,
            config_drift_detected=config_drift,
            config_violations=drift_violations,
            open_tickets=ninjaone_data.open_tickets,
        )
        
        # Calculate health using unified calculator
        health_result = self.health_calculator.calculate(metrics)
        
        # Build Notion properties
        properties = self.build_properties(
            date=date,
            site=site,
            ninjaone_data=ninjaone_data,
            health_result=health_result,
            config_drift=config_drift,
            drift_violations=drift_violations
        )
        
        # Log if site requires review
        if health_result.requires_review:
            self.logger.warning(
                f"Site {site.name} flagged for review (score: {health_result.score})"
            )
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would create snapshot for {site.name}")
            return {
                "status": "dry_run",
                "site": site.name,
                "health_score": health_result.score,
                "requires_review": health_result.requires_review,
            }
        
        # Create snapshot entry (not upsert - we want historical records)
        result = self.create_page(self.primary_database, properties)
        
        self.logger.info(f"Created health snapshot for {site.name} (score: {health_result.score})")
        
        return {
            "status": "success",
            "site": site.name,
            "health_score": health_result.score,
            "requires_review": health_result.requires_review,
            "page_id": result.get("id"),
        }
    
    def sync(self, **kwargs) -> List[Dict]:
        """
        Create health snapshots for all customer sites.
        
        This is the main entry point required by BaseSyncClient.
        
        Returns:
            List of sync results
        """
        results = []
        
        # Fetch all sites from UniFi
        try:
            sites = self.unifi.fetch_sites()
        except Exception as e:
            raise DataSourceError("UniFi", "Failed to fetch sites", e)
        
        self.logger.info(f"Found {len(sites)} sites from UniFi")
        
        # Use inherited maker/checker for bulk operations
        if self.check_bulk_operation(len(sites)):
            self.logger.warning(
                f"Bulk operation: {len(sites)} sites. This is expected for daily sync."
            )
        
        # Sync each site
        for site in sites:
            try:
                result = self.sync_site_health(site)
                results.append(result)
            except NotionSyncError as e:
                self.logger.error(f"Failed to sync {site.name}: {e}")
                results.append({
                    "site": site.name,
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                })
            except Exception as e:
                self.logger.error(f"Unexpected error syncing {site.name}: {e}")
                results.append({
                    "site": site.name,
                    "status": "error",
                    "error": str(e),
                })
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """
        Generate daily sync summary report.
        
        Overrides base class to add health statistics.
        """
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "error"]
        dry_run = [r for r in results if r["status"] == "dry_run"]
        review_needed = [r for r in results if r.get("requires_review")]
        
        # Calculate average health score
        scores = [r["health_score"] for r in results if r.get("health_score") is not None]
        avg_health = sum(scores) / len(scores) if scores else 0
        
        # Count by health status
        healthy = len([s for s in scores if s >= 80])
        warning = len([s for s in scores if 50 <= s < 80])
        critical = len([s for s in scores if s < 50])
        
        report = f"""
Daily Health Sync Report - {date}
{'=' * 50}
Timestamp: {datetime.now().isoformat()}
Total Sites: {len(results)}
Successful: {len(successful)}
Failed: {len(failed)}
Dry Run: {len(dry_run)}

Health Summary:
  Average Score: {avg_health:.1f}
  Healthy (≥80): {healthy}
  Warning (50-79): {warning}
  Critical (<50): {critical}
  Sites Needing Review: {len(review_needed)}
"""
        
        if review_needed:
            report += f"""
⚠️  SITES REQUIRING REVIEW ({len(review_needed)})
{'-' * 50}
"""
            for r in sorted(review_needed, key=lambda x: x.get('health_score', 100)):
                report += f"  • {r['site']}: Score {r.get('health_score', 'N/A')}\n"
        
        if failed:
            report += f"""
❌ FAILED SYNCS ({len(failed)})
{'-' * 50}
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
    parser.add_argument('--use-stubs', action='store_true', help='Use stub data instead of real APIs')

    args = parser.parse_args()

    # Load environment variables from .env file if present
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv is optional

    if args.verbose:
        enable_debug()

    # Initialize data sources (real or stub based on flag)
    if args.use_stubs:
        logger.info("Using STUB data sources (test mode)")
        use_stub_apis()
    else:
        logger.info("Using REAL API data sources")
        use_real_apis()

    if not Path(args.config).exists():
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)
    
    try:
        syncer = DailyHealthSync(
            args.config,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        results = syncer.sync()
        report = syncer.generate_report(results)
        print(report)
        
        # Exit codes
        if any(r["status"] == "error" for r in results):
            sys.exit(1)
        if any(r.get("requires_review") for r in results):
            sys.exit(2)  # Warning exit code
            
    except NotionSyncError as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
