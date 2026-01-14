#!/usr/bin/env python3
"""
Azure Migration Pipeline Tracker - Manage service migration in Notion

Purpose:
    Track Azure services through Lab → Production → Customer Offerings pipeline.

Usage:
    python azure_pipeline_sync.py --config config.json list
    python azure_pipeline_sync.py --config config.json add --name "Azure VPN" --category "Networking"
    python azure_pipeline_sync.py --config config.json update --name "Azure VPN" --stage "production"
    python azure_pipeline_sync.py --config config.json report

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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

AZURE_CATEGORIES = [
    "Compute", "Networking", "Storage", "Databases", "Identity", "Security",
    "Management", "DevOps", "AI/ML", "Analytics", "Integration", "IoT",
    "Migration", "Backup", "Monitoring"
]

PIPELINE_STAGES = ["backlog", "lab testing", "production validation", "customer ready", "deprecated"]
TEST_STATUSES = ["not started", "in progress", "passed", "failed"]


# =============================================================================
# Azure Pipeline Manager
# =============================================================================

class AzurePipelineManager:
    """Manage Azure service migration tracking in Notion."""
    
    def __init__(self, config_path: str, dry_run: bool = False):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.dry_run = dry_run
        self.client = None if dry_run else NotionWrapper(token=self.config.get("notion_token"))
        self.db_id = self.config["databases"]["azure_pipeline"]
    
    def list_services(self, stage: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
        """List services with optional filtering."""
        if self.dry_run:
            return []
        
        filters = []
        if stage:
            filters.append({"property": "Pipeline Stage", "select": {"equals": stage}})
        if category:
            filters.append({"property": "Category", "select": {"equals": category}})
        
        filter_obj = None
        if len(filters) == 1:
            filter_obj = filters[0]
        elif len(filters) > 1:
            filter_obj = {"and": filters}
        
        pages = self.client.query_database(
            self.db_id,
            filter_obj=filter_obj,
            sorts=[{"property": "Pipeline Stage", "direction": "ascending"}]
        )
        
        return [
            {
                "id": page["id"],
                "name": self.client.extract_title(page),
                "category": self.client.extract_property(page, "Category"),
                "stage": self.client.extract_property(page, "Pipeline Stage"),
                "lab_status": self.client.extract_property(page, "Lab Status"),
                "prod_status": self.client.extract_property(page, "Production Status"),
                "customer_requests": self.client.extract_property(page, "Customer Requests"),
                "security_review": self.client.extract_property(page, "Security Review"),
                "blockers": self.client.extract_property(page, "Blockers")
            }
            for page in pages
        ]
    
    def add_service(
        self,
        name: str,
        category: str,
        owner: Optional[str] = None,
        target_date: Optional[str] = None
    ) -> Dict:
        """Add a new service to the pipeline."""
        if category not in AZURE_CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {AZURE_CATEGORIES}")
        
        properties = {
            "Service Name": NotionWrapper.prop_title(name),
            "Category": NotionWrapper.prop_select(category),
            "Pipeline Stage": NotionWrapper.prop_select("backlog"),
            "Lab Status": NotionWrapper.prop_select("not started"),
            "Production Status": NotionWrapper.prop_select("not started"),
            "Customer Requests": NotionWrapper.prop_number(0),
            "Security Review": NotionWrapper.prop_checkbox(False),
            "Last Updated": NotionWrapper.prop_date(datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        }
        
        if owner:
            properties["Owner"] = NotionWrapper.prop_rich_text(owner)
        if target_date:
            properties["Target Date"] = NotionWrapper.prop_date(target_date)
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would add service: {name}")
            return {"status": "dry_run", "name": name}
        
        existing = self.client.find_page_by_title(self.db_id, name)
        if existing:
            raise ValueError(f"Service '{name}' already exists")
        
        result = self.client.create_page(self.db_id, properties)
        logger.info(f"Added service: {name}")
        return result
    
    def update_service(
        self,
        name: str,
        stage: Optional[str] = None,
        lab_status: Optional[str] = None,
        prod_status: Optional[str] = None,
        blockers: Optional[str] = None,
        security_review: Optional[bool] = None,
        customer_requests: Optional[int] = None
    ) -> Dict:
        """Update an existing service."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update service: {name}")
            return {"status": "dry_run", "name": name}
        
        page = self.client.find_page_by_title(self.db_id, name)
        if not page:
            raise ValueError(f"Service '{name}' not found")
        
        properties = {
            "Last Updated": NotionWrapper.prop_date(datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        }
        
        if stage:
            if stage not in PIPELINE_STAGES:
                raise ValueError(f"Invalid stage. Must be one of: {PIPELINE_STAGES}")
            properties["Pipeline Stage"] = NotionWrapper.prop_select(stage)
        
        if lab_status:
            if lab_status not in TEST_STATUSES:
                raise ValueError(f"Invalid lab status. Must be one of: {TEST_STATUSES}")
            properties["Lab Status"] = NotionWrapper.prop_select(lab_status)
        
        if prod_status:
            if prod_status not in TEST_STATUSES:
                raise ValueError(f"Invalid prod status. Must be one of: {TEST_STATUSES}")
            properties["Production Status"] = NotionWrapper.prop_select(prod_status)
        
        if blockers is not None:
            properties["Blockers"] = NotionWrapper.prop_rich_text(blockers)
        if security_review is not None:
            properties["Security Review"] = NotionWrapper.prop_checkbox(security_review)
        if customer_requests is not None:
            properties["Customer Requests"] = NotionWrapper.prop_number(customer_requests)
        
        result = self.client.update_page(page["id"], properties)
        logger.info(f"Updated service: {name}")
        return result
    
    def advance_stage(self, name: str) -> Dict:
        """Advance a service to the next pipeline stage with validation."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would advance service: {name}")
            return {"status": "dry_run", "name": name}
        
        page = self.client.find_page_by_title(self.db_id, name)
        if not page:
            raise ValueError(f"Service '{name}' not found")
        
        current_stage = self.client.extract_property(page, "Pipeline Stage")
        lab_status = self.client.extract_property(page, "Lab Status")
        prod_status = self.client.extract_property(page, "Production Status")
        security_review = self.client.extract_property(page, "Security Review")
        
        stage_order = {
            "backlog": "lab testing",
            "lab testing": "production validation",
            "production validation": "customer ready",
        }
        
        next_stage = stage_order.get(current_stage)
        if not next_stage:
            raise ValueError(f"Cannot advance from '{current_stage}'")
        
        # Validate prerequisites
        if next_stage == "production validation" and lab_status != "passed":
            raise ValueError("Lab testing must pass before advancing to production validation")
        
        if next_stage == "customer ready":
            if prod_status != "passed":
                raise ValueError("Production validation must pass before customer ready")
            if not security_review:
                raise ValueError("Security review must be complete before customer ready")
        
        return self.update_service(name, stage=next_stage)
    
    def generate_report(self) -> str:
        """Generate pipeline status report."""
        services = self.list_services()
        
        by_stage = {stage: [s for s in services if s["stage"] == stage] for stage in PIPELINE_STAGES}
        
        total = len(services)
        ready = len(by_stage.get("customer ready", []))
        blocked = len([s for s in services if s.get("blockers")])
        
        report = f"""
Azure Migration Pipeline Report
{'=' * 50}
Generated: {datetime.now().isoformat()}

SUMMARY
{'-' * 50}
Total Services: {total}
Customer Ready: {ready} ({ready/total*100:.0f}% if total else 0)
Currently Blocked: {blocked}

PIPELINE OVERVIEW
{'-' * 50}
"""
        for stage in PIPELINE_STAGES:
            services_in_stage = by_stage.get(stage, [])
            report += f"\n{stage.upper()} ({len(services_in_stage)})\n"
            for s in services_in_stage:
                icon = "🔒" if s.get("security_review") else "  "
                report += f"  {icon} {s['name']} [{s['category']}]\n"
                if s.get("blockers"):
                    report += f"       └─ Blocker: {s['blockers']}\n"
        
        return report


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Manage Azure service migration pipeline")
    parser.add_argument('--config', '-c', required=True, help='Config JSON path')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # List
    list_parser = subparsers.add_parser('list', help='List services')
    list_parser.add_argument('--stage', choices=PIPELINE_STAGES)
    list_parser.add_argument('--category', choices=AZURE_CATEGORIES)
    
    # Add
    add_parser = subparsers.add_parser('add', help='Add service')
    add_parser.add_argument('--name', required=True)
    add_parser.add_argument('--category', required=True, choices=AZURE_CATEGORIES)
    add_parser.add_argument('--owner')
    add_parser.add_argument('--target-date')
    
    # Update
    update_parser = subparsers.add_parser('update', help='Update service')
    update_parser.add_argument('--name', required=True)
    update_parser.add_argument('--stage', choices=PIPELINE_STAGES)
    update_parser.add_argument('--lab-status', choices=TEST_STATUSES)
    update_parser.add_argument('--prod-status', choices=TEST_STATUSES)
    update_parser.add_argument('--blockers')
    update_parser.add_argument('--security-review', type=lambda x: x.lower() == 'true')
    update_parser.add_argument('--customer-requests', type=int)
    
    # Advance
    advance_parser = subparsers.add_parser('advance', help='Advance to next stage')
    advance_parser.add_argument('--name', required=True)
    
    # Report
    subparsers.add_parser('report', help='Generate report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if not Path(args.config).exists():
        logger.error(f"Config not found: {args.config}")
        sys.exit(1)
    
    try:
        manager = AzurePipelineManager(args.config, dry_run=args.dry_run)
        
        if args.command == 'list':
            services = manager.list_services(stage=args.stage, category=args.category)
            print(f"\nFound {len(services)} services:\n")
            for s in services:
                print(f"  [{s['stage']}] {s['name']} - {s['category']}")
        
        elif args.command == 'add':
            manager.add_service(args.name, args.category, args.owner, args.target_date)
            print(f"Added: {args.name}")
        
        elif args.command == 'update':
            manager.update_service(
                args.name, args.stage, args.lab_status, args.prod_status,
                args.blockers, args.security_review, args.customer_requests
            )
            print(f"Updated: {args.name}")
        
        elif args.command == 'advance':
            manager.advance_stage(args.name)
            print(f"Advanced: {args.name}")
        
        elif args.command == 'report':
            print(manager.generate_report())
    
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
