#!/usr/bin/env python3
"""
Process all SharePoint documents into Second Brain
"""
from pathlib import Path
from document_processor import DocumentProcessor
from claude_processor import ClaudeProcessor
from obsidian_vault import ObsidianVault
from vector_store import VectorStore
from rename_with_tags import rename_notes_with_tags
import sys

OBSIDIAN_VAULT_PATH = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault")
CHROMA_DB_DIR = Path("/home/mavrick/Projects/Secondbrain/chroma_db")
SHAREPOINT_DIR = Path("input_documents/sharepoint")

def main():
    print("=" * 60)
    print("🚀 SharePoint Document Processor")
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

    print(f"📁 Found {len(all_files)} SharePoint files:")
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

    for i, file_path in enumerate(all_files, 1):
        try:
            print(f"\n[{i}/{len(all_files)}] Processing: {file_path.name}")

            # Extract content
            content = doc_processor.extract_content(str(file_path))

            if not content or len(content.strip()) < 100:
                print(f"⏭️  Skipped (insufficient content)")
                skipped += 1
                continue

            # Process with Claude - extract metadata only (not verbose content)
            result = claude_processor.structure_content(raw_content=content)

            # Create Obsidian note
            note_path = vault.create_note(
                title=result.get('title', file_path.stem),
                content=content[:500],  # Preserve first 500 chars of source, not AI-generated
                tags=result.get('tags', [])
            )

            # Add to vector store
            vector_store.add_note(
                note_id=note_path.stem,
                content=content[:1000],  # Index source content, not AI-generated
                metadata={
                    'title': result.get('title', file_path.stem),
                    'tags': result.get('tags', []),
                    'source': str(file_path),
                    'source_type': 'sharepoint',
                    'document_type': result.get('document_type', 'unknown'),
                    'customer': result.get('customer', 'unknown'),
                    'technology': result.get('technology', '')
                }
            )

            print(f"✅ Created note: {note_path.name}")
            processed += 1

        except Exception as e:
            print(f"❌ Error: {e}")
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
        rename_notes_with_tags(vault.notes_dir)
        print("✅ Tag renaming complete")
        print()

    print("✨ Done! Check your Obsidian vault at:")
    print(f"   {OBSIDIAN_VAULT_PATH / 'notes'}")

if __name__ == "__main__":
    main()
