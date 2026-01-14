import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Customer Checklist Sync
Runs after SharePoint sync to:
1. Check for updated circuit/network data in synced files
2. Sync customer checklist .md files to Preservation Hold Library

Runs daily at 5:15 AM (after sync_sharepoint.py)
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# Paths
MYVAULT_SHAREPOINT = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault/notes/sharepoint")
PRESERVATION_HOLD = MYVAULT_SHAREPOINT / "Shared" / "Preservation Hold Library"
SECONDBRAIN_INPUT = Path("/home/mavrick/Projects/Secondbrain/input_documents/sharepoint_all")
LOG_DIR = Path("/home/mavrick/Projects/Secondbrain/logs")
STATE_FILE = Path("/home/mavrick/Projects/Secondbrain/data/checklist_sync_state.json")

# Customer checklist files to sync
CHECKLIST_PATTERNS = [
    "Client_Name_*.md"
]


def load_state():
    """Load sync state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        'last_sync': None,
        'files_synced': {}
    }


def save_state(state):
    """Save sync state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, default=str)


def get_checklist_files():
    """Get all customer checklist files from main MyVault location"""
    files = []
    for pattern in CHECKLIST_PATTERNS:
        files.extend(MYVAULT_SHAREPOINT.glob(pattern))
    return sorted(files)


def sync_checklists_to_preservation():
    """Sync checklist files from main folder to Preservation Hold Library"""
    synced = []
    errors = []

    checklist_files = get_checklist_files()

    for src_file in checklist_files:
        dest_file = PRESERVATION_HOLD / src_file.name

        try:
            # Check if source is newer or dest doesn't exist
            should_sync = False

            if not dest_file.exists():
                should_sync = True
                reason = "new file"
            else:
                src_mtime = src_file.stat().st_mtime
                dest_mtime = dest_file.stat().st_mtime
                if src_mtime > dest_mtime:
                    should_sync = True
                    reason = "updated"

            if should_sync:
                shutil.copy2(src_file, dest_file)
                synced.append({
                    'file': src_file.name,
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"  Synced: {src_file.name} ({reason})")

        except Exception as e:
            errors.append({
                'file': src_file.name,
                'error': str(e)
            })
            print(f"  Error syncing {src_file.name}: {e}")

    return synced, errors


def check_for_circuit_updates():
    """
    Check if any circuit-related files were updated in SharePoint sync
    Returns list of potentially updated circuit data files
    """
    circuit_keywords = ['circuit', 'isp', 'network', 'wan', 'ip']
    updated_files = []

    # Check input_documents/sharepoint_all for recently modified files
    if SECONDBRAIN_INPUT.exists():
        for ext in ['.csv', '.xlsx', '.pdf']:
            for file in SECONDBRAIN_INPUT.rglob(f'*{ext}'):
                # Check if file was modified in last 24 hours
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if (datetime.now() - mtime).days < 1:
                    # Check if filename suggests circuit data
                    name_lower = file.name.lower()
                    if any(kw in name_lower for kw in circuit_keywords):
                        updated_files.append({
                            'path': str(file),
                            'name': file.name,
                            'modified': mtime.isoformat()
                        })

    return updated_files


def main():
    print("=" * 60)
    print("Customer Checklist Sync")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    state = load_state()

    # Step 1: Check for circuit data updates
    print("Checking for circuit data updates...")
    circuit_updates = check_for_circuit_updates()
    if circuit_updates:
        print(f"  Found {len(circuit_updates)} updated circuit-related files:")
        for f in circuit_updates:
            print(f"    - {f['name']}")
        print()
        print("  NOTE: Manual review may be needed to update checklists with new circuit data")
    else:
        print("  No recent circuit data updates found")
    print()

    # Step 2: Sync checklists to Preservation Hold Library
    print("Syncing checklists to Preservation Hold Library...")
    synced, errors = sync_checklists_to_preservation()

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Checklists synced: {len(synced)}")
    print(f"Errors: {len(errors)}")
    print(f"Circuit updates found: {len(circuit_updates)}")
    print(f"Completed: {datetime.now().isoformat()}")

    # Update state
    state['last_sync'] = datetime.now().isoformat()
    state['files_synced'] = {s['file']: s for s in synced}
    state['circuit_updates'] = circuit_updates
    save_state(state)

    # Log results
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"checklist_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    with open(log_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'synced': synced,
            'errors': errors,
            'circuit_updates': circuit_updates
        }, f, indent=2)

    return len(errors) == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
