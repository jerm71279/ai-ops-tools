#!/usr/bin/env python3
"""
SharePoint Document Importer
Downloads documents from SharePoint sites and libraries using Microsoft Graph API
"""
import os
import json
from pathlib import Path
from typing import List, Dict
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SharePointImporter:
    """Import documents from SharePoint using Microsoft Graph API"""

    def __init__(self, tenant_id: str = None, client_id: str = None, client_secret: str = None):
        """
        Initialize SharePoint importer

        You'll need to register an app in Azure AD and grant permissions:
        - Sites.Read.All
        - Files.Read.All
        """
        self.tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
        self.client_id = client_id or os.getenv('AZURE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('AZURE_CLIENT_SECRET')

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            print("⚠️  Azure credentials not configured.")
            print("   Set environment variables:")
            print("   - AZURE_TENANT_ID")
            print("   - AZURE_CLIENT_ID")
            print("   - AZURE_CLIENT_SECRET")
            self.token = None
        else:
            self.token = self._get_access_token()

    def _get_access_token(self) -> str:
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
            print(f"❌ Failed to get access token: {e}")
            return None

    def list_sites(self) -> List[Dict]:
        """List all SharePoint sites"""
        if not self.token:
            return []

        url = "https://graph.microsoft.com/v1.0/sites?search=*"
        headers = {'Authorization': f'Bearer {self.token}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            sites = response.json().get('value', [])

            print(f"📍 Found {len(sites)} SharePoint sites:")
            for site in sites:
                print(f"   - {site['displayName']} ({site['webUrl']})")

            return sites
        except Exception as e:
            print(f"❌ Failed to list sites: {e}")
            return []

    def list_document_libraries(self, site_id: str) -> List[Dict]:
        """List document libraries in a site"""
        if not self.token:
            return []

        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
        headers = {'Authorization': f'Bearer {self.token}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            libraries = response.json().get('value', [])

            print(f"📚 Found {len(libraries)} document libraries:")
            for lib in libraries:
                print(f"   - {lib['name']}")

            return libraries
        except Exception as e:
            print(f"❌ Failed to list libraries: {e}")
            return []

    def download_files_from_library(self, site_id: str, drive_id: str, output_dir: Path,
                                   file_extensions: List[str] = None):
        """Download files from a document library"""
        if not self.token:
            print("❌ No authentication token")
            return

        if file_extensions is None:
            file_extensions = ['.pdf', '.docx', '.html', '.md', '.txt']

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root/children"
        headers = {'Authorization': f'Bearer {self.token}'}

        downloaded = 0
        skipped = 0

        try:
            while url:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                for item in data.get('value', []):
                    if 'file' in item:  # It's a file
                        file_name = item['name']
                        file_ext = Path(file_name).suffix.lower()

                        if file_ext in file_extensions:
                            download_url = item['@microsoft.graph.downloadUrl']
                            file_path = output_dir / file_name

                            print(f"⬇️  Downloading: {file_name}")

                            file_response = requests.get(download_url)
                            file_response.raise_for_status()

                            file_path.write_bytes(file_response.content)
                            downloaded += 1
                        else:
                            skipped += 1

                # Handle pagination
                url = data.get('@odata.nextLink')

        except Exception as e:
            print(f"❌ Download failed: {e}")

        print(f"\n✅ Downloaded: {downloaded} files")
        print(f"⏭️  Skipped: {skipped} files (unsupported types)")

    def download_from_sharepoint_url(self, sharepoint_url: str, output_dir: Path):
        """
        Download files from a SharePoint URL
        Example: https://yourcompany.sharepoint.com/sites/YourSite/Shared%20Documents
        """
        print(f"📥 Downloading from: {sharepoint_url}")
        print("⚠️  This requires parsing the SharePoint URL to extract site and library IDs")
        print("   For now, use list_sites() and download_files_from_library() directly")


def setup_azure_app():
    """Print instructions for setting up Azure app registration"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║  SharePoint Importer - Azure App Registration Setup           ║
╚════════════════════════════════════════════════════════════════╝

To use the SharePoint importer, you need to register an app in Azure AD:

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to: Azure Active Directory > App registrations
3. Click "New registration"
   - Name: "SecondBrain SharePoint Importer"
   - Supported account types: Single tenant
   - Redirect URI: (leave blank)
4. Click "Register"

5. Note the following values:
   - Application (client) ID
   - Directory (tenant) ID

6. Create a client secret:
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: "SecondBrain access"
   - Expires: 24 months
   - Click "Add"
   - Copy the secret VALUE (you can only see it once!)

7. Grant API permissions:
   - Go to "API permissions"
   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Choose "Application permissions"
   - Add these permissions:
     * Sites.Read.All
     * Files.Read.All
   - Click "Grant admin consent"

8. Set environment variables:
   export AZURE_TENANT_ID="your-tenant-id"
   export AZURE_CLIENT_ID="your-client-id"
   export AZURE_CLIENT_SECRET="your-client-secret"

Or add to .env file:
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_CLIENT_SECRET=your-client-secret
""")


if __name__ == "__main__":
    import sys

    if '--setup' in sys.argv:
        setup_azure_app()
        sys.exit(0)

    # Initialize importer
    importer = SharePointImporter()

    if not importer.token:
        print("\n💡 Run with --setup for configuration instructions")
        sys.exit(1)

    # List available sites
    print("\n📍 Listing SharePoint sites...")
    sites = importer.list_sites()

    if sites:
        print("\n💡 To download files:")
        print("   1. Note the site ID from above")
        print("   2. Use list_document_libraries(site_id)")
        print("   3. Use download_files_from_library(site_id, drive_id, output_dir)")
