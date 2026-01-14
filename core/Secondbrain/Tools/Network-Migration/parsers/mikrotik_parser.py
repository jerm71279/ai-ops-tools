#!/usr/bin/env python3
"""
MikroTik RouterOS Config Parser
Parses /export output and converts to universal network schema
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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


@dataclass
class FirewallRule:
    """Firewall rule"""
    name: str
    action: str
    chain: str
    protocol: str = ""
    dst_ports: List[int] = field(default_factory=list)
    src_ports: List[int] = field(default_factory=list)
    in_interface: str = ""
    out_interface: str = ""
    comment: str = ""


@dataclass
class NATRule:
    """NAT rule"""
    action: str
    chain: str
    out_interface: str = ""
    in_interface: str = ""
    dst_address: str = ""
    to_address: str = ""
    to_port: str = ""
    protocol: str = ""
    comment: str = ""


@dataclass
class StaticLease:
    """Static DHCP lease"""
    name: str
    mac_address: str
    ip_address: str
    network: str = ""


class MikroTikParser:
    """Parse MikroTik RouterOS /export configuration"""

    def __init__(self):
        self.config_lines: List[str] = []
        self.current_section = ""

        # Parsed data
        self.vlans: Dict[str, dict] = {}  # name -> {vlan_id, interface}
        self.ip_pools: Dict[str, dict] = {}  # name -> {ranges}
        self.ip_addresses: Dict[str, dict] = {}  # interface -> {address, network}
        self.dhcp_servers: Dict[str, dict] = {}  # interface -> {pool, name}
        self.dhcp_networks: Dict[str, dict] = {}  # network -> {dns, gateway}
        self.firewall_rules: List[FirewallRule] = []
        self.nat_rules: List[NATRule] = []
        self.static_leases: List[StaticLease] = []

        # Metadata
        self.device_name = ""
        self.device_model = ""
        self.firmware_version = ""
        self.serial_number = ""
        self.wan_interface = ""
        self.wan_ip = ""
        self.wan_gateway = ""

    def parse_file(self, filepath: str) -> dict:
        """Parse a MikroTik config file and return universal schema"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            self.config_lines = f.readlines()

        self._extract_metadata()
        self._parse_sections()
        return self._build_schema()

    def _extract_metadata(self):
        """Extract device metadata from config header"""
        for line in self.config_lines[:30]:  # Check first 30 lines
            line = line.strip()

            # RouterOS version
            if 'RouterOS' in line and 'by' in line:
                match = re.search(r'RouterOS\s+([\d.]+)', line)
                if match:
                    self.firmware_version = f"RouterOS {match.group(1)}"

            # Model
            if line.startswith('# model'):
                match = re.search(r'model\s*=\s*(.+)', line)
                if match:
                    self.device_model = match.group(1).strip()

            # Serial
            if line.startswith('# serial'):
                match = re.search(r'serial number\s*=\s*(.+)', line)
                if match:
                    self.serial_number = match.group(1).strip()

    def _parse_sections(self):
        """Parse all configuration sections"""
        current_section = ""
        section_lines = []

        for line in self.config_lines:
            line = line.rstrip()

            # Skip empty lines and comments (except metadata)
            if not line or (line.startswith('#') and 'model' not in line and 'serial' not in line):
                continue

            # New section starts with /
            if line.startswith('/'):
                # Process previous section
                if current_section and section_lines:
                    self._process_section(current_section, section_lines)

                current_section = line
                section_lines = []
            else:
                section_lines.append(line)

        # Process last section
        if current_section and section_lines:
            self._process_section(current_section, section_lines)

    def _process_section(self, section: str, lines: List[str]):
        """Route section to appropriate parser"""
        if section == '/interface vlan':
            self._parse_vlans(lines)
        elif section == '/ip pool':
            self._parse_ip_pools(lines)
        elif section == '/ip address':
            self._parse_ip_addresses(lines)
        elif section == '/ip dhcp-server' and 'network' not in section:
            self._parse_dhcp_servers(lines)
        elif section == '/ip dhcp-server network':
            self._parse_dhcp_networks(lines)
        elif section == '/ip firewall filter':
            self._parse_firewall_rules(lines)
        elif section == '/ip firewall nat':
            self._parse_nat_rules(lines)
        elif section == '/ip route':
            self._parse_routes(lines)
        elif section == '/system identity':
            self._parse_identity(lines)
        elif section == '/ip dhcp-server lease':
            self._parse_static_leases(lines)

    def _parse_key_value(self, line: str) -> Dict[str, str]:
        """Parse 'add key=value key2=value2' format"""
        result = {}
        # Handle multi-line continuations (lines ending with \)
        line = line.replace('\\\n', ' ').strip()

        if line.startswith('add '):
            line = line[4:]
        elif line.startswith('set '):
            line = line[4:]

        # Parse key=value pairs
        # Handle quoted values and values with special chars
        pattern = r'(\w+(?:-\w+)*)=(?:"([^"]+)"|(\S+))'
        for match in re.finditer(pattern, line):
            key = match.group(1)
            value = match.group(2) if match.group(2) else match.group(3)
            result[key] = value

        return result

    def _parse_vlans(self, lines: List[str]):
        """Parse /interface vlan section"""
        for line in lines:
            if not line.startswith('add '):
                continue

            params = self._parse_key_value(line)
            name = params.get('name', '')
            vlan_id = params.get('vlan-id', '0')
            interface = params.get('interface', '')

            if name:
                self.vlans[name] = {
                    'vlan_id': int(vlan_id),
                    'interface': interface
                }

    def _parse_ip_pools(self, lines: List[str]):
        """Parse /ip pool section"""
        for line in lines:
            if not line.startswith('add '):
                continue

            params = self._parse_key_value(line)
            name = params.get('name', '')
            ranges = params.get('ranges', '')

            if name and ranges:
                self.ip_pools[name] = {'ranges': ranges}

    def _parse_ip_addresses(self, lines: List[str]):
        """Parse /ip address section"""
        for line in lines:
            if not line.startswith('add '):
                continue

            params = self._parse_key_value(line)
            address = params.get('address', '')
            interface = params.get('interface', '')
            network = params.get('network', '')

            if interface and address:
                self.ip_addresses[interface] = {
                    'address': address,
                    'network': network
                }

                # Detect WAN interface (public IP)
                if address and not address.startswith(('10.', '192.168.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.')):
                    self.wan_interface = interface
                    self.wan_ip = address

    def _parse_dhcp_servers(self, lines: List[str]):
        """Parse /ip dhcp-server section"""
        for line in lines:
            if not line.startswith('add '):
                continue

            params = self._parse_key_value(line)
            interface = params.get('interface', '')
            pool = params.get('address-pool', '')
            name = params.get('name', '')

            if interface:
                self.dhcp_servers[interface] = {
                    'pool': pool,
                    'name': name
                }

    def _parse_dhcp_networks(self, lines: List[str]):
        """Parse /ip dhcp-server network section"""
        for line in lines:
            if not line.startswith('add '):
                continue

            params = self._parse_key_value(line)
            address = params.get('address', '')
            gateway = params.get('gateway', '')
            dns = params.get('dns-server', '')

            if address:
                self.dhcp_networks[address] = {
                    'gateway': gateway,
                    'dns': dns.split(',') if dns else []
                }

    def _parse_firewall_rules(self, lines: List[str]):
        """Parse /ip firewall filter section"""
        for line in lines:
            if not line.startswith('add '):
                continue

            params = self._parse_key_value(line)

            rule = FirewallRule(
                name=params.get('comment', f"Rule-{len(self.firewall_rules)+1}"),
                action=params.get('action', ''),
                chain=params.get('chain', ''),
                protocol=params.get('protocol', ''),
                in_interface=params.get('in-interface', ''),
                out_interface=params.get('out-interface', ''),
                comment=params.get('comment', '')
            )

            # Parse ports
            dst_port = params.get('dst-port', '')
            if dst_port:
                rule.dst_ports = [int(p) for p in dst_port.split(',') if p.isdigit()]

            src_port = params.get('src-port', '')
            if src_port:
                rule.src_ports = [int(p) for p in src_port.split(',') if p.isdigit()]

            self.firewall_rules.append(rule)

    def _parse_nat_rules(self, lines: List[str]):
        """Parse /ip firewall nat section"""
        for line in lines:
            if not line.startswith('add '):
                continue

            params = self._parse_key_value(line)

            rule = NATRule(
                action=params.get('action', ''),
                chain=params.get('chain', ''),
                out_interface=params.get('out-interface', ''),
                in_interface=params.get('in-interface', ''),
                dst_address=params.get('dst-address', ''),
                to_address=params.get('to-addresses', ''),
                to_port=params.get('to-ports', ''),
                protocol=params.get('protocol', ''),
                comment=params.get('comment', '')
            )

            self.nat_rules.append(rule)

    def _parse_routes(self, lines: List[str]):
        """Parse /ip route section for default gateway"""
        for line in lines:
            if not line.startswith('add '):
                continue

            params = self._parse_key_value(line)
            dst = params.get('dst-address', '')
            gateway = params.get('gateway', '')

            if dst == '0.0.0.0/0' and gateway:
                self.wan_gateway = gateway

    def _parse_identity(self, lines: List[str]):
        """Parse /system identity section"""
        for line in lines:
            if line.startswith('set '):
                params = self._parse_key_value(line)
                self.device_name = params.get('name', '')

    def _parse_static_leases(self, lines: List[str]):
        """Parse /ip dhcp-server lease section for static leases"""
        for line in lines:
            if not line.startswith('add '):
                continue

            params = self._parse_key_value(line)
            mac = params.get('mac-address', '')
            ip = params.get('address', '')

            if mac and ip:
                lease = StaticLease(
                    name=params.get('comment', f"Device-{mac[-5:]}"),
                    mac_address=mac,
                    ip_address=ip,
                    network=""  # Will be determined later
                )
                self.static_leases.append(lease)

    def _build_schema(self) -> dict:
        """Build universal network schema from parsed data"""
        networks = []

        # Build complete network objects by combining VLAN + IP + DHCP data
        for vlan_name, vlan_data in self.vlans.items():
            vlan_id = vlan_data['vlan_id']

            # Get IP address for this VLAN
            ip_data = self.ip_addresses.get(vlan_name, {})
            address = ip_data.get('address', '')

            # Parse gateway and subnet from address (e.g., "10.10.2.1/24")
            gateway = ""
            subnet = ""
            if address:
                parts = address.split('/')
                gateway = parts[0]
                if len(parts) > 1:
                    # Convert CIDR to network address
                    subnet = ip_data.get('network', '') + '/' + parts[1]

            # Get DHCP pool info
            pool_name = vlan_name  # Usually matches VLAN name
            pool_data = self.ip_pools.get(pool_name, {})
            dhcp_range = pool_data.get('ranges', '')
            dhcp_start = ""
            dhcp_stop = ""
            if dhcp_range and '-' in dhcp_range:
                dhcp_start, dhcp_stop = dhcp_range.split('-')

            # Get DNS from dhcp-server network
            dns_servers = []
            for net_addr, net_data in self.dhcp_networks.items():
                # Match by network prefix
                if subnet and net_addr.split('/')[0].rsplit('.', 1)[0] == gateway.rsplit('.', 1)[0]:
                    dns_servers = net_data.get('dns', [])
                    break

            # Determine purpose based on name
            purpose = "corporate"
            name_lower = vlan_name.lower()
            if 'guest' in name_lower:
                purpose = "guest"
            elif 'camera' in name_lower or 'iot' in name_lower:
                purpose = "iot"
            elif 'mgmt' in name_lower or 'management' in name_lower:
                purpose = "management"

            network = Network(
                name=vlan_name,
                vlan_id=vlan_id,
                subnet=subnet,
                gateway=gateway,
                dhcp_enabled=bool(dhcp_start),
                dhcp_start=dhcp_start,
                dhcp_stop=dhcp_stop,
                dns_servers=dns_servers,
                purpose=purpose,
                network_isolation=(purpose in ['guest', 'iot'])
            )

            networks.append(asdict(network))

        # Also check for bridge/non-VLAN interfaces with IPs
        for interface, ip_data in self.ip_addresses.items():
            if interface not in self.vlans and interface != self.wan_interface:
                # This might be a bridge or management interface
                address = ip_data.get('address', '')
                if address and not any(n['gateway'] == address.split('/')[0] for n in networks):
                    gateway = address.split('/')[0]
                    subnet = ip_data.get('network', '') + '/' + address.split('/')[1] if '/' in address else ""

                    # Get DHCP pool
                    pool_name = interface
                    pool_data = self.ip_pools.get(pool_name, {})
                    dhcp_range = pool_data.get('ranges', '')
                    dhcp_start = ""
                    dhcp_stop = ""
                    if dhcp_range and '-' in dhcp_range:
                        dhcp_start, dhcp_stop = dhcp_range.split('-')

                    network = Network(
                        name=interface,
                        vlan_id=0,  # No VLAN ID for bridge/native
                        subnet=subnet,
                        gateway=gateway,
                        dhcp_enabled=bool(dhcp_start),
                        dhcp_start=dhcp_start,
                        dhcp_stop=dhcp_stop,
                        dns_servers=[],
                        purpose="corporate",
                        network_isolation=False
                    )
                    networks.append(asdict(network))

        # Sort networks by VLAN ID
        networks.sort(key=lambda x: x['vlan_id'])

        # Build firewall rules
        firewall_rules = []
        for rule in self.firewall_rules:
            firewall_rules.append(asdict(rule))

        # Build NAT rules
        nat_rules = []
        for rule in self.nat_rules:
            nat_rules.append(asdict(rule))

        # Build static leases
        static_leases = []
        for lease in self.static_leases:
            static_leases.append(asdict(lease))

        # Detect port forwards from NAT rules
        port_forwards = []
        for rule in self.nat_rules:
            if rule.action == 'dst-nat' and rule.to_address:
                port_forwards.append({
                    'name': rule.comment or f"Forward-{rule.to_port}",
                    'dst_port': rule.to_port,
                    'to_address': rule.to_address,
                    'to_port': rule.to_port,
                    'protocol': rule.protocol
                })

        schema = {
            'metadata': {
                'customer_name': '',  # To be filled by user
                'source_platform': 'mikrotik',
                'source_device': self.device_model,
                'source_firmware': self.firmware_version,
                'device_name': self.device_name,
                'serial_number': self.serial_number,
                'wan_interface': self.wan_interface,
                'wan_ip': self.wan_ip,
                'wan_gateway': self.wan_gateway,
                'parsed_date': datetime.now().strftime('%Y-%m-%d'),
                'total_networks': len(networks)
            },
            'networks': networks,
            'firewall_rules': firewall_rules,
            'nat_rules': nat_rules,
            'port_forwards': port_forwards,
            'static_dhcp_leases': static_leases
        }

        return schema


