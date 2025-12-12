#!/usr/bin/env python3
"""
Process ALL SharePoint documents from comprehensive download
"""
from pathlib import Path
from document_processor import DocumentProcessor
from obsidian_vault import ObsidianVault
from vector_store import VectorStore
from claude_processor import ClaudeProcessor
from config import OBSIDIAN_VAULT_PATH, CHROMA_DB_DIR

def main():
    print("=" * 70)
    print("🚀 Processing All SharePoint Documents")
    print("=" * 70)
    print()

    # Initialize
    processor = DocumentProcessor()
    vault = ObsidianVault(OBSIDIAN_VAULT_PATH)
    vector_store = VectorStore(CHROMA_DB_DIR)
    claude = ClaudeProcessor()

    # Find all files
    sharepoint_dir = Path("input_documents/sharepoint_all")

    pdf_files = list(sharepoint_dir.rglob("*.pdf"))
    docx_files = list(sharepoint_dir.rglob("*.docx"))
    txt_files = list(sharepoint_dir.rglob("*.txt"))

    all_files = pdf_files + docx_files + txt_files

    print(f"📁 Found {len(all_files)} total files:")
    print(f"   • {len(pdf_files)} PDFs")
    print(f"   • {len(docx_files)} DOCX")
    print(f"   • {len(txt_files)} TXT")
    print()

    processed = 0
    failed = 0
    skipped = 0

    for i, file_path in enumerate(all_files, 1):
        try:
            # Calculate subfolder path from sharepoint_all
            relative_path = file_path.relative_to(sharepoint_dir)
            # Use parent dirs as subfolder (e.g., "company_portal/preservation_hold_library")
            subfolder_parts = relative_path.parent.parts
            if subfolder_parts:
                subfolder = "sharepoint_all/" + "/".join(subfolder_parts)
            else:
                subfolder = "sharepoint_all"

            print(f"[{i}/{len(all_files)}] Processing: {file_path.name[:60]}")
            print(f"            Subfolder: {subfolder}")

            # Extract content using process_file method
            result = processor.process_file(file_path)

            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
                failed += 1
                continue

            content = result.get('raw_content', '')

            if not content:
                print(f"   ⏭️  Skipped: Unsupported file type")
                skipped += 1
                continue

            if not content or len(content.strip()) < 50:
                print(f"   ⏭️  Skipped: Content too short or empty")
                skipped += 1
                continue

            # Structure with Claude - extract metadata only (not verbose content)
            structured = claude.structure_content(raw_content=content)

            if not structured:
                print(f"   ❌ Failed to structure document")
                failed += 1
                continue

            # Add source metadata
            structured['source_path'] = str(file_path)
            structured['source_site'] = subfolder_parts[0] if subfolder_parts else "unknown"
            structured['raw_content'] = content[:500]  # Preserve source, not AI-generated

            # Create note in vault with subfolder
            note_result = vault.create_note(
                structured_data=structured,
                note_type="processed",
                subfolder=subfolder
            )

            # Add to vector store
            if note_result and 'file_path' in note_result:
                note_content = Path(note_result['file_path']).read_text(encoding='utf-8')
                vector_store.add_note(
                    note_id=note_result['note_id'],
                    content=note_content,
                    metadata={
                        'title': structured.get('title', file_path.stem),
                        'file_path': note_result['file_path'],
                        'tags': structured.get('tags', []),
                        'source_site': structured.get('source_site', 'unknown')
                    }
                )

            print(f"   ✅ Created: {note_result['note_id']}")
            processed += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
            continue

    print()
    print("=" * 70)
    print("📊 Processing Complete")
    print("=" * 70)
    print(f"✅ Processed: {processed}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️  Skipped: {skipped}")
    print()

if __name__ == "__main__":
    main()
