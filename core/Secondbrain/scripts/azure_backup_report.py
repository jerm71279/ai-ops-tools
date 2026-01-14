#!/usr/bin/env python3
"""
Azure VM Backup Daily Report Generator
Generates executive summary reports and uploads to SharePoint

Uses:
- Setco Service Principal for backup status (permanent, no login needed)
- OberaConnect Service Principal for SharePoint upload
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import argparse


# Load environment variables from .env file
def load_env_file(filepath):
    """Load environment variables from .env file"""
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
    except FileNotFoundError:
        pass

load_env_file('/home/mavrick/Projects/Secondbrain/.env')

# OberaConnect tenant (for SharePoint)
GRAPH_TENANT_ID = os.getenv('AZURE_TENANT_ID')
GRAPH_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
GRAPH_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

# Setco tenant (for Azure Backup)
SETCO_TENANT_ID = os.getenv('SETCO_TENANT_ID')
SETCO_CLIENT_ID = os.getenv('SETCO_CLIENT_ID')
SETCO_CLIENT_SECRET = os.getenv('SETCO_CLIENT_SECRET')
SETCO_SUBSCRIPTION_ID = os.getenv('SETCO_SUBSCRIPTION_ID')

# SharePoint Configuration
SHAREPOINT_SITE_ID = 'oberaconnect.sharepoint.com,7c44e518-e9bd-4a53-b39b-036d1b30edb4,75282f0b-6bd7-437c-99e7-1cf44cff867d'
SHAREPOINT_FOLDER = 'Setco/Daily Reports'


class AzureBackupClient:
    """Client for Azure Backup REST API using service principal"""

    def __init__(self):
        self.token = None
        self.base_url = 'https://management.azure.com'

    def _get_token(self):
        """Get Azure Management token"""
        if self.token:
            return self.token

        token_url = f'https://login.microsoftonline.com/{SETCO_TENANT_ID}/oauth2/v2.0/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': SETCO_CLIENT_ID,
            'client_secret': SETCO_CLIENT_SECRET,
            'scope': 'https://management.azure.com/.default'
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            self.token = response.json().get('access_token')
            return self.token
        else:
            print(f"Error getting Azure token: {response.text}")
            return None

    def get_backup_items(self, vault_name, resource_group):
        """Get backup items from Recovery Services vault"""
        token = self._get_token()
        if not token:
            return None, "Failed to authenticate to Azure"

        headers = {'Authorization': f'Bearer {token}'}

        # Get backup protected items
        url = (f"{self.base_url}/subscriptions/{SETCO_SUBSCRIPTION_ID}"
               f"/resourceGroups/{resource_group}/providers/Microsoft.RecoveryServices"
               f"/vaults/{vault_name}/backupProtectedItems?api-version=2023-01-01")

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('value', []), None
            else:
                return None, f"API error: {response.status_code} - {response.text[:200]}"
        except Exception as e:
            return None, str(e)


class SharePointUploader:
    """Client for SharePoint uploads via Microsoft Graph"""

    def __init__(self):
        self.token = None
        self.base_url = 'https://graph.microsoft.com/v1.0'

    def _get_token(self):
        """Get Microsoft Graph token"""
        if self.token:
            return self.token

        token_url = f'https://login.microsoftonline.com/{GRAPH_TENANT_ID}/oauth2/v2.0/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': GRAPH_CLIENT_ID,
            'client_secret': GRAPH_CLIENT_SECRET,
            'scope': 'https://graph.microsoft.com/.default'
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            self.token = response.json().get('access_token')
            return self.token
        else:
            print(f"Error getting Graph token: {response.text}")
            return None

    def upload(self, content, filename):
        """Upload file to SharePoint"""
        token = self._get_token()
        if not token:
            return False, "Failed to get Graph token"

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'text/plain'
        }

        # Get drives
        drives_url = f'{self.base_url}/sites/{SHAREPOINT_SITE_ID}/drives'
        drives_response = requests.get(drives_url, headers={'Authorization': f'Bearer {token}'})

        if drives_response.status_code != 200:
            return False, f"Failed to get drives: {drives_response.status_code}"

        drives = drives_response.json().get('value', [])
        drive_id = None
        for drive in drives:
            if drive.get('name') == 'Documents':
                drive_id = drive['id']
                break

        if not drive_id:
            return False, "Could not find Documents drive"

        # Upload file
        upload_url = f'{self.base_url}/sites/{SHAREPOINT_SITE_ID}/drives/{drive_id}/root:/{SHAREPOINT_FOLDER}/{filename}:/content'
        upload_response = requests.put(upload_url, headers=headers, data=content.encode('utf-8'))

        if upload_response.status_code in [200, 201]:
            return True, f"Uploaded to: {SHAREPOINT_FOLDER}/{filename}"
        else:
            return False, f"Upload failed: {upload_response.status_code} - {upload_response.text[:200]}"


def generate_report(vault_name="MyRecoveryServicesVault", resource_group="DataCenter"):
    """Generate the backup status report"""

    client = AzureBackupClient()
    items, error = client.get_backup_items(vault_name, resource_group)

    if items is None:
        return None, f"Error: {error}"

    if not items:
        return None, "Error: No backup items found in vault"

    # Parse backup items
    protected = []
    issues = []
    skip_vms = ['SETCO-DC02']

    for item in items:
        props = item.get('properties', {})
        vm_name = props.get('friendlyName', 'Unknown')
        status = props.get('protectionState', 'Unknown')
        last_backup = props.get('lastBackupTime', 'Never')
        policy = props.get('policyName', 'None')

        if vm_name in skip_vms:
            continue

        entry = {
            'name': vm_name,
            'status': status,
            'last_backup': last_backup,
            'policy': policy or 'None'
        }

        if status in ['Protected', 'ProtectionConfigured']:
            protected.append(entry)
        else:
            issues.append(entry)

    # Format report
    report_date = datetime.now().strftime("%B %d, %Y")

    report = f"""### **Azure VM Backup Status Report**

