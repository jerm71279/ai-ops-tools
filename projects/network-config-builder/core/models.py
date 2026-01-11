"""
Core configuration models for multi-vendor network configurations.

Uses dataclasses for type safety and validation.
Based on automation-script-builder patterns.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class VendorType(Enum):
    """Supported vendor types"""
    MIKROTIK = "mikrotik"
    SONICWALL = "sonicwall"
    UNIFI = "unifi"
    EDGEROUTER = "edgerouter"


class DeploymentType(Enum):
    """Deployment configuration types"""
    ROUTER_ONLY = "router_only"
    AP_ONLY = "ap_only"
    ROUTER_AND_AP = "router_and_ap"
    FIREWALL = "firewall"
    SWITCH = "switch"


@dataclass
class CustomerInfo:
    """Customer metadata"""
    name: str
    site: str
    contact: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class WANConfig:
    """WAN interface configuration"""
    interface: str = "ether1"
    mode: str = "static"  # static, dhcp, pppoe
    ip: Optional[str] = None
    netmask: Optional[int] = None
    gateway: Optional[str] = None
    dns: List[str] = field(default_factory=list)


@dataclass
class DHCPConfig:
    """DHCP server configuration"""
    enabled: bool = True
    pool_start: str = ""
    pool_end: str = ""
    lease_time: str = "12h"
    dns_servers: List[str] = field(default_factory=list)


@dataclass
class LANConfig:
    """LAN interface/bridge configuration"""
    interface: str = "bridge-lan"
    ip: str = ""
    netmask: int = 24
    dhcp: Optional[DHCPConfig] = None


@dataclass
class VLANConfig:
    """VLAN configuration"""
    id: int
    name: str
    subnet: str
    dhcp: bool = False
    isolation: bool = False
    dhcp_config: Optional[DHCPConfig] = None


@dataclass
class WirelessConfig:
    """Wireless configuration"""
    ssid: str
    password: str
    mode: str = "legacy"  # legacy or wifi6
    band: str = "2ghz-b/g/n"
    channel_width: str = "20mhz"
    country: str = "us"
    vlan: Optional[int] = None
    guest_mode: bool = False


@dataclass
class FirewallRule:
    """Firewall rule configuration"""
    name: str
    action: str  # accept, drop, reject
    protocol: str  # tcp, udp, icmp, any
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    chain: str = "forward"
    comment: Optional[str] = None


@dataclass
class PortForward:
    """Port forwarding rule"""
    name: str
    protocol: str
    external_port: int
    internal_ip: str
    internal_port: int
    enabled: bool = True


@dataclass
class VPNConfig:
    """VPN configuration"""
    type: str  # ipsec, wireguard, openvpn, l2tp
    name: str
    peer_ip: Optional[str] = None
    local_subnet: Optional[str] = None
    remote_subnet: Optional[str] = None
    preshared_key: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityConfig:
    """Security and admin access configuration"""
    admin_username: str
    admin_password: str
    allowed_management_ips: List[str] = field(default_factory=list)
    disable_unused_services: bool = True


@dataclass
class NetworkConfig:
    """
    Complete network configuration for any vendor.

    This is the unified configuration model that works across
    all supported vendors (MikroTik, SonicWall, Ubiquiti).
    """
    vendor: VendorType
    device_model: str
    customer: CustomerInfo
    deployment_type: DeploymentType

    wan: Optional[WANConfig] = None
    lan: Optional[LANConfig] = None
    vlans: List[VLANConfig] = field(default_factory=list)
    wireless: List[WirelessConfig] = field(default_factory=list)
    firewall_rules: List[FirewallRule] = field(default_factory=list)
    port_forwards: List[PortForward] = field(default_factory=list)
    vpn: List[VPNConfig] = field(default_factory=list)
    security: Optional[SecurityConfig] = None

    # Vendor-specific configuration extensions
    mikrotik_config: Dict[str, Any] = field(default_factory=dict)
    sonicwall_config: Dict[str, Any] = field(default_factory=dict)
    ubiquiti_config: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    version: str = "1.0"
    generated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            'vendor': self.vendor.value,
            'device_model': self.device_model,
            'customer': {
                'name': self.customer.name,
                'site': self.customer.site,
                'contact': self.customer.contact,
                'notes': self.customer.notes,
            },
            'deployment_type': self.deployment_type.value,
            'version': self.version,
        }

        if self.wan:
            result['wan'] = {
                'interface': self.wan.interface,
                'mode': self.wan.mode,
                'ip': self.wan.ip,
                'netmask': self.wan.netmask,
                'gateway': self.wan.gateway,
                'dns': self.wan.dns,
            }

        if self.lan:
            result['lan'] = {
                'interface': self.lan.interface,
                'ip': self.lan.ip,
                'netmask': self.lan.netmask,
            }
            if self.lan.dhcp:
                result['lan']['dhcp'] = {
                    'enabled': self.lan.dhcp.enabled,
                    'pool_start': self.lan.dhcp.pool_start,
                    'pool_end': self.lan.dhcp.pool_end,
                    'lease_time': self.lan.dhcp.lease_time,
                    'dns_servers': self.lan.dhcp.dns_servers,
                }

        if self.vlans:
            result['vlans'] = [
                {
                    'id': vlan.id,
                    'name': vlan.name,
                    'subnet': vlan.subnet,
                    'dhcp': vlan.dhcp,
                    'isolation': vlan.isolation,
                }
                for vlan in self.vlans
            ]

        if self.wireless:
            result['wireless'] = [
                {
                    'ssid': w.ssid,
                    'password': w.password,
                    'mode': w.mode,
                    'band': w.band,
                    'channel_width': w.channel_width,
                    'country': w.country,
                    'vlan': w.vlan,
                    'guest_mode': w.guest_mode,
                }
                for w in self.wireless
            ]

        if self.security:
            result['security'] = {
                'admin_username': self.security.admin_username,
                'admin_password': '***',  # Redacted
                'allowed_management_ips': self.security.allowed_management_ips,
                'disable_unused_services': self.security.disable_unused_services,
            }

        # Add vendor-specific configs
        if self.mikrotik_config:
            result['mikrotik_config'] = self.mikrotik_config
        if self.sonicwall_config:
            result['sonicwall_config'] = self.sonicwall_config
        if self.ubiquiti_config:
            result['ubiquiti_config'] = self.ubiquiti_config

        return result
