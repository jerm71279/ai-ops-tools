import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Find the correct UniFi Zone API endpoint.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("-u", "--user", required=True)
    parser.add_argument("-p", "--password", required=True)
    args = parser.parse_args()

    session = requests.Session()
    session.verify = False
    base_url = f"https://{args.host}"

    # Login
    print("Logging in...")
    resp = session.post(f"{base_url}/api/auth/login",
                        json={"username": args.user, "password": args.password})
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code}")
        return

    csrf = resp.headers.get('X-CSRF-Token') or session.cookies.get('csrf_token')
    print(f"Login OK. CSRF: {csrf[:20] if csrf else 'none'}...")

    # Try different zone endpoints
    endpoints = [
        "/proxy/network/v2/api/site/default/firewall-zone",
        "/proxy/network/v2/api/site/default/zones",
        "/proxy/network/api/s/default/rest/firewallzone",
        "/proxy/network/api/s/default/rest/zone",
        "/proxy/network/api/s/default/rest/routing",
        "/api/network/v2/site/default/firewall-zone",
        "/proxy/network/v2/api/site/default/firewall/zone",
        "/proxy/network/v2/api/site/default/setting/firewall",
        "/proxy/network/api/s/default/rest/firewallgroup",
        "/proxy/network/api/s/default/rest/firewallrule",
        "/proxy/network/api/s/default/stat/routing",
    ]

    print("\nTrying endpoints...")
    print("-" * 70)

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            resp = session.get(url)
            status = resp.status_code
            if status == 200:
                data = resp.json() if resp.text else {}
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    count = len(data.get('data', data.get('zones', [])))
                elif isinstance(data, list):
                    keys = f"list[{len(data)}]"
                    count = len(data)
                else:
                    keys = type(data).__name__
                    count = 0
                print(f"✓ {status} {endpoint}")
                print(f"       Response: {keys}, count={count}")
            else:
                print(f"✗ {status} {endpoint}")
        except Exception as e:
            print(f"✗ ERR {endpoint} - {e}")

    # Also check networkconf for zone info
    print("\n" + "-" * 70)
    print("Checking if zone info is in network config...")
    resp = session.get(f"{base_url}/proxy/network/api/s/default/rest/networkconf")
    if resp.status_code == 200:
        networks = resp.json().get('data', [])
        for net in networks[:3]:
            name = net.get('name')
            zone = net.get('zone', net.get('firewall_zone', 'not set'))
            print(f"  {name}: zone={zone}")

        # Find zone-related keys
        if networks:
            sample = networks[0]
            zone_keys = [k for k in sample.keys() if 'zone' in k.lower()]
            print(f"\n  Zone-related keys in network: {zone_keys}")

    session.post(f"{base_url}/api/auth/logout")
    print("\nDone.")

if __name__ == "__main__":
    main()
