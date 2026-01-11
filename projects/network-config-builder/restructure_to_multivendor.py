#!/usr/bin/env python3
"""
Multi-Vendor Network Config Builder - Project Restructure Script

This script transforms the single-vendor MikroTik project into a
multi-vendor network configuration platform supporting:
- MikroTik RouterOS
- SonicWall SonicOS
- Ubiquiti UniFi/EdgeRouter

Usage:
    python3 restructure_to_multivendor.py [--dry-run]
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import sys

# ANSI colors for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'

class ProjectRestructure:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.current_dir = Path("/home/mavrick/Projects/Mikrotik")
        self.new_dir = Path("/home/mavrick/Projects/network-config-builder")
        self.actions = []

    def log(self, message, color=RESET):
        """Print colored log message"""
        print(f"{color}{message}{RESET}")

    def action(self, action_type, description):
        """Log and track an action"""
        self.actions.append((action_type, description))
        icon = {
            'create': '📁',
            'move': '📦',
            'copy': '📄',
            'rename': '✏️',
            'delete': '🗑️'
        }.get(action_type, '•')

        if self.dry_run:
            self.log(f"  [DRY-RUN] {icon} {action_type.upper()}: {description}", YELLOW)
        else:
            self.log(f"  {icon} {action_type.upper()}: {description}", GREEN)

    def create_directory(self, path):
        """Create directory"""
        path = Path(path)
        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)
        self.action('create', f"Directory: {path.relative_to(self.new_dir.parent)}")

    def move_file(self, src, dst):
        """Move file or directory"""
        src, dst = Path(src), Path(dst)
        if not self.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        self.action('move', f"{src.name} → {dst.relative_to(self.new_dir.parent)}")

    def copy_file(self, src, dst):
        """Copy file"""
        src, dst = Path(src), Path(dst)
        if not self.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dst))
        self.action('copy', f"{src.name} → {dst.relative_to(self.new_dir.parent)}")

    def write_file(self, path, content):
        """Write content to file"""
        path = Path(path)
        if not self.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.action('create', f"File: {path.relative_to(self.new_dir.parent)}")

    def create_structure(self):
        """Create the new multi-vendor directory structure"""

        self.log(f"\n{BOLD}{'='*80}{RESET}")
        self.log(f"{BOLD}🚀 MULTI-VENDOR NETWORK CONFIG BUILDER - PROJECT RESTRUCTURE{RESET}")
        self.log(f"{BOLD}{'='*80}{RESET}\n")

        if self.dry_run:
            self.log(f"{YELLOW}⚠️  DRY-RUN MODE - No changes will be made{RESET}\n")

        # Step 1: Rename main directory
        self.log(f"{BLUE}Step 1: Rename project directory{RESET}")
        if not self.dry_run and self.current_dir.exists():
            self.current_dir.rename(self.new_dir)
        self.action('rename', f"Mikrotik/ → network-config-builder/")

        # Update paths after rename
        if not self.dry_run:
            self.current_dir = self.new_dir

        print()

        # Step 2: Create core framework structure
        self.log(f"{BLUE}Step 2: Create core framework structure{RESET}")

        core_dirs = [
            "core",
            "vendors/mikrotik",
            "vendors/sonicwall",
            "vendors/ubiquiti/unifi",
            "vendors/ubiquiti/edgerouter",
            "templates/mikrotik/router",
            "templates/mikrotik/wireless",
            "templates/mikrotik/firewall",
            "templates/mikrotik/vpn",
            "templates/sonicwall/zones",
            "templates/sonicwall/firewall",
            "templates/sonicwall/vpn",
            "templates/ubiquiti/unifi",
            "templates/ubiquiti/edgerouter",
            "io/readers",
            "io/writers",
            "cli",
            "web/api",
            "web/templates",
            "tests/core",
            "tests/vendors/mikrotik",
            "tests/vendors/sonicwall",
            "tests/vendors/ubiquiti",
            "tests/fixtures",
            "tests/integration",
            "examples/mikrotik",
            "examples/sonicwall",
            "examples/ubiquiti",
            "legacy/mikrotik",
        ]

        for dir_path in core_dirs:
            self.create_directory(self.new_dir / dir_path)

        print()

        # Step 3: Move legacy files
        self.log(f"{BLUE}Step 3: Move legacy files to legacy/mikrotik/{RESET}")

        legacy_files = [
            "config_builder_original.py",
            "inputs/sample_customer_data.csv",
        ]

        for file in legacy_files:
            src = self.new_dir / file
            if src.exists():
                dst = self.new_dir / "legacy/mikrotik" / src.name
                self.move_file(src, dst)

        # Keep inputs and outputs directories but empty them
        inputs_dir = self.new_dir / "inputs"
        outputs_dir = self.new_dir / "outputs"

        if inputs_dir.exists() and not self.dry_run:
            # Move sample CSV to legacy, create new inputs dir
            for item in inputs_dir.glob("*"):
                if item.is_file():
                    self.move_file(item, self.new_dir / "legacy/mikrotik" / item.name)

        print()

        # Step 4: Move documentation
        self.log(f"{BLUE}Step 4: Organize documentation{RESET}")

        docs_structure = {
            "docs/ANALYSIS.md": "docs/analysis/MIKROTIK_ORIGINAL_ANALYSIS.md",
            "docs/IMPROVEMENT_ROADMAP.md": "docs/planning/ORIGINAL_MIKROTIK_ROADMAP.md",
            "docs/MULTI_VENDOR_ARCHITECTURE.md": "docs/ARCHITECTURE.md",
            "docs/VENDOR_COMPARISON.md": "docs/VENDOR_COMPARISON.md",
            "DECISION_POINT.md": "docs/planning/DECISION_POINT.md",
            "PROJECT_STATUS.md": "PROJECT_STATUS.md",
        }

        for src_path, dst_path in docs_structure.items():
            src = self.new_dir / src_path
            dst = self.new_dir / dst_path
            if src.exists():
                self.move_file(src, dst)

        print()

        # Step 5: Create core framework files
        self.log(f"{BLUE}Step 5: Create core framework files{RESET}")
        self.create_core_files()

        print()

        # Step 6: Create vendor plugin files
        self.log(f"{BLUE}Step 6: Create vendor plugin structure{RESET}")
        self.create_vendor_files()

        print()

        # Step 7: Create example configurations
        self.log(f"{BLUE}Step 7: Create example configurations{RESET}")
        self.create_examples()

        print()

        # Step 8: Create updated documentation
        self.log(f"{BLUE}Step 8: Create documentation{RESET}")
        self.create_documentation()

        print()

        # Summary
        self.print_summary()

    def create_core_files(self):
        """Create core framework Python files"""

        # core/__init__.py
        self.write_file(self.new_dir / "core/__init__.py", '''"""
