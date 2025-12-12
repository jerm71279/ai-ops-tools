#!/usr/bin/env python3
"""
Batch document processor
Processes documents from input_documents and creates structured notes in Obsidian vault
"""
import sys
from pathlib import Path
from datetime import datetime
from document_processor import DocumentProcessor
from claude_processor import ClaudeProcessor
from obsidian_vault import ObsidianVault
from vector_store import VectorStore

def get_folder_tags(file_path: Path, base_dir: Path) -> list:
    """Extract folder names as tags"""
    relative_path = file_path.relative_to(base_dir)
    folder_parts = relative_path.parts[:-1]  # Exclude filename

    # Convert folder names to tags
    tags = []
    for part in folder_parts:
        # Clean up folder name for tag
        tag = part.lower().replace(' ', '-').replace('_', '-')
        tag = ''.join(c for c in tag if c.isalnum() or c == '-')
        if tag and tag != 'oberaconnect':  # Skip root folder
            tags.append(tag)

    return tags

def process_documents(file_pattern: str = "*.html", limit: int = None):
    """Process documents matching pattern"""

    print("=" * 60)
    print("🚀 Batch Document Processor")
    print("=" * 60)
    print()

    # Initialize components
    doc_processor = DocumentProcessor()
    claude_processor = ClaudeProcessor()
    vault = ObsidianVault()
    vector_store = VectorStore()

    # Find files
    input_dir = Path("input_documents")
    files = list(input_dir.rglob(file_pattern))

    if limit:
        files = files[:limit]

    print(f"📁 Found {len(files)} files to process")
    print()

    results = {
        "processed": [],
        "failed": [],
        "skipped": []
    }

    for i, file_path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Processing: {file_path.name}")

        try:
            # Extract content
            doc_data = doc_processor.process_file(file_path)

            if "error" in doc_data:
                print(f"  ⚠️  Error: {doc_data['error']}")
                results["failed"].append(file_path.name)
                continue

            # Skip if no content
            if not doc_data["raw_content"] or len(doc_data["raw_content"]) < 50:
                print(f"  ⏭️  Skipped: Content too short")
                results["skipped"].append(file_path.name)
                continue

            # Get folder tags
            folder_tags = get_folder_tags(file_path, input_dir)

            # Structure with Claude
            print(f"  🤖 Structuring with Claude AI...")
            structured = claude_processor.structure_content(
                doc_data["raw_content"][:10000],  # Limit to 10k chars for API
                existing_concepts=[]
            )

            # Add folder tags
            if "tags" not in structured:
                structured["tags"] = []
            structured["tags"].extend(folder_tags)
            structured["tags"] = list(set(structured["tags"]))  # Remove duplicates

            # Add source metadata
            if "metadata" not in structured:
                structured["metadata"] = {}
            structured["metadata"]["source_file"] = str(file_path)
            structured["metadata"]["processed_date"] = datetime.now().isoformat()

            # Create note in vault
            print(f"  📝 Creating note in Obsidian vault...")
            note_result = vault.create_note(structured, note_type="processed")

            # Add to vector store
            if vector_store.enabled:
                print(f"  🔍 Adding to vector store...")
                vector_store.add_note(
                    note_id=note_result["note_id"],
                    content=structured.get("content", ""),
                    metadata={"title": structured.get("title", "")}
                )

            print(f"  ✅ Success: {note_result['title']}")
            print(f"     Tags: {', '.join(structured['tags'])}")
            results["processed"].append(file_path.name)

        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
            results["failed"].append(file_path.name)

        print()

    # Summary
    print("=" * 60)
    print("📊 Processing Summary")
    print("=" * 60)
    print(f"✅ Processed: {len(results['processed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⏭️  Skipped: {len(results['skipped'])}")
    print()

    if results["failed"]:
        print("Failed files:")
        for f in results["failed"][:10]:
            print(f"  - {f}")
        if len(results["failed"]) > 10:
            print(f"  ... and {len(results['failed']) - 10} more")

    return results

if __name__ == "__main__":
    # Get pattern from command line or use default
    pattern = sys.argv[1] if len(sys.argv) > 1 else "*.html"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"Pattern: {pattern}")
    if limit:
        print(f"Limit: {limit} files")
    print()

    results = process_documents(pattern, limit)

    print(f"\n✨ Done! Check your Obsidian vault at:")
    print(f"   C:\\Users\\JeremySmith\\OneDrive - Obera Connect\\MyVault\\notes\\")
