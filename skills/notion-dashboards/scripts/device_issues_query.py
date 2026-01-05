#!/usr/bin/env python3
"""
Device Issues CLI Query Tool

Quick filtered access to Notion Device Issues database from terminal.

Usage:
    python device_issues_query.py                    # All active issues
    python device_issues_query.py --critical         # Critical severity only
    python device_issues_query.py --disk-space       # Disk space issues
    python device_issues_query.py --memory           # Memory issues
    python device_issues_query.py --cpu              # CPU issues
    python device_issues_query.py --disk-io          # Disk I/O issues
    python device_issues_query.py --by-org           # Group by organization
    python device_issues_query.py --resolved         # Include resolved issues
    python device_issues_query.py --json             # Output as JSON
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

import httpx


# =============================================================================
# Configuration
# =============================================================================

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
DEVICE_ISSUES_DB = os.getenv("DEVICE_ISSUES_DB", "2dc3808671fb81b39391cd513e6c416f")

SEVERITY_ORDER = {"critical": 0, "high": 1, "warning": 2, "medium": 3, "low": 4, "info": 5}
SEVERITY_COLORS = {
    "critical": "\033[91m",  # Red
    "high": "\033[93m",      # Yellow
    "warning": "\033[93m",   # Yellow
    "medium": "\033[94m",    # Blue
    "low": "\033[92m",       # Green
    "info": "\033[90m",      # Gray
}
RESET_COLOR = "\033[0m"


# =============================================================================
# Notion API Client
# =============================================================================

class NotionQueryClient:
    """Simple Notion API client for queries."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def query_database(
        self,
        database_id: str,
        filter_obj: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Query database with pagination."""
        all_results = []
        has_more = True
        start_cursor = None

        body = {}
        if filter_obj:
            body["filter"] = filter_obj
        if sorts:
            body["sorts"] = sorts

        with httpx.Client(timeout=30) as client:
            while has_more:
                if start_cursor:
                    body["start_cursor"] = start_cursor

                resp = client.post(
                    f"{self.base_url}/databases/{database_id}/query",
                    headers=self.headers,
                    json=body
                )
                resp.raise_for_status()
                data = resp.json()

                all_results.extend(data.get("results", []))
                has_more = data.get("has_more", False)
                start_cursor = data.get("next_cursor")

        return all_results


# =============================================================================
# Data Extraction
# =============================================================================

def extract_issue(page: Dict) -> Dict:
    """Extract issue data from Notion page."""
    props = page.get("properties", {})

    # Extract title (Device Name)
    title_prop = props.get("Device Name", {}).get("title", [])
    device_name = title_prop[0].get("plain_text", "Unknown") if title_prop else "Unknown"

    # Extract rich text fields
    def get_text(prop_name: str) -> str:
        rt = props.get(prop_name, {}).get("rich_text", [])
        return rt[0].get("plain_text", "") if rt else ""

    # Extract select fields
    def get_select(prop_name: str) -> str:
        sel = props.get(prop_name, {}).get("select")
        return sel.get("name", "") if sel else ""

    # Extract number fields
    def get_number(prop_name: str) -> Optional[int]:
        return props.get(prop_name, {}).get("number")

    # Extract date
    created = props.get("Created", {}).get("date", {})
    created_date = created.get("start", "") if created else ""

    return {
        "device_name": device_name,
        "organization": get_text("Organization"),
        "issue_type": get_select("Issue Type"),
        "severity": get_select("Severity"),
        "status": get_select("Status"),
        "details": get_text("Details")[:60],  # Truncate for display
        "device_id": get_number("Device ID"),
        "alert_uid": get_text("Alert UID")[:8],  # Short UID
        "created": created_date[:10] if created_date else "",
        "page_id": page.get("id", ""),
    }


# =============================================================================
# Filters
# =============================================================================

def build_filter(args) -> Optional[Dict]:
    """Build Notion filter from CLI arguments."""
    conditions = []

    # Status filter (exclude resolved unless --resolved)
    if not args.resolved:
        conditions.append({
            "property": "Status",
            "select": {"does_not_equal": "resolved"}
        })

    # Issue type filters
    if args.disk_space:
        conditions.append({
            "property": "Issue Type",
            "select": {"equals": "disk_space"}
        })
    elif args.memory:
        conditions.append({
            "property": "Issue Type",
            "select": {"equals": "memory"}
        })
    elif args.cpu:
        conditions.append({
            "property": "Issue Type",
            "select": {"equals": "cpu"}
        })
    elif args.disk_io:
        conditions.append({
            "property": "Issue Type",
            "select": {"equals": "disk_io"}
        })

    # Severity filter
    if args.critical:
        conditions.append({
            "property": "Severity",
            "select": {"equals": "critical"}
        })
    elif args.high:
        conditions.append({
            "property": "Severity",
            "select": {"equals": "high"}
        })

    # Organization filter
    if args.org:
        conditions.append({
            "property": "Organization",
            "rich_text": {"contains": args.org}
        })

    if not conditions:
        return None
    elif len(conditions) == 1:
        return conditions[0]
    else:
        return {"and": conditions}


# =============================================================================
# Output Formatters
# =============================================================================

def print_table(issues: List[Dict], use_color: bool = True):
    """Print issues as formatted table."""
    if not issues:
        print("No issues found.")
        return

    # Column widths
    cols = {
        "device": 20,
        "org": 18,
        "type": 12,
        "severity": 10,
        "status": 12,
        "created": 10,
    }

    # Header
    header = (
        f"{'Device':<{cols['device']}} "
        f"{'Organization':<{cols['org']}} "
        f"{'Type':<{cols['type']}} "
        f"{'Severity':<{cols['severity']}} "
        f"{'Status':<{cols['status']}} "
        f"{'Created':<{cols['created']}}"
    )
    print("\033[1m" + header + RESET_COLOR if use_color else header)
    print("-" * (sum(cols.values()) + len(cols) - 1))

    # Sort by severity
    issues.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "info"), 5))

    # Rows
    for issue in issues:
        severity = issue.get("severity", "info")
        color = SEVERITY_COLORS.get(severity, "") if use_color else ""

        row = (
            f"{issue['device_name'][:cols['device']-1]:<{cols['device']}} "
            f"{issue['organization'][:cols['org']-1]:<{cols['org']}} "
            f"{issue['issue_type']:<{cols['type']}} "
            f"{color}{severity:<{cols['severity']}}{RESET_COLOR if use_color else ''} "
            f"{issue['status']:<{cols['status']}} "
            f"{issue['created']:<{cols['created']}}"
        )
        print(row)

    print()
    print(f"Total: {len(issues)} issues")


def print_by_org(issues: List[Dict], use_color: bool = True):
    """Print issues grouped by organization."""
    if not issues:
        print("No issues found.")
        return

    # Group by org
    by_org = defaultdict(list)
    for issue in issues:
        org = issue.get("organization", "Unknown")
        by_org[org].append(issue)

    # Sort orgs by issue count
    for org in sorted(by_org.keys(), key=lambda x: -len(by_org[x])):
        org_issues = by_org[org]
        print(f"\033[1m{org}\033[0m ({len(org_issues)} issues)" if use_color else f"{org} ({len(org_issues)} issues)")

        # Sort by severity within org
        org_issues.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "info"), 5))

        for issue in org_issues:
            severity = issue.get("severity", "info")
            color = SEVERITY_COLORS.get(severity, "") if use_color else ""
            print(f"  {color}{severity:8}{RESET_COLOR if use_color else ''} {issue['issue_type']:12} {issue['device_name']}")
        print()

    print(f"Total: {len(issues)} issues across {len(by_org)} organizations")


def print_summary(issues: List[Dict]):
    """Print summary statistics."""
    if not issues:
        print("No issues found.")
        return

    # Count by type
    by_type = defaultdict(int)
    by_severity = defaultdict(int)
    by_status = defaultdict(int)

    for issue in issues:
        by_type[issue.get("issue_type", "unknown")] += 1
        by_severity[issue.get("severity", "unknown")] += 1
        by_status[issue.get("status", "unknown")] += 1

    print("\033[1m=== Device Issues Summary ===\033[0m\n")

    print("By Type:")
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t:15} {count:3}")

    print("\nBy Severity:")
    for s in ["critical", "high", "warning", "medium", "low", "info"]:
        if s in by_severity:
            color = SEVERITY_COLORS.get(s, "")
            print(f"  {color}{s:15}{RESET_COLOR} {by_severity[s]:3}")

    print("\nBy Status:")
    for s, count in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"  {s:15} {count:3}")

    print(f"\nTotal: {len(issues)} issues")


def print_json(issues: List[Dict]):
    """Print issues as JSON."""
    print(json.dumps(issues, indent=2))


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Query Device Issues from Notion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      # All active issues
  %(prog)s --critical           # Critical severity only
  %(prog)s --disk-space         # Disk space issues
  %(prog)s --by-org             # Group by organization
  %(prog)s --org "Acme"         # Filter by org name
  %(prog)s --summary            # Show summary stats
  %(prog)s --json               # Output as JSON
        """
    )

    # Filter options
    filter_group = parser.add_argument_group("Filters")
    filter_group.add_argument("--critical", action="store_true", help="Critical severity only")
    filter_group.add_argument("--high", action="store_true", help="High severity only")
    filter_group.add_argument("--disk-space", action="store_true", help="Disk space issues")
    filter_group.add_argument("--memory", action="store_true", help="Memory issues")
    filter_group.add_argument("--cpu", action="store_true", help="CPU issues")
    filter_group.add_argument("--disk-io", action="store_true", help="Disk I/O issues")
    filter_group.add_argument("--org", type=str, help="Filter by organization name")
    filter_group.add_argument("--resolved", action="store_true", help="Include resolved issues")

    # Output options
    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--by-org", action="store_true", help="Group by organization")
    output_group.add_argument("--summary", action="store_true", help="Show summary statistics")
    output_group.add_argument("--json", action="store_true", help="Output as JSON")
    output_group.add_argument("--no-color", action="store_true", help="Disable colored output")

    args = parser.parse_args()

    # Check token
    token = NOTION_TOKEN
    if not token:
        print("Error: NOTION_TOKEN environment variable not set", file=sys.stderr)
        print("Set it with: export NOTION_TOKEN='your-token'", file=sys.stderr)
        sys.exit(1)

    # Query Notion
    try:
        client = NotionQueryClient(token)
        filter_obj = build_filter(args)

        sorts = [{"property": "Created", "direction": "descending"}]

        pages = client.query_database(DEVICE_ISSUES_DB, filter_obj, sorts)
        issues = [extract_issue(p) for p in pages]

    except httpx.HTTPStatusError as e:
        print(f"API Error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    use_color = not args.no_color and sys.stdout.isatty()

    if args.json:
        print_json(issues)
    elif args.summary:
        print_summary(issues)
    elif args.by_org:
        print_by_org(issues, use_color)
    else:
        print_table(issues, use_color)


if __name__ == "__main__":
    main()
