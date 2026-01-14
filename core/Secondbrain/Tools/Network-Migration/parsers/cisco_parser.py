#!/usr/bin/env python3
"""
Cisco IOS Parser - Parses Cisco switch/router configurations

Supports Cisco IOS configurations from:
- Catalyst 3750X, 3650 series switches
- IOS versions 12.2, 15.x, 16.x

Extracts:
- VLANs (from interface definitions)
- Port configurations (access/trunk mode, VLANs)
- Voice VLANs
- Management interfaces
- Spanning-tree settings

Target: UniFi switches (USW-8, USW-16-PoE, USW-24, USW-48)
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class CiscoParser:
    """Parse Cisco IOS configuration files"""

    def __init__(self):
        self.hostname = ""
        self.ios_version = ""
        self.device_model = ""
        self.domain_name = ""
        self.default_gateway = ""
        self.spanning_tree_mode = ""

        self.vlans: Dict[int, Dict] = {}
        self.interfaces: List[Dict] = []
        self.management_interface: Optional[Dict] = None
        self.voice_policies: Dict[int, int] = {}  # policy_id -> voice_vlan

    def parse_file(self, filepath: str) -> dict:
        """Parse Cisco IOS config file and return universal schema"""
        with open(filepath, 'r') as f:
            content = f.read()

        return self.parse(content)

    def parse(self, content: str) -> dict:
        """Parse Cisco IOS configuration content"""
        lines = content.split('\n')

        # Reset state
        self.hostname = ""
        self.ios_version = ""
        self.device_model = ""
        self.domain_name = ""
        self.default_gateway = ""
        self.spanning_tree_mode = ""
        self.vlans = {}
        self.interfaces = []
        self.management_interface = None
        self.voice_policies = {}

        # Parse sections
        self._parse_global(lines)
        self._parse_vlans(lines)
        self._parse_network_policies(lines)
        self._parse_interfaces(lines)

        return self._build_schema()

    def _parse_global(self, lines: List[str]):
        """Parse global configuration settings"""
        for line in lines:
            line = line.strip()

            # IOS version
            if line.startswith('version '):
                self.ios_version = line.replace('version ', '').strip()

            # Hostname
            elif line.startswith('hostname '):
                self.hostname = line.replace('hostname ', '').strip()

            # Device model from provision line
            elif 'provision ws-c' in line.lower() or 'provision c' in line.lower():
                match = re.search(r'provision\s+([\w-]+)', line, re.IGNORECASE)
                if match:
                    self.device_model = match.group(1).upper()

            # Domain name
            elif line.startswith('ip domain-name ') or line.startswith('ip domain name '):
                self.domain_name = line.split()[-1]

            # Default gateway
            elif line.startswith('ip default-gateway '):
                self.default_gateway = line.replace('ip default-gateway ', '').strip()

            # Spanning-tree mode
            elif line.startswith('spanning-tree mode '):
                self.spanning_tree_mode = line.replace('spanning-tree mode ', '').strip()

    def _parse_vlans(self, lines: List[str]):
        """Parse VLAN definitions"""
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Explicit VLAN definition block
            if line.startswith('vlan ') and not 'internal' in line:
                match = re.match(r'vlan\s+(\d+)', line)
                if match:
                    vlan_id = int(match.group(1))
                    vlan_name = f"VLAN{vlan_id}"

                    # Look for name on next line
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith('name '):
                            vlan_name = next_line.replace('name ', '').strip()

                    self.vlans[vlan_id] = {
                        'vlan_id': vlan_id,
                        'name': vlan_name,
                        'purpose': self._guess_vlan_purpose(vlan_name, vlan_id)
                    }
            i += 1

    def _parse_network_policies(self, lines: List[str]):
        """Parse network-policy profiles (voice VLAN assignments)"""
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line.startswith('network-policy profile '):
                match = re.match(r'network-policy profile\s+(\d+)', line)
                if match:
                    policy_id = int(match.group(1))

                    # Look for voice vlan in following lines
                    j = i + 1
                    while j < len(lines) and lines[j].startswith(' '):
                        policy_line = lines[j].strip()
                        if policy_line.startswith('voice vlan '):
                            vlan_match = re.match(r'voice vlan\s+(\d+)', policy_line)
                            if vlan_match:
                                self.voice_policies[policy_id] = int(vlan_match.group(1))
                        j += 1
            i += 1

    def _parse_interfaces(self, lines: List[str]):
        """Parse interface configurations"""
        i = 0
        while i < len(lines):
            line = lines[i]

            # Interface block start
            if line.startswith('interface '):
                interface_name = line.replace('interface ', '').strip()
                interface_config = {
                    'name': interface_name,
                    'description': '',
                    'mode': 'access',  # default
                    'access_vlan': 1,  # default VLAN
                    'voice_vlan': None,
                    'trunk_encapsulation': None,
                    'trunk_allowed_vlans': 'all',
                    'portfast': False,
                    'shutdown': False,
                    'ip_address': None,
                    'subnet_mask': None
                }

                # Parse interface sub-commands
                j = i + 1
                while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('!')):
                    if lines[j].startswith('!'):
                        break

                    subline = lines[j].strip()

                    # Description
                    if subline.startswith('description '):
                        interface_config['description'] = subline.replace('description ', '')

                    # Shutdown
                    elif subline == 'shutdown':
                        interface_config['shutdown'] = True

                    # Switchport mode
                    elif subline == 'switchport mode access':
                        interface_config['mode'] = 'access'
                    elif subline == 'switchport mode trunk':
                        interface_config['mode'] = 'trunk'

                    # Access VLAN
                    elif subline.startswith('switchport access vlan '):
                        match = re.match(r'switchport access vlan\s+(\d+)', subline)
                        if match:
                            interface_config['access_vlan'] = int(match.group(1))
                            # Auto-add VLAN to list
                            vlan_id = int(match.group(1))
                            if vlan_id not in self.vlans:
                                self.vlans[vlan_id] = {
                                    'vlan_id': vlan_id,
                                    'name': f"VLAN{vlan_id}",
                                    'purpose': 'data'
                                }

                    # Voice VLAN
                    elif subline.startswith('switchport voice vlan '):
                        match = re.match(r'switchport voice vlan\s+(\d+)', subline)
                        if match:
                            interface_config['voice_vlan'] = int(match.group(1))
                            # Auto-add voice VLAN to list
                            vlan_id = int(match.group(1))
                            if vlan_id not in self.vlans:
                                self.vlans[vlan_id] = {
                                    'vlan_id': vlan_id,
                                    'name': f"Voice-VLAN{vlan_id}",
                                    'purpose': 'voice'
                                }
                            else:
                                self.vlans[vlan_id]['purpose'] = 'voice'

                    # Trunk encapsulation
                    elif 'trunk encapsulation dot1q' in subline:
                        interface_config['trunk_encapsulation'] = 'dot1q'

                    # Trunk allowed VLANs
                    elif subline.startswith('switchport trunk allowed vlan '):
                        interface_config['trunk_allowed_vlans'] = subline.replace(
                            'switchport trunk allowed vlan ', '')

                    # Portfast
                    elif 'spanning-tree portfast' in subline:
                        interface_config['portfast'] = True

                    # IP address (for SVI/management interfaces)
                    elif subline.startswith('ip address '):
                        parts = subline.split()
                        if len(parts) >= 4:
                            interface_config['ip_address'] = parts[2]
                            interface_config['subnet_mask'] = parts[3]

                    j += 1

                # Categorize the interface
                if interface_name.startswith('Vlan'):
                    # SVI - check if management
                    if interface_config['ip_address']:
                        vlan_match = re.match(r'Vlan(\d+)', interface_name)
                        if vlan_match:
                            vlan_id = int(vlan_match.group(1))
                            interface_config['vlan_id'] = vlan_id
                            self.management_interface = interface_config
                            # Add management VLAN
                            if vlan_id not in self.vlans:
                                self.vlans[vlan_id] = {
                                    'vlan_id': vlan_id,
                                    'name': 'Management',
                                    'purpose': 'management'
                                }
                            else:
                                self.vlans[vlan_id]['purpose'] = 'management'

                elif self._is_physical_port(interface_name):
                    # Physical port - add to interfaces list
                    self.interfaces.append(interface_config)

            i += 1

    def _is_physical_port(self, name: str) -> bool:
        """Check if interface name is a physical port"""
        physical_prefixes = [
            'GigabitEthernet', 'Gi', 'FastEthernet', 'Fa',
            'TenGigabitEthernet', 'Te', 'Ethernet', 'Eth'
        ]
        return any(name.startswith(prefix) for prefix in physical_prefixes)

    def _guess_vlan_purpose(self, name: str, vlan_id: int) -> str:
        """Guess VLAN purpose from name or ID"""
        name_lower = name.lower()

        if 'voice' in name_lower or 'phone' in name_lower:
            return 'voice'
        elif 'camera' in name_lower or 'security' in name_lower or 'ipc' in name_lower:
            return 'security'
        elif 'guest' in name_lower or 'visitor' in name_lower:
            return 'guest'
        elif 'mgmt' in name_lower or 'management' in name_lower:
            return 'management'
        elif 'server' in name_lower:
            return 'server'
        elif 'iot' in name_lower:
            return 'iot'
        elif 'native' in name_lower:
            return 'native'
        elif vlan_id == 1:
            return 'default'
        else:
            return 'data'

    def _normalize_port_name(self, name: str) -> str:
        """Normalize Cisco port name to simple format"""
        # GigabitEthernet1/0/1 -> Gi1/0/1
        name = re.sub(r'^GigabitEthernet', 'Gi', name)
        name = re.sub(r'^FastEthernet', 'Fa', name)
        name = re.sub(r'^TenGigabitEthernet', 'Te', name)
        return name

    def _get_port_number(self, name: str) -> Optional[int]:
        """Extract port number from interface name"""
        # Match patterns like 1/0/1, 0/1, etc.
        match = re.search(r'/(\d+)$', name)
        if match:
            return int(match.group(1))
        return None

    def _build_schema(self) -> dict:
        """Build universal network schema"""
        # Build port profiles (groups of ports with same config)
        port_profiles = self._build_port_profiles()

        # Build networks from VLANs
        networks = []
        for vlan_id, vlan_info in sorted(self.vlans.items()):
            network = {
                'name': vlan_info['name'],
                'vlan_id': vlan_id,
                'purpose': vlan_info['purpose'],
                'dhcp_enabled': False,  # Switch doesn't know DHCP config
                'network_isolation': vlan_info['purpose'] in ['guest', 'iot']
            }

            # Add management info if this is the management VLAN
            if self.management_interface and self.management_interface.get('vlan_id') == vlan_id:
                network['gateway'] = self.management_interface['ip_address']
                network['subnet'] = self._mask_to_cidr(
                    self.management_interface['ip_address'],
                    self.management_interface['subnet_mask']
                )

            networks.append(network)

        schema = {
            'metadata': {
                'customer_name': '',  # User will provide
                'source_platform': 'cisco',
                'source_device': self.device_model or 'Cisco Catalyst',
                'source_firmware': f'IOS {self.ios_version}',
                'hostname': self.hostname,
                'domain_name': self.domain_name,
                'default_gateway': self.default_gateway,
                'spanning_tree_mode': self.spanning_tree_mode,
                'parsed_date': datetime.now().strftime('%Y-%m-%d'),
                'total_vlans': len(self.vlans),
                'total_ports': len(self.interfaces)
            },
            'networks': networks,
            'switch_ports': self.interfaces,
            'port_profiles': port_profiles,
            'management': {
                'interface': self.management_interface['name'] if self.management_interface else None,
                'ip_address': self.management_interface['ip_address'] if self.management_interface else None,
                'subnet_mask': self.management_interface['subnet_mask'] if self.management_interface else None,
                'default_gateway': self.default_gateway
            }
        }

        return schema

    def _build_port_profiles(self) -> List[Dict]:
        """Group ports by configuration into profiles"""
        profiles = {}

        for iface in self.interfaces:
            if iface['shutdown']:
                continue

            # Create profile key based on config
            if iface['mode'] == 'trunk':
                key = f"trunk_{iface['trunk_allowed_vlans']}"
                profile_name = "All VLANs (Trunk)"
            elif iface['voice_vlan']:
                key = f"access_{iface['access_vlan']}_voice_{iface['voice_vlan']}"
                profile_name = f"VLAN {iface['access_vlan']} + Voice {iface['voice_vlan']}"
            else:
                key = f"access_{iface['access_vlan']}"
                profile_name = f"VLAN {iface['access_vlan']}"

            if key not in profiles:
                profiles[key] = {
                    'name': profile_name,
                    'mode': iface['mode'],
                    'native_vlan': iface['access_vlan'] if iface['mode'] == 'access' else 1,
                    'voice_vlan': iface['voice_vlan'],
                    'allowed_vlans': iface['trunk_allowed_vlans'] if iface['mode'] == 'trunk' else None,
                    'portfast': iface['portfast'],
                    'ports': []
                }

            profiles[key]['ports'].append({
                'name': iface['name'],
                'short_name': self._normalize_port_name(iface['name']),
                'port_number': self._get_port_number(iface['name']),
                'description': iface['description']
            })

        return list(profiles.values())

    def _mask_to_cidr(self, ip: str, mask: str) -> str:
        """Convert IP and subnet mask to CIDR notation"""
        try:
            # Count bits in mask
            mask_parts = [int(x) for x in mask.split('.')]
            bits = sum(bin(x).count('1') for x in mask_parts)

            # Calculate network address
            ip_parts = [int(x) for x in ip.split('.')]
            network_parts = [ip_parts[i] & mask_parts[i] for i in range(4)]
            network = '.'.join(str(x) for x in network_parts)

            return f"{network}/{bits}"
        except:
            return f"{ip}/24"


def interactive_parse():
    """Interactive Cisco config parsing"""
    print("\nNetwork Migration Toolkit - Cisco IOS Parser")
    print("=" * 50)
    print("Supported: Catalyst 3750X, 3650, 2960, 9200 series")
    print("           IOS 12.2, 15.x, 16.x, 17.x")
    print()

    # Get input file
    while True:
        filepath = input("Enter path to Cisco config file: ").strip()
        if not filepath:
            print("No file specified, exiting.")
            return

        if Path(filepath).exists():
            break
        print(f"File not found: {filepath}")

    # Get customer name
    customer = input("Enter customer name: ").strip() or "Unknown Customer"

    # Parse
    print("\nParsing Cisco configuration...")
    parser = CiscoParser()

    try:
        schema = parser.parse_file(filepath)
        schema['metadata']['customer_name'] = customer
    except Exception as e:
        print(f"Error parsing config: {e}")
        return

    # Summary
    print(f"\nParsed successfully!")
    print(f"  Device: {schema['metadata']['source_device']}")
    print(f"  Hostname: {schema['metadata']['hostname']}")
    print(f"  IOS Version: {schema['metadata']['source_firmware']}")
    print(f"  VLANs: {schema['metadata']['total_vlans']}")
    print(f"  Ports: {schema['metadata']['total_ports']}")

    # Show VLANs
    print("\nVLANs Found:")
    for net in sorted(schema['networks'], key=lambda x: x['vlan_id']):
        purpose = f" ({net['purpose']})" if net['purpose'] != 'data' else ""
        print(f"  VLAN {net['vlan_id']:4d}: {net['name']}{purpose}")

    # Show port profiles
    print("\nPort Profiles:")
    for profile in schema['port_profiles']:
        ports = [p['short_name'] for p in profile['ports'][:3]]
        more = f" +{len(profile['ports'])-3} more" if len(profile['ports']) > 3 else ""
        print(f"  {profile['name']}: {', '.join(ports)}{more}")

    # Output file
    default_output = Path(filepath).stem + '.json'
    output_path = input(f"\nOutput filename [{default_output}]: ").strip() or default_output

    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)

    print(f"\nSaved to: {output_path}")
    print("\nNext steps:")
    print("  1. Review the JSON and add any missing VLAN details")
    print("  2. Run: python migrate.py build unifi-switch --config " + output_path)
    print("  3. Apply port profiles to UniFi switches")


if __name__ == '__main__':
    interactive_parse()
