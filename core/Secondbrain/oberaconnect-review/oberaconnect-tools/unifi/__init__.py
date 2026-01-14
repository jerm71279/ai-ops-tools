"""
OberaConnect Tools - UniFi Module

UniFi Site Manager integration with natural language query engine.

Features:
- Site Manager API client
- Natural language fleet queries
- OberaConnect validation rules
- CLI interface

Usage:
    from oberaconnect_tools.unifi import get_client, UniFiAnalyzer
    
    client = get_client(demo=True)
    sites = client.get_sites()
    
    analyzer = UniFiAnalyzer(sites)
    result = analyzer.analyze("show sites with offline devices")
"""

from .models import (
    DeviceStatus,
    DeviceType,
    UniFiDevice,
    UniFiSite,
    FleetSummary
)

from .api_client import (
    UniFiAPIError,
    UniFiAPIConfig,
    UniFiClient,
    DemoUniFiClient,
    get_client
)

from .analyzer import (
    QueryIntent,
    QueryResult,
    UniFiAnalyzer
)

from .checkers import (
    SSIDChecker,
    VLANChecker,
    WiFiChannelChecker,
    FirewallChecker,
    DeviceOperationChecker,
    GuestNetworkChecker,
    get_unifi_checkers
)

__all__ = [
    # Models
    'DeviceStatus',
    'DeviceType',
    'UniFiDevice',
    'UniFiSite',
    'FleetSummary',
    # API Client
    'UniFiAPIError',
    'UniFiAPIConfig',
    'UniFiClient',
    'DemoUniFiClient',
    'get_client',
    # Analyzer
    'QueryIntent',
    'QueryResult',
    'UniFiAnalyzer',
    # Checkers
    'SSIDChecker',
    'VLANChecker',
    'WiFiChannelChecker',
    'FirewallChecker',
    'DeviceOperationChecker',
    'GuestNetworkChecker',
    'get_unifi_checkers'
]
