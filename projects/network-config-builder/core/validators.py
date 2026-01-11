"""
Common validation logic for all vendors.

Integrates with validation_framework.py from automation-script-builder.
"""

import ipaddress
import re
from typing import List, Optional
from .models import NetworkConfig, WANConfig, LANConfig, VLANConfig
from .exceptions import ValidationError

# Import validation framework from automation-script-builder
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'io' / 'readers'))

try:
    from validation_framework import Validator, collect_errors
except ImportError:
    # Fallback if validation_framework not available
    class Validator:
        """Fallback validator"""
        def __init__(self, value, field_name):
            self.value = value
            self.field_name = field_name
            self.errors = []

        def required(self):
            if not self.value:
                self.errors.append(f"{self.field_name} is required")
            return self

        def validate(self):
            return self.errors

    def collect_errors(*validators):
        errors = []
        for v in validators:
            if hasattr(v, 'validate'):
                errors.extend(v.validate())
        return errors


class IPValidator:
    """IP address and network validation"""

    @staticmethod
    def validate_ip(ip_str: str, field: str = "IP") -> ipaddress.IPv4Address:
        """Validate IPv4 address"""
        try:
            return ipaddress.IPv4Address(ip_str)
        except Exception as e:
            raise ValidationError(
                f"Invalid IPv4 address: {ip_str}",
                field=field,
                value=ip_str,
                suggestion="Use format: 192.168.1.1"
            )

    @staticmethod
    def validate_network(network_str: str, field: str = "Network") -> ipaddress.IPv4Network:
        """Validate IPv4 network (CIDR)"""
        try:
            return ipaddress.IPv4Network(network_str, strict=False)
        except Exception as e:
            raise ValidationError(
                f"Invalid IPv4 network: {network_str}",
                field=field,
                value=network_str,
                suggestion="Use CIDR format: 192.168.1.0/24"
            )

    @staticmethod
    def validate_ip_in_network(ip: str, network: str, field: str = "IP") -> bool:
        """Validate IP is within network"""
        ip_addr = IPValidator.validate_ip(ip, field)
        network_obj = IPValidator.validate_network(network, field)

        if ip_addr not in network_obj:
            raise ValidationError(
                f"IP {ip} is not in network {network}",
                field=field,
                value=ip,
                suggestion=f"Use an IP within {network}"
            )
        return True

    @staticmethod
    def to_prefix(mask: str) -> int:
        """Convert netmask to prefix length. Accepts '24', '/24', or dotted mask."""
        m = str(mask).strip()
        if m.startswith('/'):
            m = m[1:]
        if m.isdigit():
            n = int(m)
            if 0 <= n <= 32:
                return n
            raise ValueError("Prefix out of range")
        return ipaddress.IPv4Network(f"0.0.0.0/{m}").prefixlen


class NetworkValidator:
    """Network topology and configuration validation"""

    @staticmethod
    def validate_dhcp_pool(pool_start: str, pool_end: str, subnet: str,
                          field_prefix: str = "DHCP") -> bool:
        """Validate DHCP pool is within subnet and start <= end"""

        # Validate IPs
        start_ip = IPValidator.validate_ip(pool_start, f"{field_prefix} Pool Start")
        end_ip = IPValidator.validate_ip(pool_end, f"{field_prefix} Pool End")
        network = IPValidator.validate_network(subnet, f"{field_prefix} Subnet")

        # Check start <= end
        if int(start_ip) > int(end_ip):
            raise ValidationError(
                "DHCP pool start must be <= pool end",
                field=f"{field_prefix} Pool",
                value=f"{pool_start} - {pool_end}",
                suggestion=f"Swap the values or use {pool_end} - {pool_start}"
            )

        # Check both in subnet
        if start_ip not in network or end_ip not in network:
            raise ValidationError(
                f"DHCP pool {pool_start}-{pool_end} is not within subnet {subnet}",
                field=f"{field_prefix} Pool",
                suggestion=f"Use IPs within {network}"
            )

        return True

    @staticmethod
    def validate_vlan_ids(vlans: List[VLANConfig]) -> bool:
        """Validate VLAN IDs are unique and in valid range"""
        seen_ids = set()
        seen_names = set()

        for vlan in vlans:
            # Check ID range (1-4094)
            if not 1 <= vlan.id <= 4094:
                raise ValidationError(
                    f"VLAN ID must be between 1 and 4094",
                    field=f"VLAN {vlan.name}",
                    value=vlan.id,
                    suggestion="Use a valid VLAN ID (1-4094)"
                )

            # Check for duplicate IDs
            if vlan.id in seen_ids:
                raise ValidationError(
                    f"Duplicate VLAN ID: {vlan.id}",
                    field=f"VLAN {vlan.name}",
                    value=vlan.id,
                    suggestion=f"Each VLAN must have a unique ID"
                )
            seen_ids.add(vlan.id)

            # Check for duplicate names
            if vlan.name in seen_names:
                raise ValidationError(
                    f"Duplicate VLAN name: {vlan.name}",
                    field=f"VLAN {vlan.id}",
                    value=vlan.name,
                    suggestion="Each VLAN must have a unique name"
                )
            seen_names.add(vlan.name)

        return True


