#!/usr/bin/env python3
"""
Remove copilot-buddy-bytes platform development files
Keep OberaConnect business/operational docs
"""
import sys
from pathlib import Path
from config import OBSIDIAN_VAULT_PATH

def main():
    notes_dir = OBSIDIAN_VAULT_PATH / "notes"

    # Platform development terms (the app being built)
    platform_dev_terms = [
        "platform.*debug",
        "platform.*status",
        "dashboard.*ui",
        "component.*library",
        "module.*structure",
        "deployment.*checklist",
        "phase.*integration",
        "api.*reference.*v",
        "system.*architecture",
        "documentation.*update.*v",
        "testing.*validation.*guide",
        "feature.*integration",
        "ui.*standardization",
        "navigation.*revamp",
        "mcp.*consolidation",
        "repetitive.*task",
        "developer.*handoff",
        "developer.*onboarding",
        "lovable.*platform",
        "sales.*portal",
        "admin.*dashboard",
        "cipp.*integration",
        "revio.*integration",
        "microsoft.*365.*integration",
        "database.*3nf",
        "network.*security.*diagram",
        "snmp.*syslog",
        "cmdb.*ninjaone",
        "audit.*logging.*system"
    ]

    print(f"🗑️  Removing platform development files (copilot-buddy-bytes)")
    print(f"✅ Keeping OberaConnect business/operational docs")
    print(f"Directory: {notes_dir}")
    print()

    # Find all files to remove
    files_to_remove = []
    for note_path in notes_dir.glob("*.md"):
        name_lower = note_path.name.lower()

        # Check if filename matches platform development patterns
        import re
        if any(re.search(term, name_lower) for term in platform_dev_terms):
            files_to_remove.append(note_path)

    print(f"📊 Found {len(files_to_remove)} platform development files")
    print()

    # Show first 10 for preview
    print("Preview (first 10):")
    for file_path in files_to_remove[:10]:
        print(f"  - {file_path.name}")
    if len(files_to_remove) > 10:
        print(f"  ... and {len(files_to_remove) - 10} more")
    print()

    # Delete the files
    for file_path in files_to_remove:
        file_path.unlink()

    print()
    print("=" * 80)
    print("✅ Cleanup Complete!")
    print(f"🗑️  Deleted: {len(files_to_remove)} platform development files")
    print(f"📚 Remaining notes: {len(list(notes_dir.glob('*.md')))}")
    print()

if __name__ == "__main__":
    main()
