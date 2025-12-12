#!/usr/bin/env python3
"""
Network Installation Checklist Generator
Creates HTML checklist with clickable checkboxes for any customer
Uploads to customer's SharePoint folder
"""
import os
import re
import argparse
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv('/home/mavrick/Projects/Secondbrain/.env')

TEMPLATE_PATH = Path("/home/mavrick/Projects/network_install_workflow_checklist.md")


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
        resp = requests.get(f"{self.base_url}/sites?search=*", headers=headers)
        sites = resp.json().get('value', [])

        for site in sites:
            if site.get('displayName') == 'OberaConnect Technical':
                site_id = site['id']
                resp = requests.get(f"{self.base_url}/sites/{site_id}/drives", headers=headers)
                drives = resp.json().get('value', [])
                for drive in drives:
                    if drive['name'] == 'Documents':
                        return site_id, drive['id']
        return None, None

    def list_customer_folders(self, site_id, drive_id):
        """List all customer folders"""
        headers = {'Authorization': f'Bearer {self.token}'}
        url = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root/children"
        resp = requests.get(url, headers=headers)
        items = resp.json().get('value', [])
        return [item['name'] for item in items if 'folder' in item]

    def upload_file(self, site_id, drive_id, folder_path, filename, content):
        """Upload file to SharePoint"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/octet-stream'
        }
        upload_path = f"{folder_path}/{filename}"
        url = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root:/{upload_path}:/content"
        response = requests.put(url, headers=headers, data=content)
        return response.status_code in [200, 201], response.json() if response.status_code in [200, 201] else None


def prompt(field, default=""):
    """Simple prompt with optional default"""
    if default:
        val = input(f"{field} [{default}]: ").strip()
        return val if val else default
    return input(f"{field}: ").strip()


def select_customer(sp_client, site_id, drive_id):
    """Let user select or enter customer name with search"""
    folders = sp_client.list_customer_folders(site_id, drive_id)
    sorted_folders = sorted(folders)

    while True:
        print("\n=== Customer Folders ===")
        print("Enter number to select, type to search, or enter new customer name:\n")

        # Show first 30 alphabetically
        for i, folder in enumerate(sorted_folders[:30], 1):
            print(f"  {i:2}. {folder}")

        if len(folders) > 30:
            print(f"\n  ... and {len(folders) - 30} more")

        print()
        choice = input("Selection (or type to search): ").strip()

        if not choice:
            continue

        # Try as number first
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sorted_folders):
                return sorted_folders[idx]
            else:
                print(f"Invalid selection. Please enter 1-{len(sorted_folders)}")
                continue
        except ValueError:
            pass

        # Search for matching customers
        search_term = choice.lower()
        matches = [f for f in sorted_folders if search_term in f.lower()]

        if not matches:
            # No matches - ask if they want to create new
            print(f"\n⚠️  No customers found matching '{choice}'")
            create = input("Create new customer folder? (y/n): ").strip().lower()
            if create == 'y':
                return choice
            continue

        if len(matches) == 1:
            # Exact match or single result
            print(f"\n✓ Found: {matches[0]}")
            confirm = input("Use this customer? (y/n): ").strip().lower()
            if confirm == 'y':
                return matches[0]
            continue

        # Multiple matches - show them
        print(f"\n=== Found {len(matches)} matching customers ===")
        for i, match in enumerate(matches, 1):
            print(f"  {i:2}. {match}")
        print()

        selection = input("Select number, or press Enter to search again: ").strip()
        if not selection:
            continue

        try:
            idx = int(selection) - 1
            if 0 <= idx < len(matches):
                return matches[idx]
        except ValueError:
            pass


def extract_info_from_sharepoint(sp_client, site_id, drive_id, customer_name):
    """Extract as much customer info as possible from SharePoint documents"""
    info = {}

    headers = {'Authorization': f'Bearer {sp_client.token}'}

    # Search for SOWs, bids, proposals in customer folder
    search_url = f"{sp_client.base_url}/sites/{site_id}/drives/{drive_id}/root/search(q='{customer_name}')"
    resp = requests.get(search_url, headers=headers)

    if resp.status_code != 200:
        return info

    results = resp.json().get('value', [])

    # Look for specific document types
    for item in results:
        name = item.get('name', '').lower()

        # Check for VoIP bid (indicates phone count/users)
        if 'voip' in name or 'phone' in name:
            info['voip_required'] = 'Yes'
            # Could extract phone count from document

        # Check for SOW
        if 'sow' in name:
            info['has_sow'] = True

        # Check for network-related docs
        if any(kw in name for kw in ['network', 'firewall', 'sonicwall', 'ubiquiti', 'unifi']):
            info['has_network_docs'] = True

    # Try to download and parse a bid/proposal for more details
    from docx import Document
    from pathlib import Path
    import tempfile

    for item in results:
        name = item.get('name', '')
        if ('bid' in name.lower() or 'proposal' in name.lower()) and name.endswith('.docx'):
            download_url = item.get('@microsoft.graph.downloadUrl')
            if download_url:
                try:
                    file_resp = requests.get(download_url)
                    if file_resp.status_code == 200:
                        # Save and parse
                        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
                            tmp.write(file_resp.content)
                            tmp_path = tmp.name

                        doc = Document(tmp_path)
                        full_text = '\n'.join([p.text for p in doc.paragraphs])

                        # Extract phone count for user estimate
                        import re
                        phone_match = re.search(r'(\d+)\s*(?:phones?|lines?|extensions?)', full_text, re.I)
                        if phone_match:
                            info['num_users'] = phone_match.group(1)

                        # Look for IT contractor
                        if 'Computer Backup' in full_text:
                            info['it_contractor'] = 'Computer Backup, Inc.'

                        Path(tmp_path).unlink()
                        break
                except Exception:
                    pass

    return info


def gather_customer_info(customer_name, sp_client=None, site_id=None, drive_id=None):
    """Gather customer information - auto-fill from SharePoint, prompt for rest"""

    # Start with defaults
    info = {
        'customer_name': customer_name,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'project_manager': '',
        'site_address': '',
        'contact_name': '',
        'contact_email': '',
        'contact_phone': '',
        'current_isp': '',
        'internet_speed': '',
        'num_users': '',
        'num_devices': '',
        'current_router': '',
        'current_switches': '',
        'current_aps': '',
        'internal_subnet': '',
        'public_ip': '',
        'public_ip_range': '',
        'subnet_mask': '',
        'default_gateway': '',
        'dns_primary': '',
        'dns_secondary': '',
        'dns_tertiary': '',
        'vlans_needed': 'Data, Voice, Guest, IoT, Security',
        'guest_network': 'Yes',
        'voip_required': 'Yes',
        'vpn_required': 'Yes',
        'recommended_router': 'SonicWall TZ',
        'recommended_switches': '',
        'recommended_aps': 'Ubiquiti UniFi',
        'notes': ''
    }

    # Try to auto-fill from SharePoint
    if sp_client and site_id and drive_id:
        print("\nSearching SharePoint for customer data...")
        sp_info = extract_info_from_sharepoint(sp_client, site_id, drive_id, customer_name)

        if sp_info:
            print("\n--- Auto-filled from SharePoint ---")
            for key, value in sp_info.items():
                if key in info:
                    info[key] = value
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}")

            # Add notes about what was found
            notes = []
            if sp_info.get('it_contractor'):
                notes.append(f"IT Contractor: {sp_info['it_contractor']}")
            if sp_info.get('has_sow'):
                notes.append("SOW on file")
            if sp_info.get('has_network_docs'):
                notes.append("Network docs on file")
            if notes:
                info['notes'] = '. '.join(notes)

    print(f"\n{'='*60}")
    print(f"Network Installation Checklist - {customer_name}")
    print(f"{'='*60}")
    print("\nPress Enter to accept default/auto-filled values shown in [brackets]")

    print("\n--- Project Info ---")
    info['project_manager'] = prompt("Project Manager/Engineer", info['project_manager'])
    info['site_address'] = prompt("Site Address", info['site_address'])
    info['contact_name'] = prompt("Primary Contact Name", info['contact_name'])
    info['contact_email'] = prompt("Contact Email", info['contact_email'])
    info['contact_phone'] = prompt("Contact Phone", info['contact_phone'])

    print("\n--- Current Network ---")
    info['current_isp'] = prompt("Current ISP", info['current_isp'])
    info['internet_speed'] = prompt("Internet Speed (e.g., 100/100 Mbps)", info['internet_speed'])
    info['num_users'] = prompt("Number of Users", info['num_users'])
    info['num_devices'] = prompt("Estimated Number of Devices", info['num_devices'])
    info['current_router'] = prompt("Current Router/Firewall", info['current_router'])
    info['current_switches'] = prompt("Current Switches", info['current_switches'])
    info['current_aps'] = prompt("Current Access Points", info['current_aps'])

    print("\n--- Network Configuration ---")
    info['internal_subnet'] = prompt("Internal Subnet (e.g., 192.168.1.0/24)", info['internal_subnet'])
    info['public_ip'] = prompt("Public IP Address", info['public_ip'])
    info['public_ip_range'] = prompt("Public IP Range", info['public_ip_range'])
    info['subnet_mask'] = prompt("Subnet Mask", info['subnet_mask'])
    info['default_gateway'] = prompt("Default Gateway", info['default_gateway'])

    print("\n--- DNS Configuration ---")
    info['dns_primary'] = prompt("Primary DNS IP", info['dns_primary'])
    info['dns_secondary'] = prompt("Secondary DNS IP", info['dns_secondary'])
    info['dns_tertiary'] = prompt("Tertiary DNS IP (optional)", info['dns_tertiary'])

    print("\n--- Requirements ---")
    info['vlans_needed'] = prompt("VLANs Needed", info['vlans_needed'])
    info['guest_network'] = prompt("Guest Network Required", info['guest_network'])
    info['voip_required'] = prompt("VoIP Required", info['voip_required'])
    info['vpn_required'] = prompt("VPN Required", info['vpn_required'])

    print("\n--- Recommended Equipment ---")
    info['recommended_router'] = prompt("Recommended Router/Firewall", info['recommended_router'])
    info['recommended_switches'] = prompt("Recommended Switches", info['recommended_switches'])
    info['recommended_aps'] = prompt("Recommended Access Points", info['recommended_aps'])

    print("\n--- Notes ---")
    info['notes'] = prompt("Additional Notes", info['notes'])

    return info


def get_logo_base64():
    """Get OberaConnect logo as base64"""
    import base64
    logo_path = Path("/home/mavrick/Projects/Secondbrain/separate_projects/copilot-buddy-bytes-2/src/assets/obera-logo-cropped.png")
    if logo_path.exists():
        logo_data = logo_path.read_bytes()
        return base64.b64encode(logo_data).decode('utf-8')
    return None


def generate_html_checklist(info):
    """Generate HTML checklist with clickable checkboxes"""

    # Get logo
    logo_base64 = get_logo_base64()

    # Read markdown template
    md_content = TEMPLATE_PATH.read_text()

    # Convert markdown checklist to HTML
    checklist_html = ""
    lines = md_content.split('\n')

    for line in lines:
        if line.startswith('# '):
            # Skip main title, we'll use our own
            continue
        elif line.startswith('## '):
            checklist_html += f'<h2>{line[3:]}</h2>\n'
        elif line.startswith('### '):
            checklist_html += f'<h3>{line[4:]}</h3>\n'
        elif line.startswith('- [ ] '):
            text = line[6:]
            checklist_html += f'<div class="checklist-item"><label><input type="checkbox"> {text}</label></div>\n'
        elif line.startswith('  - [ ] '):
            text = line[8:]
            checklist_html += f'<div class="checklist-item nested"><label><input type="checkbox"> {text}</label></div>\n'
        elif line.startswith('---'):
            checklist_html += '<hr>\n'
        elif line.strip():
            checklist_html += f'<p>{line}</p>\n'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Checklist - {info['customer_name']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            padding: 20px 0;
            margin-bottom: 20px;
            border-bottom: 3px solid #4CAF50;
        }}
        .header h1 {{
            margin: 10px 0;
            font-size: 24px;
            color: #1e3a5f;
        }}
        .header div {{
            color: #333;
        }}
        .header .logo-img {{
            max-height: 100px;
            margin-bottom: 10px;
        }}
        .customer-info {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .customer-info h2 {{
            margin-top: 0;
            color: #1e3a5f;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        .info-item {{
            padding: 8px 0;
        }}
        .info-item strong {{
            color: #1e3a5f;
        }}
        .checklist-section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #1e3a5f;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        h3 {{
            color: #2d5a87;
            margin-top: 20px;
        }}
        .checklist-item {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .checklist-item:last-child {{
            border-bottom: none;
        }}
        .checklist-item.nested {{
            padding-left: 30px;
        }}
        .checklist-item label {{
            cursor: pointer;
            display: flex;
            align-items: flex-start;
        }}
        .checklist-item input[type="checkbox"] {{
            margin-right: 10px;
            margin-top: 3px;
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        .checklist-item input[type="checkbox"]:checked + span,
        .checklist-item input[type="checkbox"]:checked ~ * {{
            text-decoration: line-through;
            color: #888;
        }}
        hr {{
            border: none;
            border-top: 2px solid #4CAF50;
            margin: 30px 0;
        }}
        .progress-bar {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 20px;
            margin: 20px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #4CAF50, #45a049);
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }}
        .progress-text {{
            text-align: center;
            font-weight: bold;
            color: #1e3a5f;
        }}
        @media print {{
            body {{
                background: white;
            }}
            .checklist-section, .customer-info {{
                box-shadow: none;
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        {f'<img src="data:image/png;base64,{logo_base64}" alt="OberaConnect" class="logo-img">' if logo_base64 else '<div class="logo">Obera<span>Connect</span></div>'}
        <h1>Network Installation Checklist</h1>
        <div>Customer: {info['customer_name']}</div>
        <div>Date: {info['date']}</div>
    </div>

    <div class="customer-info">
        <h2>Project Overview</h2>
        <div class="info-grid">
            <div class="info-item"><strong>Project Manager:</strong> {info['project_manager']}</div>
            <div class="info-item"><strong>Site Address:</strong> {info['site_address']}</div>
            <div class="info-item"><strong>Contact:</strong> {info['contact_name']}</div>
            <div class="info-item"><strong>Email:</strong> {info['contact_email']}</div>
            <div class="info-item"><strong>Phone:</strong> {info['contact_phone']}</div>
        </div>

        <h3>Current Network</h3>
        <div class="info-grid">
            <div class="info-item"><strong>ISP:</strong> {info['current_isp']}</div>
            <div class="info-item"><strong>Speed:</strong> {info['internet_speed']}</div>
            <div class="info-item"><strong>Users:</strong> {info['num_users']}</div>
            <div class="info-item"><strong>Devices:</strong> {info['num_devices']}</div>
            <div class="info-item"><strong>Router:</strong> {info['current_router']}</div>
            <div class="info-item"><strong>Switches:</strong> {info['current_switches']}</div>
            <div class="info-item"><strong>APs:</strong> {info['current_aps']}</div>
        </div>

        <h3>Network Configuration</h3>
        <div class="info-grid">
            <div class="info-item"><strong>Internal Subnet:</strong> {info['internal_subnet']}</div>
            <div class="info-item"><strong>Public IP Address:</strong> {info['public_ip']}</div>
            <div class="info-item"><strong>Public IP Range:</strong> {info['public_ip_range']}</div>
            <div class="info-item"><strong>Subnet Mask:</strong> {info['subnet_mask']}</div>
            <div class="info-item"><strong>Default Gateway:</strong> {info['default_gateway']}</div>
        </div>

        <h3>DNS Configuration</h3>
        <div class="info-grid">
            <div class="info-item"><strong>Primary DNS:</strong> {info['dns_primary']}</div>
            <div class="info-item"><strong>Secondary DNS:</strong> {info['dns_secondary']}</div>
            <div class="info-item"><strong>Tertiary DNS:</strong> {info['dns_tertiary']}</div>
        </div>

        <h3>Requirements</h3>
        <div class="info-grid">
            <div class="info-item"><strong>VLANs:</strong> {info['vlans_needed']}</div>
            <div class="info-item"><strong>Guest Network:</strong> {info['guest_network']}</div>
            <div class="info-item"><strong>VoIP:</strong> {info['voip_required']}</div>
            <div class="info-item"><strong>VPN:</strong> {info['vpn_required']}</div>
        </div>

        <h3>Recommended Equipment</h3>
        <div class="info-grid">
            <div class="info-item"><strong>Router/Firewall:</strong> {info['recommended_router']}</div>
            <div class="info-item"><strong>Switches:</strong> {info['recommended_switches']}</div>
            <div class="info-item"><strong>Access Points:</strong> {info['recommended_aps']}</div>
        </div>

        {f'<h3>Notes</h3><p>{info["notes"]}</p>' if info.get('notes') else ''}
    </div>

    <div class="progress-text">Progress: <span id="progress-percent">0%</span></div>
    <div class="progress-bar">
        <div class="progress-fill" id="progress-fill"></div>
    </div>

    <div class="checklist-section">
        {checklist_html}
    </div>

    <script>
        // Update progress bar when checkboxes change
        function updateProgress() {{
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            const checked = document.querySelectorAll('input[type="checkbox"]:checked');
            const percent = Math.round((checked.length / checkboxes.length) * 100);
            document.getElementById('progress-percent').textContent = percent + '%';
            document.getElementById('progress-fill').style.width = percent + '%';
        }}

        // Add event listeners to all checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {{
            cb.addEventListener('change', updateProgress);
        }});

        // Initial update
        updateProgress();
    </script>
</body>
</html>'''

    return html


def main():
    parser = argparse.ArgumentParser(description='Generate Network Installation Checklist')
    parser.add_argument('--customer', '-c', help='Customer name (skip selection prompt)')
    args = parser.parse_args()

    print("=" * 60)
    print("Network Installation Checklist Generator")
    print("=" * 60)

    # Connect to SharePoint
    sp_client = SharePointClient()
    if not sp_client.token:
        print("Failed to connect to SharePoint")
        return

    site_id, drive_id = sp_client.get_site_and_drive()
    if not site_id:
        print("Could not find OberaConnect Technical site")
        return

    print("\nConnected to SharePoint")

    # Get customer name
    if args.customer:
        customer_name = args.customer
    else:
        customer_name = select_customer(sp_client, site_id, drive_id)

    if not customer_name:
        print("No customer selected")
        return

    # Gather info - auto-fills from SharePoint, prompts for rest
    info = gather_customer_info(customer_name, sp_client, site_id, drive_id)

    # Generate HTML
    html_content = generate_html_checklist(info)

    # Preview
    print("\n" + "=" * 60)
    print("Generated HTML checklist with:")
    print(f"  - OberaConnect branded header")
    print(f"  - Clickable checkboxes")
    print(f"  - Progress bar")
    print(f"  - Customer info section")
    print("=" * 60)

    # Confirm upload
    upload = input("\nUpload to SharePoint? (y/n): ").strip().lower()

    if upload == 'y':
        # Generate filename
        safe_name = re.sub(r'[^\w\s-]', '', customer_name).replace(' ', '_')
        filename = f"Network_Checklist_{info['date']}.html"

        # Upload to customer's Technical Docs folder
        # Structure: Customer Name/Technical Docs/
        folder_path = f"{customer_name}/Technical Docs"

        content = html_content.encode('utf-8')
        success, result = sp_client.upload_file(site_id, drive_id, folder_path, filename, content)

        if success:
            print(f"\nUploaded to SharePoint!")
            print(f"  Path: {folder_path}/{filename}")
            if result:
                print(f"  URL: {result.get('webUrl', 'N/A')}")
        else:
            print(f"\nUpload failed - saving locally instead")
            local_path = Path(f'/home/mavrick/Projects/Secondbrain/output/{filename}')
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(html_content)
            print(f"  Saved: {local_path}")

        # Also save template to Customer Template Folder
        save_template = input("\nAlso save as reusable template? (y/n): ").strip().lower()
        if save_template == 'y':
            template_folder = "Customer Template Folder/Project or Location/Technical Docs"
            template_filename = "Network_Installation_Checklist_Template.html"

            # Create a blank template version (without customer-specific info filled in)
            template_info = {
                'customer_name': '[Customer Name]',
                'date': '[Date]',
                'project_manager': '[Project Manager]',
                'site_address': '[Site Address]',
                'contact_name': '[Contact Name]',
                'contact_email': '[Contact Email]',
                'contact_phone': '[Contact Phone]',
                'current_isp': '[ISP]',
                'internet_speed': '[Speed]',
                'num_users': '[Users]',
                'num_devices': '[Devices]',
                'current_router': '[Router/Firewall]',
                'current_switches': '[Switches]',
                'current_aps': '[Access Points]',
                'internal_subnet': '[Internal Subnet]',
                'public_ip': '[Public IP Address]',
                'public_ip_range': '[Public IP Range]',
                'subnet_mask': '[Subnet Mask]',
                'default_gateway': '[Default Gateway]',
                'dns_primary': '[Primary DNS]',
                'dns_secondary': '[Secondary DNS]',
                'dns_tertiary': '[Tertiary DNS]',
                'vlans_needed': '[VLANs]',
                'guest_network': '[Yes/No]',
                'voip_required': '[Yes/No]',
                'vpn_required': '[Yes/No]',
                'recommended_router': '[Recommended Router]',
                'recommended_switches': '[Recommended Switches]',
                'recommended_aps': '[Recommended APs]',
                'notes': ''
            }
            template_html = generate_html_checklist(template_info)
            template_content = template_html.encode('utf-8')

            success, result = sp_client.upload_file(site_id, drive_id, template_folder, template_filename, template_content)
            if success:
                print(f"\nTemplate saved to: {template_folder}/{template_filename}")
            else:
                print(f"\nFailed to save template")
    else:
        # Save locally
        safe_name = re.sub(r'[^\w\s-]', '', customer_name).replace(' ', '_')
        filename = f"Network_Checklist_{safe_name}_{info['date']}.html"
        local_path = Path(f'/home/mavrick/Projects/Secondbrain/output/{filename}')
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(html_content)
        print(f"\nSaved locally: {local_path}")


if __name__ == "__main__":
    main()
