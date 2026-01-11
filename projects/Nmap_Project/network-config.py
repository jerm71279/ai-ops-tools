#!/usr/bin/env python3
"""
Customer Network Configuration Interface
Collects network topology information before scanning
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

class NetworkConfig:
    def __init__(self):
        # Use project directory instead of root filesystem
        script_dir = Path(__file__).parent
        self.config_dir = script_dir / "scans" / "configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def validate_ip_network(self, network):
        """Validate IP network in CIDR notation"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?$'
        if not re.match(pattern, network):
            return False

        # Basic validation of octets
        parts = network.split('/')[0].split('.')
        for part in parts:
            if int(part) > 255:
                return False

        # Validate CIDR if present
        if '/' in network:
            cidr = int(network.split('/')[1])
            if cidr < 0 or cidr > 32:
                return False

        return True

    def validate_ip(self, ip):
        """Validate single IP address"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False

        parts = ip.split('.')
        for part in parts:
            if int(part) > 255:
                return False

        return True

    def get_input(self, prompt, validator=None, allow_empty=False):
        """Get user input with validation"""
        while True:
            value = input(prompt).strip()

            if not value and allow_empty:
                return None

            if not value:
                print("  ❌ This field is required. Please enter a value.")
                continue

            if validator and not validator(value):
                print("  ❌ Invalid format. Please try again.")
                continue

            return value

    def get_yes_no(self, prompt):
        """Get yes/no input"""
        while True:
            value = input(f"{prompt} (y/n): ").strip().lower()
            if value in ['y', 'yes']:
                return True
            elif value in ['n', 'no']:
                return False
            else:
                print("  ❌ Please enter 'y' or 'n'")

    def get_vlan_info(self):
        """Collect VLAN information"""
        vlans = []

        print("\n--- VLAN Configuration ---")
        has_vlans = self.get_yes_no("Does this network have VLANs?")

        if not has_vlans:
            return vlans

        print("\nEnter VLAN information (press Enter on VLAN ID when done):")

        vlan_count = 1
        while True:
            print(f"\n  VLAN #{vlan_count}:")

            vlan_id = input(f"    VLAN ID (or press Enter to finish): ").strip()
            if not vlan_id:
                break

            if not vlan_id.isdigit() or int(vlan_id) < 1 or int(vlan_id) > 4094:
                print("    ❌ VLAN ID must be between 1 and 4094")
                continue

            vlan_name = input(f"    VLAN Name/Description: ").strip()

            vlan_network = self.get_input(
                f"    VLAN Network (CIDR, e.g., 192.168.10.0/24): ",
                validator=self.validate_ip_network
            )

            # Optional gateway
            gateway = input(f"    Default Gateway (optional): ").strip()
            if gateway and not self.validate_ip(gateway):
                print("    ⚠️  Invalid gateway IP, skipping...")
                gateway = None

            vlans.append({
                "id": int(vlan_id),
                "name": vlan_name,
                "network": vlan_network,
                "gateway": gateway if gateway else None
            })

            print(f"    ✓ VLAN {vlan_id} added")
            vlan_count += 1

        return vlans

    def get_exclusions(self):
        """Collect IP exclusions"""
        print("\n--- Exclusion List ---")
        print("Enter IP addresses or networks that should NOT be scanned")
        print("(e.g., production servers, critical infrastructure)")

        has_exclusions = self.get_yes_no("\nDo you have systems to exclude from scanning?")

        if not has_exclusions:
            return []

        exclusions = []
        print("\nEnter exclusions (press Enter on IP/Network when done):")

        excl_count = 1
        while True:
            print(f"\n  Exclusion #{excl_count}:")

            excl_ip = input(f"    IP/Network (or press Enter to finish): ").strip()
            if not excl_ip:
                break

            if not (self.validate_ip(excl_ip) or self.validate_ip_network(excl_ip)):
                print("    ❌ Invalid IP or network format")
                continue

            excl_reason = input(f"    Reason for exclusion: ").strip()

            exclusions.append({
                "target": excl_ip,
                "reason": excl_reason
            })

            print(f"    ✓ {excl_ip} added to exclusion list")
            excl_count += 1

        return exclusions

    def configure_customer(self):
        """Main configuration workflow"""
        print("=" * 60)
        print("CUSTOMER NETWORK CONFIGURATION")
        print("=" * 60)
        print("\nThis tool will collect network topology information")
        print("for proper scan configuration and documentation.\n")

        # Customer Information
        print("--- Customer Information ---")
        customer_name = self.get_input("Customer Name: ")
        customer_id = self.get_input("Customer ID/Code (optional): ", allow_empty=True)
        contact_name = self.get_input("Primary Contact: ")
        contact_email = self.get_input("Contact Email: ")

        # Authorization
        print("\n--- Scan Authorization ---")
        auth_received = self.get_yes_no("Have you received written authorization to scan?")

        if not auth_received:
            print("\n⚠️  WARNING: You must obtain written authorization before scanning!")
            print("   Proceeding without authorization may be illegal.")
            proceed = self.get_yes_no("\nDo you want to continue anyway (for planning purposes)?")
            if not proceed:
                print("\n❌ Configuration cancelled.")
                return None

        auth_reference = self.get_input("Authorization Reference/Ticket # (optional): ", allow_empty=True)

        # Network Information
        print("\n--- Primary Network Configuration ---")
        primary_network = self.get_input(
            "Primary Network (CIDR, e.g., 192.168.1.0/24): ",
            validator=self.validate_ip_network
        )

        # Additional networks
        additional_networks = []
        if self.get_yes_no("\nAre there additional networks to scan?"):
            print("\nEnter additional networks (press Enter when done):")
            net_count = 1
            while True:
                net = input(f"  Network #{net_count} (or press Enter to finish): ").strip()
                if not net:
                    break

                if self.validate_ip_network(net):
                    additional_networks.append(net)
                    print(f"    ✓ {net} added")
                    net_count += 1
                else:
                    print("    ❌ Invalid network format")

        # VLANs
        vlans = self.get_vlan_info()

        # Exclusions
        exclusions = self.get_exclusions()

        # Scan Settings
        print("\n--- Scan Configuration ---")
        print("Scan types:")
        print("  1. Quick Discovery (ping sweep only)")
        print("  2. Standard (discovery + port scan)")
        print("  3. Intense (comprehensive with OS/service detection)")
        print("  4. Custom (you'll specify later)")

        scan_type = self.get_input("Select scan type (1-4): ")
        scan_type_map = {
            "1": "quick",
            "2": "standard",
            "3": "intense",
            "4": "custom"
        }
        selected_scan = scan_type_map.get(scan_type, "standard")

        # Timing
        print("\nScan timing:")
        print("  1. Polite (T2 - slower, less intrusive)")
        print("  2. Normal (T3 - default)")
        print("  3. Aggressive (T4 - faster)")

        timing = self.get_input("Select timing (1-3) [default: 2]: ", allow_empty=True)
        timing_map = {"1": "T2", "2": "T3", "3": "T4"}
        selected_timing = timing_map.get(timing, "T3")

        # Schedule
        scheduled_time = self.get_input(
            "Scheduled scan time (optional, e.g., '2025-11-15 02:00'): ",
            allow_empty=True
        )

        # Build configuration
        config = {
            "customer": {
                "name": customer_name,
                "id": customer_id,
                "contact": {
                    "name": contact_name,
                    "email": contact_email
                },
                "authorization": {
                    "received": auth_received,
                    "reference": auth_reference,
                    "date": datetime.now().isoformat()
                }
            },
            "network": {
                "primary": primary_network,
                "additional": additional_networks,
                "vlans": vlans
            },
            "exclusions": exclusions,
            "scan_config": {
                "type": selected_scan,
                "timing": selected_timing,
                "scheduled_time": scheduled_time
            },
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "created_by": os.getenv("USER", "unknown"),
                "version": "1.0"
            }
        }

        # Display summary
        self.display_summary(config)

        # Confirm and save
        if self.get_yes_no("\nSave this configuration?"):
            return self.save_config(config, customer_name)
        else:
            print("\n❌ Configuration not saved.")
            return None

    def display_summary(self, config):
        """Display configuration summary"""
        print("\n" + "=" * 60)
        print("CONFIGURATION SUMMARY")
        print("=" * 60)

        print(f"\n📋 Customer: {config['customer']['name']}")
        if config['customer']['id']:
            print(f"   ID: {config['customer']['id']}")
        print(f"   Contact: {config['customer']['contact']['name']} ({config['customer']['contact']['email']})")

        print(f"\n✅ Authorization: {'Received' if config['customer']['authorization']['received'] else 'NOT RECEIVED'}")
        if config['customer']['authorization']['reference']:
            print(f"   Reference: {config['customer']['authorization']['reference']}")

        print(f"\n🌐 Primary Network: {config['network']['primary']}")

        if config['network']['additional']:
            print(f"   Additional Networks:")
            for net in config['network']['additional']:
                print(f"     - {net}")

        if config['network']['vlans']:
            print(f"\n🔀 VLANs ({len(config['network']['vlans'])}):")
            for vlan in config['network']['vlans']:
                print(f"     - VLAN {vlan['id']}: {vlan['name']} ({vlan['network']})")

        if config['exclusions']:
            print(f"\n🚫 Exclusions ({len(config['exclusions'])}):")
            for excl in config['exclusions']:
                print(f"     - {excl['target']}: {excl['reason']}")

        print(f"\n🔍 Scan Type: {config['scan_config']['type'].upper()}")
        print(f"   Timing: {config['scan_config']['timing']}")
        if config['scan_config']['scheduled_time']:
            print(f"   Scheduled: {config['scan_config']['scheduled_time']}")

        print("=" * 60)

    def save_config(self, config, customer_name):
        """Save configuration to file"""
        # Create safe filename
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', customer_name.lower())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.json"
        filepath = self.config_dir / filename

        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)

        # Also create exclude.txt file
        if config['exclusions']:
            excl_filename = f"{safe_name}_{timestamp}_exclude.txt"
            excl_filepath = self.config_dir / excl_filename

            with open(excl_filepath, 'w') as f:
                f.write(f"# Exclusion list for {config['customer']['name']}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                for excl in config['exclusions']:
                    f.write(f"{excl['target']}    # {excl['reason']}\n")

            print(f"\n✓ Exclusion file created: {excl_filepath}")

        print(f"✓ Configuration saved: {filepath}")

        # Create scan plan
        self.create_scan_plan(config, safe_name, timestamp)

        return filepath

    def create_scan_plan(self, config, safe_name, timestamp):
        """Create executable scan plan"""
        plan_filename = f"{safe_name}_{timestamp}_scan_plan.sh"
        plan_filepath = self.config_dir / plan_filename

        with open(plan_filepath, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"# Scan Plan for {config['customer']['name']}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")

            f.write("echo '======================================'\n")
            f.write(f"echo 'Scan Plan: {config['customer']['name']}'\n")
            f.write("echo '======================================'\n")
            f.write("echo ''\n\n")

            # Primary network
            scan_cmd = self.build_scan_command(
                config['network']['primary'],
                config['scan_config']['type'],
                config['scan_config']['timing'],
                config['exclusions'],
                safe_name,
                "primary"
            )
            f.write(f"# Primary Network: {config['network']['primary']}\n")
            f.write(f"echo 'Scanning primary network: {config['network']['primary']}...'\n")
            f.write(f"{scan_cmd}\n\n")

            # Additional networks
            for idx, network in enumerate(config['network']['additional'], 1):
                scan_cmd = self.build_scan_command(
                    network,
                    config['scan_config']['type'],
                    config['scan_config']['timing'],
                    config['exclusions'],
                    safe_name,
                    f"additional_{idx}"
                )
                f.write(f"# Additional Network {idx}: {network}\n")
                f.write(f"echo 'Scanning additional network: {network}...'\n")
                f.write(f"{scan_cmd}\n\n")

            # VLANs
            for vlan in config['network']['vlans']:
                scan_cmd = self.build_scan_command(
                    vlan['network'],
                    config['scan_config']['type'],
                    config['scan_config']['timing'],
                    config['exclusions'],
                    safe_name,
                    f"vlan_{vlan['id']}"
                )
                f.write(f"# VLAN {vlan['id']}: {vlan['name']} - {vlan['network']}\n")
                f.write(f"echo 'Scanning VLAN {vlan['id']} ({vlan['name']}): {vlan['network']}...'\n")
                f.write(f"{scan_cmd}\n\n")

            f.write("echo ''\n")
            f.write("echo '======================================'\n")
            f.write("echo 'All scans complete!'\n")
            f.write("echo '======================================'\n")

        os.chmod(plan_filepath, 0o755)
        print(f"✓ Scan plan created: {plan_filepath}")
        print(f"\n📝 To execute the scan plan:")
        print(f"   docker exec kali-network-discovery {plan_filepath}")

    def build_scan_command(self, network, scan_type, timing, exclusions, customer_name, segment_name):
        """Build nmap command based on configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scans_dir = self.config_dir.parent
        output_base = f"{scans_dir}/{customer_name}_{segment_name}_{timestamp}"

        cmd_parts = ["nmap"]

        # Timing
        cmd_parts.append(f"-{timing}")

        # Scan type
        if scan_type == "quick":
            cmd_parts.append("-sn")  # Ping sweep only
        elif scan_type == "standard":
            cmd_parts.append("-sV")  # Service detection
        elif scan_type == "intense":
            cmd_parts.append("-A")   # Aggressive (OS, version, scripts, traceroute)

        # Verbose
        cmd_parts.append("-v")

        # Exclusions
        if exclusions:
            excl_file = f"{self.config_dir}/{customer_name}_*_exclude.txt"
            cmd_parts.append(f"--excludefile {excl_file}")

        # Target
        cmd_parts.append(network)

        # Output
        cmd_parts.append(f"-oA {output_base}")

        return " ".join(cmd_parts)

    def list_configs(self):
        """List saved configurations"""
        configs = sorted(self.config_dir.glob("*.json"), key=os.path.getmtime, reverse=True)

        if not configs:
            print("\nNo saved configurations found.")
            return

        print("\n" + "=" * 60)
        print("SAVED CONFIGURATIONS")
        print("=" * 60)

        for idx, config_file in enumerate(configs, 1):
            with open(config_file, 'r') as f:
                config = json.load(f)

            print(f"\n{idx}. {config['customer']['name']}")
            print(f"   File: {config_file.name}")
            print(f"   Network: {config['network']['primary']}")
            if config['network']['vlans']:
                print(f"   VLANs: {len(config['network']['vlans'])}")
            print(f"   Created: {config['metadata']['created_date'][:19]}")

        print("=" * 60)

def main():
    """Main entry point"""
    config_tool = NetworkConfig()

    while True:
        print("\n" + "=" * 60)
        print("NETWORK CONFIGURATION MENU")
        print("=" * 60)
        print("1. Create new customer configuration")
        print("2. List saved configurations")
        print("3. Exit")
        print("=" * 60)

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            config_tool.configure_customer()
        elif choice == "2":
            config_tool.list_configs()
        elif choice == "3":
            print("\nGoodbye!")
            break
        else:            print("Invalid option. Please select 1-3.")

if __name__ == "__main__":
    main()
