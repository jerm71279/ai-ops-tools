import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Network Installation Checklist Filler
Pulls customer data from SharePoint, prompts for missing info, saves to customer folder
"""
import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

# Template path
TEMPLATE_PATH = Path("/home/mavrick/Projects/network_install_workflow_checklist.md")


class SharePointClient:
    """SharePoint client using Microsoft Graph API"""

    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.token = None
        self.base_url = "https://graph.microsoft.com/v1.0"

        if all([self.tenant_id, self.client_id, self.client_secret]):
            self.token = self._get_access_token()
        else:
            print("ERROR: Azure credentials not configured in .env")

    def _get_access_token(self) -> Optional[str]:
        """Get OAuth token from Microsoft"""
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }

        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return response.json()['access_token']
        except Exception as e:
            print(f"Failed to get access token: {e}")
            return None

    def _request(self, endpoint: str, method: str = 'GET', **kwargs) -> Optional[Dict]:
        """Make authenticated request to Graph API"""
        if not self.token:
            return None

        headers = {'Authorization': f'Bearer {self.token}'}
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except Exception as e:
            print(f"API request failed: {e}")
            return None

    def list_sites(self) -> List[Dict]:
        """List all SharePoint sites"""
        result = self._request("/sites?search=*")
        return result.get('value', []) if result else []

    def get_site_drives(self, site_id: str) -> List[Dict]:
        """Get document libraries for a site"""
        result = self._request(f"/sites/{site_id}/drives")
        return result.get('value', []) if result else []

    def list_folders(self, site_id: str, drive_id: str, path: str = "") -> List[Dict]:
        """List folders in a drive"""
        if path:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/root:/{path}:/children"
        else:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/root/children"

        result = self._request(endpoint)
        items = result.get('value', []) if result else []
        return [item for item in items if 'folder' in item]

    def list_files(self, site_id: str, drive_id: str, path: str = "") -> List[Dict]:
        """List files in a folder"""
        if path:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/root:/{path}:/children"
        else:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/root/children"

        result = self._request(endpoint)
        items = result.get('value', []) if result else []
        return [item for item in items if 'file' in item]

    def download_file(self, site_id: str, drive_id: str, file_path: str) -> Optional[bytes]:
        """Download a file from SharePoint"""
        if not self.token:
            return None

        # Get download URL
        endpoint = f"/sites/{site_id}/drives/{drive_id}/root:/{file_path}"
        result = self._request(endpoint)

        if result and '@microsoft.graph.downloadUrl' in result:
            download_url = result['@microsoft.graph.downloadUrl']
            response = requests.get(download_url)
            if response.status_code == 200:
                return response.content
        return None

    def upload_file(self, site_id: str, drive_id: str, folder_path: str,
                   filename: str, content: bytes) -> bool:
        """Upload a file to SharePoint"""
        if not self.token:
            return False

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/octet-stream'
        }

        # Build the upload path
        if folder_path:
            upload_path = f"{folder_path}/{filename}"
        else:
            upload_path = filename

        url = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root:/{upload_path}:/content"

        try:
            response = requests.put(url, headers=headers, data=content)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Upload failed: {e}")
            return False

    def search_files(self, site_id: str, drive_id: str, query: str) -> List[Dict]:
        """Search for files in a drive"""
        result = self._request(f"/sites/{site_id}/drives/{drive_id}/root/search(q='{query}')")
        return result.get('value', []) if result else []


def select_from_list(items: List, prompt: str, display_key: str = None) -> Optional[int]:
    """Display numbered list and get user selection"""
    if not items:
        print("No items to select from")
        return None

    print(f"\n{prompt}")
    print("-" * 40)

    for i, item in enumerate(items, 1):
        if display_key:
            display = item.get(display_key, str(item))
        else:
            display = str(item)
        print(f"  {i}. {display}")

    print()
    while True:
        try:
            choice = input("Enter number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return idx
            print("Invalid selection")
        except ValueError:
            print("Please enter a number")


def prompt_for_value(field_name: str, default: str = "", required: bool = False) -> str:
    """Prompt user for a value"""
    if default:
        prompt = f"{field_name} [{default}]: "
    else:
        prompt = f"{field_name}: "

    while True:
        value = input(prompt).strip()
        if not value and default:
            return default
        if not value and required:
            print("This field is required")
            continue
        return value


def gather_customer_info(sp_client: SharePointClient, customer_name: str,
                        site_id: str, drive_id: str, folder_path: str) -> Dict:
    """Gather customer information from SharePoint and prompts"""

    info = {
        'customer_name': customer_name,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'project_manager': '',
        'site_address': '',
        'contact_name': '',
        'contact_email': '',
        'contact_phone': '',

        # Network specifics
        'current_isp': '',
        'internet_speed': '',
        'num_users': '',
        'num_devices': '',

        # Existing equipment
        'current_router': '',
        'current_switches': '',
        'current_aps': '',

        # Requirements
        'vlans_needed': '',
        'guest_network': 'Yes',
        'voip_required': 'No',
        'vpn_required': 'No',

        # Recommended equipment
        'recommended_router': '',
        'recommended_switches': '',
        'recommended_aps': '',

        # Schedule
        'discovery_date': '',
        'install_date': '',
    }

    print(f"\n{'='*60}")
    print(f"Network Installation Checklist for: {customer_name}")
    print(f"{'='*60}")

    # Try to find existing documentation in SharePoint
    print("\nSearching for existing customer documentation...")

    files = sp_client.list_files(site_id, drive_id, folder_path)

    # Look for network-related docs
    network_docs = [f for f in files if any(kw in f['name'].lower()
                   for kw in ['network', 'config', 'topology', 'diagram', 'survey'])]

    if network_docs:
        print(f"\nFound {len(network_docs)} relevant documents:")
        for doc in network_docs:
            print(f"  - {doc['name']}")

    # Prompt for information
    print("\n--- Customer Information ---")
    info['project_manager'] = prompt_for_value("Project Manager/Engineer")
    info['site_address'] = prompt_for_value("Site Address")
    info['contact_name'] = prompt_for_value("Primary Contact Name")
    info['contact_email'] = prompt_for_value("Contact Email")
    info['contact_phone'] = prompt_for_value("Contact Phone")

    print("\n--- Current Network ---")
    info['current_isp'] = prompt_for_value("Current ISP")
    info['internet_speed'] = prompt_for_value("Internet Speed (e.g., 100/100 Mbps)")
    info['num_users'] = prompt_for_value("Number of Users")
    info['num_devices'] = prompt_for_value("Estimated Number of Devices")
    info['current_router'] = prompt_for_value("Current Router/Firewall")
    info['current_switches'] = prompt_for_value("Current Switches")
    info['current_aps'] = prompt_for_value("Current Access Points")

    print("\n--- Requirements ---")
    info['vlans_needed'] = prompt_for_value("VLANs Needed (e.g., Data, Voice, Guest, IoT)")
    info['guest_network'] = prompt_for_value("Guest Network Required", "Yes")
    info['voip_required'] = prompt_for_value("VoIP Required", "No")
    info['vpn_required'] = prompt_for_value("VPN Required", "No")

    print("\n--- Recommended Equipment ---")
    info['recommended_router'] = prompt_for_value("Recommended Router/Firewall")
    info['recommended_switches'] = prompt_for_value("Recommended Switches")
    info['recommended_aps'] = prompt_for_value("Recommended Access Points")

    print("\n--- Schedule ---")
    info['discovery_date'] = prompt_for_value("Discovery/Survey Date")
    info['install_date'] = prompt_for_value("Planned Installation Date")

    return info


def fill_checklist(info: Dict) -> str:
    """Fill the checklist template with customer information"""

    # Read template
    template = TEMPLATE_PATH.read_text()

    # Add customer header
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

### Schedule
- **Discovery Date:** {info['discovery_date']}
- **Installation Date:** {info['install_date']}

---

"""

    # Remove the original title from template (we replaced it)
    template = re.sub(r'^# Network Installation Workflow Checklist\n*', '', template)

    return header + template


