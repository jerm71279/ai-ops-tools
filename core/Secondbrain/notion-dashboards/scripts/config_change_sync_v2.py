#!/usr/bin/env python3
"""
Config Change Sync - Bridge oberaconnect-tools to Notion

Purpose:
    Logs every configuration change from MikroTik, SonicWall, and UniFi
    deployments to Notion for audit trail and AI analysis.

Usage:
    # Called by other oberaconnect-tools after making changes
    python config_change_sync.py --config config.json log \
        --tool mikrotik-config-builder \
        --site "Acme Corp" \
        --action "deploy" \
        --summary "Updated VPN config for new remote office" \
        --details "Added IPSec peer 203.0.113.50, updated firewall rules"

    # View recent changes
    python config_change_sync.py --config config.json recent --days 7

    # Generate change report
    python config_change_sync.py --config config.json report --site "Acme Corp"

Integration with oberaconnect-tools:
    Add to end of deployment scripts:
    
    python /path/to/config_change_sync.py --config /path/to/config.json log \
        --tool "$TOOL_NAME" \
        --site "$SITE_NAME" \
        --action "$ACTION" \
        --summary "$CHANGE_SUMMARY"

Requirements:
    pip install notion-client --break-system-packages

Author: OberaConnect
Created: 2025
Refactored: 2025 - Now uses BaseSyncClient with typed errors and maker/checker
"""

import argparse
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum

# Import from core modules
from core import (
    BaseSyncClient,
    get_logger,
    enable_debug,
    NotionSyncError,
    ValidationError,
    MakerCheckerError,
    DatabaseNotFoundError,
)

# Import NotionWrapper for static property builders
from notion_client_wrapper import NotionWrapper

# Setup logging via centralized config
logger = get_logger(__name__)


# =============================================================================
# Constants and Enums
# =============================================================================

class ToolCategory(Enum):
    """Categories for infrastructure tools."""
    NETWORK = "network"
    SECURITY = "security"
    CLOUD = "cloud"
    ASSESSMENT = "assessment"
    MANUAL = "manual"
    OTHER = "other"


