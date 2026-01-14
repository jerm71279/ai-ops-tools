"""
Centralized logging configuration for OberaConnect Notion integration.

Provides consistent log formatting across all sync scripts.
"""

import logging
import sys
from typing import Optional


# Default format matching existing scripts
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SIMPLE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


def setup_logging(
    name: str,
    level: int = logging.INFO,
    log_format: str = DEFAULT_FORMAT,
    stream: Optional[object] = None
) -> logging.Logger:
    """
    Configure and return a logger with consistent formatting.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (default INFO)
        log_format: Format string (default includes timestamp, name, level)
        stream: Output stream (default sys.stdout)
    
    Returns:
        Configured logger instance
    
    Example:
        from core.logging_config import setup_logging
        logger = setup_logging(__name__)
        logger.info("Sync started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(stream or sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(handler)
    
    return logger


def set_global_level(level: int) -> None:
    """
    Set logging level for all OberaConnect loggers.
    
    Args:
        level: Logging level (e.g., logging.DEBUG)
    """
    # Set root logger level
    logging.getLogger().setLevel(level)
    
    # Update all existing loggers in our namespace
    for name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            logger.setLevel(level)


def enable_debug() -> None:
    """Enable DEBUG level for all loggers."""
    set_global_level(logging.DEBUG)


def enable_quiet() -> None:
    """Set WARNING level for quieter output."""
    set_global_level(logging.WARNING)


# Module-level convenience - can be imported directly
def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with standard configuration.
    
    Convenience wrapper that applies default settings.
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger
    """
    return setup_logging(name)
