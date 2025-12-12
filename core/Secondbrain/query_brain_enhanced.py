#!/usr/bin/env python3
"""
Enhanced Query Your Second Brain with:
- Obsidian URI links to open files directly
- Feedback loop to add insights and documents
"""
import sys
import urllib.parse
from pathlib import Path
from vector_store import VectorStore
from obsidian_vault import ObsidianVault
from config import CHROMA_DB_DIR, OBSIDIAN_VAULT_PATH
import subprocess

VAULT_NAME = "MyVault"

def generate_obsidian_link(file_path):
    """Generate Obsidian URI link to open file"""
    # Extract relative path from vault
    try:
        rel_path = Path(file_path).relative_to(OBSIDIAN_VAULT_PATH)
        # URL encode the path
        encoded_path = urllib.parse.quote(str(rel_path))
        # Create Obsidian URI
        uri = f"obsidian://open?vault={VAULT_NAME}&file={encoded_path}"
        return uri
    except:
        return None

def open_in_obsidian(file_path):
    """Open file directly in Obsidian"""
    uri = generate_obsidian_link(file_path)
    if uri:
        try:
            # Windows command to open URI
            subprocess.run(['cmd.exe', '/c', 'start', uri], check=False)
            return True
        except:
            pass
    return False

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
        print()
        return []

    print(f"📚 Found {len(results)} relevant notes:\n")

    for i, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        title = metadata.get('title', 'Untitled')
        file_path = metadata.get('file_path', '')
        tags = metadata.get('tags', [])
        distance = result.get('distance', 0)
        similarity = (1 - distance) * 100

        print(f"{i}. {title}")
        print(f"   📂 File: {Path(file_path).name if file_path else 'Unknown'}")
        print(f"   🏷️  Tags: {', '.join(tags[:5]) if tags else 'None'}")
        print(f"   📊 Relevance: {similarity:.1f}%")

        # Generate Obsidian URI link
        if file_path:
            uri = generate_obsidian_link(file_path)
            if uri:
                print(f"   🔗 Open: {uri}")

        # Show preview
        content = result.get('document', '')
        if content:
            preview = content[:200].replace('\n', ' ').strip()
            if len(content) > 200:
                preview += "..."
            print(f"   📝 Preview: {preview}")

        print()

    return results

def add_insight_to_note(note_path: Path, insight: str):
    """Add insight to an existing note"""
    try:
        content = note_path.read_text(encoding='utf-8')

        # Add insight section
        timestamp = Path(__file__).stat().st_mtime
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        new_section = f"\n\n---\n\n## Added Insight ({date_str})\n\n{insight}\n"

        content += new_section
        note_path.write_text(content, encoding='utf-8')

        print(f"✅ Insight added to {note_path.name}")
        return True
    except Exception as e:
        print(f"❌ Error adding insight: {e}")
        return False

def add_new_document():
    """Add a new document to the vault"""
    print("\n📄 Add New Document")
    print("=" * 80)
    print()

    print("Choose source:")
    print("1. Paste text content")
    print("2. URL/Webpage")
    print("3. File path")
    print("4. Cancel")
    print()

    choice = input("Your choice (1-4): ").strip()

    if choice == '1':
        print("\nPaste your content (press Ctrl+Z then Enter when done):")
        print("-" * 80)
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        content = '\n'.join(lines)

        if content.strip():
            title = input("\nDocument title: ").strip()
            return create_note_from_content(title, content)

    elif choice == '2':
        url = input("\nEnter URL: ").strip()
        if url:
            return create_note_from_url(url)

    elif choice == '3':
        file_path = input("\nEnter file path: ").strip()
        if file_path and Path(file_path).exists():
            return create_note_from_file(Path(file_path))

    return False

