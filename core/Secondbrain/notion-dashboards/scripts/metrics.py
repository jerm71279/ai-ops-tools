#!/usr/bin/env python3
"""
Prometheus Metrics for OberaConnect Notion Dashboards

Provides comprehensive metrics for monitoring sync operations, API clients,
and system health. Compatible with Prometheus/Grafana.

Metrics:
    Counters:
        - oberaconnect_sync_total: Total sync operations
        - oberaconnect_sync_errors_total: Failed sync operations
        - oberaconnect_api_requests_total: API requests by service
        - oberaconnect_pages_created_total: Notion pages created
        - oberaconnect_pages_updated_total: Notion pages updated

    Gauges:
        - oberaconnect_up: Service health (1=healthy, 0=unhealthy)
        - oberaconnect_sites_total: Total UniFi sites
        - oberaconnect_devices_total: Total NinjaOne devices
        - oberaconnect_last_sync_timestamp: Last successful sync time
        - oberaconnect_circuit_breaker_state: Circuit breaker state

    Histograms:
        - oberaconnect_sync_duration_seconds: Sync operation duration
        - oberaconnect_api_request_duration_seconds: API request latency

Usage:
    from metrics import metrics, track_sync, track_api_call

    # Track a sync operation
    with track_sync("customer_status"):
        sync_customers()

    # Track an API call
    with track_api_call("notion", "create_page"):
        client.create_page(...)

    # Get metrics for /metrics endpoint
    output = metrics.export()

Author: OberaConnect
Created: 2025
"""

import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from contextlib import contextmanager
from functools import wraps
import logging

logger = logging.getLogger("oberaconnect.metrics")


# =============================================================================
# Metric Types
# =============================================================================

@dataclass
class Counter:
    """Prometheus Counter - monotonically increasing value."""
    name: str
    help: str
    labels: List[str] = field(default_factory=list)
    _values: Dict[str, float] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def inc(self, value: float = 1, **label_values) -> None:
        """Increment counter."""
        key = self._label_key(label_values)
        with self._lock:
            self._values[key] = self._values.get(key, 0) + value

    def _label_key(self, label_values: Dict) -> str:
        if not self.labels:
            return ""
        return ",".join(f'{k}="{label_values.get(k, "")}"' for k in self.labels)

    def export(self) -> str:
        """Export in Prometheus format."""
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} counter"]
        with self._lock:
            if not self._values:
                lines.append(f"{self.name} 0")
            else:
                for key, value in self._values.items():
                    if key:
                        lines.append(f"{self.name}{{{key}}} {value}")
                    else:
                        lines.append(f"{self.name} {value}")
        return "\n".join(lines)


@dataclass
class Gauge:
    """Prometheus Gauge - value that can go up and down."""
    name: str
    help: str
    labels: List[str] = field(default_factory=list)
    _values: Dict[str, float] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def set(self, value: float, **label_values) -> None:
        """Set gauge value."""
        key = self._label_key(label_values)
        with self._lock:
            self._values[key] = value

    def inc(self, value: float = 1, **label_values) -> None:
        """Increment gauge."""
        key = self._label_key(label_values)
        with self._lock:
            self._values[key] = self._values.get(key, 0) + value

    def dec(self, value: float = 1, **label_values) -> None:
        """Decrement gauge."""
        key = self._label_key(label_values)
        with self._lock:
            self._values[key] = self._values.get(key, 0) - value

    def _label_key(self, label_values: Dict) -> str:
        if not self.labels:
            return ""
        return ",".join(f'{k}="{label_values.get(k, "")}"' for k in self.labels)

    def export(self) -> str:
        """Export in Prometheus format."""
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} gauge"]
        with self._lock:
            if not self._values:
                lines.append(f"{self.name} 0")
            else:
                for key, value in self._values.items():
                    if key:
                        lines.append(f"{self.name}{{{key}}} {value}")
                    else:
                        lines.append(f"{self.name} {value}")
        return "\n".join(lines)


