#!/usr/bin/env python3
"""
Remove all copilot-buddy-bytes related content from vault
"""
import re
import sys
from pathlib import Path
from config import OBSIDIAN_VAULT_PATH

def remove_tag_from_note(file_path: Path, tag_to_remove: str):
    """Remove a specific tag from a note's frontmatter"""
    content = file_path.read_text(encoding='utf-8')

    # Parse and modify frontmatter
    lines = content.split('\n')
    new_lines = []
    in_frontmatter = False
    frontmatter_count = 0

    for line in lines:
        if line.strip() == '---':
            frontmatter_count += 1
            in_frontmatter = frontmatter_count == 1
            new_lines.append(line)
            continue

        if in_frontmatter and line.startswith('tags:'):
            # Remove tag from tags line
            tag_part = line.split(':', 1)[1]
            tags = [t.strip() for t in tag_part.split(',')]
            tags = [t for t in tags if tag_to_remove not in t]

            if tags:
                new_lines.append(f"tags: {', '.join(tags)}")
            else:
                # Skip line if no tags left
                continue
        else:
            new_lines.append(line)

    return '\n'.join(new_lines)

def main():
    notes_dir = OBSIDIAN_VAULT_PATH / "notes"
    tag_to_remove = "copilot-buddy-bytes"

    # Check for --dry-run flag
    dry_run = '--dry-run' in sys.argv

    print(f"🗑️  {'[DRY RUN] ' if dry_run else ''}Removing '{tag_to_remove}' content from vault")
    print(f"Directory: {notes_dir}")
    print()

    # Find all affected notes
    affected_files = []
    for note_path in notes_dir.glob("*.md"):
        content = note_path.read_text(encoding='utf-8')
        if tag_to_remove in content:
            affected_files.append(note_path)

    print(f"📊 Found {len(affected_files)} notes with '{tag_to_remove}' references")
    print()

    if dry_run:
        print("⚠️  DRY RUN MODE - No files will be modified")
    else:
        print("⚠️  This will:")
        print(f"   1. Remove '{tag_to_remove}' tag from all notes")
        print(f"   2. Delete notes that are ONLY about {tag_to_remove}")
    print()

    removed_count = 0
    cleaned_count = 0

    for file_path in affected_files:
        content = file_path.read_text(encoding='utf-8')

        # Check if this note is primarily about copilot-buddy-bytes
        title_lower = file_path.name.lower()

        if tag_to_remove in title_lower or 'copilot' in title_lower or 'buddy-bytes' in title_lower:
            # Delete this file entirely
            print(f"{'[DRY RUN] ' if dry_run else ''}🗑️  Deleting: {file_path.name}")
            if not dry_run:
                file_path.unlink()
            removed_count += 1
        else:
            # Just remove the tag
            print(f"{'[DRY RUN] ' if dry_run else ''}🧹 Cleaning tag from: {file_path.name}")
            if not dry_run:
                new_content = remove_tag_from_note(file_path, tag_to_remove)
                file_path.write_text(new_content, encoding='utf-8')
            cleaned_count += 1

    print()
    print("=" * 80)
    if dry_run:
        print("ℹ️  DRY RUN COMPLETE - No changes made")
        print("   Run without --dry-run to actually delete files")
    else:
        print("✅ Cleanup Complete!")
    print(f"🗑️  {'Would delete' if dry_run else 'Deleted'}: {removed_count} notes")
    print(f"🧹 {'Would clean' if dry_run else 'Cleaned'}: {cleaned_count} notes (tag removed)")
    print(f"📚 Remaining notes: {len(list(notes_dir.glob('*.md')))}")
    print()

if __name__ == "__main__":
    main()
