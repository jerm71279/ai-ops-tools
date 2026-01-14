#!/usr/bin/env python3
"""
Runbook Library Manager - Manage documentation in Notion

Usage:
    python runbook_manager.py --config config.json list
    python runbook_manager.py --config config.json add --title "VPN Setup" --category network
    python runbook_manager.py --config config.json review-due

Requirements:
    pip install notion-client --break-system-packages
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from notion_client_wrapper import NotionWrapper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CATEGORIES = ["network", "security", "cloud", "hardware", "process"]
VENDORS = ["Ubiquiti", "MikroTik", "SonicWall", "Azure", "M365"]
DOC_TYPES = ["SOP", "runbook", "troubleshooting guide", "template", "reference"]
COMPLEXITY_LEVELS = ["basic", "intermediate", "advanced"]
AUTOMATION_STATUSES = ["manual", "partially automated", "fully automated", "deprecated"]
REVIEW_INTERVALS = {"basic": 180, "intermediate": 90, "advanced": 60}


class RunbookManager:
    def __init__(self, config_path: str, dry_run: bool = False):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.dry_run = dry_run
        self.client = None if dry_run else NotionWrapper(token=self.config.get("notion_token"))
        self.db_id = self.config["databases"]["runbook_library"]
    
    def list_runbooks(self, category: Optional[str] = None, vendor: Optional[str] = None,
                      automation_status: Optional[str] = None) -> List[Dict]:
        if self.dry_run:
            return []
        
        filters = []
        if category:
            filters.append({"property": "Category", "select": {"equals": category}})
        if vendor:
            filters.append({"property": "Vendor", "multi_select": {"contains": vendor}})
        if automation_status:
            filters.append({"property": "Automation Status", "select": {"equals": automation_status}})
        
        filter_obj = filters[0] if len(filters) == 1 else {"and": filters} if filters else None
        pages = self.client.query_database(self.db_id, filter_obj=filter_obj)
        
        return [{
            "id": p["id"],
            "title": self.client.extract_title(p),
            "category": self.client.extract_property(p, "Category"),
            "vendor": self.client.extract_property(p, "Vendor"),
            "complexity": self.client.extract_property(p, "Complexity"),
            "automation_status": self.client.extract_property(p, "Automation Status"),
            "next_review": self.client.extract_property(p, "Next Review Due"),
        } for p in pages]
    
    def add_runbook(self, title: str, category: str, doc_type: str, vendors: List[str],
                    complexity: str = "intermediate", owner: Optional[str] = None,
                    tags: Optional[List[str]] = None) -> Dict:
        today = datetime.now(timezone.utc)
        next_review = today + timedelta(days=REVIEW_INTERVALS.get(complexity, 90))
        
        properties = {
            "Title": NotionWrapper.prop_title(title),
            "Category": NotionWrapper.prop_select(category),
            "Vendor": NotionWrapper.prop_multi_select(vendors),
            "Document Type": NotionWrapper.prop_select(doc_type),
            "Complexity": NotionWrapper.prop_select(complexity),
            "Automation Status": NotionWrapper.prop_select("manual"),
            "Last Review Date": NotionWrapper.prop_date(today.strftime("%Y-%m-%d")),
            "Next Review Due": NotionWrapper.prop_date(next_review.strftime("%Y-%m-%d")),
        }
        if owner:
            properties["Owner"] = NotionWrapper.prop_rich_text(owner)
        if tags:
            properties["Tags"] = NotionWrapper.prop_multi_select(tags)
        
        if self.dry_run:
            return {"status": "dry_run", "title": title}
        
        if self.client.find_page_by_title(self.db_id, title):
            raise ValueError(f"Runbook '{title}' already exists")
        
        return self.client.create_page(self.db_id, properties)
    
    def mark_reviewed(self, title: str) -> Dict:
        if self.dry_run:
            return {"status": "dry_run", "title": title}
        
        page = self.client.find_page_by_title(self.db_id, title)
        if not page:
            raise ValueError(f"Runbook '{title}' not found")
        
        complexity = self.client.extract_property(page, "Complexity") or "intermediate"
        today = datetime.now(timezone.utc)
        next_review = today + timedelta(days=REVIEW_INTERVALS.get(complexity, 90))
        
        return self.client.update_page(page["id"], {
            "Last Review Date": NotionWrapper.prop_date(today.strftime("%Y-%m-%d")),
            "Next Review Due": NotionWrapper.prop_date(next_review.strftime("%Y-%m-%d")),
        })
    
    def update_automation_status(self, title: str, status: str) -> Dict:
        if self.dry_run:
            return {"status": "dry_run", "title": title}
        
        page = self.client.find_page_by_title(self.db_id, title)
        if not page:
            raise ValueError(f"Runbook '{title}' not found")
        
        properties = {"Automation Status": NotionWrapper.prop_select(status)}
        if status == "deprecated":
            next_review = datetime.now(timezone.utc) + timedelta(days=365)
            properties["Next Review Due"] = NotionWrapper.prop_date(next_review.strftime("%Y-%m-%d"))
        
        return self.client.update_page(page["id"], properties)
    
    def get_review_due(self, days_ahead: int = 14) -> List[Dict]:
        if self.dry_run:
            return []
        
        cutoff = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        pages = self.client.query_database(
            self.db_id,
            filter_obj={"property": "Next Review Due", "date": {"on_or_before": cutoff.strftime("%Y-%m-%d")}},
            sorts=[{"property": "Next Review Due", "direction": "ascending"}]
        )
        
        today = datetime.now(timezone.utc).date()
        results = []
        for p in pages:
            next_review_str = self.client.extract_property(p, "Next Review Due")
            days_until = 0
            overdue = False
            if next_review_str:
                next_review = datetime.fromisoformat(next_review_str).date()
                days_until = (next_review - today).days
                overdue = days_until < 0
            results.append({
                "title": self.client.extract_title(p),
                "category": self.client.extract_property(p, "Category"),
                "days_until": days_until,
                "overdue": overdue
            })
        return results
    
    def get_automation_candidates(self) -> List[Dict]:
        if self.dry_run:
            return []
        
        pages = self.client.query_database(self.db_id, filter_obj={
            "and": [
                {"property": "Automation Status", "select": {"equals": "manual"}},
                {"or": [
                    {"property": "Complexity", "select": {"equals": "basic"}},
                    {"property": "Complexity", "select": {"equals": "intermediate"}}
                ]}
            ]
        })
        return [{
            "title": self.client.extract_title(p),
            "category": self.client.extract_property(p, "Category"),
            "vendor": self.client.extract_property(p, "Vendor"),
        } for p in pages]
    
    def generate_report(self) -> str:
        runbooks = self.list_runbooks()
        review_due = self.get_review_due()
        candidates = self.get_automation_candidates()
        
        total = len(runbooks)
        automated = len([r for r in runbooks if r.get("automation_status") in ["fully automated", "partially automated"]])
        rate = (automated / total * 100) if total else 0
        
        return f"""
