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
    python customer_status_sync.py --config config.json --use-stubs  # For testing

Requirements:
    pip install notion-client httpx --break-system-packages

Environment Variables (for real API mode):
    UNIFI_API_KEY - UniFi Site Manager API key
    NINJAONE_CLIENT_ID - NinjaOne OAuth client ID
    NINJAONE_CLIENT_SECRET - NinjaOne OAuth client secret

Author: OberaConnect
Created: 2025
Refactored: 2025 - Now uses BaseSyncClient and unified health scoring
Updated: 2026-01-01 - Real API integration via MCP data sources
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

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
    HealthStatus,
)

# Import NotionWrapper for static property builders
from notion_client_wrapper import NotionWrapper

# Import data sources - real and stub implementations
from data_sources import (
    get_unifi,
    get_ninjaone,
    use_real_apis,
    use_stub_apis,
    UniFiSite,
)

# Setup logging via centralized config
logger = get_logger(__name__)

# Global flag for API mode
_use_real_apis = True


# =============================================================================
# Data Collection - Real API Integration via MCP Data Sources
# =============================================================================

def initialize_data_sources(use_stubs: bool = False) -> None:
    """
    Initialize data sources based on mode.

    Args:
        use_stubs: If True, use stub data for testing. If False, use real APIs.
    """
    global _use_real_apis
    _use_real_apis = not use_stubs

    if use_stubs:
        logger.info("Using STUB data sources (test mode)")
        use_stub_apis()
    else:
        logger.info("Using REAL API data sources")
        use_real_apis()


def fetch_unifi_sites() -> List[Dict]:
    """
    Fetch site data from UniFi Site Manager API.

    Returns:
        List of site dictionaries with device counts and status
    """
    try:
        unifi = get_unifi()
        sites = unifi.fetch_sites()

        # Convert UniFiSite objects to dictionaries
        return [
            {
                "site_id": site.site_id,
                "name": site.name,
                "state": site.state,
                "devices_online": site.devices_online,
                "devices_offline": site.devices_offline,
                "devices_total": site.devices_total,
                "wifi_clients": site.wifi_clients,
                "signal_warnings": site.wifi_clients_weak_signal,
                "last_seen": site.last_seen.isoformat() if site.last_seen else None,
                "has_mikrotik": site.has_mikrotik,
                "has_sonicwall": site.has_sonicwall,
                "has_azure": site.has_azure,
                "contract_renewal": site.contract_renewal,
                "primary_contact": site.primary_contact,
                "wan_ip": site.wan_ip,
                "isp": site.isp,
            }
            for site in sites
        ]
    except Exception as e:
        logger.error(f"Failed to fetch UniFi sites: {e}")
        raise DataSourceError(f"UniFi API error: {e}")


def fetch_ninjaone_data(site_name: str) -> Dict:
    """
    Fetch monitoring data from NinjaOne RMM.

    Args:
        site_name: Customer site name to match

    Returns:
        Dictionary with tickets, alerts, backup status
    """
    try:
        ninja = get_ninjaone()
        org = ninja.fetch_organization(site_name)

        if org:
            backup = ninja.fetch_backup_status(site_name)
            return {
                "open_tickets": org.open_tickets,
                "active_alerts": org.alerts_critical + org.alerts_warning,
                "critical_alerts": org.alerts_critical,
                "warning_alerts": org.alerts_warning,
                "backup_status": backup.status,
                "device_count": org.device_count,
                "online_devices": org.online_devices,
                "offline_devices": org.offline_devices,
            }

        # Organization not found - return defaults
        return {
            "open_tickets": 0,
            "active_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "backup_status": "unknown",
            "device_count": 0,
            "online_devices": 0,
            "offline_devices": 0,
        }
    except Exception as e:
        logger.warning(f"Failed to fetch NinjaOne data for {site_name}: {e}")
        return {
            "open_tickets": 0,
            "active_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "backup_status": "unknown",
            "device_count": 0,
            "online_devices": 0,
            "offline_devices": 0,
        }


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
# Customer Status Sync - Using BaseSyncClient
# =============================================================================