class ConfigValidator:
    """Main configuration validator orchestrating all validation"""

    @staticmethod
    def validate(config: NetworkConfig) -> List[str]:
        """
        Validate complete configuration.
        Returns list of error messages (empty if valid).
        """
        errors = []

        try:
            # Validate customer info
            if not config.customer.name:
                errors.append("Customer name is required")
            if not config.customer.site:
                errors.append("Customer site is required")

            # Validate WAN
            if config.wan:
                ConfigValidator._validate_wan(config.wan)

            # Validate LAN
            if config.lan:
                ConfigValidator._validate_lan(config.lan)

            # Validate VLANs
            if config.vlans:
                NetworkValidator.validate_vlan_ids(config.vlans)
                for vlan in config.vlans:
                    ConfigValidator._validate_vlan(vlan)

            # Validate wireless
            if config.wireless:
                for wireless in config.wireless:
                    ConfigValidator._validate_wireless(wireless)

            # Validate security
            if config.security:
                ConfigValidator._validate_security(config.security)

        except ValidationError as e:
            errors.append(str(e))

        return errors

    @staticmethod
    def _validate_wan(wan: WANConfig) -> None:
        """Validate WAN configuration"""
        if wan.mode == "static":
            if not wan.ip or not wan.netmask or not wan.gateway:
                raise ValidationError(
                    "Static WAN requires IP, netmask, and gateway",
                    field="WAN"
                )
            IPValidator.validate_ip(wan.ip, "WAN IP")
            IPValidator.validate_ip(wan.gateway, "WAN Gateway")

            # Validate netmask range
            if wan.netmask and not (0 <= wan.netmask <= 32):
                raise ValidationError(
                    f"Invalid netmask: {wan.netmask}",
                    field="WAN Netmask",
                    value=wan.netmask,
                    suggestion="Use prefix length 0-32 (e.g., 24 for /24)"
                )

    @staticmethod
    def _validate_lan(lan: LANConfig) -> None:
        """Validate LAN configuration"""
        IPValidator.validate_ip(lan.ip, "LAN IP")

        # Validate netmask
        if not (0 <= lan.netmask <= 32):
            raise ValidationError(
                f"Invalid netmask: {lan.netmask}",
                field="LAN Netmask",
                value=lan.netmask,
                suggestion="Use prefix length 0-32 (e.g., 24 for /24)"
            )

        if lan.dhcp and lan.dhcp.enabled:
            subnet = f"{lan.ip}/{lan.netmask}"
            NetworkValidator.validate_dhcp_pool(
                lan.dhcp.pool_start,
                lan.dhcp.pool_end,
                subnet,
                "LAN DHCP"
            )

    @staticmethod
    def _validate_vlan(vlan: VLANConfig) -> None:
        """Validate VLAN configuration"""
        network = IPValidator.validate_network(vlan.subnet, f"VLAN {vlan.name}")

        if vlan.dhcp and vlan.dhcp_config:
            NetworkValidator.validate_dhcp_pool(
                vlan.dhcp_config.pool_start,
                vlan.dhcp_config.pool_end,
                vlan.subnet,
                f"VLAN {vlan.name} DHCP"
            )

    @staticmethod
    def _validate_wireless(wireless) -> None:
        """Validate wireless configuration"""
        # SSID length check
        if len(wireless.ssid) > 32:
            raise ValidationError(
                "SSID must be 32 characters or less",
                field="Wireless SSID",
                value=wireless.ssid,
                suggestion="Shorten the SSID"
            )

        # Password length check
        if len(wireless.password) < 8:
            raise ValidationError(
                "Wireless password must be at least 8 characters",
                field="Wireless Password",
                suggestion="Use a password with 8+ characters"
            )

    @staticmethod
    def _validate_security(security) -> None:
        """Validate security configuration"""
        if len(security.admin_password) < 8:
            raise ValidationError(
                "Admin password must be at least 8 characters",
                field="security.admin_password",
                suggestion="Use a strong password with 12+ characters"
            )

        # Validate allowed IPs
        for ip_or_cidr in security.allowed_management_ips:
            if '/' in ip_or_cidr:
                IPValidator.validate_network(ip_or_cidr, "Allowed Management IP")
            else:
                IPValidator.validate_ip(ip_or_cidr, "Allowed Management IP")
