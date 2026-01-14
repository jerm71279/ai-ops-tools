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
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from notion_client_wrapper import NotionWrapper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tool categories for classification
TOOLS = {
    "mikrotik-config-builder": {"vendor": "MikroTik", "category": "network"},
    "sonicwall-scripts": {"vendor": "SonicWall", "category": "security"},
    "unifi-deploy": {"vendor": "Ubiquiti", "category": "network"},
    "azure-automation": {"vendor": "Azure", "category": "cloud"},
    "network-troubleshooter": {"vendor": "Multi", "category": "assessment"},
    "manual": {"vendor": "Manual", "category": "manual"},
}

ACTIONS = ["deploy", "update", "rollback", "backup", "restore", "delete", "create", "modify", "assessment"]
RISK_LEVELS = ["low", "medium", "high", "critical"]


class ConfigChangeSync:
    """Sync configuration changes to Notion for audit trail."""
    
    def __init__(self, config_path: str, dry_run: bool = False):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.dry_run = dry_run
        self.client = None if dry_run else NotionWrapper(token=self.config.get("notion_token"))
        
        # Database IDs
        self.changes_db = self.config["databases"].get("config_changes")
        self.deployments_db = self.config["databases"].get("deployments")
        self.sites_db = self.config["databases"].get("customer_status")
        
        self._site_cache = {}
    
    def _get_site_page_id(self, site_name: str) -> Optional[str]:
        """Get Notion page ID for a customer site."""
        if self.dry_run or not self.sites_db:
            return None
        
        if site_name not in self._site_cache:
            page = self.client.find_page_by_title(self.sites_db, site_name)
            self._site_cache[site_name] = page["id"] if page else None
        return self._site_cache[site_name]
    
    def _get_engineer_name(self) -> str:
        """Get current engineer name from environment or system."""
        return os.getenv("OBERA_ENGINEER", os.getenv("USER", "unknown"))
    
    def _assess_risk_level(self, action: str, tool: str, summary: str) -> str:
        """Assess risk level of change based on action and content."""
        summary_lower = summary.lower()
        
        # High risk indicators
        if any(word in summary_lower for word in ["firewall", "vpn", "ipsec", "delete", "remove", "production"]):
            return "high"
        if action in ["delete", "rollback"]:
            return "high"
        if "sonicwall" in tool.lower():
            return "medium"  # Security devices default higher
        if action in ["deploy", "modify"]:
            return "medium"
        return "low"
    
    def log_change(
        self,
        tool: str,
        site: str,
        action: str,
        summary: str,
        details: Optional[str] = None,
        risk_level: Optional[str] = None,
        ticket_id: Optional[str] = None,
        rollback_plan: Optional[str] = None
    ) -> Dict:
        """
        Log a configuration change to Notion.
        
        Args:
            tool: Name of the oberaconnect-tool used
            site: Customer site name
            action: Type of action (deploy, update, rollback, etc.)
            summary: Brief description of change
            details: Detailed change information
            risk_level: Override auto-assessed risk level
            ticket_id: Associated ticket number
            rollback_plan: How to undo this change
        """
        timestamp = datetime.now(timezone.utc)
        engineer = self._get_engineer_name()
        
        # Get tool metadata
        tool_info = TOOLS.get(tool, {"vendor": "Unknown", "category": "other"})
        
        # Assess risk if not provided
        if not risk_level:
            risk_level = self._assess_risk_level(action, tool, summary)
        
        # Maker/checker: high/critical changes need rollback plan
        if risk_level in ["high", "critical"] and not rollback_plan:
            logger.warning(f"HIGH/CRITICAL change without rollback plan: {summary}")
        
        properties = {
            "Change ID": NotionWrapper.prop_title(
                f"{site[:20]}-{timestamp.strftime('%Y%m%d-%H%M%S')}"
            ),
            "Site Name": NotionWrapper.prop_rich_text(site),
            "Tool": NotionWrapper.prop_select(tool),
            "Vendor": NotionWrapper.prop_select(tool_info["vendor"]),
            "Category": NotionWrapper.prop_select(tool_info["category"]),
            "Action": NotionWrapper.prop_select(action),
            "Summary": NotionWrapper.prop_rich_text(summary[:2000]),
            "Engineer": NotionWrapper.prop_rich_text(engineer),
            "Timestamp": NotionWrapper.prop_date(timestamp.isoformat()),
            "Risk Level": NotionWrapper.prop_select(risk_level),
        }
        
        # Optional fields
        if details:
            properties["Details"] = NotionWrapper.prop_rich_text(details[:2000])
        if ticket_id:
            properties["Ticket ID"] = NotionWrapper.prop_rich_text(ticket_id)
        if rollback_plan:
            properties["Rollback Plan"] = NotionWrapper.prop_rich_text(rollback_plan[:2000])
        
        # Link to site if found
        site_page_id = self._get_site_page_id(site)
        if site_page_id:
            properties["Site"] = NotionWrapper.prop_relation([site_page_id])
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would log: {tool} | {site} | {action} | {summary}")
            return {"status": "dry_run", "properties": properties}
        
        # Write to config changes database
        if self.changes_db:
            result = self.client.create_page(self.changes_db, properties)
            logger.info(f"Logged change: {tool} | {site} | {action}")
            return result
        else:
            logger.error("config_changes database not configured")
            return {"status": "error", "message": "Database not configured"}
    
    def get_recent_changes(
        self,
        days: int = 7,
        site: Optional[str] = None,
        tool: Optional[str] = None
    ) -> List[Dict]:
        """Get recent configuration changes."""
        if self.dry_run or not self.changes_db:
            return []
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        filters = [
            {"property": "Timestamp", "date": {"on_or_after": cutoff.isoformat()}}
        ]
        
        if site:
            filters.append({"property": "Site Name", "rich_text": {"contains": site}})
        if tool:
            filters.append({"property": "Tool", "select": {"equals": tool}})
        
        filter_obj = {"and": filters} if len(filters) > 1 else filters[0]
        
        pages = self.client.query_database(
            self.changes_db,
            filter_obj=filter_obj,
            sorts=[{"property": "Timestamp", "direction": "descending"}]
        )
        
        return [{
            "id": p["id"],
            "change_id": self.client.extract_title(p),
            "site": self.client.extract_property(p, "Site Name"),
            "tool": self.client.extract_property(p, "Tool"),
            "action": self.client.extract_property(p, "Action"),
            "summary": self.client.extract_property(p, "Summary"),
            "engineer": self.client.extract_property(p, "Engineer"),
            "timestamp": self.client.extract_property(p, "Timestamp"),
            "risk_level": self.client.extract_property(p, "Risk Level"),
        } for p in pages]
    
    def generate_report(
        self,
        site: Optional[str] = None,
        days: int = 30
    ) -> str:
        """Generate change report for a site or all sites."""
        changes = self.get_recent_changes(days=days, site=site)
        
        if not changes:
            return f"No changes found in the last {days} days."
        
        # Group by site
        by_site = {}
        for c in changes:
            s = c.get("site", "Unknown")
            if s not in by_site:
                by_site[s] = []
            by_site[s].append(c)
        
        # Count by risk
        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for c in changes:
            risk = c.get("risk_level", "low")
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        # Count by tool
        tool_counts = {}
        for c in changes:
            t = c.get("tool", "unknown")
            tool_counts[t] = tool_counts.get(t, 0) + 1
        
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
                risk_icon = {"critical": "!!", "high": "!", "medium": "*", "low": "-"}.get(c.get("risk_level", ""), "-")
                report += f"  [{risk_icon}] {c.get('action', '')} via {c.get('tool', '')} - {c.get('summary', '')[:50]}\n"
            if len(site_changes) > 5:
                report += f"  ... and {len(site_changes) - 5} more\n"
        
        return report


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
    
    sub = parser.add_subparsers(dest='cmd', help='Command')
    
    # Log command
    log_parser = sub.add_parser('log', help='Log a configuration change')
    log_parser.add_argument('--tool', required=True, choices=list(TOOLS.keys()),
                           help='Tool that made the change')
    log_parser.add_argument('--site', required=True, help='Customer site name')
    log_parser.add_argument('--action', required=True, choices=ACTIONS,
                           help='Type of action')
    log_parser.add_argument('--summary', required=True, help='Brief description')
    log_parser.add_argument('--details', help='Detailed change info')
    log_parser.add_argument('--risk', choices=RISK_LEVELS, help='Override risk level')
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
    
    if not Path(args.config).exists():
        logger.error(f"Config not found: {args.config}")
        sys.exit(1)
    
    try:
        sync = ConfigChangeSync(args.config, dry_run=args.dry_run)
        
        if args.cmd == 'log':
            result = sync.log_change(
                tool=args.tool,
                site=args.site,
                action=args.action,
                summary=args.summary,
                details=args.details,
                risk_level=args.risk,
                ticket_id=args.ticket,
                rollback_plan=args.rollback
            )
            print(f"Logged: {args.tool} | {args.site} | {args.action}")
            
        elif args.cmd == 'recent':
            changes = sync.get_recent_changes(days=args.days, site=args.site, tool=args.tool)
            print(f"\nRecent Changes (last {args.days} days):\n")
            for c in changes:
                risk = c.get('risk_level', 'low')
                icon = {"critical": "!!", "high": "!", "medium": "*", "low": "-"}.get(risk, "-")
                print(f"  [{icon}] {c.get('timestamp', '')[:10]} | {c.get('site', '')} | {c.get('tool', '')} | {c.get('summary', '')[:40]}")
            print(f"\nTotal: {len(changes)}")
            
        elif args.cmd == 'report':
            print(sync.generate_report(site=args.site, days=args.days))
    
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
