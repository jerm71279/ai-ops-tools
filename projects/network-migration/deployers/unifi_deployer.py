#!/usr/bin/env python3
"""
UniFi Gateway Deployer
Deploys network configuration from universal schema to UniFi gateways via API

Supported devices:
- UniFi Dream Machine Pro (UDM-Pro)
- UniFi Dream Machine SE (UDM-SE)
- UniFi Dream Machine Pro Max (UDM-Pro-Max)
- UniFi Cloud Gateway Max (UCG-Max)
- UniFi Cloud Gateway Ultra (UCG-Ultra)
- UniFi Express (UX)

All devices use the same API structure with /proxy/network/ prefix.
"""

import json
import os
import sys
import time
import getpass
import requests
import urllib3
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Supported UniFi gateway devices
SUPPORTED_DEVICES = {
    'udm-pro': 'UniFi Dream Machine Pro',
    'udm-se': 'UniFi Dream Machine SE',
    'udm-pro-max': 'UniFi Dream Machine Pro Max',
    'ucg-max': 'UniFi Cloud Gateway Max',
    'ucg-ultra': 'UniFi Cloud Gateway Ultra',
    'ux': 'UniFi Express',
}


@dataclass
class NetworkConfig:
    """Network configuration from schema"""
    name: str
    vlan_id: int
    subnet: str
    gateway: str
    dhcp_enabled: bool = True
    dhcp_start: str = ""
    dhcp_stop: str = ""
    dns_servers: List[str] = field(default_factory=list)
    purpose: str = "corporate"
    network_isolation: bool = False