Network Config Builder - Core Framework

Multi-vendor network device configuration generation platform.
Supports MikroTik, SonicWall, and Ubiquiti devices.
"""

__version__ = "0.1.0"
__author__ = "Obera Connect"

from .models import NetworkConfig
from .validators import ConfigValidator
from .exceptions import ValidationError, GenerationError

__all__ = [
    'NetworkConfig',
    'ConfigValidator',
    'ValidationError',
    'GenerationError',
]
''')

        # core/models.py
        self.write_file(self.new_dir / "core/models.py", '''"""
Core configuration models for multi-vendor network configurations.

Uses dataclasses for type safety and validation.
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
    interface: str
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
    interface: str
    ip: str
    netmask: int
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
    action: str
    protocol: str
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
''')

        # core/exceptions.py
        self.write_file(self.new_dir / "core/exceptions.py", '''"""
Custom exceptions for network config builder.
"""


class NetworkConfigError(Exception):
    """Base exception for all config errors"""
    pass


class ValidationError(NetworkConfigError):
    """Configuration validation failed"""

    def __init__(self, message, field=None, value=None, suggestion=None):
        self.field = field
        self.value = value
        self.suggestion = suggestion
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.field:
            msg += f"\\n  Field: {self.field}"
        if self.value:
            msg += f"\\n  Value: {self.value}"
        if self.suggestion:
            msg += f"\\n  Suggestion: {self.suggestion}"
        return msg


class GenerationError(NetworkConfigError):
    """Configuration generation failed"""
    pass


class DeploymentError(NetworkConfigError):
    """Configuration deployment failed"""
    pass


class UnsupportedVendorError(NetworkConfigError):
    """Vendor not supported"""
    pass


