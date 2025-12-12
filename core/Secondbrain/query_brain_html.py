#!/usr/bin/env python3
"""
Enhanced Query with HTML Output - Clickable Obsidian Links
"""
import sys
import urllib.parse
from pathlib import Path
from vector_store import VectorStore
from obsidian_vault import ObsidianVault
from config import CHROMA_DB_DIR, OBSIDIAN_VAULT_PATH
import subprocess
import tempfile
from datetime import datetime

VAULT_NAME = "MyVault"

def generate_obsidian_link(file_path):
    """Generate Obsidian URI link to open file"""
    try:
        rel_path = Path(file_path).relative_to(OBSIDIAN_VAULT_PATH)
        encoded_path = urllib.parse.quote(str(rel_path))
        uri = f"obsidian://open?vault={VAULT_NAME}&file={encoded_path}"
        return uri
    except:
        return None

def query_brain_with_html(query: str, n_results: int = 5):
    """Query and generate HTML results with clickable links"""

    print(f"\n🔍 Searching for: '{query}'")
    print("=" * 80)
    print()

    # Initialize
    vector_store = VectorStore(CHROMA_DB_DIR)
    vault = ObsidianVault(OBSIDIAN_VAULT_PATH)

    # Search
    results = vector_store.semantic_search(query, n_results=n_results)

    if not results:
        print("❌ No results found")
        return []

    print(f"📚 Found {len(results)} relevant notes")
    print("🌐 Opening results in browser with clickable links...")
    print()

    # Generate HTML
    html_content = generate_html_results(query, results)

    # Save to Desktop for easy access
    desktop_path = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/Desktop")
    html_file = desktop_path / "RAG-Latest-Results.html"
    html_file.write_text(html_content, encoding='utf-8')

    # Convert to Windows path
    windows_path = "C:\\Users\\JeremySmith\\OneDrive - Obera Connect\\Desktop\\RAG-Latest-Results.html"

    # Open in browser using Windows path
    try:
        # Use PowerShell to open the file (more reliable than cmd.exe start)
        subprocess.run(['powershell.exe', '-Command', f'Start-Process "{windows_path}"'], check=False, cwd='C:\\')
        print(f"✅ Results opened in browser")
        print(f"📂 Also saved to Desktop: RAG-Latest-Results.html")
    except Exception as e:
        print(f"📂 Results saved to Desktop: RAG-Latest-Results.html")
        print(f"   Double-click the file to open it!")

    # Also show in terminal
    print_terminal_results(results)

    return results

def generate_html_results(query, results):
    """Generate HTML page with clickable links"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>RAG Results: {query}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }}
        .query {{
            color: #667eea;
            font-size: 1.5em;
            margin-bottom: 30px;
            font-weight: 600;
        }}
        .timestamp {{
            color: #999;
            font-size: 0.9em;
            margin-bottom: 30px;
        }}
        .result-card {{
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            transition: all 0.3s;
        }}
        .result-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .result-number {{
            display: inline-block;
            background: #667eea;
            color: white;
            width: 35px;
            height: 35px;
            line-height: 35px;
            text-align: center;
            border-radius: 50%;
            font-weight: bold;
            margin-right: 15px;
        }}
        .result-title {{
            font-size: 1.4em;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            display: inline;
        }}
        .meta {{
            display: flex;
            gap: 15px;
            margin: 15px 0;
            flex-wrap: wrap;
        }}
        .meta-item {{
            background: #e9ecef;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            color: #495057;
        }}
        .relevance {{
            background: #51cf66;
            color: white;
            font-weight: 600;
        }}
        .open-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s;
            margin-top: 15px;
            font-size: 1em;
        }}
        .open-button:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        .preview {{
            color: #555;
            line-height: 1.8;
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
        }}
        .tags {{
            margin-top: 15px;
        }}
        .tag {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            margin-right: 8px;
            margin-bottom: 8px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 Second Brain RAG Results</h1>
        <div class="query">"{query}"</div>
        <div class="timestamp">📅 {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
"""

    if not results:
        html += """
        <div style="text-align: center; padding: 60px; color: #999;">
            <h2>No results found</h2>
            <p>Try different keywords or broader search terms</p>
        </div>
"""
    else:
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            title = metadata.get('title', 'Untitled')
            file_path = metadata.get('file_path', '')
            tags = metadata.get('tags', [])
            distance = result.get('distance', 0)
            similarity = (1 - distance) * 100

            # Get preview
            content = result.get('document', '')
            preview = content[:300].replace('\n', ' ').strip() if content else 'No preview available'
            if len(content) > 300:
                preview += "..."

            # Generate Obsidian link
            obs_link = generate_obsidian_link(file_path) if file_path else '#'
            file_name = Path(file_path).name if file_path else 'Unknown'

            # Determine relevance color
            if similarity > 80:
                rel_color = '#51cf66'
            elif similarity > 50:
                rel_color = '#ffd43b'
            else:
                rel_color = '#ff6b6b'

            html += f"""
        <div class="result-card">
            <div>
                <span class="result-number">{i}</span>
                <span class="result-title">{title}</span>
            </div>

            <div class="meta">
                <span class="meta-item relevance" style="background: {rel_color}">
                    📊 {similarity:.1f}% Match
                </span>
                <span class="meta-item">📂 {file_name}</span>
            </div>
"""

            if tags and len(tags) > 0:
                html += '            <div class="tags">\n'
                for tag in tags[:8]:
                    html += f'                <span class="tag">{tag}</span>\n'
                html += '            </div>\n'

            html += f"""
            <div class="preview">{preview}</div>

            <a href="{obs_link}" class="open-button">
                🔗 Open in Obsidian
            </a>
        </div>
"""

    html += f"""
        <div class="footer">
            <p>Generated by Second Brain RAG</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Searched {len(results)} of 486 total documents
            </p>
        </div>
    </div>
</body>
</html>
"""

    return html

