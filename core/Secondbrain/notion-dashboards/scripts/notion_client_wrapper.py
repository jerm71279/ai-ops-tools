#!/usr/bin/env python3
"""
Notion API Client - Wrapper using official notion-client SDK

Purpose:
    Provides authenticated access to Notion API using the official SDK
    with helper methods for database operations and property building.

Usage:
    from notion_client_wrapper import NotionWrapper
    client = NotionWrapper()
    client.create_page(database_id, properties)

Requirements:
    pip install notion-client --break-system-packages

Author: OberaConnect
Created: 2025
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from notion_client import Client
from notion_client.helpers import iterate_paginated_api

# Import security modules (graceful fallback if not available)
try:
    from secure_config import SecureConfig, get_config
    from structured_logging import setup_logging, get_logger, log_operation, log_audit_event
    from resilience import (
        retry_with_backoff, rate_limited, validate_site_name,
        validate_database_id, sanitize_for_notion, batch_with_recovery
    )
    SECURITY_MODULES_AVAILABLE = True
except ImportError:
    SECURITY_MODULES_AVAILABLE = False
    # Fallback: basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)


class NotionWrapper:
    """Wrapper around official notion-client SDK with helper methods."""
    
    def __init__(self, token: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize Notion client.
        
        Args:
            token: Notion integration token (or set NOTION_TOKEN env var)
            config_path: Path to config file with database IDs
        """
        self.token = token or os.getenv("NOTION_TOKEN")
        if not self.token:
            raise ValueError(
                "Notion token required. Set NOTION_TOKEN env var or pass token parameter."
            )
        
        # Initialize official client with 2022-06-28 API version
        # Note: The SDK defaults to 2025-09-03 which doesn't return properties
        # in database.retrieve() responses. Using 2022-06-28 for compatibility.
        self.client = Client(auth=self.token, notion_version="2022-06-28")
        
        self.config = {}
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration with database IDs."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        logger.info(f"Loaded config from {config_path}")
    
    # =========================================================================
    # Database Operations
    # =========================================================================
    
    def get_database(self, database_id: str) -> Dict:
        """Retrieve database schema and metadata."""
        if SECURITY_MODULES_AVAILABLE:
            database_id = validate_database_id(database_id)
        return self._retry_api_call(
            lambda: self.client.databases.retrieve(database_id=database_id)
        )

    def _retry_api_call(self, func, max_retries: int = 3) -> Any:
        """Execute API call with retry logic."""
        import time
        from notion_client.errors import APIResponseError

        last_error = None
        for attempt in range(max_retries):
            try:
                return func()
            except APIResponseError as e:
                last_error = e
                # Retry on rate limit (429) or server errors (5xx)
                if e.status in (429, 500, 502, 503, 504):
                    delay = min(2 ** attempt, 30)
                    logger.warning(f"API error {e.status}, retry {attempt+1}/{max_retries} in {delay}s")
                    time.sleep(delay)
                else:
                    raise
            except Exception as e:
                last_error = e
                delay = min(2 ** attempt, 30)
                logger.warning(f"Error: {e}, retry {attempt+1}/{max_retries} in {delay}s")
                time.sleep(delay)

        raise last_error
    
    def query_database(
        self,
        database_id: str,
        filter_obj: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Query database with optional filters and sorting.
        Uses pagination helper to get all results.
        
        Args:
            database_id: Database to query
            filter_obj: Notion filter object
            sorts: List of sort objects
        
        Returns:
            List of all matching pages
        """
        # Build request body
        body = {}
        if filter_obj:
            body["filter"] = filter_obj
        if sorts:
            body["sorts"] = sorts

        # Manual pagination since SDK's databases.query doesn't exist in 2022-06-28 API
        all_results = []
        has_more = True
        start_cursor = None

        while has_more:
            if start_cursor:
                body["start_cursor"] = start_cursor

            response = self._retry_api_call(
                lambda: self.client.request(
                    path=f"databases/{database_id}/query",
                    method="POST",
                    body=body
                )
            )

            all_results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return all_results
    
    def create_database(
        self,
        parent_page_id: str,
        title: str,
        properties: Dict
    ) -> Dict:
        """
        Create a new database.
        
        Args:
            parent_page_id: Parent page ID
            title: Database title
            properties: Database property schema
        
        Returns:
            Created database object
        """
        return self.client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": title}}],
            properties=properties
        )
    
    # =========================================================================
    # Page Operations
    # =========================================================================
    
    def create_page(self, database_id: str, properties: Dict) -> Dict:
        """
        Create a new page in a database.

        Args:
            database_id: Target database
            properties: Page properties matching database schema

        Returns:
            Created page object
        """
        if SECURITY_MODULES_AVAILABLE:
            database_id = validate_database_id(database_id)

        result = self._retry_api_call(
            lambda: self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
        )

        # Audit log the creation
        if SECURITY_MODULES_AVAILABLE:
            log_audit_event(
                action="create_page",
                target=f"database:{database_id[:8]}...",
                result="success",
                page_id=result.get("id", "unknown")
            )

        return result
    
    def update_page(self, page_id: str, properties: Dict) -> Dict:
        """
        Update an existing page's properties.

        Args:
            page_id: Page to update
            properties: Properties to update

        Returns:
            Updated page object
        """
        result = self._retry_api_call(
            lambda: self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
        )

        # Audit log the update
        if SECURITY_MODULES_AVAILABLE:
            log_audit_event(
                action="update_page",
                target=f"page:{page_id[:8]}...",
                result="success"
            )

        return result
    
    def get_page(self, page_id: str) -> Dict:
        """Retrieve a page by ID."""
        return self.client.pages.retrieve(page_id=page_id)
    
    def archive_page(self, page_id: str) -> Dict:
        """Archive (soft delete) a page."""
        return self.client.pages.update(
            page_id=page_id,
            archived=True
        )
    
    # =========================================================================
    # Block Operations
    # =========================================================================
    
    def get_block_children(self, block_id: str) -> List[Dict]:
        """Get all children of a block (with pagination)."""
        return list(iterate_paginated_api(
            self.client.blocks.children.list,
            block_id=block_id
        ))
    
    def append_block_children(self, block_id: str, children: List[Dict]) -> Dict:
        """Append children blocks to a block."""
        return self.client.blocks.children.append(
            block_id=block_id,
            children=children
        )
    
    # =========================================================================
    # Search Operations
    # =========================================================================
    
    def search(
        self,
        query: str = "",
        filter_type: Optional[str] = None,
        sort_direction: str = "descending"
    ) -> List[Dict]:
        """
        Search across all shared pages and databases.
        
        Args:
            query: Search query string
            filter_type: "page" or "database"
            sort_direction: "ascending" or "descending"
        
        Returns:
            List of matching objects
        """
        kwargs = {
            "query": query,
            "sort": {
                "direction": sort_direction,
                "timestamp": "last_edited_time"
            }
        }
        
        if filter_type:
            kwargs["filter"] = {"value": filter_type, "property": "object"}
        
        return list(iterate_paginated_api(
            self.client.search,
            **kwargs
        ))
    
    # =========================================================================
    # Property Builders - Helpers to construct Notion property objects
    # =========================================================================
    
    @staticmethod
    def prop_title(text: str) -> Dict:
        """Build title property."""
        return {"title": [{"text": {"content": text}}]}
    
    @staticmethod
    def prop_rich_text(text: str) -> Dict:
        """Build rich text property."""
        return {"rich_text": [{"text": {"content": text}}]}
    
    @staticmethod
    def prop_number(value: float) -> Dict:
        """Build number property."""
        return {"number": value}
    
    @staticmethod
    def prop_select(option: str) -> Dict:
        """Build select property."""
        return {"select": {"name": option}}
    
    @staticmethod
    def prop_multi_select(options: List[str]) -> Dict:
        """Build multi-select property."""
        return {"multi_select": [{"name": opt} for opt in options]}
    
    @staticmethod
    def prop_date(date_str: str, end_str: Optional[str] = None) -> Dict:
        """Build date property (ISO format: YYYY-MM-DD or full ISO datetime)."""
        date_obj = {"start": date_str}
        if end_str:
            date_obj["end"] = end_str
        return {"date": date_obj}
    
    @staticmethod
    def prop_checkbox(checked: bool) -> Dict:
        """Build checkbox property."""
        return {"checkbox": checked}
    
    @staticmethod
    def prop_url(url: str) -> Dict:
        """Build URL property."""
        return {"url": url}
    
    @staticmethod
    def prop_email(email: str) -> Dict:
        """Build email property."""
        return {"email": email}
    
    @staticmethod
    def prop_phone(phone: str) -> Dict:
        """Build phone number property."""
        return {"phone_number": phone}
    
    @staticmethod
    def prop_relation(page_ids: List[str]) -> Dict:
        """Build relation property."""
        return {"relation": [{"id": pid} for pid in page_ids]}
    
    @staticmethod
    def prop_people(user_ids: List[str]) -> Dict:
        """Build people property."""
        return {"people": [{"id": uid} for uid in user_ids]}
    
    @staticmethod
    def prop_files(urls: List[str]) -> Dict:
        """Build files property from external URLs."""
        return {
            "files": [
                {"type": "external", "name": url.split("/")[-1], "external": {"url": url}}
                for url in urls
            ]
        }
    
    # =========================================================================
    # Property Extractors - Helpers to read values from page objects
    # =========================================================================
    
    @staticmethod
    def extract_title(page: Dict) -> str:
        """Extract title text from a page object."""
        for prop_name, prop_value in page.get("properties", {}).items():
            if prop_value.get("type") == "title":
                title_arr = prop_value.get("title", [])
                if title_arr:
                    return title_arr[0].get("text", {}).get("content", "")
        return ""
    
    @staticmethod
    def extract_property(page: Dict, prop_name: str) -> Any:
        """
        Extract a property value from a page object.
        
        Handles all common property types and returns appropriate Python types.
        """
        prop = page.get("properties", {}).get(prop_name, {})
        prop_type = prop.get("type")
        
        extractors = {
            "title": lambda p: p.get("title", [{}])[0].get("text", {}).get("content", "") if p.get("title") else "",
            "rich_text": lambda p: p.get("rich_text", [{}])[0].get("text", {}).get("content", "") if p.get("rich_text") else "",
            "number": lambda p: p.get("number"),
            "select": lambda p: p.get("select", {}).get("name") if p.get("select") else None,
            "multi_select": lambda p: [s["name"] for s in p.get("multi_select", [])],
            "date": lambda p: p.get("date", {}).get("start") if p.get("date") else None,
            "checkbox": lambda p: p.get("checkbox", False),
            "url": lambda p: p.get("url"),
            "email": lambda p: p.get("email"),
            "phone_number": lambda p: p.get("phone_number"),
            "relation": lambda p: [r["id"] for r in p.get("relation", [])],
            "people": lambda p: [u["id"] for u in p.get("people", [])],
            "files": lambda p: [
                f.get("external", {}).get("url") or f.get("file", {}).get("url")
                for f in p.get("files", [])
            ],
            "formula": lambda p: p.get("formula", {}).get(p.get("formula", {}).get("type")),
            "rollup": lambda p: p.get("rollup", {}).get(p.get("rollup", {}).get("type")),
            "created_time": lambda p: p.get("created_time"),
            "created_by": lambda p: p.get("created_by", {}).get("id"),
            "last_edited_time": lambda p: p.get("last_edited_time"),
            "last_edited_by": lambda p: p.get("last_edited_by", {}).get("id"),
            "status": lambda p: p.get("status", {}).get("name") if p.get("status") else None,
        }
        
        extractor = extractors.get(prop_type)
        if extractor:
            try:
                return extractor(prop)
            except (IndexError, KeyError, TypeError):
                return None
        return prop
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    def find_page_by_title(self, database_id: str, title: str) -> Optional[Dict]:
        """Find a page by its title property."""
        # Get database to find title property name
        db = self.get_database(database_id)
        title_prop_name = None
        for name, prop in db.get("properties", {}).items():
            if prop.get("type") == "title":
                title_prop_name = name
                break
        
        if not title_prop_name:
            logger.warning("No title property found in database")
            return None
        
        # Query with title filter
        filter_obj = {
            "property": title_prop_name,
            "title": {"equals": title}
        }
        results = self.query_database(database_id, filter_obj=filter_obj)
        return results[0] if results else None
    
    def find_or_create_page(
        self,
        database_id: str,
        title: str,
        properties: Dict
    ) -> tuple[Dict, bool]:
        """
        Find existing page by title or create new one.
        
        Returns:
            Tuple of (page, created) where created is True if new page was made
        """
        existing = self.find_page_by_title(database_id, title)
        if existing:
            return existing, False
        
        page = self.create_page(database_id, properties)
        return page, True
    
    def upsert_page(
        self,
        database_id: str,
        title: str,
        properties: Dict
    ) -> tuple[Dict, str]:
        """
        Update page if exists, otherwise create.
        
        Returns:
            Tuple of (page, action) where action is "created" or "updated"
        """
        existing = self.find_page_by_title(database_id, title)
        if existing:
            page = self.update_page(existing["id"], properties)
            return page, "updated"
        
        page = self.create_page(database_id, properties)
        return page, "created"
    
    def bulk_create_pages(
        self,
        database_id: str,
        pages_data: List[Dict],
        batch_pause: float = 0.35
    ) -> List[Dict]:
        """
        Create multiple pages with rate limiting.
        
        Notion rate limit is ~3 requests/second, so we pause between requests.
        
        Args:
            database_id: Target database
            pages_data: List of property dicts for each page
            batch_pause: Seconds to pause between requests
        
        Returns:
            List of created page objects
        """
        import time
        
        results = []
        for i, properties in enumerate(pages_data):
            try:
                page = self.create_page(database_id, properties)
                results.append({"status": "success", "page": page})
            except Exception as e:
                logger.error(f"Failed to create page {i}: {e}")
                results.append({"status": "error", "error": str(e)})
            
            if i < len(pages_data) - 1:
                time.sleep(batch_pause)
        
        return results


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Quick CLI for testing connection and basic operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Notion API wrapper test")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--search", type=str, help="Search for pages/databases")
    parser.add_argument("--list-databases", action="store_true", help="List all databases")
    
    args = parser.parse_args()
    
    try:
        client = NotionWrapper()
        print("✓ Notion client initialized successfully")
        
        if args.test:
            # Test by listing users
            users = client.client.users.list()
            print(f"✓ Connected. Found {len(users.get('results', []))} users.")
        
        if args.search:
            results = client.search(query=args.search)
            print(f"\nSearch results for '{args.search}':")
            for r in results[:10]:
                obj_type = r.get("object")
                if obj_type == "page":
                    title = client.extract_title(r)
                    print(f"  [page] {title} ({r['id']})")
                elif obj_type == "database":
                    title = r.get("title", [{}])[0].get("text", {}).get("content", "Untitled")
                    print(f"  [database] {title} ({r['id']})")
        
        if args.list_databases:
            results = client.search(filter_type="database")
            print(f"\nDatabases ({len(results)}):")
            for r in results:
                title = r.get("title", [{}])[0].get("text", {}).get("content", "Untitled")
                print(f"  • {title}")
                print(f"    ID: {r['id']}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