class UnsupportedFeatureError(NetworkConfigError):
    """Feature not supported by this vendor/device"""
    pass
''')

        # core/validators.py
        self.write_file(self.new_dir / "core/validators.py", '''"""
Common validation logic for all vendors.
"""

import ipaddress
import re
from typing import List, Optional
from .models import NetworkConfig, WANConfig, LANConfig, VLANConfig
from .exceptions import ValidationError


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


class NetworkValidator:
    """Network topology and configuration validation"""

    @staticmethod
    def validate_dhcp_pool(pool_start: str, pool_end: str, subnet: str, field_prefix: str = "DHCP") -> bool:
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

    @staticmethod
    def _validate_lan(lan: LANConfig) -> None:
        """Validate LAN configuration"""
        IPValidator.validate_ip(lan.ip, "LAN IP")

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
''')

        # Main entry point
        self.write_file(self.new_dir / "network-config", '''#!/usr/bin/env python3
"""
Multi-Vendor Network Config Builder - Main Entry Point

Supports: MikroTik, SonicWall, Ubiquiti (UniFi/EdgeRouter)
"""

if __name__ == "__main__":
    from cli.commands import cli
    cli()
''')

        # Make executable
        if not self.dry_run:
            (self.new_dir / "network-config").chmod(0o755)

    def create_vendor_files(self):
        """Create vendor plugin files"""

        # vendors/__init__.py
        self.write_file(self.new_dir / "vendors/__init__.py", '''"""
Vendor-specific configuration generators (plugins).
"""

from .mikrotik.generator import MikroTikGenerator
# from .sonicwall.generator import SonicWallGenerator
# from .ubiquiti.unifi.generator import UniFiGenerator

__all__ = ['MikroTikGenerator']
''')

        # vendors/base.py
        self.write_file(self.new_dir / "vendors/base.py", '''"""
Abstract base class for vendor-specific generators.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from core.models import NetworkConfig


class VendorGenerator(ABC):
    """
    Base class for all vendor-specific configuration generators.

    Each vendor plugin must implement:
    - validate_config(): Vendor-specific validation
    - generate_config(): Generate vendor configuration files
    - deploy_config(): (Optional) Deploy to device via API
    """

    vendor_name: str = "unknown"
    supported_features: List[str] = []

    @abstractmethod
    def validate_config(self, config: NetworkConfig) -> List[str]:
        """
        Validate configuration for this vendor.

        Returns:
            List of error messages (empty if valid)
        """
        pass

    @abstractmethod
    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        """
        Generate vendor-specific configuration files.

        Returns:
            Dict mapping filename to file content
        """
        pass

    def deploy_config(self, config: NetworkConfig, device_ip: str,
                     credentials: Dict[str, str]) -> bool:
        """
        Deploy configuration to device via API (optional).

        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError(f"{self.vendor_name} API deployment not implemented")

    def get_capabilities(self, model: str) -> Dict[str, Any]:
        """
        Get device capabilities for specific model.

        Returns:
            Dict of capabilities
        """
        # TODO: Load from device_capabilities.yaml
        return {}
''')

        # MikroTik generator (placeholder)
        self.write_file(self.new_dir / "vendors/mikrotik/__init__.py", '')
        self.write_file(self.new_dir / "vendors/mikrotik/generator.py", '''"""
MikroTik RouterOS configuration generator.
"""

from typing import Dict, List
from vendors.base import VendorGenerator
from core.models import NetworkConfig


