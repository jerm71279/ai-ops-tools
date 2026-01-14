import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Download documents from All Company SharePoint site
"""
from sharepoint_importer import SharePointImporter
from pathlib import Path

def main():
    importer = SharePointImporter()

    if not importer.token:
        print("❌ Failed to authenticate")
        return

    # List all sites to find "All Company"
    print("🔍 Searching for 'All Company' site...\n")
    sites = importer.list_sites()

    # Find the All Company site
    all_company_site = None
    for site in sites:
        if site['displayName'].lower() == 'all company':
            all_company_site = site
            break

    if not all_company_site:
        print("❌ Could not find 'All Company' site")
        return

    site_id = all_company_site['id']
    print(f"\n✅ Found 'All Company' site")
    print(f"   Site ID: {site_id}")
    print(f"   URL: {all_company_site['webUrl']}\n")

    # List document libraries
    print("📚 Listing document libraries...\n")
    libraries = importer.list_document_libraries(site_id)

    if not libraries:
        print("❌ No document libraries found")
        return

    # Download from each library
    output_base = Path("input_documents/sharepoint/allcompany")

    for library in libraries:
        library_name = library['name']
        drive_id = library['id']

        print(f"\n📥 Downloading from library: {library_name}")
        print(f"   Drive ID: {drive_id}")

        # Create output directory for this library
        output_dir = output_base / library_name.replace(' ', '_').lower()

        # Download files
        importer.download_files_from_library(
            site_id=site_id,
            drive_id=drive_id,
            output_dir=output_dir
        )

    print("\n" + "="*60)
    print("✅ All Company SharePoint download complete!")
    print(f"📁 Files saved to: {output_base}")
    print("="*60)

if __name__ == "__main__":
    main()
