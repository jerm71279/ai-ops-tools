"""
Custom exceptions for OberaConnect Notion integration.

Provides a clear exception hierarchy for better error handling
and debugging across all sync operations.
"""

from typing import Optional, Dict, Any


class NotionSyncError(Exception):
    """
    Base exception for all Notion sync operations.
    
    All custom exceptions inherit from this, allowing callers
    to catch all sync-related errors with a single except clause.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(NotionSyncError):
    """
    Configuration is missing, invalid, or incomplete.
    
    Raised when:
    - Config file not found
    - Required database ID missing
    - Invalid token format
    - Missing required settings
    """
    pass


class DatabaseNotFoundError(NotionSyncError):
    """
    Database ID not configured or doesn't exist in Notion.
    
    Raised when:
    - Database ID not in config
    - Database was deleted from Notion
    - Integration lacks access to database
    """
    
    def __init__(self, db_name: str, db_id: Optional[str] = None):
        details = {"database_name": db_name}
        if db_id:
            details["database_id"] = db_id
        super().__init__(
            f"Database '{db_name}' not found or not accessible",
            details
        )
        self.db_name = db_name
        self.db_id = db_id


class RateLimitError(NotionSyncError):
    """
    Notion API rate limit exceeded.
    
    Raised when:
    - HTTP 429 response from Notion
    - Too many requests in short period
    
    Contains retry_after hint when available.
    """
    
    def __init__(self, retry_after: Optional[float] = None):
        self.retry_after = retry_after
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            "Notion API rate limit exceeded",
            details
        )


class ValidationError(NotionSyncError):
    """
    Data validation failed before Notion API call.
    
    Raised when:
    - Required field missing
    - Field value out of range
    - Invalid enum value
    - Data type mismatch
    """
    
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.invalid_value = value
        details = {"field": field}
        if value is not None:
            details["invalid_value"] = str(value)[:100]  # Truncate long values
        super().__init__(f"Validation failed for '{field}': {message}", details)


class PageNotFoundError(NotionSyncError):
    """
    Expected page not found in database.
    
    Raised when:
    - find_page_by_title returns None unexpectedly
    - Page ID reference is stale (page was deleted)
    """
    
    def __init__(self, identifier: str, db_name: Optional[str] = None):
        details = {"identifier": identifier}
        if db_name:
            details["database"] = db_name
        super().__init__(f"Page not found: {identifier}", details)


class RelationError(NotionSyncError):
    """
    Database relation could not be established.
    
    Raised when:
    - Foreign key target doesn't exist
    - Circular relation detected
    - Relation property misconfigured
    """
    
    def __init__(self, source: str, target: str, reason: str):
        super().__init__(
            f"Cannot create relation from '{source}' to '{target}': {reason}",
            {"source": source, "target": target, "reason": reason}
        )


class DataSourceError(NotionSyncError):
    """
    External data source (UniFi, NinjaOne, etc.) failed.
    
    Raised when:
    - API connection failed
    - Authentication error
    - Unexpected response format
    """
    
    def __init__(self, source: str, message: str, original_error: Optional[Exception] = None):
        self.source = source
        self.original_error = original_error
        details = {"source": source}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(f"{source} error: {message}", details)


class MakerCheckerError(NotionSyncError):
    """
    Maker/checker validation failed - operation requires review.
    
    Raised when:
    - Bulk operation exceeds threshold
    - High-risk change without rollback plan
    - Health score drop exceeds threshold
    
    This is a soft error - operation can proceed with override.
    """
    
    def __init__(self, reason: str, threshold: Optional[int] = None):
        self.reason = reason
        self.threshold = threshold
        details = {"reason": reason}
        if threshold:
            details["threshold"] = threshold
        super().__init__(
            f"Maker/checker validation failed: {reason}",
            details
        )


# Convenience function for API error mapping
def map_notion_api_error(api_error: Exception) -> NotionSyncError:
    """
    Map notion-client library exceptions to our custom exceptions.
    
    Args:
        api_error: Exception from notion-client library
    
    Returns:
        Appropriate NotionSyncError subclass
    """
    error_str = str(api_error).lower()
    
    # Check for rate limit
    if "429" in error_str or "rate limit" in error_str:
        # Try to extract retry-after
        retry_after = None
        if hasattr(api_error, "headers"):
            retry_after = api_error.headers.get("retry-after")
            if retry_after:
                try:
                    retry_after = float(retry_after)
                except ValueError:
                    pass
        return RateLimitError(retry_after)
    
    # Check for not found
    if "404" in error_str or "not found" in error_str:
        return PageNotFoundError(str(api_error))
    
    # Check for validation
    if "400" in error_str or "validation" in error_str:
        return ValidationError("unknown", str(api_error))
    
    # Generic fallback
    return NotionSyncError(f"Notion API error: {api_error}")
