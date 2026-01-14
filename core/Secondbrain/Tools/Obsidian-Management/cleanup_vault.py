import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Clean up Obsidian vault - remove verbose AI-generated content
Keeps only frontmatter metadata and source preview
"""
import re
from pathlib import Path

VAULT_PATH = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault/notes")

def clean_note(file_path: Path) -> bool:
    """Remove verbose AI sections from a note, keep metadata"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_length = len(content)

        # Extract frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return False

        frontmatter = frontmatter_match.group(1)

        # Extract title from frontmatter
        title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"

        # Remove verbose sections
        # Pattern to match ## Summary, ## Content, ## Key Points sections
        cleaned = content

        # Remove ## Summary section and its content
        cleaned = re.sub(
            r'## Summary\n.*?(?=\n## |\n---|\Z)',
            '',
            cleaned,
            flags=re.DOTALL
        )

        # Remove ## Content section and its content
        cleaned = re.sub(
            r'## Content\n.*?(?=\n## |\n---|\Z)',
            '',
            cleaned,
            flags=re.DOTALL
        )

        # Remove ## Key Points section and its content
        cleaned = re.sub(
            r'## Key Points\n.*?(?=\n## |\n---|\Z)',
            '',
            cleaned,
            flags=re.DOTALL
        )

        # Clean up multiple blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # Only write if we actually removed content
        if len(cleaned) < original_length:
            file_path.write_text(cleaned, encoding='utf-8')
            removed = original_length - len(cleaned)
            return removed

        return 0

    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return 0

def main():
    print("=" * 60)
    print("Obsidian Vault Cleanup - Removing Verbose AI Content")
    print("=" * 60)
    print()

    if not VAULT_PATH.exists():
        print(f"Vault not found: {VAULT_PATH}")
        return

    notes = list(VAULT_PATH.rglob("*.md"))
    print(f"Found {len(notes)} notes to process")
    print()

    cleaned = 0
    total_removed = 0

    for i, note_path in enumerate(notes, 1):
        removed = clean_note(note_path)
        if removed:
            cleaned += 1
            total_removed += removed
            print(f"[{i}/{len(notes)}] Cleaned: {note_path.name[:50]} (-{removed} chars)")

    print()
    print("=" * 60)
    print("Cleanup Complete")
    print("=" * 60)
    print(f"Notes cleaned: {cleaned}/{len(notes)}")
    print(f"Total content removed: {total_removed:,} characters")
    print(f"Average per note: {total_removed // cleaned if cleaned else 0} chars")

if __name__ == "__main__":
    main()