class UniFiDeployer:
    """Deploy networks to UniFi Gateways (UDM-Pro, UCG-Max, etc.)"""

    def __init__(self, host: str, username: str, password: str, site: str = "default"):
        self.host = host
        self.username = username
        self.password = password
        self.site = site
        self.base_url = f"https://{host}"
        self.session = requests.Session()
        self.session.verify = False
        self.logged_in = False
        self.csrf_token = None
        self.created_networks = []
        self.device_type = None
        self.device_name = None

    def login(self) -> bool:
        """Authenticate with UniFi Gateway"""
        print(f"Connecting to UniFi Gateway at {self.host}...")

        login_url = f"{self.base_url}/api/auth/login"
        payload = {"username": self.username, "password": self.password}

        try:
            response = self.session.post(login_url, json=payload, timeout=10)

            self.csrf_token = response.headers.get('X-CSRF-Token') or response.headers.get('x-csrf-token')
            if not self.csrf_token:
                self.csrf_token = self.session.cookies.get('csrf_token') or self.session.cookies.get('TOKEN')

            if response.status_code == 200:
                self.logged_in = True
                self._detect_device()
                return True
            else:
                # Try accessing API anyway (some versions work differently)
                test_url = f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf"
                test_response = self.session.get(test_url, timeout=10)
                if test_response.status_code == 200:
                    self.logged_in = True
                    self._detect_device()
                    return True
                print(f"Login failed: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            print(f"ERROR: Cannot connect to {self.host}")
            print("Make sure the UniFi Gateway is reachable and you're on the same network")
            return False
        except Exception as e:
            print(f"Login error: {e}")
            return False

    def _detect_device(self):
        """Detect the UniFi device type"""
        try:
            # Try to get system info
            info_url = f"{self.base_url}/api/system"
            response = self.session.get(info_url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.device_name = data.get('name', 'UniFi Gateway')
                hardware = data.get('hardware', {})
                model = hardware.get('shortname', '') or hardware.get('name', '')

                # Map model to device type
                model_lower = model.lower()
                if 'ucg-max' in model_lower or 'cloud gateway max' in model_lower:
                    self.device_type = 'ucg-max'
                elif 'ucg-ultra' in model_lower or 'cloud gateway ultra' in model_lower:
                    self.device_type = 'ucg-ultra'
                elif 'udm-pro-max' in model_lower:
                    self.device_type = 'udm-pro-max'
                elif 'udm-se' in model_lower:
                    self.device_type = 'udm-se'
                elif 'udm-pro' in model_lower or 'udm pro' in model_lower:
                    self.device_type = 'udm-pro'
                elif 'ux' in model_lower or 'express' in model_lower:
                    self.device_type = 'ux'
                else:
                    self.device_type = 'unknown'

                device_desc = SUPPORTED_DEVICES.get(self.device_type, model or 'UniFi Gateway')
                print(f"Connected to {device_desc}")
                if self.device_name:
                    print(f"  Device name: {self.device_name}")
            else:
                print("Connected to UniFi Gateway")
                self.device_type = 'unknown'

        except Exception:
            print("Connected to UniFi Gateway")
            self.device_type = 'unknown'

    def logout(self):
        """Logout from UniFi Gateway"""
        if self.logged_in:
            try:
                self.session.post(f"{self.base_url}/api/auth/logout")
            except:
                pass

    def get_existing_networks(self) -> List[Dict]:
        """Get list of existing networks"""
        url = f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []

    def create_network(self, config: NetworkConfig, dry_run: bool = False) -> bool:
        """Create a single network/VLAN"""

        # Check if network already exists
        existing = self.get_existing_networks()
        for net in existing:
            if net.get("vlan") == str(config.vlan_id) or net.get("name") == config.name:
                print(f"  SKIP: {config.name} (VLAN {config.vlan_id}) already exists")
                return True

        # VLAN 1 - skip creation as it conflicts with default LAN
        if config.vlan_id == 1:
            print(f"  SKIP: {config.name} (VLAN 1) - use existing Default network")
            return True

        # Build gateway/CIDR from subnet
        gateway_cidr = f"{config.gateway}/{config.subnet.split('/')[-1]}" if '/' in config.subnet else config.subnet

        payload = {
            "name": config.name,
            "purpose": config.purpose if config.purpose in ["corporate", "guest"] else "corporate",
            "ip_subnet": gateway_cidr,
            "networkgroup": "LAN",
            "dhcpd_enabled": config.dhcp_enabled,
            "dhcpd_start": config.dhcp_start,
            "dhcpd_stop": config.dhcp_stop,
            "dhcpd_dns_enabled": True,
            "dhcpd_dns_1": config.dns_servers[0] if config.dns_servers else "8.8.8.8",
            "dhcpd_dns_2": config.dns_servers[1] if len(config.dns_servers) > 1 else "8.8.4.4",
            "dhcpd_leasetime": 86400,
            "dhcpguard_enabled": False,
            "igmp_snooping": False,
        }

        # Add VLAN settings
        if config.vlan_id > 1:
            payload["vlan_enabled"] = True
            payload["vlan"] = str(config.vlan_id)

        # Purpose-specific settings
        if config.purpose == "guest":
            payload["purpose"] = "guest"
            payload["network_isolation"] = True
        elif config.purpose == "iot" or config.network_isolation:
            payload["purpose"] = "corporate"
            payload["network_isolation"] = True

        if dry_run:
            print(f"  [DRY RUN] Would create: {config.name} (VLAN {config.vlan_id}) - {gateway_cidr}")
            return True

        url = f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf"

        try:
            headers = {"Content-Type": "application/json"}
            if self.csrf_token:
                headers["X-CSRF-Token"] = self.csrf_token

            response = self.session.post(url, json=payload, headers=headers)

            if response.status_code in [200, 201]:
                result = response.json()
                network_id = result.get("data", [{}])[0].get("_id", "unknown")
                self.created_networks.append({
                    "id": network_id,
                    "name": config.name,
                    "vlan": config.vlan_id
                })
                print(f"  OK: {config.name} (VLAN {config.vlan_id}) - {gateway_cidr}")
                return True
            else:
                print(f"  FAIL: {config.name} - {response.status_code}: {response.text[:100]}")
                return False

        except Exception as e:
            print(f"  ERROR: {config.name} - {e}")
            return False

    def delete_network(self, network_id: str, name: str) -> bool:
        """Delete a network by ID"""
        url = f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf/{network_id}"

        try:
            headers = {}
            if self.csrf_token:
                headers["X-CSRF-Token"] = self.csrf_token
            response = self.session.delete(url, headers=headers)
            if response.status_code == 200:
                print(f"  Deleted: {name}")
                return True
            else:
                print(f"  Failed to delete {name}: {response.status_code}")
                return False
        except Exception as e:
            print(f"  Error deleting {name}: {e}")
            return False

    def rollback(self):
        """Delete all networks created in this session"""
        if not self.created_networks:
            print("No networks to rollback")
            return

        print(f"\nRolling back {len(self.created_networks)} networks...")
        for net in reversed(self.created_networks):
            self.delete_network(net["id"], net["name"])
        self.created_networks = []
        print("Rollback complete")

    def rollback_all(self, prefix: str = "Unit-"):
        """Delete all networks matching prefix"""
        existing = self.get_existing_networks()
        to_delete = [n for n in existing if n.get("name", "").startswith(prefix)]

        if not to_delete:
            print(f"No networks found matching '{prefix}*'")
            return

        print(f"Found {len(to_delete)} networks to delete:")
        for n in to_delete:
            print(f"  - {n.get('name')} (VLAN {n.get('vlan', 'N/A')})")

        confirm = input("\nType 'DELETE' to confirm: ")
        if confirm != "DELETE":
            print("Aborted")
            return

        for n in to_delete:
            self.delete_network(n.get("_id"), n.get("name"))
        print("\nRollback complete")


def load_config(config_path: str) -> dict:
    """Load network configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


def config_to_networks(config: dict) -> List[NetworkConfig]:
    """Convert JSON config to NetworkConfig objects"""
    networks = []
    for net in config.get('networks', []):
        networks.append(NetworkConfig(
            name=net.get('name', ''),
            vlan_id=net.get('vlan_id', 0),
            subnet=net.get('subnet', ''),
            gateway=net.get('gateway', ''),
            dhcp_enabled=net.get('dhcp_enabled', True),
            dhcp_start=net.get('dhcp_start', ''),
            dhcp_stop=net.get('dhcp_stop', ''),
            dns_servers=net.get('dns_servers', []),
            purpose=net.get('purpose', 'corporate'),
            network_isolation=net.get('network_isolation', False)
        ))
    return networks


def interactive_deploy():
    """Interactive mode for deploying to UniFi Gateway"""
    print("=" * 60)
    print("Network Migration Toolkit - UniFi Gateway Deployer")
    print("=" * 60)
    print()
    print("Supported devices: UDM-Pro, UDM-SE, UDM-Pro-Max, UCG-Max, UCG-Ultra")
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
    networks = config_to_networks(config)

    print()
    print(f"Loaded: {config['metadata'].get('customer_name', 'Unknown')}")
    print(f"  Source: {config['metadata'].get('source_device', 'Unknown')}")
    print(f"  Networks: {len(networks)}")
    print()

    # Get UniFi Gateway connection details
    host = input("Enter UniFi Gateway IP address: ").strip()
    if not host:
        print("Gateway IP is required.")
        return

    username = input("Enter admin username [admin]: ").strip() or "admin"
    password = getpass.getpass("Enter admin password: ")

    print()
    print("Options:")
    print("  1. Deploy all networks")
    print("  2. Deploy infrastructure only (VLANs < 100)")
    print("  3. Deploy specific VLAN range")
    print("  4. Dry run (preview only)")
    print("  5. Rollback (delete Unit-* networks)")
    print()

    choice = input("Select option [4]: ").strip() or "4"

    # Filter networks based on choice
    if choice == "2":
        networks = [n for n in networks if n.vlan_id < 100]
        print(f"\nFiltered to {len(networks)} infrastructure networks")
    elif choice == "3":
        vlan_start = int(input("Enter start VLAN: ").strip() or "0")
        vlan_end = int(input("Enter end VLAN: ").strip() or "999")
        networks = [n for n in networks if vlan_start <= n.vlan_id <= vlan_end]
        print(f"\nFiltered to {len(networks)} networks (VLAN {vlan_start}-{vlan_end})")

    dry_run = choice == "4"
    rollback = choice == "5"

    # Connect and deploy
    deployer = UniFiDeployer(host, username, password)

    if not deployer.login():
        return

    try:
        if rollback:
            deployer.rollback_all()
            return

        print()
        print(f"{'[DRY RUN] ' if dry_run else ''}Deploying {len(networks)} networks...")
        print()

        success = 0
        failed = 0

        for i, net in enumerate(networks, 1):
            print(f"[{i:3}/{len(networks)}] {net.name}...")
            if deployer.create_network(net, dry_run=dry_run):
                success += 1
            else:
                failed += 1
            if not dry_run:
                time.sleep(0.3)  # Rate limit

        print()
        print("=" * 60)
        print(f"{'[DRY RUN] ' if dry_run else ''}Complete!")
        print(f"  Success: {success}")
        print(f"  Failed: {failed}")
        print("=" * 60)

        if not dry_run and failed > 0:
            if input("\nSome networks failed. Rollback? (y/N): ").lower() == 'y':
                deployer.rollback()

    except KeyboardInterrupt:
        print("\n\nInterrupted!")
        if deployer.created_networks and input("Rollback? (y/N): ").lower() == 'y':
            deployer.rollback()

    finally:
        deployer.logout()


if __name__ == '__main__':
    interactive_deploy()
