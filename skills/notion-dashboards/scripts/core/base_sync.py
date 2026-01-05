"""
Base class for all Notion sync operations.

Provides common functionality:
- Configuration loading
- Notion client initialization
- Dry-run support
- Logging setup
- Error handling patterns
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from core.config import Config, load_config
from core.errors import (
    NotionSyncError,
    ConfigurationError,
    DatabaseNotFoundError,
    map_notion_api_error,
)
from core.logging_config import get_logger
from core.retry import retry_notion_api

# Import NotionWrapper - handle path flexibility
try:
    from notion_client_wrapper import NotionWrapper
except ImportError:
    from scripts.notion_client_wrapper import NotionWrapper


class BaseSyncClient(ABC):
    """
    Base class for all sync operations.
    
    Provides:
    - Unified configuration loading
    - Notion client initialization with dry-run support
    - Common database access patterns
    - Standardized error handling
    
    Subclasses must implement:
    - primary_database: Property returning the main database name
    - sync(): Main sync operation
    
    Example:
        class CustomerSync(BaseSyncClient):
            @property
            def primary_database(self) -> str:
                return "customer_status"
            
            def sync(self, **kwargs) -> List[Dict]:
                # Implementation...
    """
    
    def __init__(
        self,
        config_path: str,
        dry_run: bool = False,
        verbose: bool = False
    ):
        """
        Initialize sync client.
        
        Args:
            config_path: Path to config JSON file
            dry_run: If True, preview changes without writing
            verbose: If True, enable debug logging
        """
        self.config_path = config_path
        self.dry_run = dry_run
        self.verbose = verbose
        
        # Setup logging
        self.logger = get_logger(self.__class__.__name__)
        if verbose:
            import logging
            self.logger.setLevel(logging.DEBUG)
        
        # Load configuration
        self.config = load_config(config_path)
        
        # Initialize Notion client (None if dry-run)
        self._client: Optional[NotionWrapper] = None
        if not dry_run:
            self._init_client()
        
        # Cache for page lookups
        self._page_cache: Dict[str, Dict[str, str]] = {}
    
    def _init_client(self) -> None:
        """Initialize Notion client with token from config."""
        try:
            self._client = NotionWrapper(token=self.config.notion_token)
            self.logger.debug("Notion client initialized")
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize Notion client: {e}"
            )
    
    @property
    def client(self) -> NotionWrapper:
        """
        Get Notion client instance.
        
        Raises:
            NotionSyncError: If in dry-run mode (no client available)
        """
        if self._client is None:
            raise NotionSyncError(
                "Notion client not available in dry-run mode"
            )
        return self._client
    
    @property
    @abstractmethod
    def primary_database(self) -> str:
        """
        Return the name of the primary database for this sync.
        
        Used for validation and default operations.
        """
        pass
    
    def get_db_id(self, db_name: str) -> str:
        """
        Get database ID by name from config.
        
        Args:
            db_name: Database name (e.g., "customer_status")
        
        Returns:
            Database ID string
        
        Raises:
            DatabaseNotFoundError: If database not configured
        """
        return self.config.databases.require(db_name)
    
    @property
    def primary_db_id(self) -> str:
        """Get the primary database ID for this sync."""
        return self.get_db_id(self.primary_database)
    
    # =========================================================================
    # Common Page Operations with Caching
    # =========================================================================
    
    def find_page_by_title(
        self,
        db_name: str,
        title: str,
        use_cache: bool = True
    ) -> Optional[Dict]:
        """
        Find a page by title with optional caching.
        
        Args:
            db_name: Database name
            title: Page title to find
            use_cache: Whether to use/update cache
        
        Returns:
            Page object or None if not found
        """
        if self.dry_run:
            return None
        
        cache_key = f"{db_name}:{title}"
        
        if use_cache and db_name in self._page_cache:
            if title in self._page_cache[db_name]:
                page_id = self._page_cache[db_name][title]
                # Return minimal cached result
                return {"id": page_id, "_cached": True}
        
        db_id = self.get_db_id(db_name)
        page = self.client.find_page_by_title(db_id, title)
        
        if page and use_cache:
            if db_name not in self._page_cache:
                self._page_cache[db_name] = {}
            self._page_cache[db_name][title] = page["id"]
        
        return page
    
    def get_page_id(
        self,
        db_name: str,
        title: str
    ) -> Optional[str]:
        """
        Get just the page ID for a title.
        
        Args:
            db_name: Database name
            title: Page title
        
        Returns:
            Page ID or None
        """
        page = self.find_page_by_title(db_name, title)
        return page["id"] if page else None
    
    def clear_cache(self, db_name: Optional[str] = None) -> None:
        """Clear page cache for a database or all caches."""
        if db_name:
            self._page_cache.pop(db_name, None)
        else:
            self._page_cache.clear()
    
    # =========================================================================
    # Wrapped API Operations with Retry
    # =========================================================================
    
    @retry_notion_api()
    def create_page(self, db_name: str, properties: Dict) -> Dict:
        """
        Create page with retry logic.
        
        Args:
            db_name: Target database name
            properties: Page properties
        
        Returns:
            Created page object
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would create page in {db_name}")
            return {"id": "dry-run-id", "_dry_run": True}
        
        db_id = self.get_db_id(db_name)
        try:
            return self.client.create_page(db_id, properties)
        except Exception as e:
            raise map_notion_api_error(e)
    
    @retry_notion_api()
    def update_page(self, page_id: str, properties: Dict) -> Dict:
        """
        Update page with retry logic.
        
        Args:
            page_id: Page to update
            properties: Properties to update
        
        Returns:
            Updated page object
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would update page {page_id}")
            return {"id": page_id, "_dry_run": True}
        
        try:
            return self.client.update_page(page_id, properties)
        except Exception as e:
            raise map_notion_api_error(e)
    
    @retry_notion_api()
    def upsert_page(
        self,
        db_name: str,
        title: str,
        properties: Dict
    ) -> tuple[Dict, str]:
        """
        Update if exists, create if not.
        
        Args:
            db_name: Target database name
            title: Page title for matching
            properties: Page properties
        
        Returns:
            Tuple of (page, action) where action is "created" or "updated"
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would upsert '{title}' in {db_name}")
            return {"id": "dry-run-id", "_dry_run": True}, "dry_run"
        
        db_id = self.get_db_id(db_name)
        try:
            return self.client.upsert_page(db_id, title, properties)
        except Exception as e:
            raise map_notion_api_error(e)
    
    @retry_notion_api()
    def query_database(
        self,
        db_name: str,
        filter_obj: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Query database with retry logic.
        
        Args:
            db_name: Database to query
            filter_obj: Optional Notion filter
            sorts: Optional sort configuration
        
        Returns:
            List of matching pages
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would query {db_name}")
            return []
        
        db_id = self.get_db_id(db_name)
        try:
            return self.client.query_database(db_id, filter_obj, sorts)
        except Exception as e:
            raise map_notion_api_error(e)
    
    # =========================================================================
    # Abstract Methods for Subclasses
    # =========================================================================
    
    @abstractmethod
    def sync(self, **kwargs) -> List[Dict]:
        """
        Execute the sync operation.
        
        Must be implemented by subclasses.
        
        Returns:
            List of sync results
        """
        pass
    
    def generate_report(self, results: List[Dict]) -> str:
        """
        Generate summary report from sync results.
        
        Can be overridden by subclasses for custom reporting.
        
        Args:
            results: List of sync result dictionaries
        
        Returns:
            Formatted report string
        """
        from datetime import datetime
        
        successful = len([r for r in results if r.get("status") == "success"])
        failed = len([r for r in results if r.get("status") == "error"])
        dry_run = len([r for r in results if r.get("status") == "dry_run"])
        
        return f"""
{self.__class__.__name__} Report
{'=' * 40}
Timestamp: {datetime.now().isoformat()}
Total: {len(results)}
Successful: {successful}
Failed: {failed}
Dry Run: {dry_run}
"""
    
    # =========================================================================
    # Maker/Checker Support
    # =========================================================================
    
    def check_bulk_operation(self, count: int) -> bool:
        """
        Check if operation exceeds bulk threshold.
        
        Args:
            count: Number of items to process
        
        Returns:
            True if over threshold (requires confirmation)
        """
        if not self.config.maker_checker.enabled:
            return False
        
        threshold = self.config.maker_checker.bulk_change_threshold
        if count > threshold:
            self.logger.warning(
                f"Bulk operation: {count} items exceeds threshold of {threshold}"
            )
            return True
        return False
    
    def check_health_drop(
        self,
        old_score: int,
        new_score: int
    ) -> bool:
        """
        Check if health score drop exceeds threshold.
        
        Args:
            old_score: Previous health score
            new_score: New health score
        
        Returns:
            True if drop exceeds threshold (requires review)
        """
        if not self.config.maker_checker.enabled:
            return False
        
        threshold = self.config.maker_checker.health_drop_threshold
        drop = old_score - new_score
        
        if drop > threshold:
            self.logger.warning(
                f"Health drop: {drop} points exceeds threshold of {threshold}"
            )
            return True
        return False