@dataclass
class Histogram:
    """Prometheus Histogram - distribution of values."""
    name: str
    help: str
    labels: List[str] = field(default_factory=list)
    buckets: List[float] = field(default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10])
    _counts: Dict[str, Dict[float, int]] = field(default_factory=dict)
    _sums: Dict[str, float] = field(default_factory=dict)
    _totals: Dict[str, int] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def observe(self, value: float, **label_values) -> None:
        """Observe a value."""
        key = self._label_key(label_values)
        with self._lock:
            if key not in self._counts:
                self._counts[key] = {b: 0 for b in self.buckets}
                self._counts[key][float('inf')] = 0
                self._sums[key] = 0
                self._totals[key] = 0

            self._sums[key] += value
            self._totals[key] += 1
            for bucket in self.buckets:
                if value <= bucket:
                    self._counts[key][bucket] += 1
            self._counts[key][float('inf')] += 1

    def _label_key(self, label_values: Dict) -> str:
        if not self.labels:
            return ""
        return ",".join(f'{k}="{label_values.get(k, "")}"' for k in self.labels)

    def export(self) -> str:
        """Export in Prometheus format."""
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} histogram"]
        with self._lock:
            for key, counts in self._counts.items():
                label_prefix = f"{{{key}," if key else "{"
                for bucket, count in sorted(counts.items()):
                    if bucket == float('inf'):
                        lines.append(f'{self.name}_bucket{label_prefix}le="+Inf"}} {count}')
                    else:
                        lines.append(f'{self.name}_bucket{label_prefix}le="{bucket}"}} {count}')
                sum_labels = f"{{{key}}}" if key else ""
                lines.append(f"{self.name}_sum{sum_labels} {self._sums.get(key, 0)}")
                lines.append(f"{self.name}_count{sum_labels} {self._totals.get(key, 0)}")
        return "\n".join(lines)


# =============================================================================
# Metrics Registry
# =============================================================================

class MetricsRegistry:
    """Central registry for all metrics."""

    def __init__(self):
        self._metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()

        # Initialize standard metrics
        self._init_standard_metrics()

    def _init_standard_metrics(self) -> None:
        """Initialize standard OberaConnect metrics."""

        # Counters
        self.sync_total = self.counter(
            "oberaconnect_sync_total",
            "Total sync operations",
            ["sync_type", "status"]
        )
        self.sync_errors = self.counter(
            "oberaconnect_sync_errors_total",
            "Total failed sync operations",
            ["sync_type", "error_type"]
        )
        self.api_requests = self.counter(
            "oberaconnect_api_requests_total",
            "Total API requests",
            ["service", "endpoint", "status"]
        )
        self.pages_created = self.counter(
            "oberaconnect_pages_created_total",
            "Total Notion pages created",
            ["database"]
        )
        self.pages_updated = self.counter(
            "oberaconnect_pages_updated_total",
            "Total Notion pages updated",
            ["database"]
        )
        self.circuit_breaker_trips = self.counter(
            "oberaconnect_circuit_breaker_trips_total",
            "Total circuit breaker trips",
            ["service"]
        )

        # Gauges
        self.up = self.gauge(
            "oberaconnect_up",
            "Service health status (1=up, 0=down)"
        )
        self.up.set(1)

        self.sites_total = self.gauge(
            "oberaconnect_sites_total",
            "Total UniFi sites being monitored"
        )
        self.devices_total = self.gauge(
            "oberaconnect_devices_total",
            "Total NinjaOne devices being monitored"
        )
        self.last_sync_timestamp = self.gauge(
            "oberaconnect_last_sync_timestamp_seconds",
            "Timestamp of last successful sync",
            ["sync_type"]
        )
        self.circuit_breaker_state = self.gauge(
            "oberaconnect_circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=open, 0.5=half-open)",
            ["service"]
        )
        self.sync_items_pending = self.gauge(
            "oberaconnect_sync_items_pending",
            "Items pending sync",
            ["sync_type"]
        )

        # Histograms
        self.sync_duration = self.histogram(
            "oberaconnect_sync_duration_seconds",
            "Sync operation duration in seconds",
            ["sync_type"],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300]
        )
        self.api_request_duration = self.histogram(
            "oberaconnect_api_request_duration_seconds",
            "API request duration in seconds",
            ["service", "endpoint"],
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        )

    def counter(self, name: str, help: str, labels: List[str] = None) -> Counter:
        """Create or get a counter."""
        if name not in self._metrics:
            self._metrics[name] = Counter(name, help, labels or [])
        return self._metrics[name]

    def gauge(self, name: str, help: str, labels: List[str] = None) -> Gauge:
        """Create or get a gauge."""
        if name not in self._metrics:
            self._metrics[name] = Gauge(name, help, labels or [])
        return self._metrics[name]

    def histogram(self, name: str, help: str, labels: List[str] = None,
                  buckets: List[float] = None) -> Histogram:
        """Create or get a histogram."""
        if name not in self._metrics:
            self._metrics[name] = Histogram(name, help, labels or [], buckets or [])
        return self._metrics[name]

    def export(self) -> str:
        """Export all metrics in Prometheus format."""
        lines = [
            "# OberaConnect Notion Dashboards Metrics",
            f"# Generated at {datetime.utcnow().isoformat()}Z",
            ""
        ]
        with self._lock:
            for metric in self._metrics.values():
                lines.append(metric.export())
                lines.append("")
        return "\n".join(lines)


