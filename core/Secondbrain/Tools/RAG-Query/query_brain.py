import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Query your Second Brain using RAG (Retrieval-Augmented Generation)
"""
import sys
from pathlib import Path
from core.vector_store import VectorStore
from core.obsidian_vault import ObsidianVault
from core.config import CHROMA_DB_DIR, OBSIDIAN_VAULT_PATH

def query_brain(query: str, n_results: int = 5):
    """Query the knowledge base using semantic search"""

    print(f"\n🔍 Searching for: '{query}'")
    print("=" * 80)
    print()

    # Initialize vector store
    vector_store = VectorStore(CHROMA_DB_DIR)
    vault = ObsidianVault(OBSIDIAN_VAULT_PATH)

    # Search
    results = vector_store.semantic_search(query, n_results=n_results)

    if not results:
        print("❌ No results found")
        return

    print(f"📚 Found {len(results)} relevant notes:\n")

    for i, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        title = metadata.get('title', 'Untitled')
        file_path = metadata.get('file_path', '')
        tags = metadata.get('tags', [])
        distance = result.get('distance', 0)
        similarity = (1 - distance) * 100  # Convert to percentage

        print(f"{i}. {title}")
        print(f"   📂 File: {Path(file_path).name if file_path else 'Unknown'}")
        print(f"   🏷️  Tags: {', '.join(tags[:5]) if tags else 'None'}")
        print(f"   📊 Relevance: {similarity:.1f}%")

        # Show preview of content
        content = result.get('document', '')
        if content:
            preview = content[:200].replace('\n', ' ').strip()
            if len(content) > 200:
                preview += "..."
            print(f"   📝 Preview: {preview}")

        print()

    print("=" * 80)
    print("\n💡 Tips:")
    print("   - Ask questions: 'How do I configure SonicWall?'")
    print("   - Search topics: 'Azure backup procedures'")
    print("   - Find concepts: 'ISO 27001 compliance'")
    print()

def interactive_mode():
    """Run in interactive query mode"""
    print()
    print("🧠 Second Brain - Interactive Query Mode")
    print("=" * 80)
    print("Ask questions about your knowledge base!")
    print("Type 'exit' or 'quit' to stop")
    print()

    while True:
        try:
            query = input("💬 Your question: ").strip()

            if not query:
                continue

            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break

            query_brain(query, n_results=5)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            break

def main():
    if len(sys.argv) > 1:
        # Command line query
        query = ' '.join(sys.argv[1:])
        query_brain(query, n_results=5)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
