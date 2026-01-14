import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Process Slab knowledge base content into Second Brain
Similar to process_sharepoint.py but for Slab
"""
from pathlib import Path
from dotenv import load_dotenv

from slab_importer import SlabImporter
from core.document_processor import DocumentProcessor
from core.claude_processor import ClaudeProcessor
from core.obsidian_vault import ObsidianVault
from core.vector_store import VectorStore
from core.config import OBSIDIAN_VAULT_PATH, CHROMA_DB_DIR

# Load environment variables
load_dotenv()

SLAB_DOWNLOAD_DIR = Path("input_documents/slab")


def main():
    print("=" * 60)
    print("Slab Knowledge Base Processor")
    print("=" * 60)
    print()

    # Initialize components
    try:
        slab = SlabImporter()
    except ValueError as e:
        print(f"Error: {e}")
        print()
        print("To set up Slab integration:")
        print("1. Go to your Slab workspace settings")
        print("2. Navigate to Developer Tools > API & Webhooks")
        print("3. Copy your API token")
        print("4. Update .env with: SLAB_API_TOKEN=your_token")
        return

    doc_processor = DocumentProcessor()
    claude_processor = ClaudeProcessor()
    vault = ObsidianVault(OBSIDIAN_VAULT_PATH)
    vector_store = VectorStore(CHROMA_DB_DIR)

    print(f"Connected to Obsidian vault: {OBSIDIAN_VAULT_PATH}")
    print(f"Vector store: {CHROMA_DB_DIR}")
    print()

    # Download from Slab
    print("Downloading posts from Slab...")
    downloaded_files = slab.download_all_posts(SLAB_DOWNLOAD_DIR, limit=500)

    if not downloaded_files:
        print("No files downloaded from Slab")
        return

    print()
    print(f"Downloaded {len(downloaded_files)} files")
    print("Processing into Second Brain...")
    print()

    processed = 0
    failed = 0
    skipped = 0

    for i, file_path in enumerate(downloaded_files, 1):
        try:
            print(f"[{i}/{len(downloaded_files)}] Processing: {file_path.name[:50]}")

            # Read content
            content = file_path.read_text(encoding='utf-8')

            if not content or len(content.strip()) < 50:
                print(f"   Skipped: Content too short")
                skipped += 1
                continue

            # Determine subfolder from path
            relative_path = file_path.relative_to(SLAB_DOWNLOAD_DIR)
            subfolder_parts = relative_path.parent.parts
            if subfolder_parts:
                subfolder = "slab/" + "/".join(subfolder_parts)
            else:
                subfolder = "slab"

            # Process with Claude - extract metadata
            structured = claude_processor.structure_content(raw_content=content)

            if not structured:
                print(f"   Failed to structure content")
                failed += 1
                continue

            # Add source metadata
            structured['source_path'] = str(file_path)
            structured['source_type'] = 'slab'
            structured['raw_content'] = content[:500]

            # Create note in vault
            note_result = vault.create_note(
                structured_data=structured,
                note_type="processed",
                subfolder=subfolder
            )

            # Add to vector store
            if note_result and 'file_path' in note_result:
                vector_store.add_note(
                    note_id=note_result['note_id'],
                    content=content[:1000],
                    metadata={
                        'title': structured.get('title', file_path.stem),
                        'file_path': note_result['file_path'],
                        'tags': structured.get('tags', []),
                        'source_type': 'slab',
                        'document_type': structured.get('document_type', 'unknown'),
                        'customer': structured.get('customer', 'internal'),
                        'technology': structured.get('technology', '')
                    }
                )

            print(f"   Created: {note_result['note_id']}")
            processed += 1

        except Exception as e:
            print(f"   Error: {e}")
            failed += 1
            continue

    print()
    print("=" * 60)
    print("Processing Complete")
    print("=" * 60)
    print(f"Processed: {processed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print()
    print(f"Obsidian notes: {OBSIDIAN_VAULT_PATH / 'notes' / 'slab'}")
    print(f"HTML output: {OBSIDIAN_VAULT_PATH / 'html_output' / 'slab'}")


if __name__ == "__main__":
    main()
