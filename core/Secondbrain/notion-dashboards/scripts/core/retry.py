"""
Retry decorator with exponential backoff for transient failures.

Handles Notion API rate limits and temporary network issues gracefully.
"""

import functools
import time
from typing import Tuple, Type, Callable, TypeVar, Any

from core.logging_config import get_logger
from core.errors import RateLimitError, NotionSyncError

logger = get_logger(__name__)

# Type variable for generic return type
T = TypeVar('T')


def retry_on_exception(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    max_backoff: float = 60.0,
    on_retry: Callable[[Exception, int], None] = None
) -> Callable:
    """
    Decorator to retry function on specified exceptions with exponential backoff.
    
    Args:
        exceptions: Tuple of exception types to catch and retry
        max_retries: Maximum number of retry attempts (default 3)
        backoff_factor: Base delay multiplier in seconds (default 1.0)
        max_backoff: Maximum delay between retries (default 60s)
        on_retry: Optional callback(exception, attempt) called before each retry
    
    Returns:
        Decorated function that retries on specified exceptions
    
    Example:
        @retry_on_exception(exceptions=(APIError,), max_retries=3)
        def call_api():
            return client.create_page(...)
    
    Backoff schedule (with factor=1.0):
        Attempt 1 failure -> wait 1s
        Attempt 2 failure -> wait 2s
        Attempt 3 failure -> wait 4s
        Attempt 4 failure -> raise exception
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate backoff with exponential increase
                        wait_time = min(
                            backoff_factor * (2 ** attempt),
                            max_backoff
                        )
                        
                        # Check for rate limit hint
                        if isinstance(e, RateLimitError) and e.retry_after:
                            wait_time = max(wait_time, e.retry_after)
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        
                        # Call optional callback
                        if on_retry:
                            on_retry(e, attempt)
                        
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}"
                        )
            
            # Re-raise the last exception after all retries exhausted
            raise last_exception
        
        return wrapper
    return decorator


def retry_notion_api(
    max_retries: int = 3,
    backoff_factor: float = 0.5
) -> Callable:
    """
    Specialized retry decorator for Notion API calls.
    
    Pre-configured for common Notion API failure modes:
    - Rate limits (429)
    - Temporary server errors (5xx)
    - Network timeouts
    
    Args:
        max_retries: Maximum retry attempts (default 3)
        backoff_factor: Base delay in seconds (default 0.5)
    
    Example:
        @retry_notion_api()
        def create_page(client, db_id, properties):
            return client.create_page(db_id, properties)
    """
    # Import here to avoid circular dependency
    try:
        from notion_client.errors import APIResponseError, HTTPResponseError
        notion_exceptions = (APIResponseError, HTTPResponseError, RateLimitError)
    except ImportError:
        # Fallback if notion-client not installed
        notion_exceptions = (RateLimitError, ConnectionError, TimeoutError)
    
    return retry_on_exception(
        exceptions=notion_exceptions,
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        max_backoff=30.0  # Cap at 30s for API calls
    )


class RetryBudget:
    """
    Track retry budget across multiple operations.
    
    Useful for batch operations where you want to limit
    total retries rather than per-call retries.
    
    Example:
        budget = RetryBudget(max_total_retries=10)
        for item in items:
            try:
                with budget:
                    process(item)
            except RetryBudgetExhausted:
                logger.error("Too many failures, stopping batch")
                break
    """
    
    def __init__(self, max_total_retries: int = 10):
        self.max_total_retries = max_total_retries
        self.retries_used = 0
        self.failures = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.retries_used += 1
            self.failures.append(str(exc_val))
            
            if self.retries_used >= self.max_total_retries:
                raise RetryBudgetExhausted(
                    f"Retry budget exhausted after {self.retries_used} failures"
                ) from exc_val
        return False  # Don't suppress the exception
    
    @property
    def remaining(self) -> int:
        return max(0, self.max_total_retries - self.retries_used)
    
    def reset(self) -> None:
        self.retries_used = 0
        self.failures = []


class RetryBudgetExhausted(NotionSyncError):
    """Raised when retry budget is exhausted."""
    pass
