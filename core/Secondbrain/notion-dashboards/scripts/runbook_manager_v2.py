#!/usr/bin/env python3
"""
Runbook Library Manager - Manage documentation in Notion

Purpose:
    Manage OberaConnect's runbook library with review scheduling,
    automation tracking, and documentation governance.

Usage:
    python runbook_manager.py --config config.json list
    python runbook_manager.py --config config.json add --title "VPN Setup" --category network
    python runbook_manager.py --config config.json review --title "VPN Setup"
    python runbook_manager.py --config config.json review-due
    python runbook_manager.py --config config.json report

Requirements:
    pip install notion-client --break-system-packages

Author: OberaConnect
Created: 2025
Refactored: 2025 - Now uses BaseSyncClient with typed models and review scheduling
"""

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

# Import from core modules
from core import (
    BaseSyncClient,
    get_logger,
    enable_debug,
    NotionSyncError,
    ValidationError,
)

# Import NotionWrapper for static property builders
from notion_client_wrapper import NotionWrapper

# Setup logging via centralized config
logger = get_logger(__name__)


# =============================================================================
# Enums and Constants
# =============================================================================

class RunbookCategory(Enum):
    """Categories for runbooks."""
    NETWORK = "network"
    SECURITY = "security"
    CLOUD = "cloud"
    HARDWARE = "hardware"
    PROCESS = "process"
    
    @classmethod
    def values(cls) -> List[str]:
        return [c.value for c in cls]


class Vendor(Enum):
    """Supported vendors for runbooks."""
    UBIQUITI = "Ubiquiti"
    MIKROTIK = "MikroTik"
    SONICWALL = "SonicWall"
    AZURE = "Azure"
    M365 = "M365"
    
    @classmethod
    def values(cls) -> List[str]:
        return [v.value for v in cls]


class DocumentType(Enum):
    """Types of documentation."""
    SOP = "SOP"
    RUNBOOK = "runbook"
    TROUBLESHOOTING = "troubleshooting guide"
    TEMPLATE = "template"
    REFERENCE = "reference"
    
    @classmethod
    def values(cls) -> List[str]:
        return [d.value for d in cls]


class ComplexityLevel(Enum):
    """Complexity levels with associated review intervals."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    
    @classmethod
    def values(cls) -> List[str]:
        return [c.value for c in cls]
    
    @property
    def review_interval_days(self) -> int:
        """Get review interval in days based on complexity."""
        intervals = {
            ComplexityLevel.BASIC: 180,       # 6 months
            ComplexityLevel.INTERMEDIATE: 90,  # 3 months
            ComplexityLevel.ADVANCED: 60,      # 2 months
        }
        return intervals.get(self, 90)


class AutomationStatus(Enum):
    """Automation status for runbooks."""
    MANUAL = "manual"
    PARTIALLY_AUTOMATED = "partially automated"
    FULLY_AUTOMATED = "fully automated"
    DEPRECATED = "deprecated"
    
    @classmethod
    def values(cls) -> List[str]:
        return [a.value for a in cls]


@dataclass
class Runbook:
    """
    Represents a runbook in the library.
    
    Typed data class for validation and IDE support.
    """
    title: str
    category: RunbookCategory
    doc_type: DocumentType
    vendors: List[str] = field(default_factory=list)
    
    # Metadata
    complexity: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    automation_status: AutomationStatus = AutomationStatus.MANUAL
    owner: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Review tracking (auto-calculated)
    last_review_date: Optional[datetime] = None
    next_review_due: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate and set defaults."""
        if not self.title:
            raise ValidationError("title", "Runbook title is required")
        
        # Set initial review dates if not provided
        if self.last_review_date is None:
            self.last_review_date = datetime.now(timezone.utc)
        if self.next_review_due is None:
            self.next_review_due = self.calculate_next_review()
    
    def calculate_next_review(self) -> datetime:
        """Calculate next review date based on complexity."""
        base_date = self.last_review_date or datetime.now(timezone.utc)
        return base_date + timedelta(days=self.complexity.review_interval_days)
    
    @property
    def days_until_review(self) -> int:
        """Days until next review (negative if overdue)."""
        if self.next_review_due is None:
            return 0
        delta = self.next_review_due.date() - datetime.now(timezone.utc).date()
        return delta.days
    
    @property
    def is_overdue(self) -> bool:
        """Check if review is overdue."""
        return self.days_until_review < 0
    
    @property
    def is_automation_candidate(self) -> bool:
        """Check if runbook is a candidate for automation."""
        return (
            self.automation_status == AutomationStatus.MANUAL and
            self.complexity in [ComplexityLevel.BASIC, ComplexityLevel.INTERMEDIATE]
        )


