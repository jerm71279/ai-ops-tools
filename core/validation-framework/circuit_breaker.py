"""
Circuit Breaker with Retry
==========================

Simple circuit breaker and retry logic for API calls.
Prevents cascading failures and handles transient errors.

Usage:
    from core.validation_framework import CircuitBreaker, with_retry

    # As a decorator
    @with_retry(max_retries=3, backoff_base=1.0)
    async def fetch_data():
        return await api.get_data()

    # As a context manager
    cb = CircuitBreaker(failure_threshold=5, timeout=60)
    async with cb:
        result = await api.call()
"""

import asyncio
import functools
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional, Type, Tuple

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.

    States:
        CLOSED: Normal operation, requests pass through
        OPEN: Too many failures, requests rejected immediately
        HALF_OPEN: Testing if service recovered

    Usage:
        cb = CircuitBreaker(failure_threshold=5, timeout=60)

        try:
            if cb.allow_request():
                result = await api_call()
                cb.record_success()
            else:
                raise CircuitOpenError("Circuit is open")
        except Exception as e:
            cb.record_failure()
            raise
    """
    failure_threshold: int = 5
    timeout: float = 60.0  # seconds
    half_open_max_calls: int = 1

    # Internal state
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _last_failure_time: Optional[datetime] = field(default=None, init=False)
    _half_open_calls: int = field(default=0, init=False)

    @property
    def state(self) -> CircuitState:
        """Get current state, checking for timeout transition."""
        if self._state == CircuitState.OPEN:
            if self._last_failure_time:
                elapsed = (datetime.utcnow() - self._last_failure_time).total_seconds()
                if elapsed >= self.timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
        return self._state

    def allow_request(self) -> bool:
        """Check if request should be allowed."""
        state = self.state

        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.OPEN:
            return False
        elif state == CircuitState.HALF_OPEN:
            if self._half_open_calls < self.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False

        return False

    def record_success(self) -> None:
        """Record successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            # After successful half-open call, close the circuit
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            logger.info("Circuit breaker CLOSED after successful recovery")
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0  # Reset failure count on success

    def record_failure(self) -> None:
        """Record failed call."""
        self._failure_count += 1
        self._last_failure_time = datetime.utcnow()

        if self._state == CircuitState.HALF_OPEN:
            # Failed during half-open, go back to open
            self._state = CircuitState.OPEN
            logger.warning("Circuit breaker OPEN after failed recovery attempt")
        elif self._state == CircuitState.CLOSED:
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(f"Circuit breaker OPEN after {self._failure_count} failures")

    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0

    def get_status(self) -> dict:
        """Get current status for monitoring."""
        return {
            "state": self.state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "last_failure": self._last_failure_time.isoformat() if self._last_failure_time else None
        }


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


def with_retry(
    max_retries: int = 3,
    backoff_base: float = 1.0,
    backoff_max: float = 30.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    circuit_breaker: Optional[CircuitBreaker] = None
) -> Callable:
    """
    Decorator for retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_base: Base delay in seconds (doubles each retry)
        backoff_max: Maximum delay between retries
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exceptions that trigger retry
        circuit_breaker: Optional circuit breaker instance

    Usage:
        @with_retry(max_retries=3, backoff_base=1.0)
        async def fetch_data():
            return await api.get("/data")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            cb = circuit_breaker

            for attempt in range(max_retries + 1):
                # Check circuit breaker
                if cb and not cb.allow_request():
                    raise CircuitOpenError(f"Circuit breaker is open for {func.__name__}")

                try:
                    result = await func(*args, **kwargs)
                    if cb:
                        cb.record_success()
                    return result

                except retryable_exceptions as e:
                    last_exception = e
                    if cb:
                        cb.record_failure()

                    if attempt < max_retries:
                        # Calculate backoff
                        delay = min(backoff_base * (2 ** attempt), backoff_max)
                        if jitter:
                            delay = delay * (0.5 + random.random())

                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                            f"retrying in {delay:.2f}s: {e}"
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")

            raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            cb = circuit_breaker

            for attempt in range(max_retries + 1):
                if cb and not cb.allow_request():
                    raise CircuitOpenError(f"Circuit breaker is open for {func.__name__}")

                try:
                    result = func(*args, **kwargs)
                    if cb:
                        cb.record_success()
                    return result

                except retryable_exceptions as e:
                    last_exception = e
                    if cb:
                        cb.record_failure()

                    if attempt < max_retries:
                        delay = min(backoff_base * (2 ** attempt), backoff_max)
                        if jitter:
                            delay = delay * (0.5 + random.random())

                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                            f"retrying in {delay:.2f}s: {e}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")

            raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Convenience function for quick retries without decoration
async def retry_async(
    func: Callable,
    *args,
    max_retries: int = 3,
    backoff_base: float = 1.0,
    **kwargs
) -> Any:
    """
    Retry an async function with exponential backoff.

    Usage:
        result = await retry_async(api.get_data, endpoint="/users", max_retries=3)
    """
    wrapped = with_retry(max_retries=max_retries, backoff_base=backoff_base)(func)
    return await wrapped(*args, **kwargs)
