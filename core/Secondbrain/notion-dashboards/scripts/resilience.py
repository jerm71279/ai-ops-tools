#!/usr/bin/env python3
"""
Resilience Patterns for OberaConnect Notion Dashboards

Features:
- Retry with exponential backoff
- Circuit breaker pattern
- Rate limiting
- Input validation and sanitization
- Partial failure recovery

Usage:
    from resilience import retry_with_backoff, circuit_breaker, validate_site_name

    @retry_with_backoff(max_retries=3)
    def api_call():
        ...

    @circuit_breaker(failure_threshold=5)
    def external_service():
        ...

    safe_name = validate_site_name(user_input)

Author: OberaConnect
Created: 2025
"""

import re
import time
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, List, Optional, Type, TypeVar, Set
from dataclasses import dataclass, field
import threading

logger = logging.getLogger("oberaconnect.resilience")

T = TypeVar('T')


# =============================================================================
# Retry with Exponential Backoff
# =============================================================================

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (Exception,)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator for retry with exponential backoff.

    Args:
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exceptions to retry on
        on_retry: Optional callback(attempt, exception, delay) on each retry

    Usage:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def flaky_api_call():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            import random

            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"All {max_retries} retries failed for {func.__name__}: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    # Add jitter (0-50% of delay)
                    if jitter:
                        delay += random.uniform(0, delay * 0.5)

                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.2f}s: {e}"
                    )

                    if on_retry:
                        on_retry(attempt + 1, e, delay)

                    time.sleep(delay)

            raise last_exception  # Should never reach here

        return wrapper
    return decorator


# =============================================================================
# Circuit Breaker
# =============================================================================

@dataclass
class CircuitState:
    """State for a circuit breaker."""
    failures: int = 0
    successes: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half-open


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing, requests fail fast
    - HALF-OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout: int = 60,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.name = name
        self._state = CircuitState()
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        """Get current circuit state."""
        with self._lock:
            if self._state.state == "open":
                # Check if timeout has passed
                if self._state.last_failure_time:
                    elapsed = (datetime.utcnow() - self._state.last_failure_time).seconds
                    if elapsed >= self.timeout:
                        self._state.state = "half-open"
                        self._state.successes = 0
                        logger.info(f"Circuit {self.name} entering half-open state")

            return self._state.state

    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            if self._state.state == "half-open":
                self._state.successes += 1
                if self._state.successes >= self.success_threshold:
                    self._state.state = "closed"
                    self._state.failures = 0
                    logger.info(f"Circuit {self.name} closed after recovery")
            else:
                self._state.failures = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self._state.failures += 1
            self._state.last_failure_time = datetime.utcnow()

            if self._state.state == "half-open":
                self._state.state = "open"
                logger.warning(f"Circuit {self.name} re-opened after half-open failure")
            elif self._state.failures >= self.failure_threshold:
                self._state.state = "open"
                logger.warning(
                    f"Circuit {self.name} opened after {self._state.failures} failures"
                )

    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self.state == "open"


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


def circuit_breaker(
    failure_threshold: int = 5,
    success_threshold: int = 3,
    timeout: int = 60,
    name: Optional[str] = None
):
    """
    Decorator for circuit breaker pattern.

    Usage:
        @circuit_breaker(failure_threshold=5)
        def external_api_call():
            ...
    """
    _breakers: dict = {}

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        breaker_name = name or func.__name__

        if breaker_name not in _breakers:
            _breakers[breaker_name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                success_threshold=success_threshold,
                timeout=timeout,
                name=breaker_name
            )

        breaker = _breakers[breaker_name]

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if breaker.is_open():
                raise CircuitOpenError(
                    f"Circuit {breaker_name} is open. Service appears unavailable."
                )

            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise

        # Expose breaker for testing/monitoring
        wrapper.circuit_breaker = breaker
        return wrapper

    return decorator


# =============================================================================
# Rate Limiting
# =============================================================================

