#!/usr/bin/env python3
"""
Process SharePoint documents while preserving folder structure
"""
from pathlib import Path
from document_processor import DocumentProcessor
from claude_processor import ClaudeProcessor
from obsidian_vault import ObsidianVault
from vector_store import VectorStore
from rename_with_tags import rename_notes_with_tags

OBSIDIAN_VAULT_PATH = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault")
CHROMA_DB_DIR = Path("/home/mavrick/Projects/Secondbrain/chroma_db")
SHAREPOINT_DIR = Path("input_documents/sharepoint")

def get_folder_structure(file_path: Path, base_dir: Path) -> str:
    """
    Extract relative folder path from SharePoint directory
    Example: input_documents/sharepoint/it/documents/file.pdf -> sharepoint/it/documents
    """
    relative_path = file_path.relative_to(base_dir)
    # Get all parent folders except the filename
    folder_parts = relative_path.parent.parts
    return str(Path(*folder_parts)) if folder_parts else None

def main():
    print("=" * 60)
    print("🚀 SharePoint Document Processor (Structured)")
    print("   Preserving folder hierarchy in Obsidian vault")
    print("=" * 60)
    print()

    # Initialize components
    doc_processor = DocumentProcessor()
    claude_processor = ClaudeProcessor()
    vault = ObsidianVault(OBSIDIAN_VAULT_PATH)
    vector_store = VectorStore(CHROMA_DB_DIR)

    print("✓ Document processor initialized")
    print(f"✓ Claude processor initialized (model: {claude_processor.model})")
    print(f"✓ Connected to Obsidian vault: {OBSIDIAN_VAULT_PATH}")
    print(f"✓ Vector store initialized: {CHROMA_DB_DIR}")

    # Find all SharePoint files
    pdf_files = list(SHAREPOINT_DIR.rglob("*.pdf"))
    docx_files = list(SHAREPOINT_DIR.rglob("*.docx"))
    txt_files = list(SHAREPOINT_DIR.rglob("*.txt"))

    all_files = pdf_files + docx_files + txt_files

    print(f"\n📁 Found {len(all_files)} SharePoint files:")
    print(f"   - {len(pdf_files)} PDFs")
    print(f"   - {len(docx_files)} DOCX files")
    print(f"   - {len(txt_files)} TXT files")
    print()

    if not all_files:
        print("❌ No files found to process")
        return

    processed = 0
    failed = 0
    skipped = 0

    # Track which files have already been processed (check if note exists)
    already_processed = set()
    notes_dir = OBSIDIAN_VAULT_PATH / "notes"
    if notes_dir.exists():
        # Get list of existing note titles (without .md extension)
        for note in notes_dir.rglob("*.md"):
            already_processed.add(note.stem)

    print(f"📝 {len(already_processed)} notes already exist in vault")
    print()

    for i, file_path in enumerate(all_files, 1):
        try:
            # Extract folder structure
            subfolder = get_folder_structure(file_path, Path("input_documents"))

            print(f"\n[{i}/{len(all_files)}] Processing: {file_path.name}")
            print(f"   Folder: {subfolder}")

            # Process file
            doc_data = doc_processor.process_file(file_path)

            if "error" in doc_data:
                print(f"⚠️  Error: {doc_data['error']}")
                failed += 1
                continue

            # Skip if no content
            if not doc_data["raw_content"] or len(doc_data["raw_content"]) < 100:
                print(f"⏭️  Skipped (insufficient content)")
                skipped += 1
                continue

            # Process with Claude
            structured_data = claude_processor.process_document(
                content=doc_data["raw_content"],
                filename=file_path.name,
                source_path=str(file_path)
            )

            # Create Obsidian note with subfolder structure
            note_result = vault.create_note(
                structured_data=structured_data,
                note_type="processed",
                subfolder=subfolder
            )

            # Add to vector store
            vector_store.add_note(
                note_id=note_result['note_id'],
                content=structured_data.get('content', ''),
                metadata={
                    'title': structured_data['title'],
                    'tags': structured_data.get('tags', []),
                    'source': str(file_path),
                    'source_type': 'sharepoint',
                    'subfolder': subfolder
                }
            )

            print(f"✅ Created: {note_result['path']}")
            processed += 1

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print("📊 Processing Summary")
    print("=" * 60)
    print(f"✅ Processed: {processed}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️  Skipped: {skipped}")
    print()

    if processed > 0:
        print("🏷️  Renaming files with tag prefixes...")
        # Rename within each SharePoint subfolder
        for subfolder in ["sharepoint/it", "sharepoint/admin", "sharepoint/technical", "sharepoint/shared", "sharepoint/allcompany"]:
            folder_path = OBSIDIAN_VAULT_PATH / "notes" / subfolder
            if folder_path.exists():
                print(f"   Renaming in: {subfolder}")
                rename_notes_with_tags(folder_path)
        print("✅ Tag renaming complete")
        print()

    print("✨ Done! Check your Obsidian vault at:")
    print(f"   {OBSIDIAN_VAULT_PATH / 'notes'}")
    print()
    print("📂 Folder structure preserved:")
    print("   notes/")
    print("     └── sharepoint/")
    print("           ├── it/")
    print("           ├── admin/")
    print("           ├── technical/")
    print("           ├── shared/")
    print("           └── allcompany/")

if __name__ == "__main__":
    main()