def create_note_from_content(title: str, content: str):
    """Create a new note from text content"""
    try:
        from datetime import datetime

        vault = ObsidianVault(OBSIDIAN_VAULT_PATH)

        structured_data = {
            'title': title,
            'content': content,
            'tags': ['rag-added', 'user-insight'],
            'metadata': {
                'created': datetime.now().isoformat(),
                'source': 'RAG User Input'
            }
        }

        result = vault.create_note(structured_data, note_type='processed')
        print(f"\n✅ Note created: {result['title']}")
        print(f"   Path: {result['path']}")

        # Rebuild index
        print("\n🔄 Rebuilding vector index...")
        from rebuild_index import rebuild_index
        rebuild_index()

        return True
    except Exception as e:
        print(f"\n❌ Error creating note: {e}")
        return False

def create_note_from_url(url: str):
    """Create note from webpage"""
    try:
        import requests
        from bs4 import BeautifulSoup

        print(f"\n📥 Fetching content from {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.find('title')
        title = title.get_text() if title else url

        # Extract main content
        for script in soup(["script", "style"]):
            script.decompose()

        content = soup.get_text()
        lines = (line.strip() for line in content.splitlines())
        content = '\n'.join(line for line in lines if line)

        return create_note_from_content(title, content)

    except Exception as e:
        print(f"\n❌ Error fetching URL: {e}")
        return False

def create_note_from_file(file_path: Path):
    """Create note from file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        title = file_path.stem
        return create_note_from_content(title, content)
    except Exception as e:
        print(f"\n❌ Error reading file: {e}")
        return False

def feedback_loop(results):
    """Interactive feedback loop"""
    if not results:
        return

    print("\n" + "=" * 80)
    print("💬 Feedback Options")
    print("=" * 80)
    print()
    print("1. Add insight to a result")
    print("2. Open result in Obsidian")
    print("3. Add new document/insight")
    print("4. Continue searching")
    print("5. Exit")
    print()

    choice = input("Your choice (1-5): ").strip()

    if choice == '1':
        # Add insight
        print("\nWhich result? (1-{})".format(len(results)))
        idx = input("Result number: ").strip()
        try:
            idx = int(idx) - 1
            if 0 <= idx < len(results):
                file_path = results[idx].get('metadata', {}).get('file_path')
                if file_path:
                    print("\nEnter your insight:")
                    insight = input("> ").strip()
                    if insight:
                        add_insight_to_note(Path(file_path), insight)
                        print("\n🔄 Rebuilding index...")
                        from rebuild_index import rebuild_index
                        rebuild_index()
        except:
            print("Invalid selection")

    elif choice == '2':
        # Open in Obsidian
        print("\nWhich result? (1-{})".format(len(results)))
        idx = input("Result number: ").strip()
        try:
            idx = int(idx) - 1
            if 0 <= idx < len(results):
                file_path = results[idx].get('metadata', {}).get('file_path')
                if file_path:
                    if open_in_obsidian(file_path):
                        print(f"\n✅ Opening in Obsidian...")
                    else:
                        print(f"\n⚠️  Could not open. Manual link:")
                        print(f"   {generate_obsidian_link(file_path)}")
        except:
            print("Invalid selection")

    elif choice == '3':
        # Add new document
        add_new_document()

    elif choice == '4':
        # Continue searching
        return 'continue'

    else:
        # Exit
        return 'exit'

    return None

def interactive_mode():
    """Run in interactive query mode with feedback"""
    print()
    print("🧠 Second Brain - Enhanced Interactive Mode")
    print("=" * 80)
    print("Ask questions and add insights!")
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

            results = query_brain(query, n_results=5)

            # Feedback loop
            while True:
                action = feedback_loop(results)
                if action == 'continue':
                    break
                elif action == 'exit':
                    print("\n👋 Goodbye!")
                    return
                elif action is None:
                    continue

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            break

def main():
    if len(sys.argv) > 1:
        # Command line query
        query = ' '.join(sys.argv[1:])
        results = query_brain(query, n_results=5)

        # Offer feedback
        print("\n💡 Tip: Run without arguments for interactive mode with feedback options")
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
