#!/usr/bin/env python3
"""
Upload file to SharePoint
Uploads a local file to a specified SharePoint site/folder
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class SharePointUploader:
    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.token = None

    def get_token(self):
        """Get OAuth token for Microsoft Graph API"""
        if self.token:
            return self.token

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError("Missing Azure credentials. Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET")

        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }

        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise Exception(f"Failed to get token: {response.text}")

        self.token = response.json().get('access_token')
        return self.token

    def get_headers(self, content_type='application/json'):
        """Get auth headers"""
        return {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-Type': content_type
        }

    def find_site(self, site_name: str) -> dict:
        """Find SharePoint site by name"""
        url = f"{self.base_url}/sites?search={site_name}"
        response = requests.get(url, headers=self.get_headers())

        if response.status_code != 200:
            raise Exception(f"Failed to search sites: {response.text}")

        sites = response.json().get('value', [])
        for site in sites:
            if site_name.lower() in site.get('displayName', '').lower():
                return site

        return None

    def upload_file(self, site_id: str, folder_path: str, local_file: str) -> dict:
        """
        Upload file to SharePoint

        Args:
            site_id: SharePoint site ID
            folder_path: Path in SharePoint (e.g., "Documents/Customer/Technical")
            local_file: Path to local file
        """
        local_path = Path(local_file)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_file}")

        filename = local_path.name
        file_size = local_path.stat().st_size

        # Clean folder path
        folder_path = folder_path.strip('/')

        # For files < 4MB, use simple upload
        if file_size < 4 * 1024 * 1024:
            return self._simple_upload(site_id, folder_path, local_path)
        else:
            return self._chunked_upload(site_id, folder_path, local_path)

    def _simple_upload(self, site_id: str, folder_path: str, local_path: Path) -> dict:
        """Simple upload for files < 4MB"""
        filename = local_path.name

        # Read file content
        with open(local_path, 'rb') as f:
            content = f.read()

        # Determine content type
        ext = local_path.suffix.lower()
        content_types = {
            '.html': 'text/html',
            '.htm': 'text/html',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        content_type = content_types.get(ext, 'application/octet-stream')

        # Upload URL
        url = f"{self.base_url}/sites/{site_id}/drive/root:/{folder_path}/{filename}:/content"

        headers = {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-Type': content_type
        }

        print(f"Uploading {filename} ({len(content)} bytes) to {folder_path}...")
        response = requests.put(url, headers=headers, data=content)

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"SUCCESS: Uploaded to {result.get('webUrl', 'SharePoint')}")
            return {
                'success': True,
                'id': result.get('id'),
                'name': result.get('name'),
                'webUrl': result.get('webUrl'),
                'size': result.get('size')
            }
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }

    def _chunked_upload(self, site_id: str, folder_path: str, local_path: Path) -> dict:
        """Chunked upload for files > 4MB"""
        # For large files, use upload session
        filename = local_path.name
        file_size = local_path.stat().st_size

        # Create upload session
        url = f"{self.base_url}/sites/{site_id}/drive/root:/{folder_path}/{filename}:/createUploadSession"

        response = requests.post(url, headers=self.get_headers(), json={
            "item": {"@microsoft.graph.conflictBehavior": "replace"}
        })

        if response.status_code != 200:
            return {'success': False, 'error': response.text}

        upload_url = response.json().get('uploadUrl')

        # Upload in chunks
        chunk_size = 10 * 1024 * 1024  # 10MB chunks

        with open(local_path, 'rb') as f:
            start = 0
            while start < file_size:
                end = min(start + chunk_size, file_size)
                chunk = f.read(chunk_size)

                headers = {
                    'Content-Length': str(len(chunk)),
                    'Content-Range': f'bytes {start}-{end-1}/{file_size}'
                }

                response = requests.put(upload_url, headers=headers, data=chunk)

                if response.status_code not in [200, 201, 202]:
                    return {'success': False, 'error': response.text}

                start = end
                print(f"Uploaded {end}/{file_size} bytes ({100*end//file_size}%)")

        result = response.json()
        return {
            'success': True,
            'id': result.get('id'),
            'name': result.get('name'),
            'webUrl': result.get('webUrl')
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Upload file to SharePoint')
    parser.add_argument('local_file', help='Path to local file')
    parser.add_argument('--site', default='oberaconnect_technical', help='SharePoint site name')
    parser.add_argument('--folder', required=True, help='SharePoint folder path (e.g., "Documents/Customer/Docs")')
    parser.add_argument('--site-id', help='SharePoint site ID (if known)')

    args = parser.parse_args()

    uploader = SharePointUploader()

    # Get site ID
    site_id = args.site_id
    if not site_id:
        print(f"Looking up site: {args.site}...")
        site = uploader.find_site(args.site)
        if not site:
            print(f"Site not found: {args.site}")
            sys.exit(1)
        site_id = site['id']
        print(f"Found site: {site.get('displayName')} ({site_id})")

    # Upload file
    result = uploader.upload_file(site_id, args.folder, args.local_file)

    if result.get('success'):
        print(f"\nFile uploaded successfully!")
        print(f"URL: {result.get('webUrl')}")
    else:
        print(f"\nUpload failed: {result.get('error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
