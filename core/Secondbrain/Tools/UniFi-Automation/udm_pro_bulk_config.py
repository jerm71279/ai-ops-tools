import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
UDM-Pro Bulk Network Configuration Script
Saint Annes Terrance - MikroTik to UDM-Pro Migration

Creates all 89 VLANs/networks via UniFi API

SECURITY: Credentials should be provided via environment variables, NOT command line args.
Command line passwords are visible in process lists and shell history.

Environment Variables:
    UNIFI_HOST      - UDM-Pro IP address (e.g., 192.168.1.1)
    UNIFI_USER      - Admin username
    UNIFI_PASSWORD  - Admin password (REQUIRED - never put in CLI!)
    UNIFI_SITE      - Site name (default: default)

Usage:
    # Set credentials securely
    export UNIFI_HOST=192.168.1.1
    export UNIFI_USER=admin
    export UNIFI_PASSWORD='yourpass'  # Use single quotes to avoid shell expansion

    # Preview what will be created (no changes)
    python3 udm_pro_bulk_config.py --dry-run

    # Create all networks
    python3 udm_pro_bulk_config.py

    # Create only Building 1
    python3 udm_pro_bulk_config.py --building 1

    # Delete all created networks (rollback)
    python3 udm_pro_bulk_config.py --rollback
