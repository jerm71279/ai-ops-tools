"""
UniFi Data Models

Data classes for UniFi Site Manager API responses.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class DeviceStatus(Enum):
    """Device connection status."""
    ONLINE = "online"
    OFFLINE = "offline"
    PENDING = "pending"
    UPGRADING = "upgrading"
    ADOPTING = "adopting"


class DeviceType(Enum):
    """UniFi device types."""
    UAP = "uap"      # Access Point
    USW = "usw"      # Switch  
    UGW = "ugw"      # Gateway (legacy)
    UDM = "udm"      # Dream Machine
    UDR = "udr"      # Dream Router
    UXG = "uxg"      # Next-Gen Gateway
    UCK = "uck"      # Cloud Key
    UPHONE = "uphone"  # VoIP Phone


@dataclass
class UniFiDevice:
    """Represents a single UniFi device."""
    mac: str
    name: str
    type: str
    model: str
    status: str
    ip: Optional[str] = None
    firmware: Optional[str] = None
    uptime: int = 0
    last_seen: Optional[datetime] = None
    
    # Additional fields based on device type
    clients: int = 0  # For APs
    ports: int = 0    # For switches
    
    @property
    def is_online(self) -> bool:
        return self.status.lower() == "online"
    
    @property
    def is_gateway(self) -> bool:
        return self.type.lower() in ('ugw', 'udm', 'udr', 'uxg')
    
    @property
    def is_ap(self) -> bool:
        return self.type.lower() == 'uap'
    
    @property
    def is_switch(self) -> bool:
        return self.type.lower() == 'usw'
    
    @property
    def uptime_hours(self) -> float:
        return self.uptime / 3600
    
    @property
    def uptime_days(self) -> float:
        return self.uptime / 86400
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'mac': self.mac,
            'name': self.name,
            'type': self.type,
            'model': self.model,
            'status': self.status,
            'ip': self.ip,
            'firmware': self.firmware,
            'uptime': self.uptime,
            'uptime_hours': round(self.uptime_hours, 1),
            'clients': self.clients,
            'is_online': self.is_online
        }


@dataclass
class UniFiSite:
    """
    Represents a UniFi Site with all its data.
    
    This is the primary data structure returned by the Site Manager API.
    """
    # Core identifiers
    id: str                      # Site ID from API (hostId)
    name: str                    # Site name (meta.desc or siteName)
    
    # Statistics
    total_devices: int = 0
    offline_devices: int = 0
    total_clients: int = 0
    
    # Device breakdown
    ap_count: int = 0
    switch_count: int = 0
    gateway_count: int = 0
    
    # Connectivity
    isp: str = "Unknown"
    wan_ip: Optional[str] = None
    
    # Status
    status: str = "unknown"
    health_score: int = 100
    
    # Metadata
    timezone: str = "America/Chicago"
    address: str = ""
    
    # Raw data for advanced queries
    devices: List[UniFiDevice] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def online_devices(self) -> int:
        return self.total_devices - self.offline_devices
    
    @property
    def health_status(self) -> str:
        """Human-readable health status."""
        if self.health_score >= 90:
            return "healthy"
        elif self.health_score >= 70:
            return "warning"
        elif self.health_score >= 50:
            return "degraded"
        else:
            return "critical"
    
    @property
    def has_offline_devices(self) -> bool:
        return self.offline_devices > 0
    
    @property
    def clients_per_ap(self) -> float:
        """Average clients per AP."""
        if self.ap_count == 0:
            return 0.0
        return self.total_clients / self.ap_count
    
    def calculate_health_score(self) -> int:
        """
        Calculate health score per OberaConnect formula.
        
        Factors:
        - Offline device percentage (40% weight)
        - Client load per AP (20% weight)  
        - Gateway online (40% weight)
        """
        score = 100
        
        # Offline devices penalty
        if self.total_devices > 0:
            offline_pct = self.offline_devices / self.total_devices
            score -= int(offline_pct * 40)
        
        # Client overload penalty (>50 clients/AP)
        if self.ap_count > 0 and self.clients_per_ap > 50:
            overload = min((self.clients_per_ap - 50) / 50, 1.0)
            score -= int(overload * 20)
        
        # Gateway offline is critical
        gateway_online = any(
            d.is_gateway and d.is_online 
            for d in self.devices
        )
        if not gateway_online and self.gateway_count > 0:
            score -= 40
        
        return max(0, min(100, score))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'totalDevices': self.total_devices,
            'offlineDevices': self.offline_devices,
            'onlineDevices': self.online_devices,
            'totalClients': self.total_clients,
            'apCount': self.ap_count,
            'switchCount': self.switch_count,
            'gatewayCount': self.gateway_count,
            'isp': self.isp,
            'wanIp': self.wan_ip,
            'status': self.status,
            'healthScore': self.health_score,
            'healthStatus': self.health_status,
            'timezone': self.timezone,
            'address': self.address
        }
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'UniFiSite':
        """
        Create UniFiSite from Site Manager API response.
        
        Handles the various API response formats.
        """
        # Extract site info from different possible locations
        meta = data.get('meta', {})
        statistics = data.get('statistics', {})
        
        # Site name can be in multiple places
        name = (
            meta.get('desc') or 
            data.get('siteName') or 
            data.get('name') or 
            data.get('hostId', 'Unknown')
        )
        
        # Device counts
        counts = statistics.get('counts', {})
        
        # ISP detection from WAN info
        isp = "Unknown"
        wan_info = data.get('wan', {}) or data.get('internet', {})
        if wan_info:
            isp = wan_info.get('isp') or wan_info.get('provider') or "Unknown"
        
        site = cls(
            id=data.get('hostId') or data.get('id', ''),
            name=name,
            total_devices=counts.get('totalDevice', 0) or statistics.get('deviceCount', 0),
            offline_devices=counts.get('offlineDevice', 0) or statistics.get('offlineCount', 0),
            total_clients=counts.get('totalClient', 0) or statistics.get('clientCount', 0),
            ap_count=counts.get('uap', 0),
            switch_count=counts.get('usw', 0),
            gateway_count=counts.get('ugw', 0) + counts.get('udm', 0),
            isp=isp,
            wan_ip=wan_info.get('ip'),
            status=data.get('status', 'unknown'),
            timezone=meta.get('timezone', 'America/Chicago'),
            address=meta.get('address', ''),
            raw_data=data
        )
        
        # Recalculate health score
        site.health_score = site.calculate_health_score()
        
        return site


@dataclass
class FleetSummary:
    """Summary statistics for the entire fleet."""
    total_sites: int = 0
    healthy_sites: int = 0
    warning_sites: int = 0
    critical_sites: int = 0
    
    total_devices: int = 0
    offline_devices: int = 0
    total_clients: int = 0
    
    total_aps: int = 0
    total_switches: int = 0
    total_gateways: int = 0
    
    sites_by_isp: Dict[str, int] = field(default_factory=dict)
    
    @property
    def fleet_health_score(self) -> int:
        """Overall fleet health as percentage."""
        if self.total_sites == 0:
            return 100
        return int((self.healthy_sites / self.total_sites) * 100)
    
    @property
    def device_availability(self) -> float:
        """Percentage of devices online."""
        if self.total_devices == 0:
            return 100.0
        return ((self.total_devices - self.offline_devices) / self.total_devices) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'totalSites': self.total_sites,
            'healthySites': self.healthy_sites,
            'warningSites': self.warning_sites,
            'criticalSites': self.critical_sites,
            'fleetHealthScore': self.fleet_health_score,
            'totalDevices': self.total_devices,
            'offlineDevices': self.offline_devices,
            'deviceAvailability': round(self.device_availability, 1),
            'totalClients': self.total_clients,
            'totalAPs': self.total_aps,
            'totalSwitches': self.total_switches,
            'totalGateways': self.total_gateways,
            'sitesByISP': self.sites_by_isp
        }
    
    @classmethod
    def from_sites(cls, sites: List[UniFiSite]) -> 'FleetSummary':
        """Calculate summary from list of sites."""
        summary = cls()
        
        isp_counts: Dict[str, int] = {}
        
        for site in sites:
            summary.total_sites += 1
            summary.total_devices += site.total_devices
            summary.offline_devices += site.offline_devices
            summary.total_clients += site.total_clients
            summary.total_aps += site.ap_count
            summary.total_switches += site.switch_count
            summary.total_gateways += site.gateway_count
            
            # Health categorization
            if site.health_score >= 90:
                summary.healthy_sites += 1
            elif site.health_score >= 70:
                summary.warning_sites += 1
            else:
                summary.critical_sites += 1
            
            # ISP tracking
            isp = site.isp or "Unknown"
            isp_counts[isp] = isp_counts.get(isp, 0) + 1
        
        summary.sites_by_isp = isp_counts
        
        return summary


__all__ = [
    'DeviceStatus',
    'DeviceType',
    'UniFiDevice',
    'UniFiSite',
    'FleetSummary'
]
