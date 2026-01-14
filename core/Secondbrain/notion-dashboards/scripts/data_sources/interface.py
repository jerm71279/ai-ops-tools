"""
Abstract interfaces for external data sources.

Defines contracts for UniFi, NinjaOne, and other API integrations.
Enables dependency injection and testing with stub implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


# =============================================================================
# Data Models
# =============================================================================

class DeviceStatus(Enum):
    """Device operational status."""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    UPGRADING = "upgrading"
    PROVISIONING = "provisioning"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class UniFiSite:
    """
    Represents a customer site from UniFi Site Manager.
    
    Maps to UniFi Site Manager API response structure.
    """
    site_id: str
    name: str
    
    # Location
    state: str = ""
    address: str = ""
    timezone: str = "UTC"
    
    # Device counts
    devices_online: int = 0
    devices_offline: int = 0
    devices_total: int = 0
    
    # WiFi metrics
    wifi_clients: int = 0
    wifi_clients_weak_signal: int = 0  # Below -65dBm threshold
    
    # Network metrics
    wan_ip: str = ""
    isp: str = ""
    uptime_seconds: int = 0
    
    # Timestamps
    last_seen: Optional[datetime] = None
    
    # Legacy stack flags (for transition tracking)
    has_mikrotik: bool = False
    has_sonicwall: bool = False
    has_azure: bool = False
    
    # Business metadata
    contract_renewal: Optional[str] = None
    primary_contact: str = ""
    notes: str = ""
    
    @property
    def devices_availability_pct(self) -> float:
        """Calculate device availability percentage."""
        if self.devices_total == 0:
            return 100.0
        return (self.devices_online / self.devices_total) * 100


@dataclass
class UniFiDevice:
    """
    Represents a network device from UniFi.
    
    Covers APs, switches, gateways, and other managed devices.
    """
    device_id: str
    name: str
    mac_address: str
    
    # Type and model
    device_type: str = ""  # "ap", "switch", "gateway", etc.
    model: str = ""
    
    # Status
    status: DeviceStatus = DeviceStatus.UNKNOWN
    ip_address: str = ""
    
    # Firmware
    firmware_version: str = ""
    firmware_upgradeable: bool = False
    
    # Metrics
    uptime_seconds: int = 0
    cpu_usage_pct: float = 0.0
    memory_usage_pct: float = 0.0
    
    # For APs
    wifi_clients: int = 0
    channel_2g: Optional[int] = None
    channel_5g: Optional[int] = None
    
    # For switches
    port_count: int = 0
    poe_ports: int = 0
    
    # Site reference
    site_id: str = ""
    
    # Timestamps
    last_seen: Optional[datetime] = None
    adopted_at: Optional[datetime] = None


@dataclass
class NinjaOneAlert:
    """
    Represents an alert from NinjaOne RMM.
    """
    alert_id: str
    device_id: str
    device_name: str
    
    severity: AlertSeverity = AlertSeverity.INFO
    message: str = ""
    category: str = ""  # "backup", "disk", "cpu", "memory", etc.
    
    # Timestamps
    created_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    is_acknowledged: bool = False


@dataclass
class NinjaOneOrganization:
    """
    Represents a customer organization in NinjaOne.
    
    Maps to OberaConnect customer sites.
    """
    org_id: str
    name: str
    
    # Counts
    device_count: int = 0
    online_devices: int = 0
    offline_devices: int = 0
    
    # Tickets
    open_tickets: int = 0
    
    # Alerts by severity
    alerts_critical: int = 0
    alerts_warning: int = 0
    alerts_info: int = 0
    
    # Backup status
    backup_status: str = "unknown"  # success, partial, failed, unknown
    last_backup: Optional[datetime] = None
    
    # Alert details (top alerts)
    alert_summary: List[str] = field(default_factory=list)


@dataclass 
class BackupStatus:
    """
    Backup status information.
    """
    status: str = "unknown"  # success, partial, failed, unknown
    last_successful: Optional[datetime] = None
    last_attempted: Optional[datetime] = None
    protected_devices: int = 0
    total_devices: int = 0
    failed_jobs: List[str] = field(default_factory=list)


# =============================================================================
# Abstract Interfaces
# =============================================================================

class UniFiDataSource(ABC):
    """
    Abstract interface for UniFi Site Manager data.
    
    Implementations:
    - StubUniFiDataSource: Test/development stub
    - UniFiSiteManagerAPI: Real API integration (future)
    """
    
    @abstractmethod
    def fetch_sites(self) -> List[UniFiSite]:
        """
        Fetch all customer sites.
        
        Returns:
            List of UniFiSite objects
        """
        pass
    
    @abstractmethod
    def fetch_site(self, site_id: str) -> Optional[UniFiSite]:
        """
        Fetch a specific site by ID.
        
        Args:
            site_id: Site identifier
            
        Returns:
            UniFiSite or None if not found
        """
        pass
    
    @abstractmethod
    def fetch_devices(self, site_id: str) -> List[UniFiDevice]:
        """
        Fetch all devices for a site.
        
        Args:
            site_id: Site identifier
            
        Returns:
            List of UniFiDevice objects
        """
        pass
    
    @abstractmethod
    def fetch_device(self, site_id: str, device_id: str) -> Optional[UniFiDevice]:
        """
        Fetch a specific device.
        
        Args:
            site_id: Site identifier
            device_id: Device identifier
            
        Returns:
            UniFiDevice or None if not found
        """
        pass
    
    def fetch_sites_with_devices(self) -> List[tuple[UniFiSite, List[UniFiDevice]]]:
        """
        Fetch all sites with their devices.
        
        Default implementation calls fetch_sites then fetch_devices for each.
        Override for more efficient batch fetching.
        """
        results = []
        for site in self.fetch_sites():
            devices = self.fetch_devices(site.site_id)
            results.append((site, devices))
        return results


class NinjaOneDataSource(ABC):
    """
    Abstract interface for NinjaOne RMM data.
    
    Implementations:
    - StubNinjaOneDataSource: Test/development stub
    - NinjaOneAPI: Real API integration (future)
    """
    
    @abstractmethod
    def fetch_organization(self, org_name: str) -> Optional[NinjaOneOrganization]:
        """
        Fetch organization data by name.
        
        Args:
            org_name: Organization/customer name
            
        Returns:
            NinjaOneOrganization or None if not found
        """
        pass
    
    @abstractmethod
    def fetch_organizations(self) -> List[NinjaOneOrganization]:
        """
        Fetch all organizations.
        
        Returns:
            List of NinjaOneOrganization objects
        """
        pass
    
    @abstractmethod
    def fetch_alerts(
        self, 
        org_name: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
        active_only: bool = True
    ) -> List[NinjaOneAlert]:
        """
        Fetch alerts with optional filtering.
        
        Args:
            org_name: Filter by organization name
            severity: Filter by severity level
            active_only: Only return active (unresolved) alerts
            
        Returns:
            List of NinjaOneAlert objects
        """
        pass
    
    @abstractmethod
    def fetch_backup_status(self, org_name: str) -> BackupStatus:
        """
        Fetch backup status for an organization.
        
        Args:
            org_name: Organization name
            
        Returns:
            BackupStatus object
        """
        pass


class DataSourceFactory:
    """
    Factory for creating data source instances.
    
    Allows runtime switching between stub and real implementations.
    
    Example:
        factory = DataSourceFactory()
        factory.register_unifi(MyUniFiAPI(token="..."))
        
        unifi = factory.get_unifi()
        sites = unifi.fetch_sites()
    """
    
    def __init__(self):
        self._unifi: Optional[UniFiDataSource] = None
        self._ninjaone: Optional[NinjaOneDataSource] = None
    
    def register_unifi(self, source: UniFiDataSource) -> None:
        """Register UniFi data source implementation."""
        self._unifi = source
    
    def register_ninjaone(self, source: NinjaOneDataSource) -> None:
        """Register NinjaOne data source implementation."""
        self._ninjaone = source
    
    def get_unifi(self) -> UniFiDataSource:
        """
        Get UniFi data source.
        
        Falls back to stub if not registered.
        """
        if self._unifi is None:
            from data_sources.stub import StubUniFiDataSource
            self._unifi = StubUniFiDataSource()
        return self._unifi
    
    def get_ninjaone(self) -> NinjaOneDataSource:
        """
        Get NinjaOne data source.
        
        Falls back to stub if not registered.
        """
        if self._ninjaone is None:
            from data_sources.stub import StubNinjaOneDataSource
            self._ninjaone = StubNinjaOneDataSource()
        return self._ninjaone


# Global factory instance
_factory: Optional[DataSourceFactory] = None


def get_factory() -> DataSourceFactory:
    """Get or create global data source factory."""
    global _factory
    if _factory is None:
        _factory = DataSourceFactory()
    return _factory


def get_unifi() -> UniFiDataSource:
    """Convenience function to get UniFi data source."""
    return get_factory().get_unifi()


def get_ninjaone() -> NinjaOneDataSource:
    """Convenience function to get NinjaOne data source."""
    return get_factory().get_ninjaone()
