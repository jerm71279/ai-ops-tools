#!/usr/bin/env python3
"""
Health Check Endpoints for OberaConnect Notion Dashboards

Provides /health and /ready endpoints for monitoring and orchestration.
Compatible with Kubernetes probes, Docker healthchecks, and monitoring systems.

Endpoints:
    /health  - Liveness probe (is the service running?)
    /ready   - Readiness probe (can it handle traffic?)
    /metrics - Prometheus-compatible metrics

Usage:
    # Standalone server
    python health_check.py --port 8080

    # Import into Flask app
    from health_check import health_blueprint
    app.register_blueprint(health_blueprint)

Author: OberaConnect
Created: 2025
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from functools import wraps
import threading

logger = logging.getLogger("oberaconnect.health")

# =============================================================================
# Health Check Data Structures
# =============================================================================

@dataclass
class ComponentHealth:
    """Health status of a single component."""
    name: str
    healthy: bool
    latency_ms: Optional[float] = None
    last_check: Optional[str] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Overall health status."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: str
    version: str
    uptime_seconds: float
    components: Dict[str, ComponentHealth] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["components"] = {
            name: asdict(comp) for name, comp in self.components.items()
        }
        return result


# =============================================================================
# Health Checker
# =============================================================================

class HealthChecker:
    """
    Health check manager for all service dependencies.
    """

    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self.start_time = datetime.utcnow()
        self._checks: Dict[str, callable] = {}
        self._cache: Dict[str, ComponentHealth] = {}
        self._cache_ttl = 10  # seconds
        self._lock = threading.Lock()

    def register_check(self, name: str, check_func: callable) -> None:
        """Register a health check function."""
        self._checks[name] = check_func
        logger.info(f"Registered health check: {name}")

    def _run_check(self, name: str, check_func: callable) -> ComponentHealth:
        """Run a single health check with timing."""
        start = time.time()
        try:
            result = check_func()
            latency_ms = (time.time() - start) * 1000

            if isinstance(result, dict):
                return ComponentHealth(
                    name=name,
                    healthy=result.get("healthy", True),
                    latency_ms=latency_ms,
                    last_check=datetime.utcnow().isoformat() + "Z",
                    details=result.get("details", {})
                )
            else:
                return ComponentHealth(
                    name=name,
                    healthy=bool(result),
                    latency_ms=latency_ms,
                    last_check=datetime.utcnow().isoformat() + "Z"
                )
        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            logger.warning(f"Health check {name} failed: {e}")
            return ComponentHealth(
                name=name,
                healthy=False,
                latency_ms=latency_ms,
                last_check=datetime.utcnow().isoformat() + "Z",
                error=str(e)
            )

    def check_all(self, use_cache: bool = True) -> HealthStatus:
        """Run all health checks and return overall status."""
        components = {}

        for name, check_func in self._checks.items():
            # Check cache
            if use_cache:
                with self._lock:
                    cached = self._cache.get(name)
                    if cached and cached.last_check:
                        cache_age = (
                            datetime.utcnow() -
                            datetime.fromisoformat(cached.last_check.rstrip("Z"))
                        ).total_seconds()
                        if cache_age < self._cache_ttl:
                            components[name] = cached
                            continue

            # Run check
            result = self._run_check(name, check_func)
            components[name] = result

            # Update cache
            with self._lock:
                self._cache[name] = result

        # Determine overall status
        all_healthy = all(c.healthy for c in components.values())
        any_healthy = any(c.healthy for c in components.values())

        if all_healthy:
            status = "healthy"
        elif any_healthy:
            status = "degraded"
        else:
            status = "unhealthy"

        uptime = (datetime.utcnow() - self.start_time).total_seconds()

        return HealthStatus(
            status=status,
            timestamp=datetime.utcnow().isoformat() + "Z",
            version=self.version,
            uptime_seconds=uptime,
            components=components
        )

    def is_healthy(self) -> bool:
        """Quick check if service is healthy."""
        status = self.check_all()
        return status.status in ("healthy", "degraded")

    def is_ready(self) -> bool:
        """Check if service is ready to handle traffic."""
        status = self.check_all()
        return status.status == "healthy"


# =============================================================================
# Default Health Checks
# =============================================================================

def check_notion_api() -> Dict:
    """Check Notion API connectivity."""
    try:
        from notion_client import Client

        token = os.getenv("NOTION_TOKEN")
        if not token:
            return {"healthy": False, "details": {"error": "NOTION_TOKEN not set"}}

        client = Client(auth=token)
        # Simple API call to verify connectivity
        users = client.users.me()

        return {
            "healthy": True,
            "details": {
                "user_type": users.get("type"),
                "bot_name": users.get("name", "Unknown")
            }
        }
    except ImportError:
        return {"healthy": False, "details": {"error": "notion-client not installed"}}
    except Exception as e:
        return {"healthy": False, "details": {"error": str(e)}}


def check_unifi_api() -> Dict:
    """Check UniFi Site Manager API connectivity."""
    try:
        import requests

        token = os.getenv("UNIFI_API_TOKEN")
        if not token:
            return {"healthy": False, "details": {"error": "UNIFI_API_TOKEN not set"}}

        resp = requests.get(
            "https://api.ui.com/ea/sites",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if resp.status_code == 200:
            data = resp.json()
            return {
                "healthy": True,
                "details": {"site_count": len(data.get("data", []))}
            }
        else:
            return {
                "healthy": False,
                "details": {"status_code": resp.status_code}
            }
    except Exception as e:
        return {"healthy": False, "details": {"error": str(e)}}


def check_ninjaone_api() -> Dict:
    """Check NinjaOne API connectivity."""
    try:
        import requests

        client_id = os.getenv("NINJAONE_CLIENT_ID")
        client_secret = os.getenv("NINJAONE_CLIENT_SECRET")

        if not client_id or not client_secret:
            return {"healthy": False, "details": {"error": "NinjaOne credentials not set"}}

        # Get OAuth token
        resp = requests.post(
            "https://app.ninjarmm.com/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "monitoring"
            },
            timeout=10
        )

        if resp.status_code == 200:
            return {
                "healthy": True,
                "details": {"auth": "oauth2_success"}
            }
        else:
            return {
                "healthy": False,
                "details": {"status_code": resp.status_code}
            }
    except Exception as e:
        return {"healthy": False, "details": {"error": str(e)}}


def check_disk_space() -> Dict:
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100

        return {
            "healthy": free_percent > 10,
            "details": {
                "total_gb": round(total / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "free_percent": round(free_percent, 1)
            }
        }
    except Exception as e:
        return {"healthy": False, "details": {"error": str(e)}}


def check_memory() -> Dict:
    """Check available memory."""
    try:
        with open("/proc/meminfo") as f:
            meminfo = dict(
                line.split(":")
                for line in f.read().splitlines()
                if ":" in line
            )

        total = int(meminfo["MemTotal"].strip().split()[0]) / 1024  # MB
        available = int(meminfo["MemAvailable"].strip().split()[0]) / 1024  # MB
        available_percent = (available / total) * 100

        return {
            "healthy": available_percent > 10,
            "details": {
                "total_mb": round(total, 0),
                "available_mb": round(available, 0),
                "available_percent": round(available_percent, 1)
            }
        }
    except Exception as e:
        return {"healthy": True, "details": {"error": str(e), "note": "non-linux"}}


# =============================================================================
# Metrics (Prometheus Format)
# =============================================================================

class MetricsCollector:
    """Collect and expose Prometheus-compatible metrics."""

    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._lock = threading.Lock()

    def inc(self, name: str, value: int = 1, labels: Dict = None) -> None:
        """Increment a counter."""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + value

    def set(self, name: str, value: float, labels: Dict = None) -> None:
        """Set a gauge value."""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value

    def _make_key(self, name: str, labels: Dict = None) -> str:
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def export(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        lines.append("# OberaConnect Notion Dashboards Metrics")
        lines.append("")

        with self._lock:
            for key, value in self._counters.items():
                lines.append(f"# TYPE {key.split('{')[0]} counter")
                lines.append(f"{key} {value}")

            for key, value in self._gauges.items():
                lines.append(f"# TYPE {key.split('{')[0]} gauge")
                lines.append(f"{key} {value}")

        return "\n".join(lines)


# Global instances
_health_checker: Optional[HealthChecker] = None
_metrics: Optional[MetricsCollector] = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker(version=os.getenv("APP_VERSION", "1.0.0"))
        # Register default checks
        _health_checker.register_check("notion_api", check_notion_api)
        _health_checker.register_check("disk_space", check_disk_space)
        _health_checker.register_check("memory", check_memory)
        # Optional checks based on config
        if os.getenv("UNIFI_API_TOKEN"):
            _health_checker.register_check("unifi_api", check_unifi_api)
        if os.getenv("NINJAONE_CLIENT_ID"):
            _health_checker.register_check("ninjaone_api", check_ninjaone_api)
    return _health_checker


def get_metrics() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics


# =============================================================================
# Flask Blueprint (for integration)
# =============================================================================

try:
    from flask import Blueprint, jsonify, Response

    health_blueprint = Blueprint("health", __name__)

    @health_blueprint.route("/health")
    def health_endpoint():
        """Liveness probe - is the service running?"""
        checker = get_health_checker()
        status = checker.check_all()

        http_status = 200 if status.status != "unhealthy" else 503
        return jsonify(status.to_dict()), http_status

    @health_blueprint.route("/ready")
    def ready_endpoint():
        """Readiness probe - can handle traffic?"""
        checker = get_health_checker()
        status = checker.check_all(use_cache=False)

        http_status = 200 if status.status == "healthy" else 503
        return jsonify({
            "ready": status.status == "healthy",
            "status": status.status,
            "components": {
                name: comp.healthy
                for name, comp in status.components.items()
            }
        }), http_status

    @health_blueprint.route("/metrics")
    def metrics_endpoint():
        """Prometheus metrics endpoint."""
        metrics = get_metrics()

        # Update gauge metrics
        checker = get_health_checker()
        status = checker.check_all()
        metrics.set("oberaconnect_uptime_seconds", status.uptime_seconds)
        metrics.set("oberaconnect_healthy", 1 if status.status == "healthy" else 0)

        for name, comp in status.components.items():
            metrics.set(
                "oberaconnect_component_healthy",
                1 if comp.healthy else 0,
                labels={"component": name}
            )
            if comp.latency_ms:
                metrics.set(
                    "oberaconnect_component_latency_ms",
                    comp.latency_ms,
                    labels={"component": name}
                )

        return Response(metrics.export(), mimetype="text/plain")

except ImportError:
    health_blueprint = None


# =============================================================================
# Standalone Server
# =============================================================================

def run_standalone(port: int = 8080):
    """Run standalone health check server."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json

    checker = get_health_checker()
    metrics = get_metrics()

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                status = checker.check_all()
                self.send_response(200 if status.status != "unhealthy" else 503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(status.to_dict()).encode())

            elif self.path == "/ready":
                status = checker.check_all(use_cache=False)
                ready = status.status == "healthy"
                self.send_response(200 if ready else 503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ready": ready,
                    "status": status.status
                }).encode())

            elif self.path == "/metrics":
                status = checker.check_all()
                metrics.set("oberaconnect_uptime_seconds", status.uptime_seconds)
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(metrics.export().encode())

            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            logger.debug(f"{self.address_string()} - {format % args}")

    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Health check server running on port {port}")
    print(f"Health endpoints available at http://localhost:{port}/health")
    server.serve_forever()


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Health check service")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--check", action="store_true", help="Run checks and exit")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.check:
        checker = get_health_checker()
        status = checker.check_all(use_cache=False)

        if args.json:
            print(json.dumps(status.to_dict(), indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"Health Status: {status.status.upper()}")
            print(f"Version: {status.version}")
            print(f"Uptime: {status.uptime_seconds:.0f}s")
            print(f"{'='*50}")
            for name, comp in status.components.items():
                icon = "✅" if comp.healthy else "❌"
                latency = f" ({comp.latency_ms:.0f}ms)" if comp.latency_ms else ""
                print(f"  {icon} {name}{latency}")
                if comp.error:
                    print(f"      Error: {comp.error}")
            print()

        return 0 if status.status == "healthy" else 1

    run_standalone(args.port)


if __name__ == "__main__":
    exit(main())