def main():
    print("=" * 60)
    print("Network Installation Checklist Filler")
    print("=" * 60)

    # Initialize SharePoint client
    sp_client = SharePointClient()

    if not sp_client.token:
        print("\nFailed to connect to SharePoint. Check your Azure credentials.")
        return

    print("\nConnected to SharePoint")

    # List sites
    sites = sp_client.list_sites()
    if not sites:
        print("No SharePoint sites found")
        return

    # Select site
    site_idx = select_from_list(sites, "Select SharePoint Site:", 'displayName')
    if site_idx is None:
        return

    site = sites[site_idx]
    site_id = site['id']
    print(f"\nSelected: {site['displayName']}")

    # Get document libraries
    drives = sp_client.get_site_drives(site_id)
    if not drives:
        print("No document libraries found")
        return

    # Select drive
    drive_idx = select_from_list(drives, "Select Document Library:", 'name')
    if drive_idx is None:
        return

    drive = drives[drive_idx]
    drive_id = drive['id']
    print(f"\nSelected: {drive['name']}")

    # Navigate to customer folder
    current_path = ""
    while True:
        folders = sp_client.list_folders(site_id, drive_id, current_path)

        if not folders:
            print("No subfolders found")
            break

        # Add option to select current folder
        folder_options = [{'name': '[ Use This Folder ]'}] + folders

        folder_idx = select_from_list(folder_options,
                                     f"Navigate to customer folder (current: /{current_path or 'root'}):",
                                     'name')
        if folder_idx is None:
            return

        if folder_idx == 0:
            # Use current folder
            break
        else:
            # Navigate into folder
            selected_folder = folders[folder_idx - 1]
            if current_path:
                current_path = f"{current_path}/{selected_folder['name']}"
            else:
                current_path = selected_folder['name']

    # Get customer name from folder path
    customer_name = current_path.split('/')[-1] if current_path else "Customer"

    # Gather information
    info = gather_customer_info(sp_client, customer_name, site_id, drive_id, current_path)

    # Fill the checklist
    filled_checklist = fill_checklist(info)

    # Preview
    print("\n" + "=" * 60)
    print("Preview (first 50 lines):")
    print("=" * 60)
    preview_lines = filled_checklist.split('\n')[:50]
    print('\n'.join(preview_lines))
    if len(filled_checklist.split('\n')) > 50:
        print("\n... (truncated)")

    # Confirm save
    print("\n" + "=" * 60)
    save = input("Save this checklist to SharePoint? (y/n): ").strip().lower()

    if save == 'y':
        # Generate filename
        safe_name = re.sub(r'[^\w\s-]', '', customer_name).replace(' ', '_')
        filename = f"Network_Checklist_{safe_name}_{info['date']}.md"

        # Upload to SharePoint
        content = filled_checklist.encode('utf-8')

        if sp_client.upload_file(site_id, drive_id, current_path, filename, content):
            print(f"\nSaved: {current_path}/{filename}")
        else:
            # Fallback: save locally
            local_path = Path(f"/home/mavrick/Projects/Secondbrain/output/{filename}")
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(filled_checklist)
            print(f"\nSharePoint upload failed. Saved locally: {local_path}")
    else:
        # Save locally only
        safe_name = re.sub(r'[^\w\s-]', '', customer_name).replace(' ', '_')
        filename = f"Network_Checklist_{safe_name}_{info['date']}.md"
        local_path = Path(f"/home/mavrick/Projects/Secondbrain/output/{filename}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(filled_checklist)
        print(f"\nSaved locally: {local_path}")


if __name__ == "__main__":
    main()