**Date:** {report_date}
**Vault:** {vault_name}
**Resource Group:** {resource_group}

---

### **Executive Summary**

All critical production VMs in the `{vault_name}` vault have been reviewed.

- **Total VMs Reviewed:** {len(protected) + len(issues)}
- **Successfully Protected:** {len(protected)}
- **Protection Issues:** {len(issues)}

---

### **Detailed Backup Status**

| VM Name | Status | Last Successful Backup | Backup Policy |
| ------- | ------ | ---------------------- | ------------- |
"""

    for vm in sorted(protected, key=lambda x: x['name']):
        last = vm['last_backup']
        if last and last != 'Never':
            try:
                dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
                last = dt.strftime("%Y-%m-%d %H:%M UTC")
            except:
                pass
        report += f"| {vm['name']} | ✅ Protected | {last} | `{vm['policy']}` |\n"

    for vm in sorted(issues, key=lambda x: x['name']):
        last = vm['last_backup']
        if last and last != 'Never':
            try:
                dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
                last = dt.strftime("%Y-%m-%d")
            except:
                pass
        status_emoji = "⚠️" if vm['status'] == 'ProtectionStopped' else "❌"
        report += f"| {vm['name']} | {status_emoji} {vm['status']} | {last} | *{vm['policy']}* |\n"

    report += """
---

### **Recommendations**

"""
    if issues:
        for vm in issues:
            if vm['status'] == 'ProtectionStopped':
                report += f"1. **{vm['name']}:** Protection stopped. Verify if VM is decommissioned.\n"
            else:
                report += f"1. **{vm['name']}:** Status is `{vm['status']}`. Investigate immediately.\n"
    else:
        report += "- All VMs are protected and backing up successfully. No action required.\n"

    report += "\n2. **Policy Review:** Quarterly review recommended to ensure RPO/RTO objectives are met.\n"

    return items, report


def main():
    parser = argparse.ArgumentParser(description='Generate Azure VM Backup Report')
    parser.add_argument('--vault', default='MyRecoveryServicesVault', help='Vault name')
    parser.add_argument('--resource-group', default='DataCenter', help='Resource group')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--sharepoint', '-s', action='store_true', help='Upload to SharePoint')
    parser.add_argument('--format', choices=['markdown', 'html'], default='markdown')

    args = parser.parse_args()

    items, report = generate_report(args.vault, args.resource_group)

    if items is None:
        print(report)
        exit(1)

    if args.format == 'html':
        report = f"""<!DOCTYPE html>
<html>
<head>
    <title>Azure VM Backup Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4472C4; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        h3 {{ color: #2F5496; }}
    </style>
</head>
<body><pre>{report}</pre></body>
</html>"""

    # Save locally
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)

    # Upload to SharePoint
    if args.sharepoint:
        uploader = SharePointUploader()
        filename = f"azure_backup_{datetime.now().strftime('%Y-%m-%d')}.md"
        success, message = uploader.upload(report, filename)
        if success:
            print(f"✅ SharePoint: {message}")
        else:
            print(f"❌ SharePoint: {message}")


if __name__ == '__main__':
    main()
