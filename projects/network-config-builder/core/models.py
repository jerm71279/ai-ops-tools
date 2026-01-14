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
class SiteToSiteVPNConfig:
    """Site-to-Site IPSec VPN configuration"""
    name: str
    peer_wan_ip: str  # Remote site's WAN IP
    local_network: str  # Local LAN subnet (e.g., 10.54.9.0/24)
    remote_network: str  # Remote LAN subnet (e.g., 10.54.8.0/24)
    preshared_key: str

    # IKE Phase 1 settings
    ike_version: str = "2"  # 1 or 2
    ike_encryption: str = "aes256"
    ike_authentication: str = "sha256"
    ike_dh_group: str = "14"  # DH Group 14 = 2048-bit MODP
    ike_lifetime: int = 28800  # 8 hours in seconds

    # IPSec Phase 2 settings
    ipsec_encryption: str = "aes256"
    ipsec_authentication: str = "sha256"
    ipsec_pfs_group: str = "14"  # Perfect Forward Secrecy DH Group
    ipsec_lifetime: int = 3600  # 1 hour in seconds

    # Optional settings
    local_wan_ip: Optional[str] = None  # If not set, uses WAN interface IP
    dead_peer_detection: bool = True
    nat_traversal: bool = True
    enabled: bool = True

    # NAT VPN settings (for overlapping subnets)
    nat_vpn: bool = False  # Enable NAT VPN for overlapping networks
    local_translated: Optional[str] = None  # How local appears to remote (e.g., 10.254.1.0/24)
    remote_translated: Optional[str] = None  # How remote appears to local (e.g., 10.254.2.0/24)


@dataclass
class VPNConfig:
    """VPN configuration"""
    type: str  # ipsec, wireguard, openvpn, l2tp, site-to-site
    name: str
    peer_ip: Optional[str] = None
    local_subnet: Optional[str] = None
    remote_subnet: Optional[str] = None
    preshared_key: Optional[str] = None
    site_to_site: Optional[SiteToSiteVPNConfig] = None
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
