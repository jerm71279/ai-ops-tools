import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Suggest Obsidian Wiki Links Between Notes
Analyzes notes for shared tags, concepts, and semantic similarity
"""
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from core.obsidian_vault import ObsidianVault
from core.vector_store import VectorStore

class LinkSuggester:
    """Suggest links between related notes"""

    def __init__(self, vault_path: Path, vector_store: VectorStore):
        self.vault = ObsidianVault(vault_path)
        self.vector_store = vector_store
        self.notes_dir = vault_path / "notes"

    def extract_note_metadata(self, file_path: Path) -> Dict:
        """Extract frontmatter and content from note"""
        content = file_path.read_text(encoding='utf-8')

        metadata = {
            'title': '',
            'tags': set(),
            'concepts': set(),
            'file_path': file_path,
            'file_name': file_path.name
        }

        # Parse frontmatter
        in_frontmatter = False
        in_tags = False
        in_concepts = False

        for line in content.split('\n'):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break  # End of frontmatter
                continue

            if in_frontmatter:
                # Extract title
                if line.startswith('title:'):
                    metadata['title'] = line.split(':', 1)[1].strip()

                # Extract tags
                elif line.startswith('tags:'):
                    in_tags = True
                    tag_part = line.split(':', 1)[1].strip()
                    if tag_part:
                        metadata['tags'].update([t.strip() for t in tag_part.split(',')])
                    continue

                # Extract concepts
                elif line.startswith('concepts:'):
                    in_concepts = True
                    in_tags = False
                    continue

                # Handle tag list items
                elif in_tags and not line.startswith(' '):
                    in_tags = False

                # Handle concept list items
                elif in_concepts:
                    if line.strip().startswith('- '):
                        concept = line.strip()[2:].strip()
                        if concept:
                            metadata['concepts'].add(concept)
                    elif not line.startswith(' '):
                        in_concepts = False

        return metadata

    def calculate_similarity(self, note1: Dict, note2: Dict) -> Tuple[float, List[str]]:
        """
        Calculate similarity score between two notes
        Returns: (score, reasons)
        """
        score = 0.0
        reasons = []

        # Shared tags (high weight)
        shared_tags = note1['tags'] & note2['tags']
        if shared_tags:
            tag_score = len(shared_tags) * 10
            score += tag_score
            reasons.append(f"{len(shared_tags)} shared tags: {', '.join(list(shared_tags)[:3])}")

        # Shared concepts (medium weight)
        shared_concepts = note1['concepts'] & note2['concepts']
        if shared_concepts:
            concept_score = len(shared_concepts) * 5
            score += concept_score
            reasons.append(f"{len(shared_concepts)} shared concepts: {', '.join(list(shared_concepts)[:3])}")

        # Title similarity (low weight)
        title1_words = set(note1['title'].lower().split())
        title2_words = set(note2['title'].lower().split())
        shared_words = title1_words & title2_words
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', '-', 'of'}
        shared_words = shared_words - common_words
        if len(shared_words) >= 2:
            score += len(shared_words) * 2
            reasons.append(f"Title similarity: {', '.join(list(shared_words)[:3])}")

        return score, reasons

    def find_link_suggestions(self, min_score: float = 15.0, max_suggestions_per_note: int = 5):
        """
        Find and suggest links between notes
        """
        print("🔍 Analyzing notes for link suggestions...")
        print()

        # Load all notes metadata
        notes = []
        for note_path in self.notes_dir.glob("*.md"):
            metadata = self.extract_note_metadata(note_path)
            if metadata['title']:
                notes.append(metadata)

        print(f"📚 Loaded {len(notes)} notes")
        print()

        # Calculate similarities
        suggestions = defaultdict(list)

        for i, note1 in enumerate(notes):
            for note2 in notes[i+1:]:
                score, reasons = self.calculate_similarity(note1, note2)

                if score >= min_score:
                    suggestions[note1['file_name']].append({
                        'target': note2['title'],
                        'target_file': note2['file_name'],
                        'score': score,
                        'reasons': reasons
                    })
                    suggestions[note2['file_name']].append({
                        'target': note1['title'],
                        'target_file': note1['file_name'],
                        'score': score,
                        'reasons': reasons
                    })

        # Sort and limit suggestions
        for file_name in suggestions:
            suggestions[file_name].sort(key=lambda x: x['score'], reverse=True)
            suggestions[file_name] = suggestions[file_name][:max_suggestions_per_note]

        return suggestions, notes

    def print_suggestions(self, suggestions: Dict, notes: List[Dict]):
        """Print link suggestions in a readable format"""

        if not suggestions:
            print("ℹ️  No link suggestions found with current threshold")
            print("   Try lowering min_score parameter")
            return

        # Create title to filename mapping
        note_map = {n['file_name']: n for n in notes}

        print("=" * 80)
        print("🔗 Link Suggestions")
        print("=" * 80)
        print()

        total_suggestions = sum(len(links) for links in suggestions.values())
        print(f"💡 Found {total_suggestions} potential links across {len(suggestions)} notes")
        print()

        # Sort notes by number of suggestions
        sorted_notes = sorted(suggestions.items(), key=lambda x: len(x[1]), reverse=True)

        for file_name, links in sorted_notes[:20]:  # Show top 20
            note = note_map[file_name]
            print(f"📝 {note['title']}")
            print(f"   File: {file_name}")
            print()

            for link in links:
                print(f"   → [[{link['target']}]] (score: {link['score']:.1f})")
                for reason in link['reasons']:
                    print(f"      • {reason}")
                print()

            print("-" * 80)
            print()

    def export_suggestions_to_file(self, suggestions: Dict, notes: List[Dict],
                                   output_file: Path):
        """Export suggestions to a markdown file"""
        note_map = {n['file_name']: n for n in notes}

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Obsidian Link Suggestions\n\n")
            f.write(f"Generated: {Path.cwd()}\n\n")

            total_suggestions = sum(len(links) for links in suggestions.values())
            f.write(f"**Total Suggestions**: {total_suggestions} potential links across {len(suggestions)} notes\n\n")
            f.write("---\n\n")

            sorted_notes = sorted(suggestions.items(), key=lambda x: len(x[1]), reverse=True)

            for file_name, links in sorted_notes:
                note = note_map[file_name]
                f.write(f"## {note['title']}\n\n")
                f.write(f"**File**: `{file_name}`\n\n")
                f.write("**Suggested Links**:\n\n")

                for link in links:
                    f.write(f"- [[{link['target']}]] (score: {link['score']:.1f})\n")
                    for reason in link['reasons']:
                        f.write(f"  - {reason}\n")
                    f.write("\n")

                f.write("---\n\n")

        print(f"✅ Exported suggestions to: {output_file}")


def main():
    import sys
    from config import OBSIDIAN_VAULT_PATH, CHROMA_DB_DIR

    # Parse arguments
    min_score = 15.0
    max_per_note = 5
    export = False

    for arg in sys.argv[1:]:
        if arg.startswith('--min-score='):
            min_score = float(arg.split('=')[1])
        elif arg.startswith('--max-per-note='):
            max_per_note = int(arg.split('=')[1])
        elif arg == '--export':
            export = True

    print()
    print("🔗 Link Suggestion Tool")
    print("=" * 80)
    print(f"Vault: {OBSIDIAN_VAULT_PATH}")
    print(f"Min similarity score: {min_score}")
    print(f"Max suggestions per note: {max_per_note}")
    print()

    # Initialize
    vector_store = VectorStore(CHROMA_DB_DIR)
    suggester = LinkSuggester(OBSIDIAN_VAULT_PATH, vector_store)

    # Find suggestions
    suggestions, notes = suggester.find_link_suggestions(
        min_score=min_score,
        max_suggestions_per_note=max_per_note
    )

    # Print to console
    suggester.print_suggestions(suggestions, notes)

    # Export if requested
    if export:
        output_file = Path("link_suggestions.md")
        suggester.export_suggestions_to_file(suggestions, notes, output_file)
        print()
        print(f"💾 Full report saved to: {output_file}")
    else:
        print()
        print("💡 Run with --export to save full report to file")

    print()
    print("=" * 80)
    print("Usage examples:")
    print("  ./venv/bin/python suggest_links.py")
    print("  ./venv/bin/python suggest_links.py --min-score=10")
    print("  ./venv/bin/python suggest_links.py --max-per-note=10 --export")
    print()


if __name__ == "__main__":
    main()