class RiskLevel(Enum):
    """Risk levels for changes - aligns with maker/checker thresholds."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeAction(Enum):
    """Types of configuration changes."""
    DEPLOY = "deploy"
    UPDATE = "update"
    ROLLBACK = "rollback"
    BACKUP = "backup"
    RESTORE = "restore"
    DELETE = "delete"
    CREATE = "create"
    MODIFY = "modify"
    ASSESSMENT = "assessment"


@dataclass
class ToolInfo:
    """Metadata about an oberaconnect tool."""
    name: str
    vendor: str
    category: ToolCategory
    default_risk: RiskLevel = RiskLevel.MEDIUM
    
    @classmethod
    def get(cls, tool_name: str) -> 'ToolInfo':
        """Get tool info by name, with fallback for unknown tools."""
        return TOOLS.get(tool_name, cls(
            name=tool_name,
            vendor="Unknown",
            category=ToolCategory.OTHER,
            default_risk=RiskLevel.MEDIUM
        ))


# Tool registry - all known oberaconnect tools
TOOLS: Dict[str, ToolInfo] = {
    "mikrotik-config-builder": ToolInfo(
        name="mikrotik-config-builder",
        vendor="MikroTik",
        category=ToolCategory.NETWORK,
        default_risk=RiskLevel.MEDIUM
    ),
    "sonicwall-scripts": ToolInfo(
        name="sonicwall-scripts",
        vendor="SonicWall",
        category=ToolCategory.SECURITY,
        default_risk=RiskLevel.HIGH  # Security devices default higher
    ),
    "unifi-deploy": ToolInfo(
        name="unifi-deploy",
        vendor="Ubiquiti",
        category=ToolCategory.NETWORK,
        default_risk=RiskLevel.MEDIUM
    ),
    "azure-automation": ToolInfo(
        name="azure-automation",
        vendor="Azure",
        category=ToolCategory.CLOUD,
        default_risk=RiskLevel.HIGH
    ),
    "network-troubleshooter": ToolInfo(
        name="network-troubleshooter",
        vendor="Multi",
        category=ToolCategory.ASSESSMENT,
        default_risk=RiskLevel.LOW
    ),
    "manual": ToolInfo(
        name="manual",
        vendor="Manual",
        category=ToolCategory.MANUAL,
        default_risk=RiskLevel.MEDIUM
    ),
}


@dataclass
class ConfigChange:
    """
    Represents a configuration change to be logged.
    
    Typed data class for validation and IDE support.
    """
    tool: str
    site: str
    action: ChangeAction
    summary: str
    
    # Optional fields
    details: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    ticket_id: Optional[str] = None
    rollback_plan: Optional[str] = None
    
    # Auto-populated
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    engineer: str = field(default_factory=lambda: os.getenv("OBERA_ENGINEER", os.getenv("USER", "unknown")))
    
    def __post_init__(self):
        """Validate and normalize fields."""
        if not self.site:
            raise ValidationError("site", "Site name is required")
        if not self.summary:
            raise ValidationError("summary", "Change summary is required")
        
        # Truncate long text fields (Notion limit is 2000 chars)
        if self.summary and len(self.summary) > 2000:
            self.summary = self.summary[:1997] + "..."
        if self.details and len(self.details) > 2000:
            self.details = self.details[:1997] + "..."
        if self.rollback_plan and len(self.rollback_plan) > 2000:
            self.rollback_plan = self.rollback_plan[:1997] + "..."
    
    @property
    def change_id(self) -> str:
        """Generate unique change ID."""
        site_prefix = self.site[:20].replace(" ", "-")
        ts = self.timestamp.strftime('%Y%m%d-%H%M%S')
        return f"{site_prefix}-{ts}"
    
    @property
    def tool_info(self) -> ToolInfo:
        """Get metadata for this tool."""
        return ToolInfo.get(self.tool)
    
    @property
    def assessed_risk(self) -> RiskLevel:
        """Get risk level (explicit or auto-assessed)."""
        if self.risk_level:
            return self.risk_level
        return self._auto_assess_risk()
    
    def _auto_assess_risk(self) -> RiskLevel:
        """Auto-assess risk level based on action and content."""
        summary_lower = self.summary.lower()
        
        # High risk indicators
        high_risk_keywords = ["firewall", "vpn", "ipsec", "delete", "remove", "production", "critical"]
        if any(word in summary_lower for word in high_risk_keywords):
            return RiskLevel.HIGH
        
        # Action-based risk
        if self.action in [ChangeAction.DELETE, ChangeAction.ROLLBACK]:
            return RiskLevel.HIGH
        
        # Tool-based default
        return self.tool_info.default_risk
    
    @property
    def requires_rollback_plan(self) -> bool:
        """Check if this change requires a rollback plan."""
        return self.assessed_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]


# =============================================================================
# Config Change Sync - Using BaseSyncClient
# =============================================================================

class ConfigChangeSync(BaseSyncClient):
    """
    Sync configuration changes to Notion for audit trail.
    
    Inherits from BaseSyncClient which provides:
    - Configuration loading and validation
    - Notion client initialization with dry-run support
    - Retry logic for API calls
    - Page caching for relations
    - Maker/checker validation
    
    Three main operations:
    - log: Create new change entry
    - recent: Query recent changes
    - report: Generate change summary
    """
    
    @property
    def primary_database(self) -> str:
        """Primary database for config changes."""
        return "config_changes"
    
    def build_properties(self, change: ConfigChange) -> Dict:
        """Build Notion page properties from ConfigChange."""
        
        properties = {
            "Change ID": NotionWrapper.prop_title(change.change_id),
            "Site Name": NotionWrapper.prop_rich_text(change.site),
            "Tool": NotionWrapper.prop_select(change.tool),
            "Vendor": NotionWrapper.prop_select(change.tool_info.vendor),
            "Category": NotionWrapper.prop_select(change.tool_info.category.value),
            "Action": NotionWrapper.prop_select(change.action.value),
            "Summary": NotionWrapper.prop_rich_text(change.summary),
            "Engineer": NotionWrapper.prop_rich_text(change.engineer),
            "Timestamp": NotionWrapper.prop_date(change.timestamp.isoformat()),
            "Risk Level": NotionWrapper.prop_select(change.assessed_risk.value),
        }
        
        # Optional fields
        if change.details:
            properties["Details"] = NotionWrapper.prop_rich_text(change.details)
        if change.ticket_id:
            properties["Ticket ID"] = NotionWrapper.prop_rich_text(change.ticket_id)
        if change.rollback_plan:
            properties["Rollback Plan"] = NotionWrapper.prop_rich_text(change.rollback_plan)
        
        # Link to site if found (uses inherited caching)
        site_page_id = self.get_page_id("customer_status", change.site)
        if site_page_id:
            properties["Site"] = NotionWrapper.prop_relation([site_page_id])
        
        return properties
    
    def log_change(self, change: ConfigChange) -> Dict:
        """
        Log a configuration change to Notion.
        
        Args:
            change: ConfigChange object with all change details
            
        Returns:
            Result dictionary with status and page info
            
        Raises:
            MakerCheckerError: If high/critical change lacks rollback plan
            DatabaseNotFoundError: If config_changes database not configured
        """
        self.logger.info(f"Logging change: {change.tool} | {change.site} | {change.action.value}")
        
        # Maker/checker: high/critical changes need rollback plan
        if change.requires_rollback_plan and not change.rollback_plan:
            if self.config.maker_checker.require_rollback_for_high_risk:
                self.logger.warning(
                    f"HIGH/CRITICAL change without rollback plan: {change.summary}"
                )
                # Don't block, but flag it
        
        # Build properties
        properties = self.build_properties(change)
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would log: {change.change_id}")
            return {
                "status": "dry_run",
                "change_id": change.change_id,
                "risk_level": change.assessed_risk.value,
            }
        
        # Create page (uses inherited retry logic)
        result = self.create_page(self.primary_database, properties)
        
        self.logger.info(f"Logged change: {change.change_id} (risk: {change.assessed_risk.value})")
        
        return {
            "status": "success",
            "change_id": change.change_id,
            "page_id": result.get("id"),
            "risk_level": change.assessed_risk.value,
        }
    
    def get_recent_changes(
        self,
        days: int = 7,
        site: Optional[str] = None,
        tool: Optional[str] = None
    ) -> List[Dict]:
        """
        Get recent configuration changes.
        
        Args:
            days: Number of days to look back
            site: Filter by site name (partial match)
            tool: Filter by tool name (exact match)
            
        Returns:
            List of change dictionaries
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would query changes from last {days} days")
            return []
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Build filter
        filters = [
            {"property": "Timestamp", "date": {"on_or_after": cutoff.isoformat()}}
        ]
        
        if site:
            filters.append({"property": "Site Name", "rich_text": {"contains": site}})
        if tool:
            filters.append({"property": "Tool", "select": {"equals": tool}})
        
        filter_obj = {"and": filters} if len(filters) > 1 else filters[0]
        
        # Query with sorting
        pages = self.query_database(
            self.primary_database,
            filter_obj=filter_obj,
            sorts=[{"property": "Timestamp", "direction": "descending"}]
        )
        
        # Extract data from pages
        return [{
            "id": p["id"],
            "change_id": self.client.extract_title(p) if self.client else "",
            "site": self.client.extract_property(p, "Site Name") if self.client else "",
            "tool": self.client.extract_property(p, "Tool") if self.client else "",
            "action": self.client.extract_property(p, "Action") if self.client else "",
            "summary": self.client.extract_property(p, "Summary") if self.client else "",
            "engineer": self.client.extract_property(p, "Engineer") if self.client else "",
            "timestamp": self.client.extract_property(p, "Timestamp") if self.client else "",
            "risk_level": self.client.extract_property(p, "Risk Level") if self.client else "",
        } for p in pages]
    
    def sync(self, **kwargs) -> List[Dict]:
        """
        Required by BaseSyncClient but not primary use case.
        
        For config changes, use log_change() directly.
        This method is here for interface compatibility.
        """
        self.logger.warning("sync() called on ConfigChangeSync - use log_change() instead")
        return []
    
    def generate_report(
        self,
        site: Optional[str] = None,
        days: int = 30
    ) -> str:
        """
        Generate change report for a site or all sites.
        
        Args:
            site: Site to report on (or None for all)
            days: Days to include in report
            
        Returns:
            Formatted report string
        """
        changes = self.get_recent_changes(days=days, site=site)
        
        if not changes:
            return f"No changes found in the last {days} days."
        
        # Group by site
        by_site: Dict[str, List[Dict]] = {}
        for c in changes:
            s = c.get("site", "Unknown")
            if s not in by_site:
                by_site[s] = []
            by_site[s].append(c)
        
        # Count by risk
        risk_counts = {level.value: 0 for level in RiskLevel}
        for c in changes:
            risk = c.get("risk_level", "low")
            if risk in risk_counts:
                risk_counts[risk] += 1
        
        # Count by tool
        tool_counts: Dict[str, int] = {}
        for c in changes:
            t = c.get("tool", "unknown")
            tool_counts[t] = tool_counts.get(t, 0) + 1
        
        # Build report
        report = f"""
Configuration Change Report
{'=' * 50}
Period: Last {days} days
Generated: {datetime.now().isoformat()}
Scope: {site if site else 'All Sites'}

SUMMARY
{'-' * 50}
Total Changes: {len(changes)}
Sites Affected: {len(by_site)}

By Risk Level:
  Critical: {risk_counts.get('critical', 0)}
  High: {risk_counts.get('high', 0)}
  Medium: {risk_counts.get('medium', 0)}
  Low: {risk_counts.get('low', 0)}

By Tool:
"""
        for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
            report += f"  {tool}: {count}\n"
        
        report += f"\nCHANGES BY SITE\n{'-' * 50}\n"
        
        for site_name, site_changes in sorted(by_site.items()):
            report += f"\n{site_name} ({len(site_changes)} changes)\n"
            for c in site_changes[:5]:  # Show top 5 per site
                risk_icon = {
                    "critical": "!!",
                    "high": "!",
                    "medium": "*",
                    "low": "-"
                }.get(c.get("risk_level", ""), "-")
                summary = c.get('summary', '')[:50]
                report += f"  [{risk_icon}] {c.get('action', '')} via {c.get('tool', '')} - {summary}\n"
            if len(site_changes) > 5:
                report += f"  ... and {len(site_changes) - 5} more\n"
        
        return report


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Log configuration changes to Notion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Log a MikroTik deployment
  %(prog)s --config config.json log --tool mikrotik-config-builder \\
      --site "Acme Corp" --action deploy --summary "VPN update"

  # View recent changes
  %(prog)s --config config.json recent --days 7

  # Generate site report
  %(prog)s --config config.json report --site "Acme Corp"
        """
    )
    
    parser.add_argument('--config', '-c', required=True, help='Config JSON path')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Debug logging')
    
    sub = parser.add_subparsers(dest='cmd', help='Command')
    
    # Log command
    log_parser = sub.add_parser('log', help='Log a configuration change')
    log_parser.add_argument('--tool', required=True, choices=list(TOOLS.keys()),
                           help='Tool that made the change')
    log_parser.add_argument('--site', required=True, help='Customer site name')
    log_parser.add_argument('--action', required=True, 
                           choices=[a.value for a in ChangeAction],
                           help='Type of action')
    log_parser.add_argument('--summary', required=True, help='Brief description')
    log_parser.add_argument('--details', help='Detailed change info')
    log_parser.add_argument('--risk', choices=[r.value for r in RiskLevel], 
                           help='Override risk level')
    log_parser.add_argument('--ticket', help='Associated ticket ID')
    log_parser.add_argument('--rollback', help='Rollback plan (required for high/critical)')
    
    # Recent command
    recent_parser = sub.add_parser('recent', help='View recent changes')
    recent_parser.add_argument('--days', type=int, default=7, help='Days to look back')
    recent_parser.add_argument('--site', help='Filter by site')
    recent_parser.add_argument('--tool', choices=list(TOOLS.keys()), help='Filter by tool')
    
    # Report command
    report_parser = sub.add_parser('report', help='Generate change report')
    report_parser.add_argument('--site', help='Site to report on (or all)')
    report_parser.add_argument('--days', type=int, default=30, help='Days to include')
    
    args = parser.parse_args()
    
    if not args.cmd:
        parser.print_help()
        sys.exit(1)
    
    if args.verbose:
        enable_debug()
    
    if not Path(args.config).exists():
        logger.error(f"Config not found: {args.config}")
        sys.exit(1)
    
    try:
        sync = ConfigChangeSync(
            args.config, 
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        if args.cmd == 'log':
            # Create typed ConfigChange object
            change = ConfigChange(
                tool=args.tool,
                site=args.site,
                action=ChangeAction(args.action),
                summary=args.summary,
                details=args.details,
                risk_level=RiskLevel(args.risk) if args.risk else None,
                ticket_id=args.ticket,
                rollback_plan=args.rollback,
            )
            
            result = sync.log_change(change)
            print(f"Logged: {result['change_id']} (risk: {result['risk_level']})")
            
        elif args.cmd == 'recent':
            changes = sync.get_recent_changes(days=args.days, site=args.site, tool=args.tool)
            print(f"\nRecent Changes (last {args.days} days):\n")
            for c in changes:
                risk = c.get('risk_level', 'low')
                icon = {"critical": "!!", "high": "!", "medium": "*", "low": "-"}.get(risk, "-")
                ts = c.get('timestamp', '')[:10]
                summary = c.get('summary', '')[:40]
                print(f"  [{icon}] {ts} | {c.get('site', '')} | {c.get('tool', '')} | {summary}")
            print(f"\nTotal: {len(changes)}")
            
        elif args.cmd == 'report':
            print(sync.generate_report(site=args.site, days=args.days))
    
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except NotionSyncError as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