Runbook Library Report
{'=' * 50}
Total: {total} | Automation Rate: {rate:.0f}%
Reviews Due (14 days): {len(review_due)}
Automation Candidates: {len(candidates)}

REVIEWS DUE:
{chr(10).join(f"  • {r['title']} - {'OVERDUE' if r['overdue'] else f'in {r[\"days_until\"]} days'}" for r in review_due[:10])}

AUTOMATION CANDIDATES:
{chr(10).join(f"  • {r['title']}" for r in candidates[:10])}
"""


def main():
    parser = argparse.ArgumentParser(description="Manage runbook library")
    parser.add_argument('--config', '-c', required=True)
    parser.add_argument('--dry-run', action='store_true')
    
    sub = parser.add_subparsers(dest='cmd')
    
    ls = sub.add_parser('list')
    ls.add_argument('--category', choices=CATEGORIES)
    ls.add_argument('--vendor', choices=VENDORS)
    ls.add_argument('--automation', choices=AUTOMATION_STATUSES)
    
    add = sub.add_parser('add')
    add.add_argument('--title', required=True)
    add.add_argument('--category', required=True, choices=CATEGORIES)
    add.add_argument('--type', required=True, choices=DOC_TYPES, dest='doc_type')
    add.add_argument('--vendors', nargs='+', choices=VENDORS, default=[])
    add.add_argument('--complexity', choices=COMPLEXITY_LEVELS, default='intermediate')
    add.add_argument('--owner')
    add.add_argument('--tags', nargs='+')
    
    rev = sub.add_parser('review')
    rev.add_argument('--title', required=True)
    
    auto = sub.add_parser('automate')
    auto.add_argument('--title', required=True)
    auto.add_argument('--status', required=True, choices=AUTOMATION_STATUSES)
    
    due = sub.add_parser('review-due')
    due.add_argument('--days', type=int, default=14)
    
    sub.add_parser('candidates')
    sub.add_parser('report')
    
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)
    
    if not Path(args.config).exists():
        print(f"Config not found: {args.config}")
        sys.exit(1)
    
    try:
        mgr = RunbookManager(args.config, dry_run=args.dry_run)
        
        if args.cmd == 'list':
            for r in mgr.list_runbooks(args.category, args.vendor, args.automation):
                print(f"  [{r['category']}] {r['title']} - {r['automation_status']}")
        elif args.cmd == 'add':
            mgr.add_runbook(args.title, args.category, args.doc_type, args.vendors, args.complexity, args.owner, args.tags)
            print(f"Added: {args.title}")
        elif args.cmd == 'review':
            mgr.mark_reviewed(args.title)
            print(f"Reviewed: {args.title}")
        elif args.cmd == 'automate':
            mgr.update_automation_status(args.title, args.status)
            print(f"Updated: {args.title} -> {args.status}")
        elif args.cmd == 'review-due':
            for r in mgr.get_review_due(args.days):
                print(f"  • {r['title']} - {'OVERDUE' if r['overdue'] else f'in {r[\"days_until\"]} days'}")
        elif args.cmd == 'candidates':
            for r in mgr.get_automation_candidates():
                print(f"  • {r['title']}")
        elif args.cmd == 'report':
            print(mgr.generate_report())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
