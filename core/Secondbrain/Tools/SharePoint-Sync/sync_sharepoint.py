import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
SharePoint Document Sync
Downloads new and updated documents from SharePoint to Secondbrain

Runs daily to keep input_documents/sharepoint_all in sync with SharePoint sites.
Tracks last sync time to only download changed files.
"""
import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import re

load_dotenv()


class SharePointSync:
    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.token = None

        self.download_dir = Path("input_documents/sharepoint_all")
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.sync_state_file = Path("data/sharepoint_sync_state.json")
        self.sync_state_file.parent.mkdir(parents=True, exist_ok=True)

        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # File extensions to sync
        self.allowed_extensions = {
            '.pdf', '.docx', '.doc', '.xlsx', '.xls',
            '.txt', '.md', '.html', '.htm', '.csv', '.json'
        }

        # Sites to sync (will be discovered if not specified)
        self.target_sites = []

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

    def get_headers(self):
        """Get auth headers"""
        return {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-Type': 'application/json'
        }

    def load_sync_state(self):
        """Load last sync state"""
        if self.sync_state_file.exists():
            with open(self.sync_state_file) as f:
                return json.load(f)
        return {
            'last_sync': None,
            'synced_files': {},
            'sites_synced': []
        }

    def save_sync_state(self, state):
        """Save sync state"""
        with open(self.sync_state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)

    def discover_sites(self):
        """Discover all SharePoint sites"""
        print("Discovering SharePoint sites...")
        sites = []

        # Search for all sites
        url = f"{self.base_url}/sites?search=*"

        while url:
            resp = requests.get(url, headers=self.get_headers())
            if resp.status_code != 200:
                print(f"  Error searching sites: {resp.status_code}")
                break

            data = resp.json()
            for site in data.get('value', []):
                sites.append({
                    'id': site['id'],
                    'name': site.get('displayName', 'Unknown'),
                    'webUrl': site.get('webUrl', '')
                })

            url = data.get('@odata.nextLink')

        print(f"  Found {len(sites)} sites")
        return sites

    def get_site_drives(self, site_id):
        """Get all document libraries (drives) for a site"""
        url = f"{self.base_url}/sites/{site_id}/drives"
        resp = requests.get(url, headers=self.get_headers())

        if resp.status_code != 200:
            return []

        return resp.json().get('value', [])

    def get_drive_items(self, drive_id, folder_path="root", last_sync=None):
        """Get items in a drive folder, optionally filtered by modification date"""
        items = []
        url = f"{self.base_url}/drives/{drive_id}/{folder_path}/children"

        while url:
            resp = requests.get(url, headers=self.get_headers())
            if resp.status_code != 200:
                break

            data = resp.json()
            for item in data.get('value', []):
                # Check if modified since last sync
                modified = item.get('lastModifiedDateTime')
                if last_sync and modified:
                    try:
                        mod_time = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                        if isinstance(last_sync, str):
                            # Handle both aware and naive datetimes
                            if '+' in last_sync or 'Z' in last_sync:
                                sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                            else:
                                sync_time = datetime.fromisoformat(last_sync + '+00:00')
                        else:
                            sync_time = last_sync
                        # Make both timezone-aware for comparison
                        if sync_time.tzinfo is None:
                            from datetime import timezone
                            sync_time = sync_time.replace(tzinfo=timezone.utc)
                        if mod_time <= sync_time:
                            continue
                    except Exception:
                        pass  # If date comparison fails, include the item

                items.append(item)

            url = data.get('@odata.nextLink')

        return items

    def sanitize_filename(self, name):
        """Sanitize filename for filesystem"""
        # Remove or replace invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = name.strip('. ')
        return name[:200]  # Limit length

    def download_file(self, drive_id, item_id, dest_path):
        """Download a file from SharePoint"""
        url = f"{self.base_url}/drives/{drive_id}/items/{item_id}/content"

        resp = requests.get(url, headers=self.get_headers(), stream=True)
        if resp.status_code != 200:
            return False

        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(dest_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return True

    def sync_drive(self, site_name, drive, state, stats):
        """Sync a single drive"""
        drive_id = drive['id']
        drive_name = self.sanitize_filename(drive.get('name', 'documents'))

        print(f"    Syncing drive: {drive_name}")

        # Create folder structure
        site_folder = self.sanitize_filename(site_name.lower().replace(' ', '_'))
        drive_folder = self.download_dir / site_folder / drive_name
        drive_folder.mkdir(parents=True, exist_ok=True)

        # Get items (recursively)
        self._sync_folder(
            drive_id=drive_id,
            folder_path="root",
            local_path=drive_folder,
            state=state,
            stats=stats,
            last_sync=state.get('last_sync')
        )

    def _sync_folder(self, drive_id, folder_path, local_path, state, stats, last_sync=None):
        """Recursively sync a folder"""
        items = self.get_drive_items(drive_id, folder_path, last_sync)

        for item in items:
            name = item.get('name', 'unknown')
            item_id = item['id']

            if 'folder' in item:
                # Recurse into subfolder
                subfolder = local_path / self.sanitize_filename(name)
                self._sync_folder(
                    drive_id=drive_id,
                    folder_path=f"items/{item_id}",
                    local_path=subfolder,
                    state=state,
                    stats=stats,
                    last_sync=last_sync
                )
            elif 'file' in item:
                # Check extension
                ext = Path(name).suffix.lower()
                if ext not in self.allowed_extensions:
                    continue

                # Download file
                dest_path = local_path / self.sanitize_filename(name)

                # Check if file changed (by etag or size)
                file_key = f"{drive_id}/{item_id}"
                existing = state.get('synced_files', {}).get(file_key, {})

                if (existing.get('etag') == item.get('eTag') and
                    dest_path.exists()):
                    stats['skipped'] += 1
                    continue

                print(f"      Downloading: {name[:50]}")
                if self.download_file(drive_id, item_id, dest_path):
                    stats['downloaded'] += 1
                    state.setdefault('synced_files', {})[file_key] = {
                        'name': name,
                        'path': str(dest_path),
                        'etag': item.get('eTag'),
                        'modified': item.get('lastModifiedDateTime'),
                        'synced_at': datetime.now().isoformat()
                    }
                else:
                    stats['failed'] += 1

    def sync_all(self, incremental=True):
        """Sync all SharePoint sites"""
        print("=" * 60)
        print("SharePoint Document Sync")
        print("=" * 60)
        print(f"Started: {datetime.now().isoformat()}")
        print()

        state = self.load_sync_state()

        if not incremental:
            state['last_sync'] = None
            print("Running FULL sync (ignoring last sync time)")
        elif state.get('last_sync'):
            print(f"Last sync: {state['last_sync']}")
        else:
            print("First sync - downloading all files")
        print()

        stats = {
            'sites': 0,
            'drives': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0
        }

        try:
            sites = self.discover_sites()

            for site in sites:
                site_name = site['name']
                site_id = site['id']

                print(f"  Site: {site_name}")
                stats['sites'] += 1

                drives = self.get_site_drives(site_id)

                for drive in drives:
                    stats['drives'] += 1
                    try:
                        self.sync_drive(site_name, drive, state, stats)
                    except Exception as e:
                        print(f"      Error syncing drive: {e}")

        except Exception as e:
            print(f"Error during sync: {e}")

        # Update sync state
        state['last_sync'] = datetime.now().isoformat()
        state['sites_synced'] = [s['name'] for s in sites] if 'sites' in dir() else []
        self.save_sync_state(state)

        # Print summary
        print()
        print("=" * 60)
        print("Sync Complete")
        print("=" * 60)
        print(f"Sites processed: {stats['sites']}")
        print(f"Drives processed: {stats['drives']}")
        print(f"Files downloaded: {stats['downloaded']}")
        print(f"Files skipped (unchanged): {stats['skipped']}")
        print(f"Files failed: {stats['failed']}")
        print(f"Completed: {datetime.now().isoformat()}")

        # Log results
        log_file = self.log_dir / f"sharepoint_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'stats': stats,
                'state': state
            }, f, indent=2, default=str)

        return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Sync SharePoint documents to Secondbrain')
    parser.add_argument('--full', action='store_true', help='Force full sync (ignore last sync time)')
    args = parser.parse_args()

    syncer = SharePointSync()
    syncer.sync_all(incremental=not args.full)


if __name__ == "__main__":
    main()
