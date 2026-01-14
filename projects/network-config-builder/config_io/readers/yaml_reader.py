"""
YAML Configuration Reader

Reads network configurations from YAML files and converts them to NetworkConfig objects.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.models import (
    NetworkConfig, VendorType, DeploymentType,
    CustomerInfo, WANConfig, LANConfig, DHCPConfig,
    VLANConfig, WirelessConfig, SecurityConfig,
    FirewallRule, PortForward, VPNConfig, SiteToSiteVPNConfig
)
from core.exceptions import ValidationError


class YAMLConfigReader:
    """Read and parse YAML network configurations"""

    @staticmethod
    def read(file_path: str) -> NetworkConfig:
        """
        Read configuration from YAML file.

        Args:
            file_path: Path to YAML configuration file

        Returns:
            NetworkConfig object

        Raises:
            ValidationError: If YAML is invalid or required fields missing
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            raise ValidationError(f"Configuration file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValidationError(f"Invalid YAML: {e}")

        if not data:
            raise ValidationError("Empty configuration file")

        return YAMLConfigReader._parse_config(data)

    @staticmethod
    def _parse_config(data: Dict[str, Any]) -> NetworkConfig:
        """Parse YAML data into NetworkConfig"""

        # Parse vendor
        vendor_str = data.get('vendor', '').lower()
        try:
            vendor = VendorType(vendor_str)
        except ValueError:
            raise ValidationError(
                f"Invalid vendor: {vendor_str}",
                field='vendor',
                suggestion=f"Use one of: {', '.join([v.value for v in VendorType])}"
            )

        # Parse deployment type
        deployment_str = data.get('deployment_type', 'router_only').lower()
        try:
            deployment_type = DeploymentType(deployment_str)
        except ValueError:
            raise ValidationError(
                f"Invalid deployment_type: {deployment_str}",
                field='deployment_type',
                suggestion=f"Use one of: {', '.join([d.value for d in DeploymentType])}"
            )

        # Parse customer info
        customer_data = data.get('customer', {})
        if not customer_data.get('name'):
            raise ValidationError("customer.name is required")
        if not customer_data.get('site'):
            raise ValidationError("customer.site is required")

        customer = CustomerInfo(
            name=customer_data['name'],
            site=customer_data['site'],
            contact=customer_data.get('contact'),
            notes=customer_data.get('notes')
        )

        # Parse device model
        device_model = data.get('device_model')
        if not device_model:
            raise ValidationError("device_model is required")

        # Parse WAN
        wan = None
        if 'wan' in data:
            wan = YAMLConfigReader._parse_wan(data['wan'])

        # Parse LAN
        lan = None
        if 'lan' in data:
            lan = YAMLConfigReader._parse_lan(data['lan'])

        # Parse VLANs
        vlans = []
        if 'vlans' in data:
            vlans = [YAMLConfigReader._parse_vlan(v) for v in data['vlans']]

        # Parse Wireless
        wireless = []
        if 'wireless' in data:
            wireless_data = data['wireless']
            if isinstance(wireless_data, list):
                wireless = [YAMLConfigReader._parse_wireless(w) for w in wireless_data]
            elif isinstance(wireless_data, dict):
                wireless = [YAMLConfigReader._parse_wireless(wireless_data)]

        # Parse Security
        security = None
        if 'security' in data:
            security = YAMLConfigReader._parse_security(data['security'])

        # Parse VPN configurations
        vpn = []
        if 'vpn' in data:
            vpn = [YAMLConfigReader._parse_vpn(v) for v in data['vpn']]

        # Parse vendor-specific configs
        mikrotik_config = data.get('mikrotik_config', data.get('mikrotik', {}))
        sonicwall_config = data.get('sonicwall_config', data.get('sonicwall', {}))
        ubiquiti_config = data.get('ubiquiti_config', data.get('ubiquiti', {}))

        # Create NetworkConfig
        config = NetworkConfig(
            vendor=vendor,
            device_model=device_model,
            customer=customer,
            deployment_type=deployment_type,
            wan=wan,
            lan=lan,
            vlans=vlans,
            wireless=wireless,
            security=security,
            vpn=vpn,
            mikrotik_config=mikrotik_config,
            sonicwall_config=sonicwall_config,
            ubiquiti_config=ubiquiti_config
        )

        return config

    @staticmethod
    def _parse_wan(data: Dict[str, Any]) -> WANConfig:
        """Parse WAN configuration"""
        return WANConfig(
            interface=data.get('interface', 'ether1'),
            mode=data.get('mode', 'static'),
            ip=data.get('ip'),
            netmask=data.get('netmask'),
            gateway=data.get('gateway'),
            dns=data.get('dns', [])
        )

    @staticmethod
    def _parse_lan(data: Dict[str, Any]) -> LANConfig:
        """Parse LAN configuration"""
        dhcp = None
        if 'dhcp' in data:
            dhcp_data = data['dhcp']
            dhcp = DHCPConfig(
                enabled=dhcp_data.get('enabled', True),
                pool_start=dhcp_data.get('pool_start', ''),
                pool_end=dhcp_data.get('pool_end', ''),
                lease_time=dhcp_data.get('lease_time', '12h'),
                dns_servers=dhcp_data.get('dns_servers', [])
            )

        return LANConfig(
            interface=data.get('interface', 'bridge-lan'),
            ip=data.get('ip', ''),
            netmask=data.get('netmask', 24),
            dhcp=dhcp
        )

    @staticmethod
    def _parse_vlan(data: Dict[str, Any]) -> VLANConfig:
        """Parse VLAN configuration"""
        dhcp_config = None
        if data.get('dhcp') and 'dhcp_config' in data:
            dc = data['dhcp_config']
            dhcp_config = DHCPConfig(
                enabled=True,
                pool_start=dc.get('pool_start', ''),
                pool_end=dc.get('pool_end', ''),
                lease_time=dc.get('lease_time', '12h'),
                dns_servers=dc.get('dns_servers', [])
            )

        return VLANConfig(
            id=data['id'],
            name=data['name'],
            subnet=data['subnet'],
            dhcp=data.get('dhcp', False),
            isolation=data.get('isolation', False),
            dhcp_config=dhcp_config
        )

    @staticmethod
    def _parse_wireless(data: Dict[str, Any]) -> WirelessConfig:
        """Parse wireless configuration"""
        return WirelessConfig(
            ssid=data['ssid'],
            password=data['password'],
            mode=data.get('mode', 'legacy'),
            band=data.get('band', '2ghz-b/g/n'),
            channel_width=data.get('channel_width', '20mhz'),
            country=data.get('country', 'us'),
            vlan=data.get('vlan'),
            guest_mode=data.get('guest_mode', False)
        )

    @staticmethod
    def _parse_security(data: Dict[str, Any]) -> SecurityConfig:
        """Parse security configuration"""
        return SecurityConfig(
            admin_username=data['admin_username'],
            admin_password=data['admin_password'],
            allowed_management_ips=data.get('allowed_management_ips', []),
            disable_unused_services=data.get('disable_unused_services', True)
        )

    @staticmethod
    def _parse_vpn(data: Dict[str, Any]) -> VPNConfig:
        """Parse VPN configuration"""
        site_to_site = None
        if data.get('type') == 'site-to-site' and 'site_to_site' in data:
            s2s = data['site_to_site']
            site_to_site = SiteToSiteVPNConfig(
                name=s2s['name'],
                peer_wan_ip=s2s['peer_wan_ip'],
                local_network=s2s['local_network'],
                remote_network=s2s['remote_network'],
                preshared_key=s2s['preshared_key'],
                ike_version=s2s.get('ike_version', '2'),
                ike_encryption=s2s.get('ike_encryption', 'aes256'),
                ike_authentication=s2s.get('ike_authentication', 'sha256'),
                ike_dh_group=s2s.get('ike_dh_group', '14'),
                ike_lifetime=s2s.get('ike_lifetime', 28800),
                ipsec_encryption=s2s.get('ipsec_encryption', 'aes256'),
                ipsec_authentication=s2s.get('ipsec_authentication', 'sha256'),
                ipsec_pfs_group=s2s.get('ipsec_pfs_group', '14'),
                ipsec_lifetime=s2s.get('ipsec_lifetime', 3600),
                local_wan_ip=s2s.get('local_wan_ip'),
                dead_peer_detection=s2s.get('dead_peer_detection', True),
                nat_traversal=s2s.get('nat_traversal', True),
                enabled=s2s.get('enabled', True),
                # NAT VPN settings for overlapping subnets
                nat_vpn=s2s.get('nat_vpn', False),
                local_translated=s2s.get('local_translated'),
                remote_translated=s2s.get('remote_translated')
            )

        return VPNConfig(
            type=data.get('type', 'ipsec'),
            name=data.get('name', ''),
            peer_ip=data.get('peer_ip'),
            local_subnet=data.get('local_subnet'),
            remote_subnet=data.get('remote_subnet'),
            preshared_key=data.get('preshared_key'),
            site_to_site=site_to_site,
            config=data.get('config', {})
        )
