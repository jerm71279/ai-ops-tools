#!/usr/bin/env python3
"""
Search for Celebration Church documents in SharePoint downloads
"""
from pathlib import Path
import re

SEARCH_DIR = Path("input_documents/sharepoint_all")

def search_files():
    """Search for Celebration Church related files"""
    print("=" * 70)
    print("🔍 Searching for Celebration Church Documents")
    print("=" * 70)
    print()

    keywords = [
        "celebration",
        "church",
        "scope of work",
        "sow",
        "proposal"
    ]

    # Search by filename
    print("📄 Searching by filename...")
    all_files = list(SEARCH_DIR.rglob("*.*"))

    matches = []
    for file_path in all_files:
        filename_lower = file_path.name.lower()

        # Check for Celebration Church
        if "celebration" in filename_lower or "church" in filename_lower:
            matches.append((file_path, "Exact match: Celebration/Church"))
        # Check for common SOW/proposal patterns
        elif any(kw in filename_lower for kw in ["scope", "sow", "proposal", "statement"]):
            # Check if it might be related (checking parent folder too)
            parent_lower = str(file_path.parent).lower()
            if "celebration" in parent_lower or "church" in parent_lower:
                matches.append((file_path, "SOW/Proposal in Celebration folder"))

    if matches:
        print(f"\n✅ Found {len(matches)} potential matches:\n")
        for file_path, reason in matches:
            print(f"  📁 {file_path.relative_to(SEARCH_DIR)}")
            print(f"     Reason: {reason}")
            print()
    else:
        print("❌ No files found with 'celebration' or 'church' in filename\n")

    # List all files by site to help identify
    print("\n" + "=" * 70)
    print("📊 Files by SharePoint Site")
    print("=" * 70)
    print()

    sites = {}
    for file_path in all_files:
        if file_path.is_file():
            parts = file_path.relative_to(SEARCH_DIR).parts
            if len(parts) > 0:
                site_name = parts[0]
                if site_name not in sites:
                    sites[site_name] = []
                sites[site_name].append(file_path.name)

    # Show sites with file counts
    sorted_sites = sorted(sites.items(), key=lambda x: len(x[1]), reverse=True)

    for site, files in sorted_sites[:15]:  # Top 15 sites
        print(f"  📂 {site}: {len(files)} files")
        # Show first few files as sample
        for f in files[:3]:
            print(f"     • {f[:60]}")
        if len(files) > 3:
            print(f"     ... and {len(files) - 3} more")
        print()

if __name__ == "__main__":
    search_files()