"""

import argparse
import json
import os
import requests
import urllib3
import time
import sys
import getpass
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class NetworkConfig:
    """Network configuration data"""
    name: str
    vlan_id: int
    subnet: str
    gateway: str
    dhcp_start: str
    dhcp_stop: str
    purpose: str = "corporate"
    dns_servers: List[str] = field(default_factory=lambda: ["4.2.2.2", "8.8.8.8"])


class UDMProConfigurator:
    """UniFi Dream Machine Pro API Client"""

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
        self.created_networks = []  # Track for rollback

    def login(self) -> bool:
        """Authenticate with UDM-Pro"""
        print(f"Connecting to UDM-Pro at {self.host}...")

        login_url = f"{self.base_url}/api/auth/login"
        payload = {"username": self.username, "password": self.password}

        try:
            response = self.session.post(login_url, json=payload, timeout=10)

            # Get CSRF token from response headers or cookies
            self.csrf_token = response.headers.get('X-CSRF-Token') or response.headers.get('x-csrf-token')
            if not self.csrf_token:
                # Try getting from cookies
                self.csrf_token = self.session.cookies.get('csrf_token') or self.session.cookies.get('TOKEN')

            if response.status_code == 200:
                print("Successfully connected to UDM-Pro")
                if self.csrf_token:
                    print(f"CSRF token acquired")
                self.logged_in = True
                return True
            else:
                # Some UniFi versions return 403 on login but still set cookies
                # Check if we can access the API anyway
                test_url = f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf"
                test_response = self.session.get(test_url, timeout=10)
                if test_response.status_code == 200:
                    print("Connected to UDM-Pro (via session)")
                    self.logged_in = True
                    return True
                print(f"Login failed: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            print(f"ERROR: Cannot connect to {self.host}")
            print("Make sure UDM-Pro is reachable and you're on the same network")
            return False
        except Exception as e:
            print(f"Login error: {e}")
            return False

    def logout(self):
        """Logout from UDM-Pro"""
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

        # UniFi wants gateway IP in ip_subnet (e.g., "10.10.2.1/24")
        # config.subnet already has this format
        gateway_cidr = config.subnet

        payload = {
            "name": config.name,
            "purpose": config.purpose,
            "ip_subnet": gateway_cidr,
            "networkgroup": "LAN",
            "dhcpd_enabled": True,
            "dhcpd_start": config.dhcp_start,
            "dhcpd_stop": config.dhcp_stop,
            "dhcpd_dns_enabled": True,
            "dhcpd_dns_1": config.dns_servers[0] if config.dns_servers else "8.8.8.8",
            "dhcpd_dns_2": config.dns_servers[1] if len(config.dns_servers) > 1 else "8.8.4.4",
            "dhcpd_leasetime": 86400,
            "dhcpguard_enabled": False,
            "igmp_snooping": False,
        }

        # Add VLAN settings (skip for VLAN 1 which is default/native)
        if config.vlan_id != 1:
            payload["vlan_enabled"] = True
            payload["vlan"] = str(config.vlan_id)
        else:
            # VLAN 1 - skip creation as it conflicts with default LAN
            print(f"  SKIP: {config.name} (VLAN 1) - use existing Default network instead")
            return True

        # Purpose-specific settings
        if config.purpose == "guest":
            payload["purpose"] = "guest"
            payload["network_isolation"] = True
        elif config.purpose == "iot":
            payload["purpose"] = "corporate"
            payload["network_isolation"] = True

        if dry_run:
            print(f"  [DRY RUN] Would create: {config.name} (VLAN {config.vlan_id}) - {gateway_cidr}")
            return True

        url = f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf"

        try:
            # Include CSRF token if available
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
            # Include CSRF token for DELETE requests (required on modern firmware)
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


def get_saint_annes_networks() -> List[NetworkConfig]:
    """Return all Saint Annes Terrance network configurations"""

    networks = []

    # ========== INFRASTRUCTURE VLANs ==========
    networks.extend([
        NetworkConfig(
            name="MGMT", vlan_id=1, subnet="192.168.10.1/23", gateway="192.168.10.1",
            dhcp_start="192.168.10.25", dhcp_stop="192.168.11.253",
            purpose="corporate", dns_servers=["9.9.9.9", "8.8.8.8"]
        ),
        NetworkConfig(
            name="LAN", vlan_id=10, subnet="192.168.20.1/23", gateway="192.168.20.1",
            dhcp_start="192.168.20.10", dhcp_stop="192.168.21.250",
            purpose="corporate", dns_servers=["9.9.9.9", "8.8.8.8"]
        ),
        NetworkConfig(
            name="CAMERA", vlan_id=22, subnet="10.11.12.1/24", gateway="10.11.12.1",
            dhcp_start="10.11.12.10", dhcp_stop="10.11.12.254",
            purpose="iot", dns_servers=["9.9.9.9", "8.8.8.8"]
        ),
        NetworkConfig(
            name="GUEST", vlan_id=40, subnet="10.1.40.1/24", gateway="10.1.40.1",
            dhcp_start="10.1.40.20", dhcp_stop="10.1.40.254",
            purpose="guest", dns_servers=["9.9.9.9", "8.8.8.8"]
        ),
        NetworkConfig(
            name="CORP", vlan_id=50, subnet="172.16.13.1/24", gateway="172.16.13.1",
            dhcp_start="172.16.13.10", dhcp_stop="172.16.13.254",
            purpose="corporate", dns_servers=["9.9.9.9", "8.8.8.8"]
        ),
    ])

    # ========== BUILDING 1: Units 101-116 (13 VLANs) ==========
    building1 = [
        (101, "10.10.2"), (102, "10.10.3"), (103, "10.10.4"), (104, "10.10.5"),
        (105, "10.10.6"), (106, "10.10.7"), (107, "10.10.8"), (108, "10.10.9"),
        (109, "10.10.10"), (110, "10.10.11"), (112, "10.10.12"), (114, "10.10.13"),
        (116, "10.10.15"),
    ]
    for vlan, net in building1:
        networks.append(NetworkConfig(
            name=f"Unit-{vlan}", vlan_id=vlan, subnet=f"{net}.1/24", gateway=f"{net}.1",
            dhcp_start=f"{net}.10", dhcp_stop=f"{net}.200"
        ))

    # ========== BUILDING 2: Units 201-227 (18 VLANs) ==========
    building2 = [
        (201, "10.10.16"), (202, "10.10.17"), (203, "10.10.18"), (204, "10.10.19"),
        (205, "10.10.20"), (206, "10.10.21"), (207, "10.10.22"), (208, "10.10.23"),
        (209, "10.10.24"), (210, "10.10.25"), (211, "10.10.26"), (213, "10.10.27"),
        (214, "10.10.28"), (216, "10.10.29"), (217, "10.10.30"), (218, "10.10.31"),
        (219, "10.10.32"), (220, "10.10.33"), (221, "10.10.34"), (223, "10.10.35"),
        (225, "10.10.36"), (227, "10.10.37"),
    ]
    for vlan, net in building2:
        name = "Unit-217-Office" if vlan == 217 else f"Unit-{vlan}"
        networks.append(NetworkConfig(
            name=name, vlan_id=vlan, subnet=f"{net}.1/24", gateway=f"{net}.1",
            dhcp_start=f"{net}.10", dhcp_stop=f"{net}.200"
        ))

    # ========== BUILDING 3: Units 301-327 (18 VLANs) ==========
    building3 = [
        (301, "10.10.38"), (302, "10.10.39"), (303, "10.10.40"), (304, "10.10.41"),
        (305, "10.10.42"), (306, "10.10.43"), (307, "10.10.44"), (308, "10.10.45"),
        (309, "10.10.46"), (310, "10.10.47"), (311, "10.10.48"), (312, "10.10.49"),
        (313, "10.10.50"), (314, "10.10.51"), (315, "10.10.52"), (316, "10.10.53"),
        (317, "10.10.54"), (318, "10.10.55"), (319, "10.10.56"), (320, "10.10.57"),
        (321, "10.10.58"), (323, "10.10.59"), (325, "10.10.60"), (327, "10.10.61"),
    ]
    for vlan, net in building3:
        networks.append(NetworkConfig(
            name=f"Unit-{vlan}", vlan_id=vlan, subnet=f"{net}.1/24", gateway=f"{net}.1",
            dhcp_start=f"{net}.10", dhcp_stop=f"{net}.200"
        ))

    # ========== BUILDING 4: Units 401-427 (19 VLANs) ==========
    building4 = [
        (401, "10.10.62"), (402, "10.10.63"), (403, "10.10.64"), (404, "10.10.67"),  # 404 was duplicate, fixed
        (405, "10.10.65"), (406, "10.10.106"), (407, "10.10.66"), (408, "10.10.108"),
        (409, "10.10.68"), (410, "10.10.69"), (411, "10.10.72"), (412, "10.10.73"),
        (413, "10.10.113"), (414, "10.10.75"), (415, "10.10.76"), (416, "10.10.77"),
        (417, "10.10.78"), (418, "10.10.79"), (419, "10.10.80"), (420, "10.10.81"),
        (421, "10.10.82"), (423, "10.10.83"), (425, "10.10.84"), (427, "10.10.85"),
    ]
    for vlan, net in building4:
        networks.append(NetworkConfig(
            name=f"Unit-{vlan}", vlan_id=vlan, subnet=f"{net}.1/24", gateway=f"{net}.1",
            dhcp_start=f"{net}.10", dhcp_stop=f"{net}.200"
        ))

    # ========== BUILDING 5: Units 509-527 (16 VLANs) ==========
    building5 = [
        (509, "10.10.86"), (510, "10.10.87"), (511, "10.10.88"), (512, "10.10.89"),
        (513, "10.10.90"), (514, "10.10.91"), (515, "10.10.92"), (516, "10.10.93"),
        (517, "10.10.94"), (518, "10.10.95"), (519, "10.10.96"), (520, "10.10.97"),
        (521, "10.10.98"), (523, "10.10.99"), (525, "10.10.100"), (527, "10.10.101"),
    ]
    for vlan, net in building5:
        networks.append(NetworkConfig(
            name=f"Unit-{vlan}", vlan_id=vlan, subnet=f"{net}.1/24", gateway=f"{net}.1",
            dhcp_start=f"{net}.10", dhcp_stop=f"{net}.200"
        ))

    return networks


def main():
    parser = argparse.ArgumentParser(
        description="Bulk configure UDM-Pro networks for Saint Annes Terrance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables (RECOMMENDED - more secure than CLI args):
  UNIFI_HOST      UDM-Pro IP address
  UNIFI_USER      Admin username
  UNIFI_PASSWORD  Admin password

Examples:
  # Set credentials via environment (secure)
  export UNIFI_HOST=192.168.1.1 UNIFI_USER=admin UNIFI_PASSWORD='pass'
  python3 udm_pro_bulk_config.py --dry-run

  # Preview (no changes)
  python3 udm_pro_bulk_config.py --dry-run

  # Create all 89 networks
  python3 udm_pro_bulk_config.py

  # Create only Building 2
  python3 udm_pro_bulk_config.py --building 2

  # Delete all Unit-* networks
  python3 udm_pro_bulk_config.py --rollback
        """
    )
    # Host/user can be passed via CLI or env var; password ONLY via env var or prompt
    parser.add_argument("--host", default=os.getenv("UNIFI_HOST"),
                        help="UDM-Pro IP address (or set UNIFI_HOST env var)")
    parser.add_argument("--user", "-u", default=os.getenv("UNIFI_USER"),
                        help="Admin username (or set UNIFI_USER env var)")
    parser.add_argument("--site", default=os.getenv("UNIFI_SITE", "default"),
                        help="UniFi site name (default: default)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")
    parser.add_argument("--rollback", action="store_true", help="Delete Unit-* networks")
    parser.add_argument("--building", type=int, choices=[1, 2, 3, 4, 5],
                        help="Only configure specific building (1-5)")
    parser.add_argument("--infra-only", action="store_true",
                        help="Only create infrastructure VLANs (MGMT, LAN, CAMERA, GUEST, CORP)")

    args = parser.parse_args()

    # Validate required credentials
    if not args.host:
        print("ERROR: Host required. Set UNIFI_HOST env var or use --host")
        sys.exit(1)
    if not args.user:
        print("ERROR: Username required. Set UNIFI_USER env var or use --user")
        sys.exit(1)

    # Get password from environment (secure) or prompt (interactive)
    password = os.getenv("UNIFI_PASSWORD")
    if not password:
        if sys.stdin.isatty():
            password = getpass.getpass(f"Password for {args.user}@{args.host}: ")
        else:
            print("ERROR: Password required. Set UNIFI_PASSWORD env var")
            print("       (Never pass passwords via command line - visible in ps/history)")
            sys.exit(1)

    # Get network configurations
    networks = get_saint_annes_networks()

    # Filter options
    if args.infra_only:
        networks = [n for n in networks if n.vlan_id < 100]
    elif args.building:
        building_ranges = {
            1: range(100, 120),
            2: range(200, 230),
            3: range(300, 330),
            4: range(400, 430),
            5: range(500, 530),
        }
        vlan_range = building_ranges.get(args.building, range(0))
        networks = [n for n in networks if n.vlan_id in vlan_range]

    # Display banner
    print("=" * 60)
    print("Saint Annes Terrance - UDM-Pro Bulk Network Configuration")
    print("=" * 60)
    print(f"Target:   {args.host}")
    print(f"Networks: {len(networks)}")
    print(f"Mode:     {'DRY RUN (no changes)' if args.dry_run else 'LIVE'}")
    if args.building:
        print(f"Filter:   Building {args.building} only")
    if args.infra_only:
        print(f"Filter:   Infrastructure VLANs only")
    print("=" * 60)

    # Dry run - just print
    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")
        for net in networks:
            print(f"  {net.name:20} VLAN {net.vlan_id:4}  {net.subnet:18}  DHCP: {net.dhcp_start}-{net.dhcp_stop.split('.')[-1]}")
        print(f"\nTotal: {len(networks)} networks")
        return

    # Connect to UDM-Pro
    udm = UDMProConfigurator(args.host, args.user, password, args.site)

    if not udm.login():
        sys.exit(1)

    try:
        if args.rollback:
            print("\nFinding networks to delete...")
            existing = udm.get_existing_networks()
            to_delete = [n for n in existing if
                         n.get("name", "").startswith("Unit-") or
                         n.get("name") in ["MGMT", "LAN", "CAMERA", "GUEST", "CORP"]]

            if not to_delete:
                print("No matching networks found")
                return

            print(f"Found {len(to_delete)} networks:")
            for n in to_delete:
                print(f"  - {n.get('name')} (VLAN {n.get('vlan', 'N/A')})")

            confirm = input("\nType 'DELETE' to confirm: ")
            if confirm != "DELETE":
                print("Aborted")
                return

            for n in to_delete:
                udm.delete_network(n.get("_id"), n.get("name"))
            print("\nRollback complete")
            return

        # Create networks
        print(f"\nCreating {len(networks)} networks...\n")

        success = 0
        failed = 0

        for i, net in enumerate(networks, 1):
            print(f"[{i:2}/{len(networks)}] {net.name}...")
            if udm.create_network(net):
                success += 1
            else:
                failed += 1
            time.sleep(0.3)  # Rate limit

        print("\n" + "=" * 60)
        print(f"Complete! Success: {success}, Failed: {failed}")
        print("=" * 60)

        if failed > 0:
            print("\nSome networks failed.")
            if input("Rollback created networks? (y/N): ").lower() == 'y':
                udm.rollback()

    except KeyboardInterrupt:
        print("\n\nInterrupted!")
        if udm.created_networks and input("Rollback? (y/N): ").lower() == 'y':
            udm.rollback()

    finally:
        udm.logout()


if __name__ == "__main__":
    main()
