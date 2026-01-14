"""
OberaConnect Structured Logging

JSON-formatted logging for production observability.
Compatible with log aggregation systems (ELK, Datadog, Splunk).

Usage:
    from oberaconnect_tools.common.logging import setup_logging, get_logger

    # Set up logging at application start
    setup_logging(level="INFO", json_format=True)

    # Get a logger for your module
    logger = get_logger(__name__)
    logger.info("Processing request", extra={"user": "admin", "action": "query"})

Environment Variables:
    LOG_LEVEL       - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_FORMAT      - Format type: 'json' or 'text' (default: json)
    LOG_FILE        - Path to log file (default: stdout)
    SERVICE_NAME    - Service name for log context (default: oberaconnect)
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """
    JSON log formatter for structured logging.

    Outputs each log record as a single-line JSON object with:
    - timestamp (ISO 8601)
    - level
    - logger name
    - message
    - Any extra fields passed to the log call
    - Exception info if present
    """

    def __init__(self, service_name: str = "oberaconnect"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
        }

        # Add module/function context
        if record.pathname:
            log_data["source"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add any extra fields passed to the logger
        # Skip standard LogRecord attributes
        skip_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'pathname', 'process', 'processName', 'relativeCreated',
            'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
            'message', 'taskName'
        }

        extra = {}
        for key, value in record.__dict__.items():
            if key not in skip_attrs:
                # Try to serialize, skip if not possible
                try:
                    json.dumps(value)
                    extra[key] = value
                except (TypeError, ValueError):
                    extra[key] = str(value)

        if extra:
            log_data["extra"] = extra

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info[2] else None
            }

        return json.dumps(log_data, separators=(',', ':'))


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for development.

    Format: TIMESTAMP | LEVEL | LOGGER | MESSAGE [extra fields]
    """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base = f"{timestamp} | {record.levelname:8} | {record.name} | {record.getMessage()}"

        # Add extra fields if present
        skip_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'pathname', 'process', 'processName', 'relativeCreated',
            'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
            'message', 'taskName'
        }

        extra = {k: v for k, v in record.__dict__.items() if k not in skip_attrs}
        if extra:
            base += f" | {extra}"

        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base


def setup_logging(
    level: str = None,
    json_format: bool = None,
    log_file: str = None,
    service_name: str = None
) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format (True) or text format (False)
        log_file: Path to log file (None for stdout)
        service_name: Service name for log context
    """
    # Get config from env vars or arguments
    level = level or os.getenv('LOG_LEVEL', 'INFO')
    log_file = log_file or os.getenv('LOG_FILE')
    service_name = service_name or os.getenv('SERVICE_NAME', 'oberaconnect')

    # Determine format
    if json_format is None:
        log_format = os.getenv('LOG_FORMAT', 'json').lower()
        json_format = log_format == 'json'

    # Create handler
    if log_file:
        handler = logging.FileHandler(log_file, encoding='utf-8')
    else:
        handler = logging.StreamHandler(sys.stdout)

    # Set formatter
    if json_format:
        handler.setFormatter(JSONFormatter(service_name=service_name))
    else:
        handler.setFormatter(TextFormatter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers and add new one
    root_logger.handlers = []
    root_logger.addHandler(handler)

    # Also configure oberaconnect loggers specifically
    for logger_name in ['oberaconnect', 'oberaconnect_tools']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for adding contextual fields to log messages.

    Usage:
        with LogContext(request_id="abc123", user="admin"):
            logger.info("Processing request")  # Includes request_id and user
    """

    _context: Dict[str, Any] = {}

    def __init__(self, **kwargs):
        self.fields = kwargs

    def __enter__(self):
        LogContext._context.update(self.fields)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.fields:
            LogContext._context.pop(key, None)

    @classmethod
    def get_context(cls) -> Dict[str, Any]:
        return cls._context.copy()


__all__ = [
    'JSONFormatter',
    'TextFormatter',
    'setup_logging',
    'get_logger',
    'LogContext'
]
