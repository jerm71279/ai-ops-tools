"""
AI Operating System - Logging System
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add extra fields
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'layer'):
            log_data['layer'] = record.layer
        if hasattr(record, 'agent'):
            log_data['agent'] = record.agent
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms

        # Add exception info
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored console log formatter"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, '')

        # Format base message
        formatted = super().format(record)

        # Add color
        if color:
            formatted = f"{color}{formatted}{self.RESET}"

        return formatted


class AILogger:
    """
    Central logging system for AI OS
    Provides structured logging with context propagation
    """

    def __init__(
        self,
        name: str = "ai_os",
        level: str = "INFO",
        log_path: Optional[str] = None,
        structured: bool = False,
        console: bool = True
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers = []  # Clear existing handlers

        # Console handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            if structured:
                console_handler.setFormatter(StructuredFormatter())
            else:
                console_handler.setFormatter(ColoredFormatter(
                    fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    datefmt='%H:%M:%S'
                ))
            self.logger.addHandler(console_handler)

        # File handler
        if log_path:
            log_dir = Path(log_path)
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)

            if structured:
                file_handler.setFormatter(StructuredFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(
                    fmt='%(asctime)s [%(levelname)s] %(name)s (%(module)s:%(lineno)d): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            self.logger.addHandler(file_handler)

        # Context for log enrichment
        self._context: Dict[str, Any] = {}

    def set_context(self, **kwargs):
        """Set context fields that will be added to all logs"""
        self._context.update(kwargs)

    def clear_context(self):
        """Clear context fields"""
        self._context = {}

    def _log(self, level: int, msg: str, *args, **kwargs):
        """Internal log method with context enrichment"""
        extra = kwargs.pop('extra', {})
        extra.update(self._context)
        self.logger.log(level, msg, *args, extra=extra, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self._log(logging.CRITICAL, msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        kwargs['exc_info'] = True
        self._log(logging.ERROR, msg, *args, **kwargs)

    # Convenience methods for AI OS events
    def layer_start(self, layer: str, request_id: str, msg: str = ""):
        self.info(
            f"[{layer}] START {request_id} {msg}",
            extra={"layer": layer, "request_id": request_id}
        )

    def layer_end(self, layer: str, request_id: str, success: bool, duration_ms: float):
        status = "SUCCESS" if success else "FAILED"
        self.info(
            f"[{layer}] {status} {request_id} ({duration_ms:.2f}ms)",
            extra={"layer": layer, "request_id": request_id, "duration_ms": duration_ms}
        )

    def agent_start(self, agent: str, request_id: str, task: str):
        self.info(
            f"[Agent:{agent}] START {request_id}: {task[:50]}...",
            extra={"agent": agent, "request_id": request_id}
        )

    def agent_end(self, agent: str, request_id: str, success: bool, duration_ms: float):
        status = "SUCCESS" if success else "FAILED"
        self.info(
            f"[Agent:{agent}] {status} {request_id} ({duration_ms:.2f}ms)",
            extra={"agent": agent, "request_id": request_id, "duration_ms": duration_ms}
        )

    def pipeline_step(self, step: str, status: str, details: str = ""):
        self.info(f"[Pipeline] Step '{step}': {status} {details}")


# Global logger instances
_loggers: Dict[str, AILogger] = {}


def get_logger(name: str = "ai_os") -> AILogger:
    """Get or create a named logger"""
    if name not in _loggers:
        _loggers[name] = AILogger(name)
    return _loggers[name]


def configure_logging(
    level: str = "INFO",
    log_path: Optional[str] = None,
    structured: bool = False
):
    """Configure the global logging system"""
    global _loggers
    _loggers["ai_os"] = AILogger(
        name="ai_os",
        level=level,
        log_path=log_path,
        structured=structured
    )
