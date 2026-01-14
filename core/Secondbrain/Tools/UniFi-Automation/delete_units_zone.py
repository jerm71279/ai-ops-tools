import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Delete the Units zone from UniFi Zone-Based Firewall via API.
Networks in the zone will return to Internal zone.

Usage:
  python3 delete_units_zone.py --host <UDM-IP> -u <user> -p <pass> --dry-run
  python3 delete_units_zone.py --host <UDM-IP> -u <user> -p <pass>
"""

import argparse
import requests
import urllib3
import sys

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
        try:
            self.session.post(f"{self.base_url}/api/auth/logout")
        except:
            pass

    def get_zones(self) -> list:
        """Get all firewall zones."""
        url = f"{self.base_url}/proxy/network/v2/api/site/{self.site}/firewall/zone"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get zones: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error getting zones: {e}")
            return []

    def delete_zone(self, zone_id: str) -> bool:
        """Delete a firewall zone by ID."""
        url = f"{self.base_url}/proxy/network/v2/api/site/{self.site}/firewall/zone/{zone_id}"

        headers = {"Content-Type": "application/json"}
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token

        try:
            response = self.session.delete(url, headers=headers)
            if response.status_code in [200, 204]:
                return True
            else:
                print(f"Delete failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Delete error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Delete Units zone from UniFi")
    parser.add_argument("--host", required=True, help="UDM-Pro IP address")
    parser.add_argument("-u", "--user", required=True, help="Admin username")
    parser.add_argument("-p", "--password", required=True, help="Admin password")
    parser.add_argument("--site", default="default", help="Site name")
    parser.add_argument("--dry-run", action="store_true", help="Show zone info without deleting")
    parser.add_argument("--zone-name", default="Units", help="Zone name to delete (default: Units)")
    args = parser.parse_args()

    client = UDMProClient(args.host, args.user, args.password, args.site)

    print("=" * 60)
    print("UniFi Zone Deletion Tool")
    print("=" * 60)

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made\n")

    # Login
    if not client.login():
        print("Failed to authenticate.")
        sys.exit(1)

    try:
        # Get all zones
        print("\nFetching firewall zones...")
        zones = client.get_zones()

        if not zones:
            print("No zones found.")
            sys.exit(1)

        print(f"\nFound {len(zones)} zones:")
        print("-" * 50)

        target_zone = None
        for zone in zones:
            zone_name = zone.get('name', 'Unknown')
            zone_id = zone.get('_id', zone.get('id', 'Unknown'))
            zone_type = zone.get('zone_type', zone.get('type', ''))
            network_ids = zone.get('network_ids', zone.get('networks', []))

            # Show info
            print(f"  {zone_name}")
            print(f"    ID: {zone_id}")
            print(f"    Type: {zone_type}")
            print(f"    Networks: {len(network_ids) if isinstance(network_ids, list) else network_ids}")
            print()

            if zone_name.lower() == args.zone_name.lower():
                target_zone = zone

        print("-" * 50)

        if not target_zone:
            print(f"\nZone '{args.zone_name}' not found.")
            print("Available zones listed above.")
            sys.exit(1)

        zone_id = target_zone.get('_id', target_zone.get('id'))
        zone_name = target_zone.get('name')

        if args.dry_run:
            print(f"\nWOULD DELETE: '{zone_name}' (ID: {zone_id})")
            print("Networks would return to their default zone.")
        else:
            print(f"\nDeleting '{zone_name}' zone...", end=" ")
            if client.delete_zone(zone_id):
                print("OK")
                print("\nUnit networks have been moved back to Internal zone.")
            else:
                print("FAILED")
                sys.exit(1)

    finally:
        client.logout()
        print("\nDone.")


if __name__ == "__main__":
    main()
