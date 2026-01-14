#!/usr/bin/env python3
"""
Azure Migration Pipeline Tracker - Manage service migration in Notion

Purpose:
    Track Azure services through Lab → Production → Customer Offerings pipeline.
    Enforces stage gate validation before advancing services.

Usage:
    python azure_pipeline_sync.py --config config.json list
    python azure_pipeline_sync.py --config config.json add --name "Azure VPN" --category "Networking"
    python azure_pipeline_sync.py --config config.json update --name "Azure VPN" --stage "production"
    python azure_pipeline_sync.py --config config.json advance --name "Azure VPN"
    python azure_pipeline_sync.py --config config.json report

Requirements:
    pip install notion-client --break-system-packages

Author: OberaConnect
Created: 2025
Refactored: 2025 - Now uses BaseSyncClient with typed models and stage gate validation
"""

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    MakerCheckerError,
)

# Import NotionWrapper for static property builders
from notion_client_wrapper import NotionWrapper

# Setup logging via centralized config
logger = get_logger(__name__)


# =============================================================================
# Enums and Constants
# =============================================================================

class AzureCategory(Enum):
    """Azure service categories - maps to 75+ services across 15 categories."""
    COMPUTE = "Compute"
    NETWORKING = "Networking"
    STORAGE = "Storage"
    DATABASES = "Databases"
    IDENTITY = "Identity"
    SECURITY = "Security"
    MANAGEMENT = "Management"
    DEVOPS = "DevOps"
    AI_ML = "AI/ML"
    ANALYTICS = "Analytics"
    INTEGRATION = "Integration"
    IOT = "IoT"
    MIGRATION = "Migration"
    BACKUP = "Backup"
    MONITORING = "Monitoring"
    
    @classmethod
    def values(cls) -> List[str]:
        return [c.value for c in cls]


class PipelineStage(Enum):
    """Pipeline stages - services progress through these in order."""
    BACKLOG = "backlog"
    LAB_TESTING = "lab testing"
    PRODUCTION_VALIDATION = "production validation"
    CUSTOMER_READY = "customer ready"
    DEPRECATED = "deprecated"
    
    @classmethod
    def values(cls) -> List[str]:
        return [s.value for s in cls]
    
    def next_stage(self) -> Optional['PipelineStage']:
        """Get the next stage in the pipeline."""
        order = [
            PipelineStage.BACKLOG,
            PipelineStage.LAB_TESTING,
            PipelineStage.PRODUCTION_VALIDATION,
            PipelineStage.CUSTOMER_READY,
        ]
        try:
            idx = order.index(self)
            if idx < len(order) - 1:
                return order[idx + 1]
        except ValueError:
            pass
        return None


class TestStatus(Enum):
    """Test/validation status for lab and production."""
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    PASSED = "passed"
    FAILED = "failed"
    
    @classmethod
    def values(cls) -> List[str]:
        return [s.value for s in cls]


@dataclass
class StageGateResult:
    """Result of stage gate validation."""
    can_advance: bool
    current_stage: PipelineStage
    next_stage: Optional[PipelineStage]
    blockers: List[str] = field(default_factory=list)
    
    @property
    def is_blocked(self) -> bool:
        return len(self.blockers) > 0