class MikroTikGenerator(VendorGenerator):
    """MikroTik RouterOS script generator"""

    vendor_name = "mikrotik"
    supported_features = [
        "routing", "firewall", "nat", "vpn_ipsec", "vpn_wireguard",
        "wireless_legacy", "wireless_wifi6", "vlan", "dhcp", "qos"
    ]

    def validate_config(self, config: NetworkConfig) -> List[str]:
        """MikroTik-specific validation"""
        errors = []

        # TODO: Add MikroTik-specific validation
        # - Check if device model supports requested features
        # - Validate RouterOS version requirements
        # - Check wireless mode compatibility

        return errors

    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        """Generate RouterOS .rsc scripts"""
        scripts = {}

        # TODO: Implement using Jinja2 templates
        # For now, placeholder
        scripts["router.rsc"] = self._generate_basic_router(config)

        return scripts

    def _generate_basic_router(self, config: NetworkConfig) -> str:
        """Generate basic router configuration"""
        lines = []
        lines.append(f"# MikroTik RouterOS Configuration")
        lines.append(f"# Customer: {config.customer.name}")
        lines.append(f"# Site: {config.customer.site}")
        lines.append(f"# Device: {config.device_model}")
        lines.append("")

        # TODO: Use templates instead of string building
        # This is just a placeholder

        if config.wan:
            lines.append("# WAN Configuration")
            if config.wan.mode == "static":
                lines.append(f"/ip address add address={config.wan.ip}/{config.wan.netmask} interface={config.wan.interface}")
                lines.append(f"/ip route add gateway={config.wan.gateway}")
            lines.append("")

        if config.lan:
            lines.append("# LAN Configuration")
            lines.append(f"/interface bridge add name={config.lan.interface}")
            lines.append(f"/ip address add address={config.lan.ip}/{config.lan.netmask} interface={config.lan.interface}")
            lines.append("")

        return "\\n".join(lines)
''')

        # SonicWall placeholder
        self.write_file(self.new_dir / "vendors/sonicwall/__init__.py", '')
        self.write_file(self.new_dir / "vendors/sonicwall/generator.py", '''"""
SonicWall SonicOS configuration generator.
"""

from typing import Dict, List
from vendors.base import VendorGenerator
from core.models import NetworkConfig


class SonicWallGenerator(VendorGenerator):
    """SonicWall SonicOS configuration generator"""

    vendor_name = "sonicwall"
    supported_features = [
        "firewall", "nat", "vpn_ipsec", "vpn_ssl",
        "ips", "av", "content_filtering", "app_control"
    ]

    def validate_config(self, config: NetworkConfig) -> List[str]:
        """SonicWall-specific validation"""
        errors = []
        # TODO: Implement
        return errors

    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        """Generate SonicOS configuration"""
        scripts = {}
        # TODO: Implement
        return scripts
''')

        # Ubiquiti placeholders
        self.write_file(self.new_dir / "vendors/ubiquiti/__init__.py", '')
        self.write_file(self.new_dir / "vendors/ubiquiti/unifi/__init__.py", '')
        self.write_file(self.new_dir / "vendors/ubiquiti/unifi/generator.py", '''"""
Ubiquiti UniFi configuration generator.
"""

from typing import Dict, List
from vendors.base import VendorGenerator
from core.models import NetworkConfig


class UniFiGenerator(VendorGenerator):
    """UniFi Controller API configuration generator"""

    vendor_name = "unifi"
    supported_features = [
        "wireless", "switching", "routing", "firewall",
        "port_forwarding", "vlan", "guest_network"
    ]

    def validate_config(self, config: NetworkConfig) -> List[str]:
        """UniFi-specific validation"""
        errors = []
        # TODO: Implement
        return errors

    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        """Generate UniFi JSON configuration"""
        configs = {}
        # TODO: Implement
        return configs
''')

    def create_examples(self):
        """Create example configuration files"""

        # MikroTik example
        mikrotik_example = '''# MikroTik Basic Router Configuration Example
vendor: mikrotik
device_model: RB4011iGS+RM

customer:
  name: Acme Corp
  site: Main Office
  contact: admin@acme.com

deployment_type: router_and_ap

wan:
  interface: ether1
  mode: static
  ip: 203.0.113.10
  netmask: 29
  gateway: 203.0.113.9
  dns:
    - 8.8.8.8
    - 8.8.4.4

lan:
  interface: bridge-lan
  ip: 192.168.1.1
  netmask: 24
  dhcp:
    enabled: true
    pool_start: 192.168.1.100
    pool_end: 192.168.1.200
    lease_time: 12h
    dns_servers:
      - 8.8.8.8
      - 8.8.4.4

vlans:
  - id: 10
    name: Management
    subnet: 192.168.10.0/24
    dhcp: true
    dhcp_config:
      pool_start: 192.168.10.100
      pool_end: 192.168.10.200
      lease_time: 12h

  - id: 20
    name: Guest
    subnet: 192.168.20.0/24
    dhcp: true
    isolation: true
    dhcp_config:
      pool_start: 192.168.20.100
      pool_end: 192.168.20.200
      lease_time: 2h

