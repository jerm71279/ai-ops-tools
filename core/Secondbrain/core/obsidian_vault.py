"""
Obsidian Vault Manager - Simplified stub version
Handles interactions with Obsidian vault files
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .config import OBSIDIAN_VAULT_PATH
from .html_generator import generate_html_document


class ObsidianVault:
    """Manages Obsidian vault operations"""

    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = Path(vault_path) if vault_path else OBSIDIAN_VAULT_PATH

        # Ensure vault exists
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        print(f"✓ Connected to Obsidian vault: {self.vault_path}")

    def create_note(self, structured_data: Dict[str, Any], note_type: str = "processed", subfolder: str = None) -> Dict[str, Any]:
        """Create a new note in the vault

        Args:
            structured_data: Note data including title, content, tags, etc.
            note_type: Type of note (processed, inbox, etc.)
            subfolder: Optional subfolder path within the base folder (e.g., "sharepoint/it/documents")
        """
        title = structured_data.get("title", "Untitled")

        # Sanitize filename
        filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = filename.replace(' ', '_') + '.md'

        # Determine folder based on note_type
        folder_map = {
            "inbox": "inbox",
            "processed": "notes",
            "concept": "notes",
            "process": "notes",
            "project": "projects"
        }
        folder = folder_map.get(note_type, "notes")

        # Build path with optional subfolder
        if subfolder:
            note_path = self.vault_path / folder / subfolder / filename
        else:
            note_path = self.vault_path / folder / filename

        # Build markdown content
        content = self._build_markdown(structured_data)

        # Write markdown file
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text(content, encoding='utf-8')

        # Also generate HTML with OberaConnect branding
        html_dir = self.vault_path / "html_output"
        if subfolder:
            html_path = html_dir / subfolder / (note_path.stem + '.html')
        else:
            html_path = html_dir / (note_path.stem + '.html')

        try:
            generate_html_document(structured_data, html_path)
        except Exception as e:
            print(f"Warning: HTML generation failed: {e}")

        return {
            "note_id": filename,
            "file_path": str(note_path),
            "html_path": str(html_path),
            "title": title,
            "created": datetime.now().isoformat()
        }

    def update_note(self, note_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing note"""
        # Find the note file
        note_path = self._find_note(note_id)

        if not note_path:
            return {"error": f"Note not found: {note_id}"}

        # Read current content
        content = note_path.read_text(encoding='utf-8')

        # Apply updates (simplified - just append for now)
        if 'content' in updates:
            content += f"\n\n{updates['content']}"

        # Write back
        note_path.write_text(content, encoding='utf-8')

        return {
            "note_id": note_id,
            "updated": datetime.now().isoformat(),
            "path": str(note_path)
        }

    def search_notes(self, query: str = "", tags: List[str] = None,
                    concepts: List[str] = None) -> List[Dict[str, Any]]:
        """Search notes in vault"""
        results = []

        # Search all markdown files
        for note_path in self.vault_path.rglob("*.md"):
            content = note_path.read_text(encoding='utf-8')

            # Simple search logic
            if query and query.lower() in content.lower():
                results.append(self._note_info(note_path))
            elif tags and any(f"#{tag}" in content for tag in tags):
                results.append(self._note_info(note_path))
            elif concepts and any(concept.lower() in content.lower() for concept in concepts):
                results.append(self._note_info(note_path))

        return results

    def get_note_content(self, note_id: str) -> Optional[str]:
        """Get full content of a note"""
        note_path = self._find_note(note_id)
        if note_path:
            return note_path.read_text(encoding='utf-8')
        return None

    def list_all_concepts(self) -> List[str]:
        """Extract all unique concepts from notes"""
        concepts = set()

        for note_path in self.vault_path.rglob("*.md"):
            content = note_path.read_text(encoding='utf-8')
            # Extract concepts from frontmatter or content (simplified)
            if "concepts:" in content:
                # Very basic extraction
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() == "concepts:":
                        # Get next few lines
                        for j in range(i+1, min(i+10, len(lines))):
                            if lines[j].strip().startswith('- '):
                                concept = lines[j].strip()[2:]
                                concepts.add(concept)

        return sorted(list(concepts))

    def get_recent_notes(self, days: int = 1) -> List[Dict[str, Any]]:
        """Get notes created/modified in the last N days"""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        recent = []

        for note_path in self.vault_path.rglob("*.md"):
            mtime = datetime.fromtimestamp(note_path.stat().st_mtime)
            if mtime > cutoff:
                recent.append(self._note_info(note_path))

        return sorted(recent, key=lambda x: x['modified'], reverse=True)

    def _build_markdown(self, structured_data: Dict[str, Any]) -> str:
        """Build markdown content from structured data - metadata-focused, not verbose"""
        lines = []

        # Frontmatter with operational metadata
        lines.append("---")
        lines.append(f"title: {structured_data.get('title', 'Untitled')}")
        lines.append(f"created: {datetime.now().isoformat()}")

        # OberaConnect operational metadata
        if 'document_type' in structured_data:
            lines.append(f"document_type: {structured_data['document_type']}")
        if 'customer' in structured_data:
            lines.append(f"customer: {structured_data['customer']}")
        if 'technology' in structured_data:
            lines.append(f"technology: {structured_data['technology']}")

        if 'tags' in structured_data:
            lines.append(f"tags: {', '.join(structured_data['tags'])}")

        if 'concepts' in structured_data:
            lines.append("concepts:")
            for concept in structured_data['concepts']:
                lines.append(f"  - {concept}")

        if 'source_path' in structured_data:
            lines.append(f"source: {structured_data['source_path']}")

        lines.append("---")
        lines.append("")

        # Title
        lines.append(f"# {structured_data.get('title', 'Untitled')}")
        lines.append("")

        # Key data (concise operational info)
        if 'key_data' in structured_data and structured_data['key_data']:
            lines.append("## Key Data")
            for key, value in structured_data['key_data'].items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        # Raw content preview (source, not AI-generated)
        if 'raw_content' in structured_data:
            lines.append("## Source Preview")
            lines.append(structured_data['raw_content'])
            lines.append("")

        return '\n'.join(lines)

    def _find_note(self, note_id: str) -> Optional[Path]:
        """Find a note by ID (filename)"""
        for note_path in self.vault_path.rglob("*.md"):
            if note_path.name == note_id or note_path.stem == note_id:
                return note_path
        return None

    def _note_info(self, note_path: Path) -> Dict[str, Any]:
        """Extract basic info about a note"""
        stat = note_path.stat()
        return {
            "note_id": note_path.name,
            "title": note_path.stem.replace('_', ' '),
            "path": str(note_path),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size": stat.st_size
        }
