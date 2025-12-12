#!/usr/bin/env python3
"""
Organize Obsidian Notes by Tags
Moves notes from root notes/ directory into SharePoint folder structure based on frontmatter tags.

Usage:
    python organize_notes_by_tags.py           # Dry run (shows what would be moved)
    python organize_notes_by_tags.py --execute # Actually move files
"""
import os
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime

OBSIDIAN_VAULT_PATH = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault")
NOTES_DIR = OBSIDIAN_VAULT_PATH / "notes"
LOG_DIR = Path(__file__).parent / "logs"

# Tag to folder mapping (priority order - first match wins)
# Format: (tag_pattern, destination_folder)
TAG_MAPPINGS = [
    # Technical + Preservation Hold Library
    (["oberaconnect-technical", "preservation-hold-library"], "sharepoint/Technical/Preservation Hold Library"),
    # Technical only
    (["oberaconnect-technical"], "sharepoint/Technical/Documents"),

    # Admin + Preservation Hold Library
    (["oberaconnect-admin", "preservation-hold-library"], "sharepoint/Admin/Preservation Hold Library"),
    # Admin only
    (["oberaconnect-admin"], "sharepoint/Admin/Documents"),

    # Shared Directory + Preservation Hold Library
    (["oberaconnect-shared-directory", "preservation-hold-library"], "sharepoint/Shared/Preservation Hold Library"),
    # Shared Directory only
    (["oberaconnect-shared-directory"], "sharepoint/Shared/Documents"),

    # IT related tags
    (["azure"], "sharepoint/IT/Documents"),
    (["security"], "sharepoint/IT/Documents"),
    (["authentication"], "sharepoint/IT/Documents"),

    # Device configurations -> Technical
    (["obera-connect-managed-service-device-configurations"], "sharepoint/Technical/Documents"),

    # Marketing -> Shared
    (["marketing"], "sharepoint/Shared/Documents"),

    # Onboarding -> Admin
    (["onboarding"], "sharepoint/Admin/Documents"),

    # Compliance -> Admin
    (["compliance"], "sharepoint/Admin/Documents"),

    # Customer-specific tags -> Technical (site surveys, configs)
    (["sexton"], "sharepoint/Technical/Documents"),
]


def extract_tags(file_path: Path) -> list:
    """Extract tags from frontmatter of markdown file"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')[:1000]
        match = re.search(r'^tags:\s*(.+)$', content, re.MULTILINE)
        if match:
            tags = [t.strip().lower() for t in match.group(1).split(',')]
            return tags
    except Exception as e:
        print(f"  Error reading {file_path.name}: {e}")
    return []


def find_destination(tags: list) -> str:
    """Find destination folder based on tags (first matching rule wins)"""
    tags_lower = [t.lower() for t in tags]

    for required_tags, destination in TAG_MAPPINGS:
        if all(req_tag.lower() in tags_lower for req_tag in required_tags):
            return destination

    return None


def main():
    parser = argparse.ArgumentParser(description='Organize notes by tags')
    parser.add_argument('--execute', action='store_true', help='Actually move files (default is dry run)')
    args = parser.parse_args()

    dry_run = not args.execute

    print("=" * 70)
    print("Notes Organizer - Tag-Based Filing")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (no files will be moved)' if dry_run else 'EXECUTE (files will be moved)'}")
    print(f"Source: {NOTES_DIR}")
    print()

    if not NOTES_DIR.exists():
        print("Error: Notes directory not found")
        return

    # Get all markdown files in root notes directory (not in subdirectories)
    root_notes = list(NOTES_DIR.glob("*.md"))
    print(f"Found {len(root_notes)} notes in root directory")
    print()

    # Ensure destination folders exist
    destinations_used = set()
    for _, dest in TAG_MAPPINGS:
        dest_path = NOTES_DIR / dest
        if not dest_path.exists() and not dry_run:
            dest_path.mkdir(parents=True, exist_ok=True)
            print(f"Created: {dest}")

    # Process notes
    moved = 0
    skipped = 0
    no_match = 0
    errors = 0

    moves = []  # Track for summary

    for note_path in root_notes:
        tags = extract_tags(note_path)

        if not tags:
            no_match += 1
            continue

        destination = find_destination(tags)

        if destination:
            dest_path = NOTES_DIR / destination / note_path.name

            if dest_path.exists():
                skipped += 1
                continue

            moves.append((note_path.name[:50], destination, tags[:3]))

            if not dry_run:
                try:
                    # Ensure destination exists
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(note_path), str(dest_path))
                    moved += 1
                except Exception as e:
                    print(f"  Error moving {note_path.name}: {e}")
                    errors += 1
            else:
                moved += 1
        else:
            no_match += 1

    # Print moves
    if moves:
        print("Files to move:" if dry_run else "Files moved:")
        print("-" * 70)
        for name, dest, tags in moves[:30]:  # Show first 30
            print(f"  {name}...")
            print(f"    -> {dest}")
            print(f"       tags: {', '.join(tags)}")
        if len(moves) > 30:
            print(f"  ... and {len(moves) - 30} more")
        print()

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"{'Would move' if dry_run else 'Moved'}: {moved}")
    print(f"Skipped (already exists): {skipped}")
    print(f"No matching tags: {no_match}")
    if errors:
        print(f"Errors: {errors}")
    print()

    if dry_run and moved > 0:
        print("To execute, run:")
        print("  python organize_notes_by_tags.py --execute")

    # Log the run
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / "organize_notes.log"
    with open(log_file, 'a') as f:
        f.write(f"\n{datetime.now().isoformat()} - {'DRY RUN' if dry_run else 'EXECUTE'}\n")
        f.write(f"  Moved: {moved}, Skipped: {skipped}, No match: {no_match}, Errors: {errors}\n")


if __name__ == "__main__":
    main()
