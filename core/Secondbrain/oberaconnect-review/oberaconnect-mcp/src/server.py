"""
OberaConnect MCP Server

Model Context Protocol server for Claude Code integration.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for MCP
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DEMO_MODE = os.getenv('OBERACONNECT_DEMO', 'false').lower() == 'true'
# Data refresh interval in seconds (default: 5 minutes)
DATA_REFRESH_INTERVAL = int(os.getenv('DATA_REFRESH_INTERVAL', '300'))


class DataManager:
    """
    Manages data fetching and caching with automatic refresh.

    Ensures data is never older than the configured refresh interval,
    preventing stale data issues that plagued the original implementation.
    """

    def __init__(self, unifi_client, ninjaone_client, refresh_interval: int = 300):
        self._unifi_client = unifi_client
        self._ninjaone_client = ninjaone_client
        self._refresh_interval = timedelta(seconds=refresh_interval)

        # Cached data
        self._unifi_sites = []
        self._ninjaone_alerts = []
        self._ninjaone_devices = []

        # Last refresh timestamps
        self._unifi_last_refresh: Optional[datetime] = None
        self._ninjaone_last_refresh: Optional[datetime] = None

        # Lazy-loaded analyzers
        self._analyzer = None
        self._correlator = None

        logger.info(f"DataManager initialized with {refresh_interval}s refresh interval")

    def _needs_refresh(self, last_refresh: Optional[datetime]) -> bool:
        """Check if data needs to be refreshed."""
        if last_refresh is None:
            return True
        return datetime.now() >= (last_refresh + self._refresh_interval)

    def _refresh_unifi(self) -> None:
        """Refresh UniFi data if stale."""
        if self._needs_refresh(self._unifi_last_refresh):
            logger.info("Refreshing UniFi site data...")
            try:
                self._unifi_sites = self._unifi_client.get_sites()
                self._unifi_last_refresh = datetime.now()
                self._analyzer = None  # Invalidate cached analyzer
                self._correlator = None  # Invalidate correlator too
                logger.info(f"UniFi data refreshed: {len(self._unifi_sites)} sites")
            except Exception as e:
                logger.error(f"Failed to refresh UniFi data: {e}")
                # Keep using stale data if refresh fails
                if not self._unifi_sites:
                    raise

    def _refresh_ninjaone(self) -> None:
        """Refresh NinjaOne data if stale."""
        if self._needs_refresh(self._ninjaone_last_refresh):
            logger.info("Refreshing NinjaOne data...")
            try:
                if hasattr(self._ninjaone_client, 'get_alerts'):
                    self._ninjaone_alerts = self._ninjaone_client.get_alerts()
                if hasattr(self._ninjaone_client, 'get_devices'):
                    self._ninjaone_devices = self._ninjaone_client.get_devices()
                self._ninjaone_last_refresh = datetime.now()
                self._correlator = None  # Invalidate cached correlator
                logger.info(f"NinjaOne data refreshed: {len(self._ninjaone_alerts)} alerts, {len(self._ninjaone_devices)} devices")
            except Exception as e:
                logger.error(f"Failed to refresh NinjaOne data: {e}")
                if not self._ninjaone_alerts and not self._ninjaone_devices:
                    raise

    @property
    def unifi_sites(self):
        """Get UniFi sites, refreshing if stale."""
        self._refresh_unifi()
        return self._unifi_sites

    @property
    def ninjaone_alerts(self):
        """Get NinjaOne alerts, refreshing if stale."""
        self._refresh_ninjaone()
        return self._ninjaone_alerts

    @property
    def ninjaone_devices(self):
        """Get NinjaOne devices, refreshing if stale."""
        self._refresh_ninjaone()
        return self._ninjaone_devices

    def get_analyzer(self):
        """Get UniFi analyzer with fresh data."""
        from oberaconnect_tools.unifi import UniFiAnalyzer
        self._refresh_unifi()
        if self._analyzer is None:
            self._analyzer = UniFiAnalyzer(self._unifi_sites)
        return self._analyzer

    def get_correlator(self):
        """Get cross-platform correlator with fresh data."""
        from oberaconnect_tools.ninjaone import Correlator
        self._refresh_unifi()
        self._refresh_ninjaone()
        if self._correlator is None:
            self._correlator = Correlator(
                self._unifi_sites,
                self._ninjaone_alerts,
                self._ninjaone_devices
            )
        return self._correlator

    def force_refresh(self) -> Dict[str, Any]:
        """Force immediate refresh of all data."""
        self._unifi_last_refresh = None
        self._ninjaone_last_refresh = None
        self._refresh_unifi()
        self._refresh_ninjaone()
        return {
            "unifi_sites": len(self._unifi_sites),
            "ninjaone_alerts": len(self._ninjaone_alerts),
            "ninjaone_devices": len(self._ninjaone_devices),
            "timestamp": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """Get data freshness status."""
        now = datetime.now()
        return {
            "unifi": {
                "site_count": len(self._unifi_sites),
                "last_refresh": self._unifi_last_refresh.isoformat() if self._unifi_last_refresh else None,
                "age_seconds": (now - self._unifi_last_refresh).total_seconds() if self._unifi_last_refresh else None,
                "stale": self._needs_refresh(self._unifi_last_refresh)
            },
            "ninjaone": {
                "alert_count": len(self._ninjaone_alerts),
                "device_count": len(self._ninjaone_devices),
                "last_refresh": self._ninjaone_last_refresh.isoformat() if self._ninjaone_last_refresh else None,
                "age_seconds": (now - self._ninjaone_last_refresh).total_seconds() if self._ninjaone_last_refresh else None,
                "stale": self._needs_refresh(self._ninjaone_last_refresh)
            },
            "refresh_interval_seconds": self._refresh_interval.total_seconds()
        }


def create_server():
    """Create MCP server."""
    from oberaconnect_tools.unifi import get_client as get_unifi_client
    from oberaconnect_tools.ninjaone import get_client as get_ninjaone_client
    from oberaconnect_tools.common import validate_operation
    from oberaconnect_tools.unifi.checkers import get_unifi_checkers

    server = Server("oberaconnect")

    # Initialize clients
    unifi_client = get_unifi_client(demo=DEMO_MODE)
    ninjaone_client = get_ninjaone_client(demo=DEMO_MODE)

    # Use DataManager for automatic data refresh (no more stale data!)
    data_manager = DataManager(
        unifi_client=unifi_client,
        ninjaone_client=ninjaone_client,
        refresh_interval=DATA_REFRESH_INTERVAL
    )

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name="unifi_query",
                description="Query UniFi fleet with natural language",
                inputSchema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
            ),
            Tool(
                name="unifi_summary",
                description="Get fleet summary",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="unifi_validate",
                description="Validate a proposed UniFi operation",
                inputSchema={"type": "object", "properties": {
                    "action": {"type": "string"},
                    "sites": {"type": "array", "items": {"type": "string"}},
                    "plan": {"type": "object"}
                }, "required": ["action"]}
            ),
            Tool(
                name="ninjaone_alerts",
                description="Get NinjaOne alerts",
                inputSchema={"type": "object", "properties": {"severity": {"type": "string"}}}
            ),
            Tool(
                name="incident_context",
                description="Get correlated incident context",
                inputSchema={"type": "object", "properties": {"customer": {"type": "string"}}, "required": ["customer"]}
            ),
            Tool(
                name="morning_check",
                description="Run morning check",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="data_status",
                description="Get data freshness status",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="force_refresh",
                description="Force refresh all data from APIs",
                inputSchema={"type": "object", "properties": {}}
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            if name == "unifi_query":
                analyzer = data_manager.get_analyzer()
                result = analyzer.analyze(arguments.get("query", "summary"))
                return [TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]

            elif name == "unifi_summary":
                analyzer = data_manager.get_analyzer()
                summary = analyzer.summary()
                return [TextContent(type="text", text=json.dumps(summary.to_dict(), indent=2))]

            elif name == "unifi_validate":
                result = validate_operation(
                    action=arguments.get("action", ""),
                    sites=arguments.get("sites", []),
                    plan=arguments.get("plan", {}),
                    extra_checkers=get_unifi_checkers()
                )
                return [TextContent(type="text", text=json.dumps({
                    "canProceed": result.can_proceed,
                    "blocked": result.blocked,
                    "issues": result.all_issues,
                    "suggestions": result.all_suggestions
                }, indent=2))]

            elif name == "ninjaone_alerts":
                alerts = data_manager.ninjaone_alerts
                severity = arguments.get("severity")
                if severity:
                    alerts = [a for a in alerts if a.severity == severity]
                return [TextContent(type="text", text=json.dumps({
                    "count": len(alerts),
                    "alerts": [a.to_dict() for a in alerts]
                }, indent=2))]

            elif name == "incident_context":
                correlator = data_manager.get_correlator()
                incident = correlator.get_incident_context(arguments.get("customer", ""))
                return [TextContent(type="text", text=json.dumps(incident.to_dict(), indent=2))]

            elif name == "morning_check":
                correlator = data_manager.get_correlator()
                report = correlator.get_morning_check_report()
                return [TextContent(type="text", text=json.dumps(report, indent=2))]

            elif name == "data_status":
                status = data_manager.get_status()
                return [TextContent(type="text", text=json.dumps(status, indent=2))]

            elif name == "force_refresh":
                result = data_manager.force_refresh()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as e:
            logger.exception(f"Error in tool {name}")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    return server


async def main():
    if not HAS_MCP:
        print("MCP not installed. pip install mcp")
        sys.exit(1)
    
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