class CustomerStatusSync(BaseSyncClient):
    """
    Sync customer site data to Notion database.
    
    Inherits from BaseSyncClient which provides:
    - Configuration loading and validation
    - Notion client initialization with dry-run support
    - Retry logic for API calls
    - Page caching for relations
    - Maker/checker validation
    
    Example:
        syncer = CustomerStatusSync("config.json", dry_run=True)
        results = syncer.sync(filter_site="Acme")
        print(syncer.generate_report(results))
    """
    
    def __init__(
        self,
        config_path: str,
        dry_run: bool = False,
        verbose: bool = False
    ):
        """
        Initialize customer status sync.
        
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
    
    @property
    def primary_database(self) -> str:
        """Primary database for this sync operation."""
        return "customer_status"
    
    def build_properties(self, site_data: Dict, ninjaone_data: Dict) -> Dict:
        """
        Build Notion page properties from collected data.
        
        Uses unified health scoring from services.health_score.
        """
        # Build metrics for unified health calculator
        metrics = HealthMetrics(
            devices_online=site_data.get("devices_online", 0),
            devices_total=site_data.get("devices_total", 0),
            wifi_clients_total=site_data.get("wifi_clients", 0),
            wifi_clients_weak_signal=site_data.get("signal_warnings", 0),
            alerts_critical=ninjaone_data.get("critical_alerts", 0),
            alerts_warning=ninjaone_data.get("warning_alerts", ninjaone_data.get("active_alerts", 0)),
            backup_status=ninjaone_data.get("backup_status", "unknown"),
            open_tickets=ninjaone_data.get("open_tickets", 0),
        )
        
        # Calculate health using unified calculator
        health_result = self.health_calculator.calculate(metrics)
        stack = determine_stack_type(site_data)
        
        # Determine deployment status from health status enum
        status_map = {
            HealthStatus.HEALTHY: "active",
            HealthStatus.WARNING: "maintenance",
            HealthStatus.CRITICAL: "needs attention",
        }
        status = status_map.get(health_result.status, "maintenance")
        
        # Handle empty state - use "Alabama" as default if state is empty/None
        state = site_data.get("state") or "Alabama"

        properties = {
            "Site Name": NotionWrapper.prop_title(site_data["name"]),
            "Customer ID": NotionWrapper.prop_rich_text(site_data.get("site_id", "")),
            "State": NotionWrapper.prop_select(state),
            "Device Count": NotionWrapper.prop_number(site_data.get("devices_total", 0)),
            "Stack Type": NotionWrapper.prop_multi_select(stack),
            "Deployment Status": NotionWrapper.prop_select(status),
            "Health Score": NotionWrapper.prop_number(health_result.score),
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
        
        return properties, health_result
    
    def sync_site(self, site_data: Dict) -> Dict:
        """
        Sync a single site to Notion.
        
        Creates new page or updates existing based on site name match.
        Uses inherited upsert_page with retry logic.
        """
        site_name = site_data["name"]
        self.logger.info(f"Syncing site: {site_name}")
        
        # Fetch additional data from NinjaOne
        try:
            ninjaone_data = fetch_ninjaone_data(site_name)
        except Exception as e:
            raise DataSourceError("NinjaOne", f"Failed to fetch data for {site_name}", e)
        
        # Build properties using unified health scoring
        properties, health_result = self.build_properties(site_data, ninjaone_data)
        
        # Log if site requires review
        if health_result.requires_review:
            self.logger.warning(
                f"Site {site_name} requires review: {', '.join(health_result.review_reasons)}"
            )
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would sync: {site_name} (score: {health_result.score})")
            return {
                "status": "dry_run",
                "site": site_name,
                "health_score": health_result.score,
                "requires_review": health_result.requires_review,
            }
        
        # Use inherited upsert_page (includes retry logic)
        result, action = self.upsert_page(
            self.primary_database,
            site_name,
            properties
        )
        
        self.logger.info(f"{action.capitalize()} page for: {site_name} (score: {health_result.score})")
        return {
            "status": "success",
            "action": action,
            "page": result,
            "health_score": health_result.score,
            "requires_review": health_result.requires_review,
        }
    
    def sync(self, filter_site: Optional[str] = None) -> List[Dict]:
        """
        Sync all sites (or filtered site) to Notion.
        
        This is the main entry point required by BaseSyncClient.
        
        Args:
            filter_site: Optional site name to sync only matching sites
        
        Returns:
            List of sync results
        """
        results = []
        
        # Fetch site data from UniFi
        try:
            sites = fetch_unifi_sites()
        except Exception as e:
            raise DataSourceError("UniFi", "Failed to fetch sites", e)
        
        self.logger.info(f"Found {len(sites)} sites from UniFi")
        
        # Filter if specified
        if filter_site:
            sites = [s for s in sites if filter_site.lower() in s["name"].lower()]
            self.logger.info(f"Filtered to {len(sites)} sites matching '{filter_site}'")
        
        # Use inherited maker/checker for bulk operations
        if self.check_bulk_operation(len(sites)):
            self.logger.warning(
                f"Bulk operation: {len(sites)} sites exceeds threshold. "
                "Consider --dry-run first."
            )
        
        # Sync each site
        for site in sites:
            try:
                result = self.sync_site(site)
                results.append({
                    "site": site["name"],
                    "status": result.get("status", "success"),
                    "action": result.get("action"),
                    "health_score": result.get("health_score"),
                    "requires_review": result.get("requires_review", False),
                })
            except NotionSyncError as e:
                self.logger.error(f"Failed to sync {site['name']}: {e}")
                results.append({
                    "site": site["name"],
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                })
            except Exception as e:
                self.logger.error(f"Unexpected error syncing {site['name']}: {e}")
                results.append({
                    "site": site["name"],
                    "status": "error",
                    "error": str(e),
                })
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """
        Generate sync summary report.
        
        Overrides base class to add health score statistics.
        """
        successful = [r for r in results if r["status"] == "success"]
        created = len([r for r in results if r.get("action") == "created"])
        updated = len([r for r in results if r.get("action") == "updated"])
        failed = [r for r in results if r["status"] == "error"]
        dry_run = [r for r in results if r["status"] == "dry_run"]
        review_needed = [r for r in results if r.get("requires_review")]
        
        # Calculate average health score
        scores = [r["health_score"] for r in results if r.get("health_score") is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        report = f"""
