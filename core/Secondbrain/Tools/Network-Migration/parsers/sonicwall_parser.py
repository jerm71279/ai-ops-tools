#!/usr/bin/env python3
"""
SonicWall Config Parser
Parses SonicWall CLI configuration files and converts to universal network schema
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Network:
    """Network/VLAN configuration"""
    name: str
    vlan_id: int
    subnet: str = ""
    gateway: str = ""
    dhcp_enabled: bool = True
    dhcp_start: str = ""
    dhcp_stop: str = ""
    dns_servers: List[str] = field(default_factory=list)
    purpose: str = "corporate"
    network_isolation: bool = False
    interface: str = ""
    zone: str = ""


@dataclass
class FirewallRule:
    """Firewall access rule"""
    name: str
    action: str
    from_zone: str = ""
    to_zone: str = ""
    source: str = "any"
    destination: str = "any"
    service: str = "any"
    enabled: bool = True
    comment: str = ""


@dataclass
class NATRule:
    """NAT policy"""
    name: str
    from_zone: str = ""
    to_zone: str = ""
    source: str = "any"
    destination: str = "any"
    nat_type: str = "dynamic-ip"
    enabled: bool = True


class SonicWallParser:
    """Parse SonicWall CLI configuration"""

    def __init__(self):
        self.config_lines: List[str] = []

        # Parsed data
        self.hostname = ""
        self.interfaces: Dict[str, dict] = {}  # interface name -> config
        self.dhcp_servers: Dict[str, dict] = {}  # dhcp name -> config
        self.firewall_rules: List[FirewallRule] = []
        self.nat_rules: List[NATRule] = []
        self.zones: Dict[str, str] = {}  # zone name -> description

        # WAN info
        self.wan_interface = ""
        self.wan_ip = ""
        self.wan_gateway = ""
        self.dns_servers: List[str] = []

    def parse_file(self, filepath: str) -> dict:
        """Parse a SonicWall CLI config file and return universal schema"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            self.config_lines = f.readlines()

        self._parse_config()
        return self._build_schema()

    def _parse_config(self):
        """Parse the CLI configuration"""
        i = 0
        while i < len(self.config_lines):
            line = self.config_lines[i].strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                i += 1
                continue

            # Hostname
            if line.startswith('hostname '):
                self.hostname = line.replace('hostname ', '').strip('"')
                i += 1
                continue

            # DNS servers
            if line.startswith('dns nameserver'):
                match = re.search(r'dns nameserver \d+ (\S+)', line)
                if match:
                    self.dns_servers.append(match.group(1))
                i += 1
                continue

            # Default route
            if line.startswith('route 0.0.0.0/0'):
                match = re.search(r'route 0\.0\.0\.0/0 (\S+)', line)
                if match:
                    self.wan_gateway = match.group(1)
                i += 1
                continue

            # Interface block
            if line.startswith('interface '):
                interface_name = line.replace('interface ', '').strip()
                interface_config, i = self._parse_block(i + 1)
                self._process_interface(interface_name, interface_config)
                continue

            # DHCP server block
            if line.startswith('dhcp-server '):
                dhcp_name = line.replace('dhcp-server ', '').strip()
                dhcp_config, i = self._parse_block(i + 1)
                self._process_dhcp(dhcp_name, dhcp_config)
                continue

            # NAT policy block
            if line.startswith('nat-policy '):
                nat_name = line.replace('nat-policy ', '').strip()
                nat_config, i = self._parse_block(i + 1)
                self._process_nat(nat_name, nat_config)
                continue

            # Access rule block
            if line.startswith('access-rule '):
                rule_name = line.replace('access-rule ', '').strip()
                rule_config, i = self._parse_block(i + 1)
                self._process_access_rule(rule_name, rule_config)
                continue

            i += 1

    def _parse_block(self, start_index: int) -> tuple:
        """Parse a configuration block until 'exit'"""
        block_lines = []
        i = start_index

        while i < len(self.config_lines):
            line = self.config_lines[i].strip()

            if line == 'exit':
                i += 1
                break

            if line and not line.startswith('#'):
                block_lines.append(line)

            i += 1

        return block_lines, i

    def _process_interface(self, name: str, config_lines: List[str]):
        """Process an interface configuration block"""
        interface = {
            'name': name,
            'ip': '',
            'cidr': '',
            'zone': '',
            'vlan_id': 0,
            'enabled': True
        }

        # Check for VLAN subinterface (X1:10 format)
        if ':' in name:
            base, vlan = name.split(':')
            interface['vlan_id'] = int(vlan)
            interface['parent'] = base

        for line in config_lines:
            # IP address
            if line.startswith('ip '):
                ip_match = re.search(r'ip (\S+)', line)
                if ip_match:
                    ip_cidr = ip_match.group(1)
                    if '/' in ip_cidr:
                        interface['ip'], interface['cidr'] = ip_cidr.split('/')
                    else:
                        interface['ip'] = ip_cidr

            # VLAN ID
            elif line.startswith('vlan '):
                vlan_match = re.search(r'vlan (\d+)', line)
                if vlan_match:
                    interface['vlan_id'] = int(vlan_match.group(1))

            # Zone
            elif line.startswith('zone '):
                interface['zone'] = line.replace('zone ', '').strip()

            # Shutdown state
            elif line == 'no shutdown':
                interface['enabled'] = True
            elif line == 'shutdown':
                interface['enabled'] = False

        self.interfaces[name] = interface

        # Detect WAN interface
        if interface['zone'].upper() == 'WAN':
            self.wan_interface = name
            self.wan_ip = f"{interface['ip']}/{interface['cidr']}" if interface['cidr'] else interface['ip']

    def _process_dhcp(self, name: str, config_lines: List[str]):
        """Process a DHCP server configuration block"""
        dhcp = {
            'name': name,
            'pool_start': '',
            'pool_end': '',
            'lease_time': '',
            'dns_servers': [],
            'enabled': False
        }

        for line in config_lines:
            # Pool range
            if line.startswith('pool '):
                pool_match = re.search(r'pool (\S+) (\S+)', line)
                if pool_match:
                    dhcp['pool_start'] = pool_match.group(1)
                    dhcp['pool_end'] = pool_match.group(2)

            # Lease time
            elif line.startswith('lease-time '):
                dhcp['lease_time'] = line.replace('lease-time ', '').strip()

            # DNS servers
            elif line.startswith('dns-server '):
                dns_str = line.replace('dns-server ', '').strip()
                dhcp['dns_servers'] = dns_str.split()

            # Enable state
            elif line == 'enable':
                dhcp['enabled'] = True
            elif line == 'disable':
                dhcp['enabled'] = False

        self.dhcp_servers[name] = dhcp

    def _process_nat(self, name: str, config_lines: List[str]):
        """Process a NAT policy block"""
        nat = NATRule(name=name)

        for line in config_lines:
            # From/to zones
            if line.startswith('from '):
                match = re.search(r'from (\S+) to (\S+)', line)
                if match:
                    nat.from_zone = match.group(1)
                    nat.to_zone = match.group(2)

            # Source
            elif line.startswith('source '):
                nat.source = line.replace('source ', '').strip()

            # Destination
            elif line.startswith('destination '):
                nat.destination = line.replace('destination ', '').strip()

            # NAT type
            elif line.startswith('nat '):
                nat.nat_type = line.replace('nat ', '').strip()

            # Enable state
            elif line == 'enable':
                nat.enabled = True
            elif line == 'disable':
                nat.enabled = False

        self.nat_rules.append(nat)

    def _process_access_rule(self, name: str, config_lines: List[str]):
        """Process a firewall access rule block"""
        rule = FirewallRule(name=name, action='allow')

        for line in config_lines:
            # From/to zones
            if line.startswith('from '):
                match = re.search(r'from (\S+) to (\S+)', line)
                if match:
                    rule.from_zone = match.group(1)
                    rule.to_zone = match.group(2)

            # Source
            elif line.startswith('source '):
                rule.source = line.replace('source ', '').strip()

            # Destination
            elif line.startswith('destination '):
                rule.destination = line.replace('destination ', '').strip()

            # Service
            elif line.startswith('service '):
                rule.service = line.replace('service ', '').strip()

            # Action
            elif line.startswith('action '):
                rule.action = line.replace('action ', '').strip()

            # Enable state
            elif line == 'enable':
                rule.enabled = True
            elif line == 'disable':
                rule.enabled = False

        self.firewall_rules.append(rule)

    def _build_schema(self) -> dict:
        """Build universal network schema from parsed data"""
        networks = []

        # Build network objects from interfaces
        for iface_name, iface in self.interfaces.items():
            # Skip WAN interface
            if iface['zone'].upper() == 'WAN':
                continue

            # Skip interfaces without IP
            if not iface['ip']:
                continue

            vlan_id = iface['vlan_id']
            zone = iface['zone']

            # Determine network name
            if zone:
                name = zone
            elif vlan_id > 0:
                name = f"VLAN{vlan_id}"
            else:
                name = iface_name

            # Build subnet
            subnet = f"{iface['ip'].rsplit('.', 1)[0]}.0/{iface['cidr']}" if iface['cidr'] else ""

            # Find matching DHCP config
            dhcp_enabled = False
            dhcp_start = ""
            dhcp_stop = ""
            dns_servers = []

            # Try to match DHCP by zone name or VLAN
            for dhcp_name, dhcp in self.dhcp_servers.items():
                if zone.upper() in dhcp_name.upper() or (vlan_id > 0 and str(vlan_id) in dhcp_name):
                    dhcp_enabled = dhcp['enabled']
                    dhcp_start = dhcp['pool_start']
                    dhcp_stop = dhcp['pool_end']
                    dns_servers = dhcp['dns_servers']
                    break
                elif dhcp_name.upper() == 'LAN' and iface_name == 'X1':
                    dhcp_enabled = dhcp['enabled']
                    dhcp_start = dhcp['pool_start']
                    dhcp_stop = dhcp['pool_end']
                    dns_servers = dhcp['dns_servers']

            # Use global DNS if no DHCP-specific DNS
            if not dns_servers:
                dns_servers = self.dns_servers

            # Determine purpose based on zone name
            purpose = "corporate"
            zone_lower = zone.lower()
            if 'guest' in zone_lower:
                purpose = "guest"
            elif 'iot' in zone_lower or 'camera' in zone_lower:
                purpose = "iot"
            elif 'mgmt' in zone_lower or 'management' in zone_lower:
                purpose = "management"
            elif 'voip' in zone_lower or 'voice' in zone_lower:
                purpose = "voip"

            # Check for isolation (deny rules to LAN)
            network_isolation = False
            for rule in self.firewall_rules:
                if rule.from_zone.upper() == zone.upper() and rule.to_zone.upper() == 'LAN' and rule.action == 'deny':
                    network_isolation = True
                    break

            network = Network(
                name=name,
                vlan_id=vlan_id,
                subnet=subnet,
                gateway=iface['ip'],
                dhcp_enabled=dhcp_enabled,
                dhcp_start=dhcp_start,
                dhcp_stop=dhcp_stop,
                dns_servers=dns_servers,
                purpose=purpose,
                network_isolation=network_isolation,
                interface=iface_name,
                zone=zone
            )

            networks.append(asdict(network))

        # Sort by VLAN ID
        networks.sort(key=lambda x: x['vlan_id'])

        # Build firewall rules
        firewall_rules = []
        for rule in self.firewall_rules:
            firewall_rules.append({
                'name': rule.name,
                'action': rule.action,
                'chain': 'forward',  # SonicWall uses zone-based, map to forward
                'from_zone': rule.from_zone,
                'to_zone': rule.to_zone,
                'source': rule.source,
                'destination': rule.destination,
                'service': rule.service,
                'enabled': rule.enabled
            })

        # Build NAT rules
        nat_rules = []
        for nat in self.nat_rules:
            nat_rules.append({
                'action': nat.nat_type,
                'chain': 'srcnat',
                'from_zone': nat.from_zone,
                'to_zone': nat.to_zone,
                'source': nat.source,
                'destination': nat.destination,
                'enabled': nat.enabled
            })

        schema = {
            'metadata': {
                'customer_name': '',  # To be filled by user
                'source_platform': 'sonicwall',
                'source_device': '',  # Would need device info
                'source_firmware': '',
                'device_name': self.hostname,
                'serial_number': '',
                'wan_interface': self.wan_interface,
                'wan_ip': self.wan_ip,
                'wan_gateway': self.wan_gateway,
                'parsed_date': datetime.now().strftime('%Y-%m-%d'),
                'total_networks': len(networks)
            },
            'networks': networks,
            'firewall_rules': firewall_rules,
            'nat_rules': nat_rules,
            'port_forwards': [],
            'static_dhcp_leases': []
        }

        return schema


