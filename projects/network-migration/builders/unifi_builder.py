#!/usr/bin/env python3
"""
UniFi Config Builder
Generates UniFi-compatible configuration files from universal network schema

Outputs:
- unifi_networks.json - Network/VLAN configurations
- unifi_firewall.json - Firewall rules
- unifi_port_forwards.json - Port forwarding rules
- unifi_static_dhcp.json - Static DHCP reservations
- MIGRATION_GUIDE.md - Step-by-step migration guide
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class UniFiNetwork:
    """UniFi network configuration"""
    name: str
    purpose: str  # corporate, guest, wan, vlan-only
    vlan_id: Optional[int]
    subnet: str
    gateway: str
    dhcp_enabled: bool
    dhcp_start: str
    dhcp_stop: str
    dhcp_dns: List[str]
    igmp_snooping: bool = False
    network_isolation: bool = False


class UniFiConfigBuilder:
    """Build UniFi configuration from universal schema"""

    # Purpose mapping from source to UniFi
    PURPOSE_MAP = {
        'corporate': 'corporate',
        'management': 'corporate',
        'guest': 'guest',
        'iot': 'corporate',  # UniFi doesn't have IoT purpose, use isolation instead
        'voip': 'corporate',
    }

    def __init__(self, config: dict):
        self.config = config
        self.metadata = config.get('metadata', {})
        self.networks = config.get('networks', [])
        self.firewall_rules = config.get('firewall_rules', [])
        self.nat_rules = config.get('nat_rules', [])
        self.port_forwards = config.get('port_forwards', [])
        self.static_leases = config.get('static_dhcp_leases', [])

    def build_all(self, output_dir: str) -> Dict[str, str]:
        """Generate all UniFi configuration files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        files = {}

        # Generate network config
        networks_json = self._build_networks()
        networks_file = output_path / 'unifi_networks.json'
        with open(networks_file, 'w') as f:
            json.dump(networks_json, f, indent=2)
        files['unifi_networks.json'] = str(networks_file)

        # Generate firewall config
        firewall_json = self._build_firewall()
        firewall_file = output_path / 'unifi_firewall.json'
        with open(firewall_file, 'w') as f:
            json.dump(firewall_json, f, indent=2)
        files['unifi_firewall.json'] = str(firewall_file)

        # Generate port forwards
        if self.port_forwards:
            forwards_json = self._build_port_forwards()
            forwards_file = output_path / 'unifi_port_forwards.json'
            with open(forwards_file, 'w') as f:
                json.dump(forwards_json, f, indent=2)
            files['unifi_port_forwards.json'] = str(forwards_file)

        # Generate static DHCP
        if self.static_leases:
            dhcp_json = self._build_static_dhcp()
            dhcp_file = output_path / 'unifi_static_dhcp.json'
            with open(dhcp_file, 'w') as f:
                json.dump(dhcp_json, f, indent=2)
            files['unifi_static_dhcp.json'] = str(dhcp_file)

        # Generate migration guide
        guide = self._build_migration_guide()
        guide_file = output_path / 'MIGRATION_GUIDE.md'
        with open(guide_file, 'w') as f:
            f.write(guide)
        files['MIGRATION_GUIDE.md'] = str(guide_file)

        return files

    def _build_networks(self) -> dict:
        """Build UniFi networks JSON"""
        unifi_networks = []

        for net in self.networks:
            name = net.get('name', '')
            vlan_id = net.get('vlan_id', 0)
            purpose = net.get('purpose', 'corporate')
            subnet = net.get('subnet', '')
            gateway = net.get('gateway', '')

            # Skip if no gateway (likely WAN or invalid)
            if not gateway:
                continue

            # Build gateway/subnet in UniFi format
            if subnet:
                prefix = subnet.split('/')[-1] if '/' in subnet else '24'
                ip_subnet = f"{gateway}/{prefix}"
            else:
                ip_subnet = f"{gateway}/24"

            # Map purpose
            unifi_purpose = self.PURPOSE_MAP.get(purpose, 'corporate')

            # Determine if isolation needed
            network_isolation = net.get('network_isolation', False)
            if purpose in ['iot', 'guest']:
                network_isolation = True

            unifi_net = {
                'name': name,
                'purpose': unifi_purpose,
                'ip_subnet': ip_subnet,
                'networkgroup': 'LAN',
                'dhcpd_enabled': net.get('dhcp_enabled', True),
            }

            # Add VLAN if not native
            if vlan_id and vlan_id > 1:
                unifi_net['vlan_enabled'] = True
                unifi_net['vlan'] = str(vlan_id)

            # Add DHCP settings
            if net.get('dhcp_enabled', True):
                dhcp_start = net.get('dhcp_start', '')
                dhcp_stop = net.get('dhcp_stop', '')
                dns_servers = net.get('dns_servers', [])

                if dhcp_start:
                    unifi_net['dhcpd_start'] = dhcp_start
                if dhcp_stop:
                    unifi_net['dhcpd_stop'] = dhcp_stop

                unifi_net['dhcpd_dns_enabled'] = True
                if dns_servers:
                    unifi_net['dhcpd_dns_1'] = dns_servers[0]
                    if len(dns_servers) > 1:
                        unifi_net['dhcpd_dns_2'] = dns_servers[1]
                else:
                    unifi_net['dhcpd_dns_1'] = '8.8.8.8'
                    unifi_net['dhcpd_dns_2'] = '8.8.4.4'

                unifi_net['dhcpd_leasetime'] = 86400  # 1 day

            # Add isolation
            if network_isolation:
                unifi_net['network_isolation'] = True

            unifi_networks.append(unifi_net)

        return {
            'meta': {
                'generator': 'Network Migration Toolkit',
                'customer': self.metadata.get('customer_name', 'Unknown'),
                'source_platform': self.metadata.get('source_platform', 'unknown'),
                'source_device': self.metadata.get('source_device', ''),
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_networks': len(unifi_networks)
            },
            'networks': unifi_networks
        }

    def _build_firewall(self) -> dict:
        """Build UniFi firewall rules JSON"""
        unifi_rules = []

        # Add standard WAN input blocking rules
        wan_block_tcp = {
            'name': 'Block-Dangerous-TCP-WAN',
            'action': 'drop',
            'rule_index': 2001,
            'enabled': True,
            'protocol': 'tcp',
            'protocol_match_excepted': False,
            'src_firewallgroup_ids': [],
            'dst_firewallgroup_ids': [],
            'dst_port': '21,22,23,80,443,2000,8080',
            'ruleset': 'WAN_IN',
        }
        unifi_rules.append(wan_block_tcp)

        wan_block_udp = {
            'name': 'Block-Dangerous-UDP-WAN',
            'action': 'drop',
            'rule_index': 2002,
            'enabled': True,
            'protocol': 'udp',
            'protocol_match_excepted': False,
            'src_firewallgroup_ids': [],
            'dst_firewallgroup_ids': [],
            'dst_port': '53,123,161',
            'ruleset': 'WAN_IN',
        }
        unifi_rules.append(wan_block_udp)

        # Process source firewall rules
        for i, rule in enumerate(self.firewall_rules):
            action = rule.get('action', 'drop')
            name = rule.get('name', f'Rule-{i+1}')

            # Map action
            unifi_action = 'accept' if action in ['accept', 'allow'] else 'drop'

            unifi_rule = {
                'name': name,
                'action': unifi_action,
                'rule_index': 3000 + i,
                'enabled': rule.get('enabled', True),
            }

            # Add protocol if specified
            protocol = rule.get('protocol', '')
            if protocol:
                unifi_rule['protocol'] = protocol

            # Add ports if specified
            dst_ports = rule.get('dst_ports', [])
            if dst_ports:
                unifi_rule['dst_port'] = ','.join(str(p) for p in dst_ports)

            # Determine ruleset
            chain = rule.get('chain', 'forward')
            if chain == 'input':
                unifi_rule['ruleset'] = 'WAN_IN'
            else:
                unifi_rule['ruleset'] = 'LAN_IN'

            unifi_rules.append(unifi_rule)

        return {
            'meta': {
                'generator': 'Network Migration Toolkit',
                'customer': self.metadata.get('customer_name', 'Unknown'),
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_rules': len(unifi_rules)
            },
            'firewall_rules': unifi_rules
        }

    def _build_port_forwards(self) -> dict:
        """Build UniFi port forwarding JSON"""
        forwards = []

        for pf in self.port_forwards:
            name = pf.get('name', 'Port-Forward')
            dst_port = pf.get('dst_port', '')
            to_address = pf.get('to_address', '')
            to_port = pf.get('to_port', dst_port)
            protocol = pf.get('protocol', 'tcp')

            if not dst_port or not to_address:
                continue

            forward = {
                'name': name,
                'enabled': True,
                'src': 'any',
                'dst_port': str(dst_port),
                'fwd': to_address,
                'fwd_port': str(to_port),
                'proto': protocol if protocol != 'tcp_udp' else 'tcp_udp',
                'log': False,
            }

            forwards.append(forward)

        return {
            'meta': {
                'generator': 'Network Migration Toolkit',
                'customer': self.metadata.get('customer_name', 'Unknown'),
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_forwards': len(forwards)
            },
            'port_forwards': forwards
        }

    def _build_static_dhcp(self) -> dict:
        """Build UniFi static DHCP reservations JSON"""
        reservations = []

        for lease in self.static_leases:
            name = lease.get('name', 'Device')
            mac = lease.get('mac_address', '')
            ip = lease.get('ip_address', '')

            if not mac or not ip:
                continue

            reservation = {
                'name': name,
                'mac': mac.upper(),
                'fixed_ip': ip,
            }

            reservations.append(reservation)

        return {
            'meta': {
                'generator': 'Network Migration Toolkit',
                'customer': self.metadata.get('customer_name', 'Unknown'),
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_reservations': len(reservations)
            },
            'static_dhcp': reservations
        }

    def _build_migration_guide(self) -> str:
        """Build comprehensive migration guide in Markdown"""
        customer = self.metadata.get('customer_name', 'Unknown')
        source = self.metadata.get('source_platform', 'unknown').title()
        source_device = self.metadata.get('source_device', '')
        wan_ip = self.metadata.get('wan_ip', 'N/A')
        wan_gateway = self.metadata.get('wan_gateway', 'N/A')

        # Count networks by type
        infra_nets = [n for n in self.networks if n.get('vlan_id', 0) < 100]
        unit_nets = [n for n in self.networks if n.get('vlan_id', 0) >= 100]

        guide = f"""# {customer} - Network Migration Guide

## Migration Summary

| Field | Value |
|-------|-------|
| **Customer** | {customer} |
| **Source Platform** | {source} |
| **Source Device** | {source_device} |
| **Target Platform** | UniFi Gateway (UDM-Pro / UCG-Max) |
| **Generated** | {datetime.now().strftime('%Y-%m-%d %H:%M')} |

---

## Pre-Migration Checklist

- [ ] Backup source device configuration
- [ ] Verify UniFi Gateway firmware is up to date
- [ ] Document current DHCP leases from source device
- [ ] Plan maintenance window (off-hours recommended)
- [ ] Have rollback plan ready

---

## WAN Configuration

Configure in: **Settings > Internet > Primary (WAN1)**

| Setting | Value |
|---------|-------|
| **Connection Type** | Static IP |
| **IP Address** | {wan_ip} |
| **Gateway** | {wan_gateway} |
| **DNS Servers** | 9.9.9.9, 8.8.8.8 |

---

## Networks to Create

**Total Networks:** {len(self.networks)}
- Infrastructure Networks: {len(infra_nets)}
- Unit/Customer Networks: {len(unit_nets)}

### Infrastructure Networks (Create First)

| VLAN | Name | Subnet | Gateway | DHCP Range | Purpose |
|------|------|--------|---------|------------|---------|
"""
        # Add infrastructure networks
        for net in sorted(infra_nets, key=lambda x: x.get('vlan_id', 0)):
            vlan = net.get('vlan_id', 0)
            name = net.get('name', '')
            subnet = net.get('subnet', '')
            gateway = net.get('gateway', '')
            dhcp_start = net.get('dhcp_start', '')
            dhcp_stop = net.get('dhcp_stop', '')
            purpose = net.get('purpose', 'corporate')

            dhcp_range = f"{dhcp_start} - {dhcp_stop}" if dhcp_start else "Disabled"
            guide += f"| {vlan} | {name} | {subnet} | {gateway} | {dhcp_range} | {purpose} |\n"

        if unit_nets:
            guide += f"""
### Unit Networks ({len(unit_nets)} VLANs)

| VLAN | Name | Subnet | Gateway | DHCP Range |
|------|------|--------|---------|------------|
"""
            for net in sorted(unit_nets, key=lambda x: x.get('vlan_id', 0)):
                vlan = net.get('vlan_id', 0)
                name = net.get('name', '')
                subnet = net.get('subnet', '')
                gateway = net.get('gateway', '')
                dhcp_start = net.get('dhcp_start', '')
                dhcp_stop = net.get('dhcp_stop', '')

                dhcp_range = f"{dhcp_start} - {dhcp_stop}" if dhcp_start else "Disabled"
                guide += f"| {vlan} | {name} | {subnet} | {gateway} | {dhcp_range} |\n"

        # Port forwards section
        if self.port_forwards:
            guide += f"""
---

## Port Forwarding Rules

Configure in: **Settings > Firewall & Security > Port Forwarding**

| Name | External Port | Internal IP | Internal Port | Protocol |
|------|---------------|-------------|---------------|----------|
"""
            for pf in self.port_forwards:
                name = pf.get('name', 'Forward')
                dst_port = pf.get('dst_port', '')
                to_addr = pf.get('to_address', '')
                to_port = pf.get('to_port', dst_port)
                proto = pf.get('protocol', 'tcp')
                guide += f"| {name} | {dst_port} | {to_addr} | {to_port} | {proto} |\n"

        # Static DHCP section
        if self.static_leases:
            guide += f"""
---

## Static DHCP Reservations

Configure in: **Settings > Networks > [Network] > DHCP > Static IP Settings**

| Name | MAC Address | IP Address |
|------|-------------|------------|
"""
            for lease in self.static_leases:
                name = lease.get('name', 'Device')
                mac = lease.get('mac_address', '')
                ip = lease.get('ip_address', '')
                guide += f"| {name} | {mac} | {ip} |\n"

        # Migration steps
        guide += f"""
---

## Migration Steps

### Phase 1: Preparation
1. Export source device configuration backup
2. Document all current DHCP leases
3. Update UniFi Gateway firmware to latest
4. Pre-configure all networks in UniFi (can do while source is live)

### Phase 2: Network Creation (Before Cutover)
1. Create all {len(infra_nets)} infrastructure networks
2. Create all {len(unit_nets)} unit networks (if applicable)
3. Configure DHCP settings for each network
4. Create firewall rules
5. Create port forwarding rules
6. Add static DHCP reservations

### Phase 3: Cutover
1. Schedule maintenance window
2. Disconnect source device WAN
3. Connect UniFi Gateway WAN (Port 9 SFP+ or Port 11 RJ45)
4. Configure WAN static IP: {wan_ip}
5. Set gateway: {wan_gateway}
6. Connect trunk port to switch
7. Verify connectivity per-VLAN
8. Test port forwards
9. Monitor for issues

### Phase 4: Validation
- [ ] All networks have internet access
- [ ] Port forwards working correctly
- [ ] Static DHCP devices getting correct IPs
- [ ] Guest/IoT networks properly isolated
- [ ] Management access working

---

## Rollback Plan

If migration fails:
1. Disconnect UniFi Gateway
2. Reconnect source device ({source_device})
3. Verify all services restored
4. Document issues encountered
5. Plan remediation

---

## Files Generated

- `unifi_networks.json` - Network configurations for reference
- `unifi_firewall.json` - Firewall rules for reference
- `unifi_port_forwards.json` - Port forwarding rules
- `unifi_static_dhcp.json` - Static DHCP reservations
- `MIGRATION_GUIDE.md` - This guide

---

*Generated by Network Migration Toolkit | {datetime.now().strftime('%Y-%m-%d')}*
"""

        return guide


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


