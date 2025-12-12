#!/usr/bin/env python3
"""
Rebuild vector store index from current vault notes
"""
from pathlib import Path
from vector_store import VectorStore
from obsidian_vault import ObsidianVault
from config import CHROMA_DB_DIR, OBSIDIAN_VAULT_PATH

def rebuild_index():
    """Rebuild the vector store from scratch"""
    print("🔄 Rebuilding vector store index...")
    print()

    # Delete and recreate vector store
    import shutil
    if CHROMA_DB_DIR.exists():
        print(f"🗑️  Clearing old index: {CHROMA_DB_DIR}")
        shutil.rmtree(CHROMA_DB_DIR)

    vector_store = VectorStore(CHROMA_DB_DIR)
    vault = ObsidianVault(OBSIDIAN_VAULT_PATH)

    notes_dir = OBSIDIAN_VAULT_PATH / "notes"
    notes = list(notes_dir.rglob("*.md"))  # Use rglob to include subdirectories

    print(f"📚 Found {len(notes)} notes to index")
    print()

    indexed = 0
    for i, note_path in enumerate(notes, 1):
        try:
            # Read note content
            content = note_path.read_text(encoding='utf-8')

            # Extract title and metadata
            title = note_path.stem
            metadata = {
                'title': title,
                'file_path': str(note_path),
                'tags': []
            }

            # Parse frontmatter for tags
            in_frontmatter = False
            for line in content.split('\n'):
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break
                    continue

                if in_frontmatter:
                    if line.startswith('title:'):
                        metadata['title'] = line.split(':', 1)[1].strip()
                    elif line.startswith('tags:'):
                        tag_part = line.split(':', 1)[1].strip()
                        if tag_part:
                            metadata['tags'] = [t.strip() for t in tag_part.split(',')]

            # Add to vector store
            note_id = f"note_{i}"
            vector_store.add_note(note_id, content, metadata)
            indexed += 1

            if indexed % 10 == 0:
                print(f"✓ Indexed {indexed}/{len(notes)} notes...")

        except Exception as e:
            print(f"❌ Error indexing {note_path.name}: {e}")

    print()
    print("=" * 80)
    print("✅ Index rebuilt successfully!")
    print(f"📊 Total notes indexed: {indexed}/{len(notes)}")
    print()

if __name__ == "__main__":
    rebuild_index()
