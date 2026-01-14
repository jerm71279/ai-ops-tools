"""
Vector Store Manager - Simplified stub version
Handles vector embeddings and semantic search using ChromaDB
"""
from typing import List, Dict, Any, Optional
from pathlib import Path

from .config import CHROMA_DB_DIR


class VectorStore:
    """Manages vector embeddings for semantic search"""

    def __init__(self, persist_directory: Optional[Path] = None):
        self.persist_directory = persist_directory or CHROMA_DB_DIR
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Lazy import to avoid dependency issues if not installed
        try:
            import chromadb

            # Use PersistentClient for proper persistence
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory)
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="obsidian_notes",
                metadata={"description": "Second brain notes"}
            )

            self.enabled = True
            print(f"✓ Vector store initialized: {self.persist_directory}")

        except ImportError:
            print("⚠ ChromaDB not installed - vector search disabled")
            print("  Install with: pip install chromadb")
            self.enabled = False
            self.client = None
            self.collection = None

    def add_note(self, note_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add a note to the vector store"""
        if not self.enabled:
            return

        try:
            # Convert lists to strings for ChromaDB compatibility
            clean_metadata = {}
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, list):
                        clean_metadata[key] = ', '.join(str(v) for v in value)
                    else:
                        clean_metadata[key] = value

            self.collection.add(
                ids=[note_id],
                documents=[content],
                metadatas=[clean_metadata or {}]
            )
        except Exception as e:
            print(f"⚠ Vector store add failed: {e}")

    def semantic_search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search"""
        if not self.enabled:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            # Format results
            formatted = []
            if results['ids'] and results['ids'][0]:
                for i, note_id in enumerate(results['ids'][0]):
                    formatted.append({
                        'note_id': note_id,
                        'content': results['documents'][0][i] if results['documents'] else '',
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results.get('distances') else 0
                    })

            return formatted

        except Exception as e:
            print(f"⚠ Vector search failed: {e}")
            return []

    def update_note(self, note_id: str, content: str, metadata: Dict[str, Any] = None):
        """Update a note in the vector store"""
        if not self.enabled:
            return

        try:
            self.collection.update(
                ids=[note_id],
                documents=[content],
                metadatas=[metadata or {}]
            )
        except Exception as e:
            print(f"⚠ Vector store update failed: {e}")

    def delete_note(self, note_id: str):
        """Remove a note from the vector store"""
        if not self.enabled:
            return

        try:
            self.collection.delete(ids=[note_id])
        except Exception as e:
            print(f"⚠ Vector store delete failed: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        if not self.enabled:
            return {"enabled": False}

        try:
            count = self.collection.count()
            return {
                "enabled": True,
                "total_notes": count,
                "collection": "obsidian_notes"
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}
