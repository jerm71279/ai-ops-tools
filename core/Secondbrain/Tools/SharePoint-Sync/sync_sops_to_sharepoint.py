#!/usr/bin/env python3
"""
Sync SOPs to SharePoint
Uploads local SOPs (MD, HTML, PDF) to OberaConnect Technical SharePoint site
"""
import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from upload_to_sharepoint import SharePointUploader


class SOPSyncer:
    def __init__(self):
        self.uploader = SharePointUploader()
        self.site_name = "OberaConnect Technical"
        self.base_folder = "SOPs"

        # Local SOP directories
        self.sop_dirs = {
            'md': Path("/home/mavrick/Projects/Secondbrain/SOPs"),
            'html': Path("/home/mavrick/Projects/Secondbrain/SOPs_html"),
            'pdf': Path("/home/mavrick/Projects/Secondbrain/SOPs_pdf")
        }

        # State file to track what's been uploaded
        self.state_file = Path("/home/mavrick/Projects/Secondbrain/data/sop_sync_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def get_file_hash(self, filepath):
        """Get MD5 hash of file for change detection"""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def load_state(self):
        """Load sync state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def save_state(self, state):
        """Save sync state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def get_sop_files(self, directory, extension):
        """Get all SOP files from a directory"""
        if not directory.exists():
            return []
        return list(directory.glob(f"SOP-*.{extension}"))

    def sync(self, force=False):
        """Sync all SOPs to SharePoint"""
        print(f"{'='*60}")
        print(f"SOP SharePoint Sync - {datetime.now().isoformat()}")
        print(f"{'='*60}")

        # Get site ID
        print(f"\nLooking up site: {self.site_name}...")
        site = self.uploader.find_site(self.site_name)
        if not site:
            print(f"ERROR: Site not found: {self.site_name}")
            return False

        site_id = site['id']
        print(f"Found site: {site.get('displayName')} ({site_id})")

        # Load previous sync state
        state = self.load_state()

        stats = {
            'uploaded': 0,
            'skipped': 0,
            'failed': 0
        }

        # Sync each format
        format_folders = {
            'md': 'Markdown',
            'html': 'HTML',
            'pdf': 'PDF'
        }

        for fmt, folder_name in format_folders.items():
            print(f"\n--- Syncing {fmt.upper()} files ---")
            source_dir = self.sop_dirs.get(fmt)

            if not source_dir or not source_dir.exists():
                print(f"  Directory not found: {source_dir}")
                continue

            files = self.get_sop_files(source_dir, fmt)
            print(f"  Found {len(files)} SOP files")

            target_folder = f"{self.base_folder}/{folder_name}"

            for filepath in files:
                file_key = f"{fmt}:{filepath.name}"
                current_hash = self.get_file_hash(filepath)

                # Check if file has changed
                if not force and file_key in state and state[file_key] == current_hash:
                    print(f"  Skipping (unchanged): {filepath.name}")
                    stats['skipped'] += 1
                    continue

                # Upload file
                print(f"  Uploading: {filepath.name} -> {target_folder}/")
                try:
                    result = self.uploader.upload_file(site_id, target_folder, str(filepath))

                    if result.get('success'):
                        print(f"    ✓ Uploaded: {result.get('webUrl', 'OK')}")
                        state[file_key] = current_hash
                        stats['uploaded'] += 1
                    else:
                        print(f"    ✗ Failed: {result.get('error', 'Unknown error')}")
                        stats['failed'] += 1

                except Exception as e:
                    print(f"    ✗ Error: {str(e)}")
                    stats['failed'] += 1

        # Save state
        self.save_state(state)

        # Summary
        print(f"\n{'='*60}")
        print(f"Sync Complete")
        print(f"{'='*60}")
        print(f"Uploaded: {stats['uploaded']}")
        print(f"Skipped (unchanged): {stats['skipped']}")
        print(f"Failed: {stats['failed']}")
        print(f"Completed: {datetime.now().isoformat()}")

        return stats['failed'] == 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Sync SOPs to SharePoint')
    parser.add_argument('--force', action='store_true', help='Force upload all files (ignore cache)')

    args = parser.parse_args()

    syncer = SOPSyncer()
    success = syncer.sync(force=args.force)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
