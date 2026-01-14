import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Download documents from key OberaConnect SharePoint sites
"""
from sharepoint_importer import SharePointImporter
from pathlib import Path

def download_site(importer, site_name, output_subdir):
    """Download all documents from a specific site"""
    print(f"\n{'='*60}")
    print(f"🔍 Processing: {site_name}")
    print(f"{'='*60}\n")

    # Find the site
    sites = importer.list_sites()
    target_site = None

    for site in sites:
        if site['displayName'].lower() == site_name.lower():
            target_site = site
            break

    if not target_site:
        print(f"❌ Could not find '{site_name}' site\n")
        return 0

    site_id = target_site['id']
    print(f"✅ Found site: {site_name}")
    print(f"   URL: {target_site['webUrl']}\n")

    # List document libraries
    libraries = importer.list_document_libraries(site_id)

    if not libraries:
        print("❌ No document libraries found\n")
        return 0

    total_files = 0
    output_base = Path(f"input_documents/sharepoint/{output_subdir}")

    for library in libraries:
        library_name = library['name']
        drive_id = library['id']

        print(f"\n📥 Library: {library_name}")

        # Create output directory for this library
        output_dir = output_base / library_name.replace(' ', '_').lower()

        # Download files
        importer.download_files_from_library(
            site_id=site_id,
            drive_id=drive_id,
            output_dir=output_dir
        )

    return total_files

def main():
    importer = SharePointImporter()

    if not importer.token:
        print("❌ Failed to authenticate")
        return

    # Key sites to download from
    key_sites = [
        ("All Company", "allcompany"),
        ("OberaConnect Admin", "admin"),
        ("IT", "it"),
        ("OberaConnect Technical", "technical"),
        ("OberaConnect Shared Directory", "shared"),
    ]

    print("🚀 Starting download from key SharePoint sites...")
    print(f"   Total sites to process: {len(key_sites)}\n")

    total_downloaded = 0

    for site_name, output_dir in key_sites:
        files = download_site(importer, site_name, output_dir)
        total_downloaded += files

    print("\n" + "="*60)
    print("✅ SharePoint download complete!")
    print(f"📁 Files saved to: input_documents/sharepoint/")
    print("="*60)

if __name__ == "__main__":
    main()