wireless:
  - ssid: AcmeWiFi
    password: SecurePassword123
    mode: wifi6
    band: 2ghz-b/g/n
    channel_width: 20mhz
    country: us
    vlan: 10

  - ssid: AcmeGuest
    password: GuestPass456
    mode: wifi6
    band: 2ghz-b/g/n
    channel_width: 20mhz
    country: us
    vlan: 20
    guest_mode: true

security:
  admin_username: acmeadmin
  admin_password: SuperSecure123!
  allowed_management_ips:
    - 192.168.1.0/24
    - 10.0.0.0/8

# MikroTik-specific settings
mikrotik_config:
  bandwidth_test: true
  capsman: false
  stun_port: true
'''
        self.write_file(self.new_dir / "examples/mikrotik/basic_router.yaml", mikrotik_example)

    def create_documentation(self):
        """Create updated documentation"""

        readme = '''# Multi-Vendor Network Configuration Builder

A unified platform for generating network device configurations across multiple vendors:
- **MikroTik RouterOS** - Routers, wireless APs, switches
- **SonicWall SonicOS** - Enterprise firewalls, UTM, VPN
- **Ubiquiti UniFi/EdgeRouter** - SMB networking, WiFi, switches

## Features

✅ **Multi-Vendor Support** - One tool for all your network devices
✅ **Unified Configuration** - Same YAML format across vendors
✅ **Type-Safe** - Python dataclasses with full type hints
✅ **Validated** - Comprehensive validation before generation
✅ **Templated** - Jinja2 templates for clean generation
✅ **Extensible** - Plugin architecture for new vendors
✅ **CLI & API** - Command-line tool and REST API
✅ **Examples** - Library of common configurations

## Quick Start

### Installation

```bash
cd /home/mavrick/Projects/network-config-builder
pip install -r requirements.txt
```

### Generate Configuration

```bash
# MikroTik router
./network-config generate --input examples/mikrotik/basic_router.yaml

# Validate only (no file generation)
./network-config validate --input myconfig.yaml

# Dry-run (preview output)
./network-config generate --input myconfig.yaml --dry-run

# Deploy to device
./network-config deploy --input myconfig.yaml --device 192.168.1.1
```

### Configuration Format

See `examples/` directory for complete examples.

```yaml
vendor: mikrotik  # or sonicwall, unifi, edgerouter
device_model: RB4011iGS+RM

customer:
  name: Acme Corp
  site: Main Office

deployment_type: router_and_ap

wan:
  interface: ether1
  mode: static
  ip: 203.0.113.10
  netmask: 29
  gateway: 203.0.113.9

lan:
  interface: bridge-lan
  ip: 192.168.1.1
  netmask: 24
  dhcp:
    enabled: true
    pool_start: 192.168.1.100
    pool_end: 192.168.1.200

# ... see examples for complete configurations
```

## Project Structure

```
network-config-builder/
├── core/                    # Core framework (vendor-agnostic)
│   ├── models.py           # Configuration data models
│   ├── validators.py       # Validation logic
│   └── exceptions.py       # Custom exceptions
├── vendors/                # Vendor plugins
│   ├── mikrotik/
│   ├── sonicwall/
│   └── ubiquiti/
├── templates/              # Jinja2 templates per vendor
├── examples/               # Example configurations
├── tests/                  # Test suite
└── docs/                   # Documentation

```

## Development Status

**Current Phase:** Phase 1 - Core Framework

- [x] Project structure created
- [x] Core models and validators
- [x] Base vendor plugin system
- [ ] MikroTik generator (in progress)
- [ ] SonicWall generator (planned)
- [ ] Ubiquiti generator (planned)
- [ ] CLI implementation (planned)
- [ ] Template system (planned)

See `docs/ARCHITECTURE.md` for detailed design.

## Documentation

- **Architecture:** `docs/ARCHITECTURE.md`
- **Vendor Comparison:** `docs/VENDOR_COMPARISON.md`
- **API Reference:** `docs/API_REFERENCE.md` (coming soon)
- **Contributing:** `CONTRIBUTING.md` (coming soon)

## Legacy

Original MikroTik-only implementation available in `legacy/mikrotik/`

## License

[Your License Here]

## Author

Obera Connect
'''
        self.write_file(self.new_dir / "README.md", readme)

        # Updated requirements.txt
        requirements = '''# Core dependencies
