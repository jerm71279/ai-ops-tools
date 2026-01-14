"""
Data source interfaces and implementations.

Provides abstraction layer for external APIs:
- UniFi Site Manager
- NinjaOne RMM
- Future: Azure, Axcient, etc.

Usage:
    from data_sources import get_unifi, get_ninjaone

    # Get stub implementation (default)
    unifi = get_unifi()
    sites = unifi.fetch_sites()

    # Or register real MCP implementation
    from data_sources import get_factory, MCPUniFiDataSource, MCPNinjaOneDataSource

    factory = get_factory()
    factory.register_unifi(MCPUniFiDataSource())
    factory.register_ninjaone(MCPNinjaOneDataSource())

    unifi = factory.get_unifi()
    sites = unifi.fetch_sites()  # Now uses real API

    # Or use convenience function for production mode
    from data_sources import use_real_apis
    use_real_apis()  # Registers MCP implementations
"""

from data_sources.interface import (
    # Interfaces
    UniFiDataSource,
    NinjaOneDataSource,
    DataSourceFactory,
    # Data models
    UniFiSite,
    UniFiDevice,
    NinjaOneOrganization,
    NinjaOneAlert,
    BackupStatus,
    DeviceStatus,
    AlertSeverity,
    # Factory functions
    get_factory,
    get_unifi,
    get_ninjaone,
)

from data_sources.stub import (
    StubUniFiDataSource,
    StubNinjaOneDataSource,
)

# Real MCP implementations
from data_sources.unifi_mcp import MCPUniFiDataSource
from data_sources.ninjaone_mcp import MCPNinjaOneDataSource


def use_real_apis() -> None:
    """
    Register real API implementations with the factory.

    After calling this, get_unifi() and get_ninjaone() will return
    real API clients instead of stubs.

    Requires environment variables:
    - UniFi: UNIFI_API_KEY or legacy token file
    - NinjaOne: NINJAONE_CLIENT_ID, NINJAONE_CLIENT_SECRET
    """
    factory = get_factory()
    factory.register_unifi(MCPUniFiDataSource())
    factory.register_ninjaone(MCPNinjaOneDataSource())


def use_stub_apis() -> None:
    """
    Register stub implementations with the factory.

    Useful for testing or when real APIs are unavailable.
    """
    factory = get_factory()
    factory.register_unifi(StubUniFiDataSource())
    factory.register_ninjaone(StubNinjaOneDataSource())


__all__ = [
    # Interfaces
    "UniFiDataSource",
    "NinjaOneDataSource",
    "DataSourceFactory",
    # Data models
    "UniFiSite",
    "UniFiDevice",
    "NinjaOneOrganization",
    "NinjaOneAlert",
    "BackupStatus",
    "DeviceStatus",
    "AlertSeverity",
    # Factory functions
    "get_factory",
    "get_unifi",
    "get_ninjaone",
    "use_real_apis",
    "use_stub_apis",
    # Stub implementations
    "StubUniFiDataSource",
    "StubNinjaOneDataSource",
    # Real MCP implementations
    "MCPUniFiDataSource",
    "MCPNinjaOneDataSource",
]
