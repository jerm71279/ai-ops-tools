#!/usr/bin/env python3
"""
Network Migration Toolkit
Main CLI for parsing, building, and deploying network configurations

Usage:
    python migrate.py parse mikrotik       # Parse MikroTik config
    python migrate.py parse sonicwall      # Parse SonicWall config
    python migrate.py parse cisco          # Parse Cisco IOS config
    python migrate.py build unifi          # Build UniFi config files
    python migrate.py deploy unifi         # Deploy to UniFi Gateway
    python migrate.py validate config.json
    python migrate.py report config.json
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from parsers.mikrotik_parser import MikroTikParser, interactive_parse as mikrotik_interactive
from parsers.sonicwall_parser import SonicWallParser, interactive_parse as sonicwall_interactive
from parsers.cisco_parser import CiscoParser, interactive_parse as cisco_interactive
from deployers.unifi_deployer import interactive_deploy as unifi_interactive, load_config
from builders.unifi_builder import UniFiConfigBuilder, interactive_build as unifi_build_interactive


def cmd_parse(args):
    """Parse command - extract config from source device"""
    if args.source == 'mikrotik':
        if args.input:
            # Non-interactive mode
            parser = MikroTikParser()
            schema = parser.parse_file(args.input)

            if args.customer:
                schema['metadata']['customer_name'] = args.customer

            output_path = args.output or args.input.replace('.txt', '.json')
            with open(output_path, 'w') as f:
                json.dump(schema, f, indent=2)

            print(f"Parsed {len(schema['networks'])} networks")
            print(f"Output: {output_path}")
        else:
            # Interactive mode
            mikrotik_interactive()

    elif args.source == 'sonicwall':
        if args.input:
            # Non-interactive mode
            parser = SonicWallParser()
            schema = parser.parse_file(args.input)

            if args.customer:
                schema['metadata']['customer_name'] = args.customer

            output_path = args.output or args.input.replace('.cli', '.json').replace('.txt', '.json')
            with open(output_path, 'w') as f:
                json.dump(schema, f, indent=2)

            print(f"Parsed {len(schema['networks'])} networks")
            print(f"Output: {output_path}")
        else:
            # Interactive mode
            sonicwall_interactive()

    elif args.source == 'cisco':
        if args.input:
            # Non-interactive mode
            parser = CiscoParser()
            schema = parser.parse_file(args.input)

            if args.customer:
                schema['metadata']['customer_name'] = args.customer

            output_path = args.output or args.input.replace('.txt', '.json')
            with open(output_path, 'w') as f:
                json.dump(schema, f, indent=2)

            print(f"Parsed {len(schema['networks'])} VLANs, {len(schema.get('switch_ports', []))} ports")
            print(f"Output: {output_path}")
        else:
            # Interactive mode
            cisco_interactive()

    else:
        print(f"Unknown source platform: {args.source}")
        print("Supported: mikrotik, sonicwall, cisco")
        sys.exit(1)


def cmd_build(args):
    """Build command - generate target device config files"""
    if args.target == 'unifi':
        if args.config:
            # Non-interactive mode
            config = load_config(args.config)
            builder = UniFiConfigBuilder(config)

            output_dir = args.output or str(Path(args.config).parent / f"{Path(args.config).stem}_unifi")
            files = builder.build_all(output_dir)

            print(f"Generated {len(files)} files:")
            for name, path in files.items():
                print(f"  - {name}")
            print(f"\nOutput: {output_dir}")
        else:
            # Interactive mode
            unifi_build_interactive()
    else:
        print(f"Unknown target platform: {args.target}")
        print("Supported: unifi")
        sys.exit(1)


def cmd_deploy(args):
    """Deploy command - push config to target device"""
    if args.target == 'unifi':
        if args.config and args.host:
            # Non-interactive mode
            from deployers.unifi_deployer import UniFiDeployer, config_to_networks
            import getpass

            config = load_config(args.config)
            networks = config_to_networks(config)

            username = args.user or 'admin'
            password = args.password or getpass.getpass("Password: ")

            deployer = UniFiDeployer(args.host, username, password)
            if not deployer.login():
                sys.exit(1)

            try:
                for net in networks:
                    deployer.create_network(net, dry_run=args.dry_run)
            finally:
                deployer.logout()
        else:
            # Interactive mode
            unifi_interactive()
    else:
        print(f"Unknown target platform: {args.target}")
        print("Supported: unifi")
        sys.exit(1)


def cmd_validate(args):
    """Validate command - check config file against schema"""
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)

        errors = []

        # Check required fields
        if 'metadata' not in config:
            errors.append("Missing 'metadata' section")
        if 'networks' not in config:
            errors.append("Missing 'networks' section")

        # Check metadata
        meta = config.get('metadata', {})
        if not meta.get('customer_name'):
            errors.append("Missing metadata.customer_name")
        if not meta.get('source_platform'):
            errors.append("Missing metadata.source_platform")

        # Check networks
        for i, net in enumerate(config.get('networks', [])):
            if not net.get('name'):
                errors.append(f"Network {i}: missing 'name'")
            if 'vlan_id' not in net:
                errors.append(f"Network {i}: missing 'vlan_id'")

        if errors:
            print(f"Validation FAILED ({len(errors)} errors):")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        else:
            print(f"Validation PASSED")
            print(f"  Customer: {meta.get('customer_name')}")
            print(f"  Platform: {meta.get('source_platform')}")
            print(f"  Networks: {len(config.get('networks', []))}")

    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {args.config}")
        sys.exit(1)


def cmd_report(args):
    """Report command - generate migration summary"""
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)

        meta = config.get('metadata', {})
        networks = config.get('networks', [])
        firewall = config.get('firewall_rules', [])
        nat = config.get('nat_rules', [])
        port_fwd = config.get('port_forwards', [])
        static_dhcp = config.get('static_dhcp_leases', [])

        # Generate report
        report = []
        report.append(f"# Network Migration Report: {meta.get('customer_name', 'Unknown')}")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"**Source:** {meta.get('source_device', 'Unknown')} ({meta.get('source_firmware', 'Unknown')})")
        report.append("")
        report.append("## Summary")
        report.append("")
        report.append(f"| Item | Count |")
        report.append(f"|------|-------|")
        report.append(f"| Networks/VLANs | {len(networks)} |")
        report.append(f"| Firewall Rules | {len(firewall)} |")
        report.append(f"| NAT Rules | {len(nat)} |")
        report.append(f"| Port Forwards | {len(port_fwd)} |")
        report.append(f"| Static DHCP | {len(static_dhcp)} |")
        report.append("")

        # WAN config
        report.append("## WAN Configuration")
        report.append("")
        report.append(f"| Setting | Value |")
        report.append(f"|---------|-------|")
        report.append(f"| WAN IP | {meta.get('wan_ip', 'N/A')} |")
        report.append(f"| Gateway | {meta.get('wan_gateway', 'N/A')} |")
        report.append(f"| Interface | {meta.get('wan_interface', 'N/A')} |")
        report.append("")

        # Networks table
        report.append("## Networks")
        report.append("")
        report.append("| VLAN | Name | Subnet | Gateway | DHCP Range |")
        report.append("|------|------|--------|---------|------------|")
        for net in sorted(networks, key=lambda x: x.get('vlan_id', 0)):
            vlan = net.get('vlan_id', 0)
            name = net.get('name', '')
            subnet = net.get('subnet', '')
            gateway = net.get('gateway', '')
            dhcp_start = net.get('dhcp_start', '')
            dhcp_stop = net.get('dhcp_stop', '')
            dhcp_range = f"{dhcp_start} - {dhcp_stop}" if dhcp_start else "Disabled"
            report.append(f"| {vlan} | {name} | {subnet} | {gateway} | {dhcp_range} |")
        report.append("")

        # Output
        output = '\n'.join(report)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Report saved to: {args.output}")
        else:
            print(output)

    except FileNotFoundError:
        print(f"File not found: {args.config}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Network Migration Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive parsing (prompts for file)
  python migrate.py parse mikrotik
  python migrate.py parse sonicwall
  python migrate.py parse cisco

  # Interactive UniFi deployment (prompts for config and credentials)
  python migrate.py deploy unifi

  # Non-interactive parsing
  python migrate.py parse mikrotik --input config.txt --output config.json --customer "Acme Corp"
  python migrate.py parse cisco --input switch.txt --output switch.json --customer "Sexton"

  # Non-interactive deployment (dry-run)
  python migrate.py deploy unifi --config config.json --host 192.168.1.1 --dry-run

  # Validate config file
  python migrate.py validate config.json

  # Generate migration report
  python migrate.py report config.json --output report.md
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse source device config')
    parse_parser.add_argument('source', choices=['mikrotik', 'sonicwall', 'cisco'], help='Source platform')
    parse_parser.add_argument('--input', '-i', help='Input config file (omit for interactive)')
    parse_parser.add_argument('--output', '-o', help='Output JSON file')
    parse_parser.add_argument('--customer', '-c', help='Customer name')

    # Build command
    build_parser = subparsers.add_parser('build', help='Build target device config files')
    build_parser.add_argument('target', choices=['unifi'], help='Target platform')
    build_parser.add_argument('--config', '-c', help='Config JSON file (omit for interactive)')
    build_parser.add_argument('--output', '-o', help='Output directory')

    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy to target device via API')
    deploy_parser.add_argument('target', choices=['unifi'], help='Target platform')
    deploy_parser.add_argument('--config', '-c', help='Config JSON file (omit for interactive)')
    deploy_parser.add_argument('--host', '-H', help='Target device IP')
    deploy_parser.add_argument('--user', '-u', help='Admin username')
    deploy_parser.add_argument('--password', '-p', help='Admin password (not recommended)')
    deploy_parser.add_argument('--dry-run', action='store_true', help='Preview only, no changes')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate config file')
    validate_parser.add_argument('config', help='Config JSON file to validate')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate migration report')
    report_parser.add_argument('config', help='Config JSON file')
    report_parser.add_argument('--output', '-o', help='Output file (default: stdout)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'parse':
        cmd_parse(args)
    elif args.command == 'build':
        cmd_build(args)
    elif args.command == 'deploy':
        cmd_deploy(args)
    elif args.command == 'validate':
        cmd_validate(args)
    elif args.command == 'report':
        cmd_report(args)


if __name__ == '__main__':
    main()