def interactive_parse():
    """Interactive mode for parsing SonicWall configs"""
    print("=" * 60)
    print("Network Migration Toolkit - SonicWall Parser")
    print("=" * 60)
    print()
    print("Supported formats:")
    print("  - CLI configuration (.cli, .txt)")
    print()

    # Get config file path
    while True:
        config_path = input("Enter path to SonicWall config file: ").strip()
        if not config_path:
            print("  Config file path is required.")
            continue

        config_path = Path(config_path).expanduser()
        if not config_path.exists():
            print(f"  File not found: {config_path}")
            continue
        break

    # Get customer name
    customer_name = input("Enter customer name: ").strip()
    if not customer_name:
        customer_name = config_path.stem

    # Get output filename
    default_output = customer_name.lower().replace(' ', '_') + '.json'
    output_name = input(f"Enter output filename [{default_output}]: ").strip()
    if not output_name:
        output_name = default_output

    if not output_name.endswith('.json'):
        output_name += '.json'

    print()
    print(f"Parsing: {config_path}")
    print()

    # Parse config
    parser = SonicWallParser()
    schema = parser.parse_file(str(config_path))

    # Set customer name
    schema['metadata']['customer_name'] = customer_name

    # Display summary
    print("Parsing complete!")
    print("-" * 40)
    print(f"  Hostname:   {schema['metadata']['device_name']}")
    print(f"  WAN IP:     {schema['metadata']['wan_ip']}")
    print(f"  Gateway:    {schema['metadata']['wan_gateway']}")
    print("-" * 40)
    print(f"  Networks:   {len(schema['networks'])}")
    print(f"  Firewall:   {len(schema['firewall_rules'])} rules")
    print(f"  NAT:        {len(schema['nat_rules'])} rules")
    print("-" * 40)
    print()

    # Save output
    output_path = Path('/home/mavrick/Projects/Secondbrain/Tools/Network-Migration/configs') / output_name
    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)

    print(f"Output saved to: {output_path}")
    print()

    return schema, output_path


if __name__ == '__main__':
    interactive_parse()