def interactive_build():
    """Interactive mode for building UniFi configs"""
    print("=" * 60)
    print("Network Migration Toolkit - UniFi Config Builder")
    print("=" * 60)
    print()
    print("Generates UniFi-compatible configuration files from parsed configs")
    print()

    # Get config file path
    while True:
        config_path = input("Enter path to config JSON: ").strip()
        if not config_path:
            print("  Config file path is required.")
            continue

        config_path = Path(config_path).expanduser()
        if not config_path.exists():
            print(f"  File not found: {config_path}")
            continue
        break

    # Load config
    config = load_config(str(config_path))

    customer = config.get('metadata', {}).get('customer_name', 'Unknown')
    source = config.get('metadata', {}).get('source_platform', 'unknown')
    num_networks = len(config.get('networks', []))

    print()
    print(f"Loaded: {customer}")
    print(f"  Source: {source}")
    print(f"  Networks: {num_networks}")
    print()

    # Get output directory
    default_output = config_path.parent / f"{config_path.stem}_unifi"
    output_dir = input(f"Enter output directory [{default_output}]: ").strip()
    if not output_dir:
        output_dir = str(default_output)

    print()
    print("Building UniFi configuration...")
    print()

    # Build configs
    builder = UniFiConfigBuilder(config)
    files = builder.build_all(output_dir)

    print("Generated files:")
    for name, path in files.items():
        print(f"  - {name}: {path}")

    print()
    print(f"Output directory: {output_dir}")
    print()

    return files


if __name__ == '__main__':
    interactive_build()