# =============================================================================
# Runbook Manager - Using BaseSyncClient
# =============================================================================

class RunbookManager(BaseSyncClient):
    """
    Manage runbook library in Notion.
    
    Inherits from BaseSyncClient which provides:
    - Configuration loading and validation
    - Notion client initialization with dry-run support
    - Retry logic for API calls
    - Page caching
    
    Operations:
    - list: Query runbooks with filtering
    - add: Create new runbook entry
    - review: Mark runbook as reviewed (updates dates)
    - automate: Update automation status
    - review-due: Get runbooks due for review
    - candidates: Get automation candidates
    - report: Generate library status report
    """
    
    @property
    def primary_database(self) -> str:
        """Primary database for runbook library."""
        return "runbook_library"
    
    def build_properties(self, runbook: Runbook) -> Dict:
        """Build Notion page properties from Runbook."""
        
        properties = {
            "Title": NotionWrapper.prop_title(runbook.title),
            "Category": NotionWrapper.prop_select(runbook.category.value),
            "Document Type": NotionWrapper.prop_select(runbook.doc_type.value),
            "Complexity": NotionWrapper.prop_select(runbook.complexity.value),
            "Automation Status": NotionWrapper.prop_select(runbook.automation_status.value),
        }
        
        if runbook.vendors:
            properties["Vendor"] = NotionWrapper.prop_multi_select(runbook.vendors)
        if runbook.owner:
            properties["Owner"] = NotionWrapper.prop_rich_text(runbook.owner)
        if runbook.tags:
            properties["Tags"] = NotionWrapper.prop_multi_select(runbook.tags)
        if runbook.last_review_date:
            properties["Last Review Date"] = NotionWrapper.prop_date(
                runbook.last_review_date.strftime("%Y-%m-%d")
            )
        if runbook.next_review_due:
            properties["Next Review Due"] = NotionWrapper.prop_date(
                runbook.next_review_due.strftime("%Y-%m-%d")
            )
        
        return properties
    
    def _page_to_runbook_dict(self, page: Dict) -> Dict:
        """Extract runbook data from Notion page."""
        return {
            "id": page["id"],
            "title": self.client.extract_title(page) if self.client else "",
            "category": self.client.extract_property(page, "Category") if self.client else "",
            "vendor": self.client.extract_property(page, "Vendor") if self.client else [],
            "complexity": self.client.extract_property(page, "Complexity") if self.client else "",
            "automation_status": self.client.extract_property(page, "Automation Status") if self.client else "",
            "next_review": self.client.extract_property(page, "Next Review Due") if self.client else None,
        }
    
    def list_runbooks(
        self,
        category: Optional[str] = None,
        vendor: Optional[str] = None,
        automation_status: Optional[str] = None
    ) -> List[Dict]:
        """
        List runbooks with optional filtering.
        
        Args:
            category: Filter by category
            vendor: Filter by vendor (multi-select contains)
            automation_status: Filter by automation status
            
        Returns:
            List of runbook dictionaries
        """
        if self.dry_run:
            self.logger.info("[DRY RUN] Would list runbooks")
            return []
        
        # Build filter
        filters = []
        if category:
            filters.append({"property": "Category", "select": {"equals": category}})
        if vendor:
            filters.append({"property": "Vendor", "multi_select": {"contains": vendor}})
        if automation_status:
            filters.append({"property": "Automation Status", "select": {"equals": automation_status}})
        
        filter_obj = None
        if len(filters) == 1:
            filter_obj = filters[0]
        elif len(filters) > 1:
            filter_obj = {"and": filters}
        
        pages = self.query_database(self.primary_database, filter_obj=filter_obj)
        
        return [self._page_to_runbook_dict(page) for page in pages]
    
    def add_runbook(self, runbook: Runbook) -> Dict:
        """
        Add a new runbook to the library.
        
        Args:
            runbook: Runbook object with details
            
        Returns:
            Result dictionary with status and page info
            
        Raises:
            ValidationError: If runbook already exists
        """
        self.logger.info(f"Adding runbook: {runbook.title}")
        
        # Build properties
        properties = self.build_properties(runbook)
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would add runbook: {runbook.title}")
            return {"status": "dry_run", "title": runbook.title}
        
        # Check for duplicates
        existing = self.client.find_page_by_title(
            self.config.databases.require(self.primary_database),
            runbook.title
        )
        if existing:
            raise ValidationError("title", f"Runbook '{runbook.title}' already exists")
        
        # Create page
        result = self.create_page(self.primary_database, properties)
        
        self.logger.info(f"Added runbook: {runbook.title}")
        return {
            "status": "success",
            "title": runbook.title,
            "page_id": result.get("id"),
        }
    
    def mark_reviewed(self, title: str) -> Dict:
        """
        Mark a runbook as reviewed.
        
        Updates last review date to today and calculates next review.
        
        Args:
            title: Runbook title
            
        Returns:
            Result dictionary
            
        Raises:
            ValidationError: If runbook not found
        """
        self.logger.info(f"Marking reviewed: {title}")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would mark reviewed: {title}")
            return {"status": "dry_run", "title": title}
        
        # Find the runbook
        page = self.client.find_page_by_title(
            self.config.databases.require(self.primary_database),
            title
        )
        if not page:
            raise ValidationError("title", f"Runbook '{title}' not found")
        
        # Get complexity to calculate next review
        complexity_str = self.client.extract_property(page, "Complexity") or "intermediate"
        try:
            complexity = ComplexityLevel(complexity_str)
        except ValueError:
            complexity = ComplexityLevel.INTERMEDIATE
        
        today = datetime.now(timezone.utc)
        next_review = today + timedelta(days=complexity.review_interval_days)
        
        # Update dates
        properties = {
            "Last Review Date": NotionWrapper.prop_date(today.strftime("%Y-%m-%d")),
            "Next Review Due": NotionWrapper.prop_date(next_review.strftime("%Y-%m-%d")),
        }
        
        result = self.update_page(page["id"], properties)
        
        self.logger.info(f"Marked reviewed: {title} (next: {next_review.strftime('%Y-%m-%d')})")
        return {
            "status": "success",
            "title": title,
            "next_review": next_review.strftime("%Y-%m-%d"),
        }
    
    def update_automation_status(self, title: str, status: str) -> Dict:
        """
        Update automation status for a runbook.
        
        Args:
            title: Runbook title
            status: New automation status
            
        Returns:
            Result dictionary
            
        Raises:
            ValidationError: If runbook not found or invalid status
        """
        self.logger.info(f"Updating automation status: {title} → {status}")
        
        if status not in AutomationStatus.values():
            raise ValidationError("status", f"Invalid automation status: {status}")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would update status: {title} → {status}")
            return {"status": "dry_run", "title": title}
        
        # Find the runbook
        page = self.client.find_page_by_title(
            self.config.databases.require(self.primary_database),
            title
        )
        if not page:
            raise ValidationError("title", f"Runbook '{title}' not found")
        
        properties = {
            "Automation Status": NotionWrapper.prop_select(status)
        }
        
        # If deprecated, extend next review to 1 year
        if status == "deprecated":
            next_review = datetime.now(timezone.utc) + timedelta(days=365)
            properties["Next Review Due"] = NotionWrapper.prop_date(
                next_review.strftime("%Y-%m-%d")
            )
        
        result = self.update_page(page["id"], properties)
        
        self.logger.info(f"Updated automation status: {title} → {status}")
        return {"status": "success", "title": title, "automation_status": status}
    
    def get_review_due(self, days_ahead: int = 14) -> List[Dict]:
        """
        Get runbooks due for review.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of runbooks due for review with days_until and overdue flag
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would get reviews due in {days_ahead} days")
            return []
        
        cutoff = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        
        pages = self.query_database(
            self.primary_database,
            filter_obj={
                "property": "Next Review Due",
                "date": {"on_or_before": cutoff.strftime("%Y-%m-%d")}
            },
            sorts=[{"property": "Next Review Due", "direction": "ascending"}]
        )
        
        today = datetime.now(timezone.utc).date()
        results = []
        
        for p in pages:
            next_review_str = self.client.extract_property(p, "Next Review Due")
            days_until = 0
            overdue = False
            
            if next_review_str:
                try:
                    next_review = datetime.fromisoformat(next_review_str).date()
                    days_until = (next_review - today).days
                    overdue = days_until < 0
                except ValueError:
                    pass
            
            results.append({
                "title": self.client.extract_title(p),
                "category": self.client.extract_property(p, "Category"),
                "days_until": days_until,
                "overdue": overdue,
            })
        
        return results
    
    def get_automation_candidates(self) -> List[Dict]:
        """
        Get runbooks that are candidates for automation.
        
        Candidates are manual runbooks with basic/intermediate complexity.
        
        Returns:
            List of candidate runbooks
        """
        if self.dry_run:
            self.logger.info("[DRY RUN] Would get automation candidates")
            return []
        
        pages = self.query_database(
            self.primary_database,
            filter_obj={
                "and": [
                    {"property": "Automation Status", "select": {"equals": "manual"}},
                    {"or": [
                        {"property": "Complexity", "select": {"equals": "basic"}},
                        {"property": "Complexity", "select": {"equals": "intermediate"}}
                    ]}
                ]
            }
        )
        
        return [{
            "title": self.client.extract_title(p),
            "category": self.client.extract_property(p, "Category"),
            "vendor": self.client.extract_property(p, "Vendor"),
            "complexity": self.client.extract_property(p, "Complexity"),
        } for p in pages]
    
    def sync(self, **kwargs) -> List[Dict]:
        """
        Required by BaseSyncClient - returns list of all runbooks.
        
        For runbook library, use specific methods (list_runbooks, add_runbook, etc.)
        """
        return self.list_runbooks()
    
    def generate_report(self) -> str:
        """
        Generate library status report.
        
        Returns:
            Formatted report string with library statistics
        """
        runbooks = self.list_runbooks()
        review_due = self.get_review_due()
        candidates = self.get_automation_candidates()
        
        total = len(runbooks)
        automated = len([r for r in runbooks 
                        if r.get("automation_status") in ["fully automated", "partially automated"]])
        automation_rate = (automated / total * 100) if total > 0 else 0
        
        overdue = len([r for r in review_due if r.get("overdue")])
        
        report = f"""
