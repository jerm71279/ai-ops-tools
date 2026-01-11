#!/usr/bin/env python3
"""
Retry Decorator
Implements retry logic with exponential backoff for resilient automation.
"""

import time
import functools
import logging
from typing import Callable, Type, Tuple


logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] = None
):
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function(exception, attempt_number)
    
    Example:
        @retry(max_attempts=5, delay=2, backoff=2, exceptions=(ConnectionError,))
        def upload_file(path):
            # Upload logic that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts")
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


class RetryableError(Exception):
    """Exception class for errors that should trigger a retry."""
    pass


class NonRetryableError(Exception):
    """Exception class for errors that should NOT trigger a retry."""
    pass


# Example usage patterns
if __name__ == "__main__":
    # Setup logging for demonstration
    logging.basicConfig(level=logging.INFO)
    
    # Example 1: Simple retry
    @retry(max_attempts=3, delay=1)
    def flaky_operation():
        import random
        if random.random() < 0.7:
            raise ConnectionError("Network error")
        return "Success!"
    
    # Example 2: Retry with callback
    def log_retry(exception, attempt):
        print(f"Custom handler: Retry {attempt} due to {type(exception).__name__}")
    
    @retry(max_attempts=4, delay=0.5, backoff=2, on_retry=log_retry)
    def api_call():
        raise TimeoutError("API timeout")
    
    # Example 3: Retry specific exceptions only
    @retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
    def network_operation():
        raise ValueError("This won't be retried")
