#!/usr/bin/env python3
"""
Process Slab exported/scraped content into Second Brain
Works with manually exported markdown or browser-scraped content
"""
from pathlib import Path
from dotenv import load_dotenv

from claude_processor import ClaudeProcessor
from obsidian_vault import ObsidianVault
from vector_store import VectorStore
from config import OBSIDIAN_VAULT_PATH, CHROMA_DB_DIR

# Load environment variables
load_dotenv()

# Input directories - check both scraped and manual export locations
SLAB_DIRS = [
    Path("input_documents/slab_scraped"),
    Path("input_documents/slab"),
    Path("input_documents/slab_export"),
]


def main():
    print("=" * 60)
    print("Slab Export Processor")
    print("=" * 60)
    print()

    # Find input directory with files
    input_dir = None
    all_files = []

    for slab_dir in SLAB_DIRS:
        if slab_dir.exists():
            files = list(slab_dir.rglob("*.txt")) + list(slab_dir.rglob("*.md"))
            if files:
                input_dir = slab_dir
                all_files = files
                break

    if not input_dir or not all_files:
        print("No Slab files found!")
        print()
        print("Run the scraper first:")
        print("  python3 slab_scraper.py")
        print()
        print("Or place exported files in one of:")
        for d in SLAB_DIRS:
            print(f"  {d}")
        return

    print(f"Input directory: {input_dir}")
    print(f"Found {len(all_files)} files to process")
    print()

    # Initialize components
    claude_processor = ClaudeProcessor()
    vault = ObsidianVault(OBSIDIAN_VAULT_PATH)
    vector_store = VectorStore(CHROMA_DB_DIR)

    print(f"Connected to Obsidian vault: {OBSIDIAN_VAULT_PATH}")
    print(f"Vector store: {CHROMA_DB_DIR}")
    print()

    processed = 0
    failed = 0
    skipped = 0

    for i, file_path in enumerate(all_files, 1):
        try:
            print(f"[{i}/{len(all_files)}] Processing: {file_path.name[:50]}")

            # Read content
            content = file_path.read_text(encoding='utf-8')

            if not content or len(content.strip()) < 50:
                print(f"   Skipped: Content too short")
                skipped += 1
                continue

            # Determine subfolder from path
            relative_path = file_path.relative_to(input_dir)
            subfolder_parts = relative_path.parent.parts
            if subfolder_parts:
                subfolder = "slab/" + "/".join(subfolder_parts)
            else:
                subfolder = "slab"

            # Process with Claude - extract metadata only
            structured = claude_processor.structure_content(raw_content=content)

            if not structured:
                print(f"   Failed to structure content")
                failed += 1
                continue

            # Add source metadata
            structured['source_path'] = str(file_path)
            structured['source_type'] = 'slab'
            structured['raw_content'] = content[:500]

            # Create note in vault (also generates HTML with logo)
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
