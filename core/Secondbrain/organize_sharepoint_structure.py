#!/usr/bin/env python3
"""
Organize SharePoint notes into folder structure matching SharePoint sites
Creates the folder structure in Obsidian vault and moves notes accordingly
"""
from pathlib import Path
import shutil
import re

OBSIDIAN_VAULT_PATH = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault")
SHAREPOINT_SOURCE = Path("input_documents/sharepoint")

# Map of SharePoint source folders to destination folders in vault
FOLDER_MAPPING = {
    "it/preservation_hold_library": "sharepoint/IT/Preservation Hold Library",
    "it/documents": "sharepoint/IT/Documents",
    "admin/preservation_hold_library": "sharepoint/Admin/Preservation Hold Library",
    "admin/documents": "sharepoint/Admin/Documents",
    "technical/preservation_hold_library": "sharepoint/Technical/Preservation Hold Library",
    "technical/documents": "sharepoint/Technical/Documents",
    "shared/preservation_hold_library": "sharepoint/Shared/Preservation Hold Library",
    "shared/documents": "sharepoint/Shared/Documents",
    "allcompany/documents": "sharepoint/All Company/Documents",
}

def extract_guid_from_filename(filename: str) -> str:
    """Extract GUID from SharePoint filename (before timestamp)"""
    # Pattern: NAME_GUID_timestamp.ext
    # GUID is 8-4-4-4-12 format
    guid_pattern = r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})'
    match = re.search(guid_pattern, filename, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def find_source_folder(guid: str, sharepoint_dir: Path) -> str:
    """Find which SharePoint folder contains the file with this GUID"""
    if not guid:
        return None

    for folder_key in FOLDER_MAPPING.keys():
        folder_path = sharepoint_dir / folder_key
        if folder_path.exists():
            for file in folder_path.iterdir():
                if file.is_file() and guid.upper() in file.name.upper():
                    return folder_key

    return None

def main():
    print("=" * 70)
    print("🗂️  SharePoint Folder Structure Organizer")
    print("   Creating folder structure matching SharePoint sites")
    print("=" * 70)
    print()

    notes_dir = OBSIDIAN_VAULT_PATH / "notes"

    if not notes_dir.exists():
        print("❌ Notes directory doesn't exist")
        return

    # Get all notes currently in root notes/ directory
    all_notes = list(notes_dir.glob("*.md"))

    print(f"📁 Found {len(all_notes)} notes in notes/ directory")
    print(f"📂 SharePoint source: {SHAREPOINT_SOURCE}")
    print()

    # Create destination folder structure
    print("Creating folder structure:")
    for dest_folder in set(FOLDER_MAPPING.values()):
        folder_path = notes_dir / dest_folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dest_folder}/")
    print()

    moved = 0
    skipped = 0
    not_matched = 0

    for note_path in all_notes:
        # Extract GUID from note filename
        guid = extract_guid_from_filename(note_path.stem)

        if guid:
            # Find source folder
            source_folder = find_source_folder(guid, SHAREPOINT_SOURCE)

            if source_folder and source_folder in FOLDER_MAPPING:
                dest_folder = FOLDER_MAPPING[source_folder]
                dest_path = notes_dir / dest_folder / note_path.name

                if not dest_path.exists():
                    shutil.move(str(note_path), str(dest_path))
                    print(f"✅ {note_path.name[:60]}")
                    print(f"   → {dest_folder}/")
                    moved += 1
                else:
                    print(f"⏭️  Already exists: {note_path.name[:60]}")
                    skipped += 1
            else:
                # Not a SharePoint file, leave it in root
                not_matched += 1
        else:
            # No GUID found, likely not a SharePoint file
            not_matched += 1

    print("\n" + "=" * 70)
    print("📊 Organization Summary")
    print("=" * 70)
    print(f"✅ Moved into folders: {moved}")
    print(f"⏭️  Skipped (already in folders): {skipped}")
    print(f"📝 Left in root (non-SharePoint notes): {not_matched}")
    print()
    print("📂 Folder structure created:")
    print(f"   {notes_dir}/")
    print("     └── sharepoint/")
    print("           ├── IT/")
    print("           │   ├── Documents/")
    print("           │   └── Preservation Hold Library/")
    print("           ├── Admin/")
    print("           │   ├── Documents/")
    print("           │   └── Preservation Hold Library/")
    print("           ├── Technical/")
    print("           │   ├── Documents/")
    print("           │   └── Preservation Hold Library/")
    print("           ├── Shared/")
    print("           │   ├── Documents/")
    print("           │   └── Preservation Hold Library/")
    print("           └── All Company/")
    print("                └── Documents/")

if __name__ == "__main__":
    main()