def interactive_parse():
    """Interactive mode for parsing MikroTik configs"""
    print("=" * 60)
    print("Network Migration Toolkit - MikroTik Parser")
    print("=" * 60)
    print()

    # Get config file path
    while True:
        config_path = input("Enter path to MikroTik config file: ").strip()
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
        customer_name = config_path.stem  # Use filename as default

    # Get output filename
    default_output = customer_name.lower().replace(' ', '_') + '.json'
    output_name = input(f"Enter output filename [{default_output}]: ").strip()
    if not output_name:
        output_name = default_output

    # Ensure .json extension
    if not output_name.endswith('.json'):
        output_name += '.json'

    print()
    print(f"Parsing: {config_path}")
    print()

    # Parse config
    parser = MikroTikParser()
    schema = parser.parse_file(str(config_path))

    # Set customer name
    schema['metadata']['customer_name'] = customer_name

    # Display summary
    print("Parsing complete!")
    print("-" * 40)
    print(f"  Device:     {schema['metadata']['source_device']}")
    print(f"  Firmware:   {schema['metadata']['source_firmware']}")
    print(f"  Device Name: {schema['metadata']['device_name']}")
    print(f"  WAN IP:     {schema['metadata']['wan_ip']}")
    print(f"  Gateway:    {schema['metadata']['wan_gateway']}")
    print("-" * 40)
    print(f"  Networks:   {len(schema['networks'])}")
    print(f"  Firewall:   {len(schema['firewall_rules'])} rules")
    print(f"  NAT:        {len(schema['nat_rules'])} rules")
    print(f"  Port Fwd:   {len(schema['port_forwards'])} rules")
    print(f"  Static DHCP: {len(schema['static_dhcp_leases'])} leases")
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