Runbook Library Report
{'=' * 50}
Generated: {datetime.now().isoformat()}

SUMMARY
{'-' * 50}
Total Runbooks: {total}
Automation Rate: {automation_rate:.0f}%
Reviews Due (14 days): {len(review_due)}
Overdue Reviews: {overdue}
Automation Candidates: {len(candidates)}

REVIEWS DUE
{'-' * 50}
"""
        if review_due:
            for r in review_due[:10]:
                status = "OVERDUE" if r["overdue"] else f"in {r['days_until']} days"
                report += f"  • {r['title']} - {status}\n"
            if len(review_due) > 10:
                report += f"  ... and {len(review_due) - 10} more\n"
        else:
            report += "  No reviews due\n"
        
        report += f"""
AUTOMATION CANDIDATES
{'-' * 50}
"""
        if candidates:
            for c in candidates[:10]:
                report += f"  • {c['title']} [{c['complexity']}]\n"
            if len(candidates) > 10:
                report += f"  ... and {len(candidates) - 10} more\n"
        else:
            report += "  No candidates identified\n"
        
        return report


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Manage runbook library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config config.json list
  %(prog)s --config config.json add --title "VPN Setup" --category network --type runbook
  %(prog)s --config config.json review --title "VPN Setup"
  %(prog)s --config config.json review-due --days 14
        """
    )
    parser.add_argument('--config', '-c', required=True, help='Config JSON path')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Debug logging')
    
    sub = parser.add_subparsers(dest='cmd', help='Command')
    
    # List
    ls = sub.add_parser('list', help='List runbooks')
    ls.add_argument('--category', choices=RunbookCategory.values())
    ls.add_argument('--vendor', choices=Vendor.values())
    ls.add_argument('--automation', choices=AutomationStatus.values())
    
    # Add
    add = sub.add_parser('add', help='Add runbook')
    add.add_argument('--title', required=True)
    add.add_argument('--category', required=True, choices=RunbookCategory.values())
    add.add_argument('--type', required=True, choices=DocumentType.values(), dest='doc_type')
    add.add_argument('--vendors', nargs='+', choices=Vendor.values(), default=[])
    add.add_argument('--complexity', choices=ComplexityLevel.values(), default='intermediate')
    add.add_argument('--owner')
    add.add_argument('--tags', nargs='+')
    
    # Review
    rev = sub.add_parser('review', help='Mark runbook as reviewed')
    rev.add_argument('--title', required=True)
    
    # Automate
    auto = sub.add_parser('automate', help='Update automation status')
    auto.add_argument('--title', required=True)
    auto.add_argument('--status', required=True, choices=AutomationStatus.values())
    
    # Review due
    due = sub.add_parser('review-due', help='List runbooks due for review')
    due.add_argument('--days', type=int, default=14)
    
    # Candidates
    sub.add_parser('candidates', help='List automation candidates')
    
    # Report
    sub.add_parser('report', help='Generate library report')
    
    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    # Load environment variables from .env file if present
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv is optional

    if args.verbose:
        enable_debug()

    if not Path(args.config).exists():
        logger.error(f"Config not found: {args.config}")
        sys.exit(1)
    
    try:
        mgr = RunbookManager(
            args.config,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        if args.cmd == 'list':
            runbooks = mgr.list_runbooks(
                category=args.category,
                vendor=args.vendor,
                automation_status=args.automation
            )
            print(f"\nFound {len(runbooks)} runbooks:\n")
            for r in runbooks:
                print(f"  [{r['category']}] {r['title']} - {r['automation_status']}")
        
        elif args.cmd == 'add':
            runbook = Runbook(
                title=args.title,
                category=RunbookCategory(args.category),
                doc_type=DocumentType(args.doc_type),
                vendors=args.vendors,
                complexity=ComplexityLevel(args.complexity),
                owner=args.owner,
                tags=args.tags or [],
            )
            mgr.add_runbook(runbook)
            print(f"Added: {args.title}")
        
        elif args.cmd == 'review':
            result = mgr.mark_reviewed(args.title)
            print(f"Reviewed: {args.title} (next review: {result.get('next_review')})")
        
        elif args.cmd == 'automate':
            mgr.update_automation_status(args.title, args.status)
            print(f"Updated: {args.title} → {args.status}")
        
        elif args.cmd == 'review-due':
            runbooks = mgr.get_review_due(args.days)
            print(f"\nRunbooks due for review ({args.days} days):\n")
            for r in runbooks:
                status = "OVERDUE" if r["overdue"] else f"in {r['days_until']} days"
                print(f"  • {r['title']} - {status}")
            print(f"\nTotal: {len(runbooks)}")
        
        elif args.cmd == 'candidates':
            candidates = mgr.get_automation_candidates()
            print("\nAutomation candidates:\n")
            for c in candidates:
                print(f"  • {c['title']} [{c['complexity']}]")
            print(f"\nTotal: {len(candidates)}")
        
        elif args.cmd == 'report':
            print(mgr.generate_report())
    
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