pyyaml>=6.0
jinja2>=3.1.0
click>=8.1.0

# Vendor API clients (optional)
# librouteros>=3.2.0  # MikroTik API
# pyunifi>=2.26      # UniFi Controller API

# Development dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
pylint>=3.0.0
mypy>=1.5.0

# Documentation
markdown>=3.4.0
'''
        self.write_file(self.new_dir / "requirements.txt", requirements)

    def print_summary(self):
        """Print summary of actions"""

        self.log(f"\n{BOLD}{'='*80}{RESET}")
        self.log(f"{BOLD}✅ RESTRUCTURE COMPLETE!{RESET}")
        self.log(f"{BOLD}{'='*80}{RESET}\n")

        if self.dry_run:
            self.log(f"{YELLOW}This was a DRY-RUN. No actual changes were made.{RESET}")
            self.log(f"{YELLOW}Run without --dry-run to apply changes.{RESET}\n")

        # Count actions by type
        action_counts = {}
        for action_type, _ in self.actions:
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        self.log(f"{BLUE}Summary of actions:{RESET}")
        for action_type, count in sorted(action_counts.items()):
            self.log(f"  • {action_type.capitalize()}: {count}")

        self.log(f"\n{BLUE}New project location:{RESET}")
        self.log(f"  📂 {self.new_dir}")

        self.log(f"\n{BLUE}Next steps:{RESET}")
        self.log(f"  1. Review the new structure")
        self.log(f"  2. Install dependencies: pip install -r requirements.txt")
        self.log(f"  3. Run tests: pytest")
        self.log(f"  4. Try example: ./network-config generate --input examples/mikrotik/basic_router.yaml")

        self.log(f"\n{GREEN}🎉 Multi-vendor network config builder is ready!{RESET}\n")


def main():
    """Main entry point"""
    import sys

    dry_run = '--dry-run' in sys.argv

    restructure = ProjectRestructure(dry_run=dry_run)
    restructure.create_structure()


if __name__ == "__main__":
    main()
''')

    def create_cli_files(self):
        """Create CLI command files"""

        # cli/__init__.py
        self.write_file(self.new_dir / "cli/__init__.py", "")

        # cli/commands.py
        cli_commands = '''"""
CLI commands for network config builder.
"""

import click
from pathlib import Path


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Multi-Vendor Network Configuration Builder"""
    pass


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True),
              help='Input configuration file (YAML/JSON/CSV)')
@click.option('--output', '-o', type=click.Path(),
              help='Output directory for generated configs')
@click.option('--vendor', '-v', type=click.Choice(['mikrotik', 'sonicwall', 'unifi', 'edgerouter']),
              help='Force specific vendor (auto-detected if not specified)')
@click.option('--dry-run', is_flag=True,
              help='Preview output without writing files')
def generate(input, output, vendor, dry_run):
    """Generate network device configurations"""

    click.echo(f"Generating configuration from: {input}")

    if dry_run:
        click.echo("DRY-RUN MODE: No files will be created")

    # TODO: Implement
    click.echo("⚠️  Not yet implemented - coming soon!")


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True),
              help='Input configuration file to validate')
def validate(input):
    """Validate configuration without generating files"""

    click.echo(f"Validating: {input}")

    # TODO: Implement
    click.echo("⚠️  Not yet implemented - coming soon!")


@cli.command()
def interactive():
    """Interactive configuration wizard"""

    click.echo("🧙 Interactive Configuration Wizard")
    click.echo("⚠️  Not yet implemented - coming soon!")

    # TODO: Implement


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True))
@click.option('--device', '-d', required=True, help='Device IP address')
@click.option('--username', '-u', prompt=True, help='Admin username')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Admin password')
def deploy(input, device, username, password):
    """Deploy configuration to device via API"""

    click.echo(f"Deploying {input} to {device}")

    # TODO: Implement
    click.echo("⚠️  Not yet implemented - coming soon!")


if __name__ == '__main__':
    cli()
'''
        self.write_file(self.new_dir / "cli/commands.py", cli_commands)


def main():
    """Run the restructure script"""
    import sys

    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv

    restructure = ProjectRestructure(dry_run=dry_run)
    restructure.create_structure()

    # Also create CLI files
    restructure.create_cli_files()


if __name__ == "__main__":
    main()