def print_terminal_results(results):
    """Print simplified results in terminal"""
    print("Terminal Summary:")
    print("-" * 80)

    for i, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        title = metadata.get('title', 'Untitled')
        distance = result.get('distance', 0)
        similarity = (1 - distance) * 100

        print(f"{i}. {title}")
        print(f"   📊 Relevance: {similarity:.1f}%")

    print("-" * 80)
    print()

def add_insight_to_note(note_path: Path, insight: str):
    """Add insight to an existing note"""
    try:
        content = note_path.read_text(encoding='utf-8')
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_section = f"\n\n---\n\n## Added Insight ({date_str})\n\n{insight}\n"
        content += new_section
        note_path.write_text(content, encoding='utf-8')
        print(f"✅ Insight added to {note_path.name}")
        return True
    except Exception as e:
        print(f"❌ Error adding insight: {e}")
        return False

def feedback_loop(results):
    """Interactive feedback loop"""
    if not results:
        return

    print("\n💬 Feedback Options")
    print("=" * 80)
    print("1. Add insight to a result")
    print("2. New search")
    print("3. Exit")
    print()

    choice = input("Your choice (1-3): ").strip()

    if choice == '1':
        print("\nWhich result? (1-{})".format(len(results)))
        idx = input("Result number: ").strip()
        try:
            idx = int(idx) - 1
            if 0 <= idx < len(results):
                file_path = results[idx].get('metadata', {}).get('file_path')
                if file_path:
                    print("\nEnter your insight (press Enter twice when done):")
                    lines = []
                    while True:
                        line = input()
                        if not line:
                            break
                        lines.append(line)

                    insight = '\n'.join(lines)
                    if insight.strip():
                        add_insight_to_note(Path(file_path), insight)
                        print("\n🔄 Rebuilding index...")
                        from rebuild_index import rebuild_index
                        rebuild_index()
        except:
            print("Invalid selection")

    elif choice == '2':
        return 'continue'

    return None

def interactive_mode():
    """Interactive mode with HTML output"""
    print()
    print("🧠 Second Brain - RAG with Clickable Links")
    print("=" * 80)
    print("Results open in browser with clickable Obsidian links!")
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

            results = query_brain_with_html(query, n_results=5)

            # Feedback loop
            while results:
                action = feedback_loop(results)
                if action == 'continue':
                    break
                elif action is None:
                    continue

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            break

def main():
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        results = query_brain_with_html(query, n_results=5)
        print("\n💡 Tip: Run without arguments for interactive mode")
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