# Global metrics instance
metrics = MetricsRegistry()


# =============================================================================
# Convenience Functions & Decorators
# =============================================================================

@contextmanager
def track_sync(sync_type: str):
    """
    Context manager to track sync operations.

    Usage:
        with track_sync("customer_status"):
            sync_customers()
    """
    start_time = time.time()
    error_type = None

    try:
        yield
        metrics.sync_total.inc(sync_type=sync_type, status="success")
        metrics.last_sync_timestamp.set(time.time(), sync_type=sync_type)
    except Exception as e:
        error_type = type(e).__name__
        metrics.sync_total.inc(sync_type=sync_type, status="error")
        metrics.sync_errors.inc(sync_type=sync_type, error_type=error_type)
        raise
    finally:
        duration = time.time() - start_time
        metrics.sync_duration.observe(duration, sync_type=sync_type)
        logger.debug(f"Sync {sync_type} completed in {duration:.2f}s")


@contextmanager
def track_api_call(service: str, endpoint: str):
    """
    Context manager to track API calls.

    Usage:
        with track_api_call("notion", "create_page"):
            client.create_page(...)
    """
    start_time = time.time()

    try:
        yield
        metrics.api_requests.inc(service=service, endpoint=endpoint, status="success")
    except Exception as e:
        metrics.api_requests.inc(service=service, endpoint=endpoint, status="error")
        raise
    finally:
        duration = time.time() - start_time
        metrics.api_request_duration.observe(duration, service=service, endpoint=endpoint)


def track_page_created(database: str) -> None:
    """Track a page creation."""
    metrics.pages_created.inc(database=database)


def track_page_updated(database: str) -> None:
    """Track a page update."""
    metrics.pages_updated.inc(database=database)


def track_circuit_breaker(service: str, state: str) -> None:
    """Track circuit breaker state change."""
    state_value = {"closed": 0, "open": 1, "half-open": 0.5}.get(state, 0)
    metrics.circuit_breaker_state.set(state_value, service=service)
    if state == "open":
        metrics.circuit_breaker_trips.inc(service=service)


def set_fleet_counts(sites: int, devices: int) -> None:
    """Update fleet size gauges."""
    metrics.sites_total.set(sites)
    metrics.devices_total.set(devices)


def timed_sync(sync_type: str):
    """
    Decorator to track sync function timing.

    Usage:
        @timed_sync("customer_status")
        def sync_customers():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with track_sync(sync_type):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def timed_api(service: str, endpoint: str):
    """
    Decorator to track API function timing.

    Usage:
        @timed_api("notion", "query_database")
        def query_database(db_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with track_api_call(service, endpoint):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# CLI & Testing
# =============================================================================

def main():
    """Demo metrics functionality."""
    import argparse

    parser = argparse.ArgumentParser(description="Prometheus metrics demo")
    parser.add_argument("--export", action="store_true", help="Export current metrics")
    parser.add_argument("--demo", action="store_true", help="Generate demo metrics")
    parser.add_argument("--serve", type=int, metavar="PORT", help="Serve metrics on port")

    args = parser.parse_args()

    if args.demo:
        print("Generating demo metrics...")

        # Simulate some sync operations
        set_fleet_counts(sites=98, devices=323)

        for _ in range(5):
            with track_sync("customer_status"):
                time.sleep(0.1)

        for _ in range(3):
            with track_sync("daily_health"):
                time.sleep(0.05)

        # Simulate API calls
        for _ in range(10):
            with track_api_call("notion", "create_page"):
                time.sleep(0.02)
                track_page_created("customer_status")

        for _ in range(5):
            with track_api_call("unifi", "get_sites"):
                time.sleep(0.01)

        # Simulate a circuit breaker trip
        track_circuit_breaker("notion", "open")
        track_circuit_breaker("notion", "half-open")
        track_circuit_breaker("notion", "closed")

        print("Demo metrics generated!\n")

    if args.export or args.demo:
        print(metrics.export())

    if args.serve:
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class MetricsHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/metrics":
                    output = metrics.export()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(output.encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # Suppress logging

        server = HTTPServer(("0.0.0.0", args.serve), MetricsHandler)
        print(f"Serving metrics at http://localhost:{args.serve}/metrics")
        server.serve_forever()


if __name__ == "__main__":
    main()
