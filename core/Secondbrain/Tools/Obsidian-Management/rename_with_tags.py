import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Rename notes to include primary tags at the front of filename
Format: [tag1][tag2] Original Title.md
"""
import re
from pathlib import Path
from core.obsidian_vault import ObsidianVault

def extract_tags_from_note(file_path: Path) -> list:
    """Extract tags from frontmatter"""
    content = file_path.read_text(encoding='utf-8')

    # Look for tags in frontmatter
    tags = []
    in_frontmatter = False
    in_tags_section = False

    for line in content.split('\n'):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                break  # End of frontmatter
            continue

        if in_frontmatter:
            if line.strip().startswith('tags:'):
                in_tags_section = True
                # Check if tags are on same line: "tags: tag1, tag2"
                if ':' in line:
                    tag_part = line.split(':', 1)[1].strip()
                    if tag_part:
                        tags.extend([t.strip() for t in tag_part.split(',')])
                continue

            if in_tags_section:
                if line.strip().startswith('- '):
                    # Tag list item
                    tag = line.strip()[2:].strip()
                    if tag:
                        tags.append(tag)
                elif not line.strip().startswith(' '):
                    # End of tags section
                    in_tags_section = False

    # Clean tags (remove # if present)
    tags = [t.replace('#', '').strip() for t in tags if t.strip()]

    return tags

def sanitize_for_filename(text: str) -> str:
    """Clean text for use in filename"""
    # Remove or replace invalid filename characters
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def rename_notes_with_tags(vault_path: Path, max_tags: int = 3, dry_run: bool = False):
    """Rename all notes to include primary tags"""

    vault = ObsidianVault(vault_path)
    notes_dir = vault_path / "notes"

    if not notes_dir.exists():
        print(f"❌ Notes directory not found: {notes_dir}")
        return

    renamed = 0
    skipped = 0
    errors = 0

    print(f"{'🔍 DRY RUN - No files will be renamed' if dry_run else '📝 Renaming notes with tags'}")
    print(f"Directory: {notes_dir}")
    print("=" * 80)
    print()

    for note_path in notes_dir.glob("*.md"):
        try:
            # Skip if already has tags in filename
            if note_path.name.startswith('['):
                skipped += 1
                continue

            # Extract tags
            tags = extract_tags_from_note(note_path)

            if not tags:
                print(f"⏭️  No tags: {note_path.name}")
                skipped += 1
                continue

            # Get primary tags (up to max_tags)
            primary_tags = tags[:max_tags]

            # Build new filename
            tag_prefix = ''.join(f'[{sanitize_for_filename(tag)}]' for tag in primary_tags)
            new_name = f"{tag_prefix} {note_path.name}"

            # Ensure unique filename
            new_path = note_path.parent / new_name
            counter = 1
            while new_path.exists():
                stem = note_path.stem
                new_name = f"{tag_prefix} {stem}_{counter}.md"
                new_path = note_path.parent / new_name
                counter += 1

            print(f"{'[DRY RUN] ' if dry_run else ''}✏️  {note_path.name}")
            print(f"         → {new_name}")

            if not dry_run:
                note_path.rename(new_path)

            renamed += 1
            print()

        except Exception as e:
            print(f"❌ Error processing {note_path.name}: {e}")
            errors += 1
            print()

    # Summary
    print("=" * 80)
    print("📊 Summary:")
    print(f"✅ Renamed: {renamed}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")

    if dry_run:
        print()
        print("💡 This was a dry run. Run without --dry-run to actually rename files.")

if __name__ == "__main__":
    import sys

    from config import OBSIDIAN_VAULT_PATH

    # Check for dry-run flag
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    # Check for max-tags setting
    max_tags = 3
    for arg in sys.argv:
        if arg.startswith('--max-tags='):
            max_tags = int(arg.split('=')[1])

    print()
    print("🏷️  Note Renaming Tool")
    print("=" * 80)
    print(f"Vault: {OBSIDIAN_VAULT_PATH}")
    print(f"Max tags per filename: {max_tags}")
    print()

    rename_notes_with_tags(OBSIDIAN_VAULT_PATH, max_tags=max_tags, dry_run=dry_run)
