import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Reorganize existing SharePoint notes into folder structure
Moves notes from flat structure to hierarchical folders matching SharePoint sites
"""
from pathlib import Path
import shutil

OBSIDIAN_VAULT_PATH = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault")
SHAREPOINT_DIR = Path("input_documents/sharepoint")

def find_source_file(filename_base: str, sharepoint_dir: Path) -> Path:
    """Find the original SharePoint file to determine its folder"""
    # Remove tag prefixes like [tag1][tag2] from the beginning
    clean_name = filename_base
    while clean_name.startswith('['):
        if ']' in clean_name:
            clean_name = clean_name[clean_name.index(']')+1:].strip()
        else:
            break

    # Try to find matching file in SharePoint directory
    for file_path in sharepoint_dir.rglob("*"):
        if file_path.is_file():
            # Check if the note name matches the file name (roughly)
            file_stem = file_path.stem.split('_')[0]  # Get first part before GUID
            if clean_name.lower().startswith(file_stem.lower()[:20]):  # Match first 20 chars
                return file_path

            # Also try matching on the cleaned filename
            clean_file_name = "".join(c for c in file_path.stem if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_file_name = clean_file_name.replace(' ', '_')
            if clean_name.lower().startswith(clean_file_name.lower()[:20]):
                return file_path

    return None

def get_folder_for_file(file_path: Path, base_dir: Path) -> str:
    """Extract relative folder path"""
    relative_path = file_path.relative_to(base_dir)
    folder_parts = relative_path.parent.parts
    return str(Path(*folder_parts)) if folder_parts else None

def main():
    print("=" * 60)
    print("🔄 SharePoint Notes Reorganizer")
    print("   Moving notes into folder structure")
    print("=" * 60)
    print()

    notes_dir = OBSIDIAN_VAULT_PATH / "notes"

    if not notes_dir.exists():
        print("❌ Notes directory doesn't exist")
        return

    # Get all notes in the root notes directory (not in subfolders)
    flat_notes = list(notes_dir.glob("*.md"))

    print(f"📁 Found {len(flat_notes)} notes in root notes/ directory")
    print()

    moved = 0
    not_found = 0
    errors = 0

    for note_path in flat_notes:
        try:
            # Try to find the source SharePoint file
            source_file = find_source_file(note_path.stem, SHAREPOINT_DIR)

            if source_file:
                # Get the folder structure
                subfolder = get_folder_for_file(source_file, Path("input_documents"))

                if subfolder:
                    # Create destination folder
                    dest_folder = notes_dir / subfolder
                    dest_folder.mkdir(parents=True, exist_ok=True)

                    # Move the note
                    dest_path = dest_folder / note_path.name

                    if not dest_path.exists():
                        shutil.move(str(note_path), str(dest_path))
                        print(f"✅ Moved: {note_path.name}")
                        print(f"   → {subfolder}/")
                        moved += 1
                    else:
                        print(f"⏭️  Skipped: {note_path.name} (already exists in destination)")
                else:
                    print(f"⚠️  No subfolder: {note_path.name}")
                    not_found += 1
            else:
                print(f"❓ Source not found: {note_path.name}")
                not_found += 1

        except Exception as e:
            print(f"❌ Error processing {note_path.name}: {e}")
            errors += 1

    print("\n" + "=" * 60)
    print("📊 Reorganization Summary")
    print("=" * 60)
    print(f"✅ Moved: {moved}")
    print(f"❓ Not found/skipped: {not_found}")
    print(f"❌ Errors: {errors}")
    print()
    print(f"📂 Notes organized in: {notes_dir}")

if __name__ == "__main__":
    main()
