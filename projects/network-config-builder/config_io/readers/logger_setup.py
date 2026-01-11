#!/usr/bin/env python3
"""
Logger Setup
Standard logging configuration for automation scripts.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = __name__,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_dir: str = "./logs",
    console: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup a logger with file and/or console handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Specific log file name (auto-generated if None)
        log_dir: Directory for log files
        console: Whether to also log to console
        format_string: Custom format string (uses default if None)
    
    Returns:
        Configured logger instance
    
    Example:
        logger = setup_logger(__name__, level=logging.DEBUG, log_file="myapp.log")
        logger.info("Application started")
        logger.error("Something went wrong", exc_info=True)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # File handler
    if log_file or log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        if log_file is None:
            # Auto-generate log filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f"{name}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_path / log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def setup_rotating_logger(
    name: str = __name__,
    level: int = logging.INFO,
    log_file: str = "app.log",
    log_dir: str = "./logs",
    max_bytes: int = 10_485_760,  # 10MB
    backup_count: int = 5,
    console: bool = True
) -> logging.Logger:
    """
    Setup a logger with rotating file handler (prevents log files from growing too large).
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Log file name
        log_dir: Directory for log files
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        console: Whether to also log to console
    
    Returns:
        Configured logger with rotating file handler
    """
    from logging.handlers import RotatingFileHandler
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Rotating file handler
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_path / log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


class LoggerContext:
    """Context manager for temporarily changing log level."""
    
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.new_level = level
        self.old_level = None
    
    def __enter__(self):
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)


# Example usage
if __name__ == "__main__":
    # Basic logger
    logger = setup_logger(__name__, level=logging.DEBUG, log_file="example.log")
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Rotating logger
    rotating_logger = setup_rotating_logger(
        "my_app",
        log_file="app.log",
        max_bytes=1_048_576,  # 1MB
        backup_count=3
    )
    
    rotating_logger.info("This will rotate when file reaches 1MB")
    
    # Temporary level change
    with LoggerContext(logger, logging.WARNING):
        logger.info("This won't be logged")
        logger.warning("This will be logged")
