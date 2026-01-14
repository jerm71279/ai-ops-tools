import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Move all SharePoint notes into sharepoint/ subfolder
Keeps non-SharePoint notes in root notes/ directory
"""
from pathlib import Path
import shutil
import re

OBSIDIAN_VAULT_PATH = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault")

def has_sharepoint_tag(note_path: Path) -> bool:
    """Check if note has sharepoint-flat tag"""
    try:
        content = note_path.read_text(encoding='utf-8')
        # Check frontmatter for sharepoint-flat tag
        if 'tags: sharepoint-flat' in content or 'tags:' in content:
            # Parse frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = parts[1]
                    if 'sharepoint-flat' in frontmatter:
                        return True
        return False
    except Exception as e:
        print(f"Error reading {note_path}: {e}")
        return False

def main():
    print("=" * 70)
    print("📂 SharePoint Notes Organizer")
    print("   Moving SharePoint notes to sharepoint/ subfolder")
    print("=" * 70)
    print()

    notes_dir = OBSIDIAN_VAULT_PATH / "notes"
    sharepoint_dir = notes_dir / "sharepoint"

    if not notes_dir.exists():
        print("❌ Notes directory doesn't exist")
        return

    # Create sharepoint subfolder
    sharepoint_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {sharepoint_dir}")
    print()

    # Get all notes in root notes/ directory (not in subfolders)
    all_notes = list(notes_dir.glob("*.md"))

    print(f"📁 Found {len(all_notes)} notes in root notes/ directory")
    print()

    moved = 0
    kept = 0

    for note_path in all_notes:
        if has_sharepoint_tag(note_path):
            # Move to sharepoint subfolder
            dest_path = sharepoint_dir / note_path.name

            if not dest_path.exists():
                shutil.move(str(note_path), str(dest_path))
                print(f"→ sharepoint/: {note_path.name[:70]}")
                moved += 1
            else:
                print(f"⏭️  Already exists: {note_path.name[:70]}")
        else:
            # Keep in root
            kept += 1

    print("\n" + "=" * 70)
    print("📊 Organization Summary")
    print("=" * 70)
    print(f"✅ Moved to sharepoint/: {moved}")
    print(f"📝 Kept in notes/: {kept}")
    print()
    print(f"📂 Folder structure:")
    print(f"   {notes_dir}/")
    print(f"     ├── sharepoint/ ({moved} notes)")
    print(f"     └── (root) ({kept} notes)")

if __name__ == "__main__":
    main()
