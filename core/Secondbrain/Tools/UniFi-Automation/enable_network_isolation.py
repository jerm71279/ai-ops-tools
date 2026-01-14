import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Enable Network Isolation on all Unit-* networks via UniFi API.
This prevents devices within the same VLAN from communicating with each other.

Usage:
  python3 enable_network_isolation.py --host <UDM-IP> -u <user> -p <pass> --dry-run
  python3 enable_network_isolation.py --host <UDM-IP> -u <user> -p <pass>
"""

import argparse
import requests
import urllib3
import sys
import time

# Suppress SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class UDMProClient:
    def __init__(self, host: str, username: str, password: str, site: str = "default"):
        self.base_url = f"https://{host}"
        self.site = site
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False
        self.csrf_token = None

    def login(self) -> bool:
        """Authenticate to UDM-Pro and get CSRF token."""
        url = f"{self.base_url}/api/auth/login"
        payload = {"username": self.username, "password": self.password}

        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                # Extract CSRF token from headers or cookies
                self.csrf_token = response.headers.get('X-CSRF-Token')
                if not self.csrf_token:
                    self.csrf_token = self.session.cookies.get('csrf_token')
                if not self.csrf_token:
                    self.csrf_token = self.session.cookies.get('TOKEN')
                print(f"Login successful. CSRF token: {'found' if self.csrf_token else 'not found'}")
                return True
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Login error: {e}")
            return False

    def logout(self):
        """Logout from UDM-Pro."""
        url = f"{self.base_url}/api/auth/logout"
        try:
            self.session.post(url)
        except:
            pass

    def get_networks(self) -> list:
        """Get all networks from UDM-Pro."""
        url = f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                print(f"Failed to get networks: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting networks: {e}")
            return []

    def update_network(self, network_id: str, updates: dict) -> bool:
        """Update a network configuration."""
        url = f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf/{network_id}"

        headers = {"Content-Type": "application/json"}
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token

        try:
            response = self.session.put(url, json=updates, headers=headers)
            if response.status_code == 200:
                return True
            else:
                print(f"  Update failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"  Update error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Enable network isolation on Unit-* networks")
    parser.add_argument("--host", required=True, help="UDM-Pro IP address")
    parser.add_argument("-u", "--user", required=True, help="Admin username")
    parser.add_argument("-p", "--password", required=True, help="Admin password")
    parser.add_argument("--site", default="default", help="Site name (default: default)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--disable", action="store_true", help="Disable isolation instead of enabling")
    args = parser.parse_args()

    client = UDMProClient(args.host, args.user, args.password, args.site)

    print("=" * 60)
    print("UniFi Network Isolation Updater")
    print("=" * 60)

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made\n")

    # Login
    if not client.login():
        print("Failed to authenticate. Check credentials.")
        sys.exit(1)

    try:
        # Get all networks
        print("\nFetching networks...")
        networks = client.get_networks()
        print(f"Found {len(networks)} total networks\n")

        # Filter for Unit-* networks
        unit_networks = [n for n in networks if n.get('name', '').startswith('Unit-')]
        print(f"Found {len(unit_networks)} Unit-* networks\n")

        if not unit_networks:
            print("No Unit-* networks found. Nothing to do.")
            return

        # Track results
        updated = 0
        skipped = 0
        failed = 0

        target_value = not args.disable  # True to enable, False to disable
        action = "Disabling" if args.disable else "Enabling"

        print(f"{action} network isolation on Unit-* networks:\n")
        print("-" * 60)

        for network in sorted(unit_networks, key=lambda x: x.get('name', '')):
            name = network.get('name', 'Unknown')
            network_id = network.get('_id')
            current_isolation = network.get('network_isolation', False)

            if current_isolation == target_value:
                print(f"  SKIP: {name} - already {'enabled' if target_value else 'disabled'}")
                skipped += 1
                continue

            if args.dry_run:
                print(f"  WOULD UPDATE: {name} - isolation: {current_isolation} → {target_value}")
                updated += 1
            else:
                print(f"  Updating: {name}...", end=" ")

                # Prepare update payload - include required fields
                update_payload = {
                    "_id": network_id,
                    "network_isolation": target_value
                }

                if client.update_network(network_id, update_payload):
                    print("OK")
                    updated += 1
                else:
                    print("FAILED")
                    failed += 1

                # Small delay to avoid rate limiting
                time.sleep(0.2)

        print("-" * 60)
        print(f"\nSummary:")
        print(f"  {'Would update' if args.dry_run else 'Updated'}: {updated}")
        print(f"  Skipped (already set): {skipped}")
        if not args.dry_run:
            print(f"  Failed: {failed}")

    finally:
        client.logout()
        print("\nDone.")


if __name__ == "__main__":
    main()
