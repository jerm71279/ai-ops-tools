import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Download ALL documents from ALL SharePoint sites
"""
from sharepoint_importer import SharePointImporter
from pathlib import Path
import re

def sanitize_folder_name(name: str) -> str:
    """Convert site name to safe folder name"""
    # Remove special characters, keep alphanumeric and spaces
    safe_name = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces with underscores
    safe_name = safe_name.replace(' ', '_')
    # Remove multiple underscores
    safe_name = re.sub(r'_+', '_', safe_name)
    return safe_name.lower()

def main():
    print("=" * 70)
    print("🚀 Complete SharePoint Download - All Sites")
    print("=" * 70)
    print()

    importer = SharePointImporter()

    if not importer.token:
        print("❌ Failed to authenticate")
        return

    # Get all sites
    print("📍 Fetching all SharePoint sites...")
    sites = importer.list_sites()

    print(f"\n✅ Found {len(sites)} SharePoint sites")
    print(f"📥 Beginning comprehensive download...\n")

    total_downloaded = 0
    total_skipped = 0
    sites_processed = 0
    sites_failed = 0

    for i, site in enumerate(sites, 1):
        site_name = site['displayName']
        site_id = site['id']

        # Skip workspace/designer sites (usually empty)
        if 'workspace' in site_name.lower() or 'designer' in site_name.lower() or 'pages' in site_name.lower():
            print(f"[{i}/{len(sites)}] ⏭️  Skipping: {site_name} (workspace/designer)")
            continue

        print(f"\n{'='*70}")
        print(f"[{i}/{len(sites)}] 📂 {site_name}")
        print(f"{'='*70}")

        try:
            # Get document libraries
            libraries = importer.list_document_libraries(site_id)

            if not libraries:
                print(f"   ℹ️  No document libraries found")
                sites_processed += 1
                continue

            # Create output folder
            folder_name = sanitize_folder_name(site_name)
            output_base = Path(f"input_documents/sharepoint_all/{folder_name}")

            for library in libraries:
                library_name = library['name']
                drive_id = library['id']

                print(f"\n   📚 Library: {library_name}")

                # Create library subfolder
                library_folder = sanitize_folder_name(library_name)
                output_dir = output_base / library_folder

                # Download files
                print(f"   ⬇️  Downloading to: {output_dir}")

                # Track before download
                before_count = len(list(output_dir.glob("*"))) if output_dir.exists() else 0

                importer.download_files_from_library(
                    site_id=site_id,
                    drive_id=drive_id,
                    output_dir=output_dir
                )

                # Track after download
                after_count = len(list(output_dir.glob("*"))) if output_dir.exists() else 0
                downloaded = after_count - before_count
                total_downloaded += downloaded

            sites_processed += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            sites_failed += 1
            continue

    print("\n" + "=" * 70)
    print("📊 Complete Download Summary")
    print("=" * 70)
    print(f"✅ Sites processed: {sites_processed}/{len(sites)}")
    print(f"❌ Sites failed: {sites_failed}")
    print(f"📥 Total files downloaded: {total_downloaded}")
    print()
    print(f"📁 All files saved to: input_documents/sharepoint_all/")
    print()
    print("🎯 Next steps:")
    print("   1. Process files: ./venv/bin/python process_batch.py 'sharepoint_all/*'")
    print("   2. Rebuild vector index: ./venv/bin/python rebuild_index.py")

if __name__ == "__main__":
    main()