@dataclass
class RateLimitState:
    """State for rate limiter."""
    tokens: float = 0
    last_update: datetime = field(default_factory=datetime.utcnow)


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        rate: float = 3.0,  # tokens per second
        burst: int = 10,     # max tokens
        name: str = "default"
    ):
        self.rate = rate
        self.burst = burst
        self.name = name
        self._state = RateLimitState(tokens=burst)
        self._lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens.

        Returns True if tokens acquired, False if rate limited.
        """
        with self._lock:
            now = datetime.utcnow()
            elapsed = (now - self._state.last_update).total_seconds()

            # Add tokens based on elapsed time
            self._state.tokens = min(
                self.burst,
                self._state.tokens + (elapsed * self.rate)
            )
            self._state.last_update = now

            if self._state.tokens >= tokens:
                self._state.tokens -= tokens
                return True

            logger.debug(f"Rate limited: {self.name}")
            return False

    def wait_and_acquire(self, tokens: int = 1, timeout: float = 30.0) -> bool:
        """Wait until tokens available or timeout."""
        start = datetime.utcnow()

        while True:
            if self.acquire(tokens):
                return True

            elapsed = (datetime.utcnow() - start).total_seconds()
            if elapsed >= timeout:
                return False

            # Wait for a token to become available
            time.sleep(1.0 / self.rate)


def rate_limited(
    rate: float = 3.0,
    burst: int = 10,
    wait: bool = True,
    timeout: float = 30.0
):
    """
    Decorator for rate limiting.

    Args:
        rate: Requests per second
        burst: Maximum burst size
        wait: If True, wait for rate limit; if False, raise exception
        timeout: Maximum wait time in seconds
    """
    _limiters: dict = {}

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        name = func.__name__

        if name not in _limiters:
            _limiters[name] = RateLimiter(rate=rate, burst=burst, name=name)

        limiter = _limiters[name]

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if wait:
                if not limiter.wait_and_acquire(timeout=timeout):
                    raise TimeoutError(f"Rate limit timeout for {name}")
            else:
                if not limiter.acquire():
                    raise RuntimeError(f"Rate limited: {name}")

            return func(*args, **kwargs)

        wrapper.rate_limiter = limiter
        return wrapper

    return decorator


# =============================================================================
# Input Validation
# =============================================================================

# Patterns for safe site/org names
SAFE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\s\-_\.&\']+$')
MAX_NAME_LENGTH = 200

# Characters that should never appear in identifiers
DANGEROUS_CHARS = frozenset(['<', '>', '"', '\\', '/', '\x00', '\n', '\r'])


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_site_name(name: str, field_name: str = "site_name") -> str:
    """
    Validate and sanitize a site/organization name.

    Args:
        name: Input name to validate
        field_name: Name of field for error messages

    Returns:
        Sanitized name

    Raises:
        ValidationError: If name is invalid
    """
    if not name:
        raise ValidationError(f"{field_name} cannot be empty")

    # Trim whitespace
    name = name.strip()

    if len(name) > MAX_NAME_LENGTH:
        raise ValidationError(
            f"{field_name} exceeds maximum length of {MAX_NAME_LENGTH} characters"
        )

    # Check for dangerous characters
    dangerous_found = set(name) & DANGEROUS_CHARS
    if dangerous_found:
        raise ValidationError(
            f"{field_name} contains invalid characters: {dangerous_found}"
        )

    # Validate pattern
    if not SAFE_NAME_PATTERN.match(name):
        raise ValidationError(
            f"{field_name} must start with alphanumeric and contain only "
            "letters, numbers, spaces, hyphens, underscores, periods, ampersands, or apostrophes"
        )

    return name


def validate_database_id(db_id: str) -> str:
    """
    Validate a Notion database ID.

    Args:
        db_id: Database ID to validate

    Returns:
        Validated database ID

    Raises:
        ValidationError: If ID is invalid
    """
    if not db_id:
        raise ValidationError("database_id cannot be empty")

    # Notion IDs are UUIDs (with or without hyphens)
    uuid_pattern = re.compile(
        r'^[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}$',
        re.IGNORECASE
    )

    if not uuid_pattern.match(db_id):
        raise ValidationError(
            f"Invalid database_id format: {db_id[:20]}... "
            "Expected UUID format"
        )

    return db_id.lower()


def validate_health_score(score: Any) -> int:
    """
    Validate a health score value.

    Args:
        score: Score to validate

    Returns:
        Validated score (0-100)

    Raises:
        ValidationError: If score is invalid
    """
    try:
        score = int(score)
    except (ValueError, TypeError):
        raise ValidationError(f"Health score must be a number, got: {type(score)}")

    if not 0 <= score <= 100:
        raise ValidationError(f"Health score must be 0-100, got: {score}")

    return score


def sanitize_for_notion(text: str, max_length: int = 2000) -> str:
    """
    Sanitize text for safe use in Notion.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes
    text = text.replace('\x00', '')

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."

    return text


# =============================================================================
# Partial Failure Recovery
# =============================================================================

@dataclass
class BatchResult:
    """Result of a batch operation with partial failure support."""
    total: int
    succeeded: int
    failed: int
    errors: List[dict] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total == 0:
            return 100.0
        return (self.succeeded / self.total) * 100

    @property
    def all_succeeded(self) -> bool:
        """Check if all items succeeded."""
        return self.failed == 0


def batch_with_recovery(
    items: list,
    process_func: Callable,
    continue_on_error: bool = True,
    max_errors: int = 10
) -> BatchResult:
    """
    Process items in batch with partial failure recovery.

    Args:
        items: List of items to process
        process_func: Function to call for each item
        continue_on_error: Continue processing after errors
        max_errors: Maximum errors before stopping

    Returns:
        BatchResult with success/failure counts
    """
    result = BatchResult(total=len(items), succeeded=0, failed=0)

    for i, item in enumerate(items):
        try:
            process_func(item)
            result.succeeded += 1
        except Exception as e:
            result.failed += 1
            result.errors.append({
                "index": i,
                "item": str(item)[:100],
                "error": str(e)
            })

            logger.warning(f"Batch item {i} failed: {e}")

            if not continue_on_error:
                break

            if result.failed >= max_errors:
                logger.error(f"Stopping batch after {max_errors} errors")
                break

    return result


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Demo resilience patterns."""
    import argparse

    parser = argparse.ArgumentParser(description="Resilience patterns demo")
    parser.add_argument("--retry", action="store_true", help="Demo retry")
    parser.add_argument("--validate", action="store_true", help="Demo validation")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    if args.retry:
        print("=== Retry Demo ===")

        @retry_with_backoff(max_retries=3, base_delay=0.5)
        def flaky_function():
            import random
            if random.random() < 0.7:
                raise ConnectionError("Random failure")
            return "Success!"

        try:
            result = flaky_function()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Final failure: {e}")

    if args.validate:
        print("=== Validation Demo ===")

        test_names = [
            "Acme Corporation",
            "Test-Site_123",
            "Bad<Script>Name",
            "",
            "A" * 250
        ]

        for name in test_names:
            try:
                safe = validate_site_name(name)
                print(f"'{name}' -> '{safe}'")
            except ValidationError as e:
                print(f"'{name}' -> INVALID: {e}")


if __name__ == "__main__":
    main()
