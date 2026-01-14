import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Fill Network Checklist for City of Spanish Fort
"""
import os
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

TEMPLATE_PATH = Path("/home/mavrick/Projects/network_install_workflow_checklist.md")

# SharePoint configuration for City of Spanish Fort
CUSTOMER_NAME = "City of Spanish Fort"
FOLDER_PATH = "City of Spanish Fort/Technical Docs"


class SharePointClient:
    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.token = self._get_token()
        self.base_url = "https://graph.microsoft.com/v1.0"

    def _get_token(self):
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        response = requests.post(url, data=data)
        return response.json().get('access_token')

    def get_site_and_drive(self):
        """Get OberaConnect Technical site and Documents drive IDs"""
        headers = {'Authorization': f'Bearer {self.token}'}

        # Get sites
        resp = requests.get(f"{self.base_url}/sites?search=*", headers=headers)
        sites = resp.json().get('value', [])

        for site in sites:
            if site.get('displayName') == 'OberaConnect Technical':
                site_id = site['id']

                # Get drives
                resp = requests.get(f"{self.base_url}/sites/{site_id}/drives", headers=headers)
                drives = resp.json().get('value', [])

                for drive in drives:
                    if drive['name'] == 'Documents':
                        return site_id, drive['id']

        return None, None

    def upload_file(self, site_id, drive_id, folder_path, filename, content):
        """Upload file to SharePoint"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/octet-stream'
        }
        upload_path = f"{folder_path}/{filename}"
        url = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root:/{upload_path}:/content"

        response = requests.put(url, headers=headers, data=content)
        return response.status_code in [200, 201]


def prompt(field, default=""):
    """Simple prompt with optional default"""
    if default:
        val = input(f"{field} [{default}]: ").strip()
        return val if val else default
    return input(f"{field}: ").strip()


def main():
    print("=" * 60)
    print(f"Network Installation Checklist - {CUSTOMER_NAME}")
    print("=" * 60)

    # Pre-filled from SharePoint
    info = {
        'customer_name': CUSTOMER_NAME,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'num_users': '54-56',  # Based on phone count from VoIP bid
        'voip_required': 'Yes',  # Active VoIP project
    }

    print("\n--- Pre-filled from SharePoint ---")
    print(f"  Number of Users: {info['num_users']} (from VoIP bid)")
    print(f"  VoIP Required: {info['voip_required']} (active project)")
    print(f"  IT Contractor: Computer Backup, Inc.")
    print(f"  Site Survey: Oct 10, 2024 (photos on file)")

    print("\n--- Project Info ---")
    info['project_manager'] = prompt("Project Manager/Engineer")
    info['site_address'] = prompt("Site Address", "Spanish Fort, AL")
    info['contact_name'] = prompt("Primary Contact Name")
    info['contact_email'] = prompt("Contact Email")
    info['contact_phone'] = prompt("Contact Phone")

    print("\n--- Current Network ---")
    info['current_isp'] = prompt("Current ISP")
    info['internet_speed'] = prompt("Internet Speed (e.g., 100/100 Mbps)")
    info['num_users'] = prompt("Number of Users", info['num_users'])
    info['num_devices'] = prompt("Estimated Number of Devices")
    info['current_router'] = prompt("Current Router/Firewall")
    info['current_switches'] = prompt("Current Switches")
    info['current_aps'] = prompt("Current Access Points")

    print("\n--- Requirements ---")
    info['vlans_needed'] = prompt("VLANs Needed", "Data, Voice, Guest, IoT, Security")
    info['guest_network'] = prompt("Guest Network Required", "Yes")
    info['voip_required'] = prompt("VoIP Required", info['voip_required'])
    info['vpn_required'] = prompt("VPN Required", "Yes")

    print("\n--- Recommended Equipment ---")
    info['recommended_router'] = prompt("Recommended Router/Firewall", "SonicWall TZ")
    info['recommended_switches'] = prompt("Recommended Switches")
    info['recommended_aps'] = prompt("Recommended Access Points", "Ubiquiti UniFi")

    print("\n--- Notes ---")
    info['notes'] = prompt("Additional Notes (optional)", "IT Contractor: Computer Backup, Inc. Site survey completed Oct 10, 2024.")

    # Build the checklist
    template = TEMPLATE_PATH.read_text()

    header = f"""# Network Installation Checklist
## Customer: {info['customer_name']}

**Date Created:** {info['date']}
**Project Manager:** {info['project_manager']}
**Site Address:** {info['site_address']}
**Contact:** {info['contact_name']} | {info['contact_email']} | {info['contact_phone']}

---

## Project Overview

### Current Network
- **ISP:** {info['current_isp']}
- **Internet Speed:** {info['internet_speed']}
- **Number of Users:** {info['num_users']}
- **Estimated Devices:** {info['num_devices']}

### Existing Equipment
- **Router/Firewall:** {info['current_router']}
- **Switches:** {info['current_switches']}
- **Access Points:** {info['current_aps']}

### Requirements
- **VLANs Needed:** {info['vlans_needed']}
- **Guest Network:** {info['guest_network']}
- **VoIP:** {info['voip_required']}
- **VPN:** {info['vpn_required']}

### Recommended Equipment
- **Router/Firewall:** {info['recommended_router']}
- **Switches:** {info['recommended_switches']}
- **Access Points:** {info['recommended_aps']}

### Notes
{info.get('notes', '') or 'None'}

---

"""

    # Remove original title
    template = re.sub(r'^# Network Installation Workflow Checklist\n*', '', template)
    filled = header + template

    # Preview
    print("\n" + "=" * 60)
    print("Generated checklist preview:")
    print("=" * 60)
    for line in filled.split('\n')[:40]:
        print(line)
    print("\n... (checklist continues with all phases)")

    # Save
    print("\n" + "=" * 60)
    save = input("Upload to SharePoint? (y/n): ").strip().lower()

    if save == 'y':
        sp = SharePointClient()
        site_id, drive_id = sp.get_site_and_drive()

        if site_id and drive_id:
            filename = f"Network_Checklist_{info['date']}.md"
            content = filled.encode('utf-8')

            if sp.upload_file(site_id, drive_id, FOLDER_PATH, filename, content):
                print(f"\nUploaded to: {FOLDER_PATH}/{filename}")
            else:
                print("\nUpload failed")
        else:
            print("\nCouldn't find SharePoint site/drive")

    # Always save local copy
    local_path = Path(f"/home/mavrick/Projects/Secondbrain/output/Network_Checklist_Spanish_Fort_{info['date']}.md")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(filled)
    print(f"Local copy: {local_path}")


if __name__ == "__main__":
    main()
