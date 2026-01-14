#!/usr/bin/env python3
"""
Structured Logging for OberaConnect Notion Dashboards

Features:
- JSON-formatted logs for ELK/Splunk/CloudWatch ingestion
- Correlation IDs for request tracing
- Separate audit log for compliance
- Performance metrics logging
- Error context capture

Usage:
    from structured_logging import setup_logging, get_logger, log_operation

    setup_logging(level="INFO", json_format=True)
    logger = get_logger(__name__)

    with log_operation("sync_sites", site_count=98):
        # Your code here
        pass

Author: OberaConnect
Created: 2025
"""

import os
import sys
import json
import logging
import traceback
import uuid
from datetime import datetime
from contextlib import contextmanager
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional
from functools import wraps
import threading

# Thread-local storage for correlation IDs
_context = threading.local()


def get_correlation_id() -> str:
    """Get current correlation ID or generate new one."""
    if not hasattr(_context, 'correlation_id'):
        _context.correlation_id = str(uuid.uuid4())[:8]
    return _context.correlation_id


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current thread."""
    _context.correlation_id = correlation_id


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def __init__(self, include_timestamp: bool = True):
        super().__init__()
        self.include_timestamp = include_timestamp

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }

        if self.include_timestamp:
            log_entry["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "correlation_id"
            ]:
                try:
                    json.dumps(value)  # Check if serializable
                    log_entry[key] = value
                except (TypeError, ValueError):
                    log_entry[key] = str(value)

        return json.dumps(log_entry)


class ReadableFormatter(logging.Formatter):
    """Human-readable formatter for development."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        correlation_id = get_correlation_id()

        base = f"{timestamp} [{correlation_id}] {record.levelname:8} {record.name}: {record.getMessage()}"

        if record.exc_info:
            base += "\n" + "".join(traceback.format_exception(*record.exc_info))

        return base


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None,
    audit_file: Optional[str] = None
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format (True) or readable format (False)
        log_file: Optional file path for application logs
        audit_file: Optional file path for audit logs
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Choose formatter
    formatter = JSONFormatter() if json_format else ReadableFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Audit logger (always JSON, separate file)
    audit_logger = logging.getLogger("oberaconnect.audit")
    audit_logger.handlers.clear()
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False  # Don't send to root logger

    if audit_file:
        audit_handler = logging.FileHandler(audit_file)
        audit_handler.setFormatter(JSONFormatter())
        audit_logger.addHandler(audit_handler)
    else:
        # Default to stderr for audit logs
        audit_handler = logging.StreamHandler(sys.stderr)
        audit_handler.setFormatter(JSONFormatter())
        audit_logger.addHandler(audit_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


@dataclass
class OperationMetrics:
    """Metrics for a logged operation."""
    operation: str
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@contextmanager
def log_operation(
    operation: str,
    logger: Optional[logging.Logger] = None,
    **context
):
    """
    Context manager for logging operations with timing and metrics.

    Usage:
        with log_operation("sync_sites", site_count=98) as metrics:
            # Do work
            metrics.context["processed"] = 50

    Args:
        operation: Name of the operation
        logger: Logger to use (defaults to oberaconnect.operations)
        **context: Additional context to log
    """
    if logger is None:
        logger = logging.getLogger("oberaconnect.operations")

    start_time = datetime.utcnow()
    metrics = OperationMetrics(
        operation=operation,
        started_at=start_time.isoformat() + "Z",
        context=context
    )

    logger.info(f"Starting {operation}", extra={
        "event": "operation_start",
        "operation": operation,
        **context
    })

    try:
        yield metrics
        metrics.success = True
    except Exception as e:
        metrics.success = False
        metrics.error = str(e)
        logger.exception(f"Failed {operation}: {e}", extra={
            "event": "operation_error",
            "operation": operation,
            "error_type": type(e).__name__,
            **context
        })
        raise
    finally:
        end_time = datetime.utcnow()
        metrics.completed_at = end_time.isoformat() + "Z"
        metrics.duration_ms = (end_time - start_time).total_seconds() * 1000

        logger.info(f"Completed {operation}", extra={
            "event": "operation_complete",
            "operation": operation,
            "duration_ms": metrics.duration_ms,
            "success": metrics.success,
            **metrics.context
        })


def log_audit_event(
    action: str,
    target: str,
    result: str,
    user: str = "system",
    **details
) -> None:
    """
    Log an audit event for compliance tracking.

    Args:
        action: Action performed (e.g., "create_page", "update_config")
        target: Target of action (e.g., "site:Acme Corp", "database:daily_health")
        result: Result of action ("success", "failed", "denied")
        user: User/service performing action
        **details: Additional audit details
    """
    audit_logger = logging.getLogger("oberaconnect.audit")

    event = {
        "event_type": "audit",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "correlation_id": get_correlation_id(),
        "action": action,
        "target": target,
        "result": result,
        "user": user,
        **details
    }

    audit_logger.info(json.dumps(event))


def timed(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function execution time.

    Usage:
        @timed()
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)

            start = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception:
                success = False
                raise
            finally:
                duration_ms = (datetime.utcnow() - start).total_seconds() * 1000
                logger.info(f"{func.__name__} completed", extra={
                    "event": "function_timed",
                    "function": func.__name__,
                    "duration_ms": duration_ms,
                    "success": success
                })

        return wrapper
    return decorator


# =============================================================================
# Health Check Logging
# =============================================================================

def log_health_check(
    component: str,
    healthy: bool,
    latency_ms: Optional[float] = None,
    **details
) -> None:
    """Log a health check result."""
    logger = logging.getLogger("oberaconnect.health")
    logger.info(f"Health check: {component}", extra={
        "event": "health_check",
        "component": component,
        "healthy": healthy,
        "latency_ms": latency_ms,
        **details
    })


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Demo the logging system."""
    import argparse

    parser = argparse.ArgumentParser(description="Structured logging demo")
    parser.add_argument("--json", action="store_true", help="Use JSON format")
    parser.add_argument("--level", default="DEBUG", help="Log level")

    args = parser.parse_args()

    setup_logging(level=args.level, json_format=args.json)
    logger = get_logger("demo")

    print("=== Structured Logging Demo ===\n")

    # Demo basic logging
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")

    # Demo operation logging
    with log_operation("demo_sync", site_count=5) as metrics:
        logger.info("Processing sites...")
        metrics.context["processed"] = 5

    # Demo audit logging
    log_audit_event(
        action="update_page",
        target="site:Acme Corp",
        result="success",
        user="sync_service",
        old_health=85,
        new_health=92
    )

    # Demo timed decorator
    @timed()
    def slow_function():
        import time
        time.sleep(0.1)

    slow_function()

    # Demo exception logging
    try:
        raise ValueError("Demo error")
    except ValueError:
        logger.exception("Caught demo error")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
