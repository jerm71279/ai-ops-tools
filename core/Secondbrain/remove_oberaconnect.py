#!/usr/bin/env python3
"""
Remove all OberaConnect/copilot-buddy-bytes related content from vault
"""
import sys
from pathlib import Path
from config import OBSIDIAN_VAULT_PATH

def main():
    notes_dir = OBSIDIAN_VAULT_PATH / "notes"

    # Terms to search for removal
    remove_terms = [
        "oberaconnect",
        "obera",
        "cipp",
        "revio",
        "platform",
        "dashboard",
        "msp",
        "lovable"
    ]

    print(f"🗑️  Removing OberaConnect/Platform related content from vault")
    print(f"Directory: {notes_dir}")
    print()

    # Find all files to remove
    files_to_remove = []
    for note_path in notes_dir.glob("*.md"):
        name_lower = note_path.name.lower()

        # Check if filename contains any removal terms
        if any(term in name_lower for term in remove_terms):
            files_to_remove.append(note_path)

    print(f"📊 Found {len(files_to_remove)} files to remove")
    print()

    # Delete the files
    for file_path in files_to_remove:
        print(f"🗑️  Deleting: {file_path.name}")
        file_path.unlink()

    print()
    print("=" * 80)
    print("✅ Cleanup Complete!")
    print(f"🗑️  Deleted: {len(files_to_remove)} files")
    print(f"📚 Remaining notes: {len(list(notes_dir.glob('*.md')))}")
    print()

if __name__ == "__main__":
    main()