Customer Status Sync Report
{'=' * 50}
Timestamp: {datetime.now().isoformat()}
Total Sites: {len(results)}
Successful: {len(successful)} (Created: {created}, Updated: {updated})
Failed: {len(failed)}
Dry Run: {len(dry_run)}

Health Summary:
  Average Score: {avg_score:.1f}
  Sites Needing Review: {len(review_needed)}
"""
        
        if review_needed:
            report += f"""
⚠️  SITES REQUIRING REVIEW
{'-' * 50}
"""
            for r in review_needed:
                report += f"  • {r['site']}: Score {r.get('health_score', 'N/A')}\n"
        
        report += f"""
Details:
{'-' * 50}
"""
        for r in results:
            if r["status"] == "success":
                icon = "✓"
                detail = f"{r.get('action', 'synced')} (score: {r.get('health_score', 'N/A')})"
            elif r["status"] == "error":
                icon = "✗"
                detail = f"error: {r.get('error_type', 'Unknown')}"
            else:
                icon = "○"
                detail = f"dry run (score: {r.get('health_score', 'N/A')})"
            
            report += f"  {icon} {r['site']}: {detail}\n"
            if r.get("error"):
                report += f"      → {r['error']}\n"
        
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

    parser.add_argument(
        '--use-stubs',
        action='store_true',
        help='Use stub data instead of real APIs (for testing)'
    )

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
    initialize_data_sources(use_stubs=args.use_stubs)

    if not Path(args.config).exists():
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)

    try:
        # Initialize sync using new pattern
        syncer = CustomerStatusSync(
            args.config,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        # Run sync (uses inherited retry, caching, etc.)
        results = syncer.sync(filter_site=args.site)
        
        # Generate and print report
        report = syncer.generate_report(results)
        print(report)
        
        # Exit codes
        if any(r["status"] == "error" for r in results):
            sys.exit(1)
        if any(r.get("requires_review") for r in results):
            sys.exit(2)  # Warning exit code
            
    except NotionSyncError as e:
        logger.error(f"Sync failed: {e}")
        if e.details:
            logger.debug(f"Error details: {e.details}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
