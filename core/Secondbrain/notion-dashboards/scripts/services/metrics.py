"""
Observability metrics for Notion dashboards.

Provides:
- Prometheus-style metrics collection
- Structured logging with correlation IDs
- Health check endpoints
- Sync operation tracking

Based on AI Council recommendations for production observability.
"""

import time
import uuid
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
from enum import Enum
from functools import wraps
import threading


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class SyncStatus(Enum):
    """Sync operation status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Metric:
    """A single metric measurement."""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    help_text: str = ""

    def to_prometheus(self) -> str:
        """Format as Prometheus text exposition."""
        labels_str = ""
        if self.labels:
            label_pairs = [f'{k}="{v}"' for k, v in self.labels.items()]
            labels_str = "{" + ",".join(label_pairs) + "}"

        return f"{self.name}{labels_str} {self.value}"


@dataclass
class SyncRun:
    """Record of a sync operation run."""
    run_id: str
    script_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: SyncStatus = SyncStatus.PENDING
    sites_processed: int = 0
    sites_updated: int = 0
    sites_failed: int = 0
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    dry_run: bool = False


@dataclass
class HealthStatus:
    """System health status."""
    healthy: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    details: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# METRICS COLLECTOR
# ============================================================================

class MetricsCollector:
    """
    Collects and exposes metrics for the Notion dashboard system.

    Thread-safe metric collection with Prometheus-compatible output.

    Example:
        metrics = MetricsCollector()

        # Track sync operations
        with metrics.track_sync("customer_status_sync"):
            sync.run()

        # Increment counters
        metrics.increment("sites_updated", labels={"script": "customer_status"})

        # Get Prometheus output
        print(metrics.to_prometheus())
    """

    def __init__(self):
        self._metrics: Dict[str, Metric] = {}
        self._sync_runs: List[SyncRun] = []
        self._lock = threading.Lock()
        self._current_run: Optional[SyncRun] = None

        # Initialize default metrics
        self._init_default_metrics()

    def _init_default_metrics(self) -> None:
        """Initialize default metric definitions."""
        self._register("sync_runs_total", MetricType.COUNTER, "Total sync runs")
        self._register("sync_runs_success", MetricType.COUNTER, "Successful sync runs")
        self._register("sync_runs_failed", MetricType.COUNTER, "Failed sync runs")
        self._register("sites_processed_total", MetricType.COUNTER, "Total sites processed")
        self._register("sites_updated_total", MetricType.COUNTER, "Total sites updated")
        self._register("sites_failed_total", MetricType.COUNTER, "Total site failures")
        self._register("sync_duration_seconds", MetricType.GAUGE, "Last sync duration in seconds")
        self._register("api_calls_total", MetricType.COUNTER, "Total API calls")
        self._register("api_errors_total", MetricType.COUNTER, "Total API errors")
        self._register("notion_pages_created", MetricType.COUNTER, "Notion pages created")
        self._register("notion_pages_updated", MetricType.COUNTER, "Notion pages updated")

    def _register(self, name: str, metric_type: MetricType, help_text: str = "") -> None:
        """Register a metric definition."""
        key = self._metric_key(name, {})
        if key not in self._metrics:
            self._metrics[key] = Metric(
                name=name,
                value=0.0,
                metric_type=metric_type,
                help_text=help_text,
            )

    def _metric_key(self, name: str, labels: Dict[str, str]) -> str:
        """Generate unique key for metric with labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def increment(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        labels = labels or {}
        key = self._metric_key(name, labels)

        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = Metric(
                    name=name,
                    value=0.0,
                    metric_type=MetricType.COUNTER,
                    labels=labels,
                )
            self._metrics[key].value += value
            self._metrics[key].timestamp = datetime.now(timezone.utc)

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value."""
        labels = labels or {}
        key = self._metric_key(name, labels)

        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = Metric(
                    name=name,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    labels=labels,
                )
            else:
                self._metrics[key].value = value
            self._metrics[key].timestamp = datetime.now(timezone.utc)

    @contextmanager
    def track_sync(self, script_name: str, dry_run: bool = False):
        """
        Context manager to track a sync operation.

        Example:
            with metrics.track_sync("customer_status_sync") as run:
                run.sites_processed = 98
                # do sync work
                run.sites_updated = 50
        """
        run = SyncRun(
            run_id=str(uuid.uuid4())[:8],
            script_name=script_name,
            started_at=datetime.now(timezone.utc),
            status=SyncStatus.RUNNING,
            dry_run=dry_run,
        )

        self._current_run = run
        self.increment("sync_runs_total", labels={"script": script_name})

        start_time = time.time()

        try:
            yield run
            run.status = SyncStatus.SUCCESS
            self.increment("sync_runs_success", labels={"script": script_name})
        except Exception as e:
            run.status = SyncStatus.FAILED
            run.errors.append(str(e))
            self.increment("sync_runs_failed", labels={"script": script_name})
            raise
        finally:
            run.completed_at = datetime.now(timezone.utc)
            run.duration_seconds = time.time() - start_time

            self.set_gauge("sync_duration_seconds", run.duration_seconds, {"script": script_name})
            self.increment("sites_processed_total", run.sites_processed, {"script": script_name})
            self.increment("sites_updated_total", run.sites_updated, {"script": script_name})
            self.increment("sites_failed_total", run.sites_failed, {"script": script_name})

            with self._lock:
                self._sync_runs.append(run)
                # Keep last 100 runs
                if len(self._sync_runs) > 100:
                    self._sync_runs = self._sync_runs[-100:]

            self._current_run = None

    def track_api_call(self, api_name: str, success: bool = True) -> None:
        """Track an API call."""
        self.increment("api_calls_total", labels={"api": api_name})
        if not success:
            self.increment("api_errors_total", labels={"api": api_name})

    def track_notion_operation(self, operation: str) -> None:
        """Track a Notion API operation."""
        if operation == "create":
            self.increment("notion_pages_created")
        elif operation == "update":
            self.increment("notion_pages_updated")

    def get_current_run(self) -> Optional[SyncRun]:
        """Get the currently running sync operation."""
        return self._current_run

    def get_recent_runs(self, limit: int = 10) -> List[SyncRun]:
        """Get recent sync runs."""
        with self._lock:
            return self._sync_runs[-limit:]

    def get_metrics(self) -> Dict[str, Metric]:
        """Get all metrics."""
        with self._lock:
            return dict(self._metrics)

    def to_prometheus(self) -> str:
        """
        Format metrics as Prometheus text exposition.

        Returns:
            Prometheus-compatible metrics output
        """
        lines = []
        lines.append("# Notion Dashboard Sync Metrics")
        lines.append(f"# Generated at {datetime.now(timezone.utc).isoformat()}")
        lines.append("")

        with self._lock:
            # Group by metric name
            by_name: Dict[str, List[Metric]] = {}
            for metric in self._metrics.values():
                by_name.setdefault(metric.name, []).append(metric)

            for name, metrics in sorted(by_name.items()):
                first = metrics[0]
                if first.help_text:
                    lines.append(f"# HELP {name} {first.help_text}")
                lines.append(f"# TYPE {name} {first.metric_type.value}")
                for m in metrics:
                    lines.append(m.to_prometheus())
                lines.append("")

        return "\n".join(lines)

    def to_json(self) -> Dict[str, Any]:
        """Export metrics as JSON."""
        with self._lock:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics": {
                    key: {
                        "name": m.name,
                        "value": m.value,
                        "type": m.metric_type.value,
                        "labels": m.labels,
                    }
                    for key, m in self._metrics.items()
                },
                "recent_runs": [asdict(r) for r in self._sync_runs[-10:]],
            }


# ============================================================================
# STRUCTURED LOGGING
# ============================================================================

class StructuredLogger:
    """
    Structured logger with correlation ID support.

    Provides JSON-formatted logs with consistent fields for
    log aggregation and analysis.

    Example:
        logger = StructuredLogger("customer_status_sync")

        with logger.correlation_context() as log:
            log.info("Starting sync", extra={"sites": 98})
            log.error("Failed to update", extra={"site": "Acme Corp"})
    """

    def __init__(self, name: str, level: int = logging.INFO):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Add JSON handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JsonFormatter())
            self.logger.addHandler(handler)

        self._correlation_id: Optional[str] = None

    @contextmanager
    def correlation_context(self, correlation_id: Optional[str] = None):
        """Create a correlation context for related log entries."""
        self._correlation_id = correlation_id or str(uuid.uuid4())[:8]
        try:
            yield self
        finally:
            self._correlation_id = None

    def _add_context(self, extra: Optional[Dict] = None) -> Dict:
        """Add standard context to log extra fields."""
        context = {
            "service": "notion-dashboards",
            "script": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if self._correlation_id:
            context["correlation_id"] = self._correlation_id
        if extra:
            context.update(extra)
        return context

    def info(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log info message."""
        self.logger.info(message, extra={"structured": self._add_context(extra)})

    def warning(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log warning message."""
        self.logger.warning(message, extra={"structured": self._add_context(extra)})

    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False) -> None:
        """Log error message."""
        self.logger.error(message, extra={"structured": self._add_context(extra)}, exc_info=exc_info)

    def debug(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log debug message."""
        self.logger.debug(message, extra={"structured": self._add_context(extra)})


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add structured context if present
        if hasattr(record, "structured"):
            log_entry.update(record.structured)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


# ============================================================================
# HEALTH CHECKS
# ============================================================================

class HealthChecker:
    """
    Health check system for the Notion dashboard services.

    Provides /health, /ready, and /metrics style endpoints.

    Example:
        health = HealthChecker()
        health.register_check("unifi_api", check_unifi_connection)
        health.register_check("notion_api", check_notion_connection)

        status = health.check()
        if not status.healthy:
            print("System unhealthy:", status.details)
    """

    def __init__(self):
        self._checks: Dict[str, Callable[[], bool]] = {}
        self._last_check: Optional[HealthStatus] = None

    def register_check(self, name: str, check_fn: Callable[[], bool]) -> None:
        """Register a health check function."""
        self._checks[name] = check_fn

    def check(self) -> HealthStatus:
        """Run all health checks and return status."""
        checks = {}
        details = {}

        for name, check_fn in self._checks.items():
            try:
                result = check_fn()
                checks[name] = result
                details[name] = "OK" if result else "FAILED"
            except Exception as e:
                checks[name] = False
                details[name] = f"ERROR: {str(e)}"

        healthy = all(checks.values()) if checks else True

        self._last_check = HealthStatus(
            healthy=healthy,
            checks=checks,
            details=details,
        )

        return self._last_check

    def is_ready(self) -> bool:
        """Quick readiness check (returns cached result if recent)."""
        if self._last_check is None:
            return self.check().healthy
        return self._last_check.healthy

    def to_json(self) -> Dict[str, Any]:
        """Export health status as JSON."""
        status = self.check()
        return {
            "status": "healthy" if status.healthy else "unhealthy",
            "checks": status.details,
            "timestamp": status.timestamp.isoformat(),
        }


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Global metrics collector
_metrics: Optional[MetricsCollector] = None

# Global health checker
_health: Optional[HealthChecker] = None


def get_metrics() -> MetricsCollector:
    """Get global metrics collector."""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics


def get_health_checker() -> HealthChecker:
    """Get global health checker."""
    global _health
    if _health is None:
        _health = HealthChecker()
    return _health


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger for a script."""
    return StructuredLogger(name)


# ============================================================================
# DECORATOR
# ============================================================================

def track_sync(script_name: str):
    """
    Decorator to track sync function execution.

    Example:
        @track_sync("customer_status_sync")
        def run_sync():
            # sync logic
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            dry_run = kwargs.get("dry_run", False)

            with metrics.track_sync(script_name, dry_run=dry_run) as run:
                result = func(*args, **kwargs)

                # If function returns stats, update run
                if isinstance(result, dict):
                    run.sites_processed = result.get("processed", 0)
                    run.sites_updated = result.get("updated", 0)
                    run.sites_failed = result.get("failed", 0)

                return result

        return wrapper
    return decorator