@dataclass
class AzureService:
    """
    Represents an Azure service in the migration pipeline.
    
    Typed data class for validation and IDE support.
    """
    name: str
    category: AzureCategory
    
    # Pipeline tracking
    stage: PipelineStage = PipelineStage.BACKLOG
    lab_status: TestStatus = TestStatus.NOT_STARTED
    prod_status: TestStatus = TestStatus.NOT_STARTED
    
    # Metadata
    owner: Optional[str] = None
    target_date: Optional[str] = None
    customer_requests: int = 0
    security_review: bool = False
    blockers: Optional[str] = None
    
    # Auto-populated
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Validate fields."""
        if not self.name:
            raise ValidationError("name", "Service name is required")
        if not isinstance(self.category, AzureCategory):
            # Try to convert from string
            if isinstance(self.category, str):
                try:
                    self.category = AzureCategory(self.category)
                except ValueError:
                    raise ValidationError("category", f"Invalid category: {self.category}")
    
    def check_stage_gate(self) -> StageGateResult:
        """
        Check if service can advance to next stage.
        
        Stage gate rules:
        - Backlog → Lab: Always allowed
        - Lab → Production: Lab status must be "passed"
        - Production → Customer Ready: Prod status "passed" AND security review complete
        """
        next_stage = self.stage.next_stage()
        blockers = []
        
        if next_stage is None:
            blockers.append(f"Cannot advance from '{self.stage.value}'")
            return StageGateResult(
                can_advance=False,
                current_stage=self.stage,
                next_stage=None,
                blockers=blockers
            )
        
        # Check prerequisites based on target stage
        if next_stage == PipelineStage.PRODUCTION_VALIDATION:
            if self.lab_status != TestStatus.PASSED:
                blockers.append("Lab testing must pass before production validation")
        
        elif next_stage == PipelineStage.CUSTOMER_READY:
            if self.prod_status != TestStatus.PASSED:
                blockers.append("Production validation must pass before customer ready")
            if not self.security_review:
                blockers.append("Security review must be complete before customer ready")
        
        return StageGateResult(
            can_advance=len(blockers) == 0,
            current_stage=self.stage,
            next_stage=next_stage,
            blockers=blockers
        )


# =============================================================================
# Azure Pipeline Manager - Using BaseSyncClient
# =============================================================================

class AzurePipelineManager(BaseSyncClient):
    """
    Manage Azure service migration tracking in Notion.
    
    Inherits from BaseSyncClient which provides:
    - Configuration loading and validation
    - Notion client initialization with dry-run support
    - Retry logic for API calls
    - Page caching
    
    Operations:
    - list: Query services with filtering
    - add: Create new service entry
    - update: Modify service properties
    - advance: Move to next pipeline stage (with validation)
    - report: Generate pipeline status report
    """
    
    @property
    def primary_database(self) -> str:
        """Primary database for Azure pipeline."""
        return "azure_pipeline"
    
    def build_properties(self, service: AzureService) -> Dict:
        """Build Notion page properties from AzureService."""
        
        properties = {
            "Service Name": NotionWrapper.prop_title(service.name),
            "Category": NotionWrapper.prop_select(service.category.value),
            "Pipeline Stage": NotionWrapper.prop_select(service.stage.value),
            "Lab Status": NotionWrapper.prop_select(service.lab_status.value),
            "Production Status": NotionWrapper.prop_select(service.prod_status.value),
            "Customer Requests": NotionWrapper.prop_number(service.customer_requests),
            "Security Review": NotionWrapper.prop_checkbox(service.security_review),
            "Last Updated": NotionWrapper.prop_date(
                service.last_updated.strftime("%Y-%m-%d")
            ),
        }
        
        if service.owner:
            properties["Owner"] = NotionWrapper.prop_rich_text(service.owner)
        if service.target_date:
            properties["Target Date"] = NotionWrapper.prop_date(service.target_date)
        if service.blockers:
            properties["Blockers"] = NotionWrapper.prop_rich_text(service.blockers)
        
        return properties
    
    def _page_to_service(self, page: Dict) -> Dict:
        """Extract service data from Notion page."""
        return {
            "id": page["id"],
            "name": self.client.extract_title(page) if self.client else "",
            "category": self.client.extract_property(page, "Category") if self.client else "",
            "stage": self.client.extract_property(page, "Pipeline Stage") if self.client else "",
            "lab_status": self.client.extract_property(page, "Lab Status") if self.client else "",
            "prod_status": self.client.extract_property(page, "Production Status") if self.client else "",
            "customer_requests": self.client.extract_property(page, "Customer Requests") if self.client else 0,
            "security_review": self.client.extract_property(page, "Security Review") if self.client else False,
            "blockers": self.client.extract_property(page, "Blockers") if self.client else "",
        }
    
    def list_services(
        self,
        stage: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        List services with optional filtering.
        
        Args:
            stage: Filter by pipeline stage
            category: Filter by Azure category
            
        Returns:
            List of service dictionaries
        """
        if self.dry_run:
            self.logger.info("[DRY RUN] Would list services")
            return []
        
        # Build filter
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
        
        # Query with sorting
        pages = self.query_database(
            self.primary_database,
            filter_obj=filter_obj,
            sorts=[{"property": "Pipeline Stage", "direction": "ascending"}]
        )
        
        return [self._page_to_service(page) for page in pages]
    
    def add_service(self, service: AzureService) -> Dict:
        """
        Add a new service to the pipeline.
        
        Args:
            service: AzureService object with service details
            
        Returns:
            Result dictionary with status and page info
            
        Raises:
            ValidationError: If service already exists
        """
        self.logger.info(f"Adding service: {service.name} ({service.category.value})")
        
        # Build properties
        properties = self.build_properties(service)
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would add service: {service.name}")
            return {"status": "dry_run", "name": service.name}
        
        # Check for duplicates
        existing = self.client.find_page_by_title(
            self.config.databases.require(self.primary_database),
            service.name
        )
        if existing:
            raise ValidationError("name", f"Service '{service.name}' already exists")
        
        # Create page (uses inherited retry logic)
        result = self.create_page(self.primary_database, properties)
        
        self.logger.info(f"Added service: {service.name}")
        return {
            "status": "success",
            "name": service.name,
            "page_id": result.get("id"),
        }
    
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
        """
        Update an existing service.
        
        Args:
            name: Service name to update
            stage: New pipeline stage
            lab_status: New lab test status
            prod_status: New production test status
            blockers: Blocker text (empty string to clear)
            security_review: Security review completed
            customer_requests: Number of customer requests
            
        Returns:
            Result dictionary
            
        Raises:
            ValidationError: If service not found or invalid values
        """
        self.logger.info(f"Updating service: {name}")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would update service: {name}")
            return {"status": "dry_run", "name": name}
        
        # Find the service
        page = self.client.find_page_by_title(
            self.config.databases.require(self.primary_database),
            name
        )
        if not page:
            raise ValidationError("name", f"Service '{name}' not found")
        
        # Build properties to update
        properties = {
            "Last Updated": NotionWrapper.prop_date(
                datetime.now(timezone.utc).strftime("%Y-%m-%d")
            )
        }
        
        if stage is not None:
            if stage not in PipelineStage.values():
                raise ValidationError("stage", f"Invalid stage: {stage}")
            properties["Pipeline Stage"] = NotionWrapper.prop_select(stage)
        
        if lab_status is not None:
            if lab_status not in TestStatus.values():
                raise ValidationError("lab_status", f"Invalid lab status: {lab_status}")
            properties["Lab Status"] = NotionWrapper.prop_select(lab_status)
        
        if prod_status is not None:
            if prod_status not in TestStatus.values():
                raise ValidationError("prod_status", f"Invalid prod status: {prod_status}")
            properties["Production Status"] = NotionWrapper.prop_select(prod_status)
        
        if blockers is not None:
            properties["Blockers"] = NotionWrapper.prop_rich_text(blockers)
        if security_review is not None:
            properties["Security Review"] = NotionWrapper.prop_checkbox(security_review)
        if customer_requests is not None:
            properties["Customer Requests"] = NotionWrapper.prop_number(customer_requests)
        
        # Update page
        result = self.update_page(page["id"], properties)
        
        self.logger.info(f"Updated service: {name}")
        return {"status": "success", "name": name, "page_id": page["id"]}
    
    def advance_stage(self, name: str, force: bool = False) -> Dict:
        """
        Advance a service to the next pipeline stage.
        
        Validates stage gate prerequisites before advancing.
        
        Args:
            name: Service name to advance
            force: If True, skip validation (not recommended)
            
        Returns:
            Result dictionary with old/new stage
            
        Raises:
            MakerCheckerError: If stage gate validation fails
            ValidationError: If service not found
        """
        self.logger.info(f"Advancing service: {name}")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would advance service: {name}")
            return {"status": "dry_run", "name": name}
        
        # Find the service
        page = self.client.find_page_by_title(
            self.config.databases.require(self.primary_database),
            name
        )
        if not page:
            raise ValidationError("name", f"Service '{name}' not found")
        
        # Extract current state
        current_stage_str = self.client.extract_property(page, "Pipeline Stage") or "backlog"
        lab_status_str = self.client.extract_property(page, "Lab Status") or "not started"
        prod_status_str = self.client.extract_property(page, "Production Status") or "not started"
        security_review = self.client.extract_property(page, "Security Review") or False
        
        # Convert to enums
        try:
            current_stage = PipelineStage(current_stage_str)
            lab_status = TestStatus(lab_status_str)
            prod_status = TestStatus(prod_status_str)
        except ValueError as e:
            raise ValidationError("stage", f"Invalid enum value: {e}")
        
        # Build service object for validation
        service = AzureService(
            name=name,
            category=AzureCategory.COMPUTE,  # Not needed for validation
            stage=current_stage,
            lab_status=lab_status,
            prod_status=prod_status,
            security_review=security_review,
        )
        
        # Check stage gate
        gate_result = service.check_stage_gate()
        
        if not gate_result.can_advance and not force:
            self.logger.error(f"Cannot advance {name}: {gate_result.blockers}")
            raise MakerCheckerError(
                f"Stage gate validation failed for '{name}'",
                {
                    "current_stage": current_stage.value,
                    "blockers": gate_result.blockers,
                }
            )
        
        if force and not gate_result.can_advance:
            self.logger.warning(f"Force advancing {name} despite blockers: {gate_result.blockers}")
        
        # Advance to next stage
        next_stage = gate_result.next_stage
        if next_stage is None:
            raise ValidationError("stage", f"Cannot advance from '{current_stage.value}'")
        
        result = self.update_service(name, stage=next_stage.value)
        
        self.logger.info(f"Advanced {name}: {current_stage.value} → {next_stage.value}")
        return {
            "status": "success",
            "name": name,
            "old_stage": current_stage.value,
            "new_stage": next_stage.value,
        }
    
    def sync(self, **kwargs) -> List[Dict]:
        """
        Required by BaseSyncClient - returns list of all services.
        
        For Azure pipeline, use specific methods (list_services, add_service, etc.)
        """
        return self.list_services()
    
    def generate_report(self) -> str:
        """
        Generate pipeline status report.
        
        Returns:
            Formatted report string with pipeline overview
        """
        services = self.list_services()
        
        # Group by stage
        by_stage: Dict[str, List[Dict]] = {stage: [] for stage in PipelineStage.values()}
        for s in services:
            stage = s.get("stage", "backlog")
            if stage in by_stage:
                by_stage[stage].append(s)
        
        total = len(services)
        ready = len(by_stage.get("customer ready", []))
        blocked = len([s for s in services if s.get("blockers")])
        
        # Calculate percentages safely
        ready_pct = (ready / total * 100) if total > 0 else 0
        
        report = f"""
Azure Migration Pipeline Report
{'=' * 50}
Generated: {datetime.now().isoformat()}

SUMMARY
{'-' * 50}
Total Services: {total}
Customer Ready: {ready} ({ready_pct:.0f}%)
Currently Blocked: {blocked}

PIPELINE OVERVIEW
{'-' * 50}
"""
        for stage in PipelineStage.values():
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
    parser = argparse.ArgumentParser(
        description="Manage Azure service migration pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config config.json list
  %(prog)s --config config.json add --name "Azure VPN" --category Networking
  %(prog)s --config config.json update --name "Azure VPN" --stage "lab testing"
  %(prog)s --config config.json advance --name "Azure VPN"
        """
    )
    parser.add_argument('--config', '-c', required=True, help='Config JSON path')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Debug logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # List
    list_parser = subparsers.add_parser('list', help='List services')
    list_parser.add_argument('--stage', choices=PipelineStage.values())
    list_parser.add_argument('--category', choices=AzureCategory.values())
    
    # Add
    add_parser = subparsers.add_parser('add', help='Add service')
    add_parser.add_argument('--name', required=True)
    add_parser.add_argument('--category', required=True, choices=AzureCategory.values())
    add_parser.add_argument('--owner')
    add_parser.add_argument('--target-date')
    
    # Update
    update_parser = subparsers.add_parser('update', help='Update service')
    update_parser.add_argument('--name', required=True)
    update_parser.add_argument('--stage', choices=PipelineStage.values())
    update_parser.add_argument('--lab-status', choices=TestStatus.values())
    update_parser.add_argument('--prod-status', choices=TestStatus.values())
    update_parser.add_argument('--blockers')
    update_parser.add_argument('--security-review', type=lambda x: x.lower() == 'true')
    update_parser.add_argument('--customer-requests', type=int)
    
    # Advance
    advance_parser = subparsers.add_parser('advance', help='Advance to next stage')
    advance_parser.add_argument('--name', required=True)
    advance_parser.add_argument('--force', action='store_true', help='Skip validation')
    
    # Report
    subparsers.add_parser('report', help='Generate report')
    
    args = parser.parse_args()

    if not args.command:
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
        manager = AzurePipelineManager(
            args.config,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        if args.command == 'list':
            services = manager.list_services(stage=args.stage, category=args.category)
            print(f"\nFound {len(services)} services:\n")
            for s in services:
                print(f"  [{s['stage']}] {s['name']} - {s['category']}")
        
        elif args.command == 'add':
            service = AzureService(
                name=args.name,
                category=AzureCategory(args.category),
                owner=args.owner,
                target_date=args.target_date,
            )
            manager.add_service(service)
            print(f"Added: {args.name}")
        
        elif args.command == 'update':
            manager.update_service(
                args.name,
                stage=args.stage,
                lab_status=args.lab_status,
                prod_status=args.prod_status,
                blockers=args.blockers,
                security_review=args.security_review,
                customer_requests=args.customer_requests
            )
            print(f"Updated: {args.name}")
        
        elif args.command == 'advance':
            result = manager.advance_stage(args.name, force=args.force)
            print(f"Advanced: {args.name} ({result['old_stage']} → {result['new_stage']})")
        
        elif args.command == 'report':
            print(manager.generate_report())
    
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except MakerCheckerError as e:
        logger.error(f"Stage gate failed: {e}")
        sys.exit(1)
    except NotionSyncError as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
