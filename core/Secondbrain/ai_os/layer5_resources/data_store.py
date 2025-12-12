"""
Layer 5: Data Store
Unified data storage abstraction
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import AIConfig
from ..core.logging import get_logger


class DataStore:
    """
    Unified data storage for AI OS

    Supports:
    - Key-value storage
    - Vector storage (via ChromaDB)
    - File storage
    - State persistence
    """

    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.datastore")

        # Storage backends
        self._kv_store: Dict[str, Any] = {}
        self._vector_store = None
        self._file_store_path: Optional[Path] = None

        # Configuration
        resource_config = self.config.resources
        self._vector_config = resource_config.get("vector_db", {})
        self._state_config = resource_config.get("state_store", {})

    async def initialize(self) -> bool:
        """Initialize data store"""
        self.logger.info("Initializing Data Store...")

        # Initialize file storage
        data_path = Path(self.config.data_path)
        data_path.mkdir(parents=True, exist_ok=True)
        self._file_store_path = data_path / "files"
        self._file_store_path.mkdir(exist_ok=True)

        # Load persisted KV store
        kv_path = data_path / "kv_store.json"
        if kv_path.exists():
            with open(kv_path, 'r') as f:
                self._kv_store = json.load(f)

        # Initialize vector store (ChromaDB)
        try:
            await self._init_vector_store()
        except Exception as e:
            self.logger.warning(f"Vector store not available: {e}")

        self.logger.info("Data Store initialized")
        return True

    async def shutdown(self) -> bool:
        """Shutdown data store"""
        self.logger.info("Shutting down Data Store...")

        # Persist KV store
        await self._persist_kv()

        return True

    async def _init_vector_store(self):
        """Initialize ChromaDB vector store"""
        try:
            import chromadb

            persist_path = self._vector_config.get("persist_path", "./chromadb_data")
            collection_name = self._vector_config.get("collection_name", "ai_os_knowledge")

            client = chromadb.PersistentClient(path=persist_path)
            self._vector_store = client.get_or_create_collection(name=collection_name)

            self.logger.info(f"Vector store initialized: {collection_name}")

        except ImportError:
            self.logger.warning("chromadb not installed")
            self._vector_store = None

    async def _persist_kv(self):
        """Persist KV store to disk"""
        data_path = Path(self.config.data_path)
        kv_path = data_path / "kv_store.json"

        with open(kv_path, 'w') as f:
            json.dump(self._kv_store, f, indent=2, default=str)

    # Key-Value Operations
    async def store(self, key: str, value: Any, persist: bool = True):
        """Store a value"""
        self._kv_store[key] = value
        if persist:
            await self._persist_kv()

    async def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a value"""
        return self._kv_store.get(key, default)

    async def delete(self, key: str):
        """Delete a value"""
        if key in self._kv_store:
            del self._kv_store[key]
            await self._persist_kv()

    async def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix"""
        if prefix:
            return [k for k in self._kv_store.keys() if k.startswith(prefix)]
        return list(self._kv_store.keys())

    # Vector Operations
    async def add_embedding(
        self,
        id: str,
        text: str,
        metadata: Dict = None,
        embedding: List[float] = None
    ):
        """Add document with embedding to vector store"""
        if not self._vector_store:
            self.logger.warning("Vector store not available")
            return

        self._vector_store.add(
            ids=[id],
            documents=[text],
            metadatas=[metadata] if metadata else None,
            embeddings=[embedding] if embedding else None
        )

    async def search_similar(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict]:
        """Search for similar documents"""
        if not self._vector_store:
            return []

        results = self._vector_store.query(
            query_texts=[query],
            n_results=n_results
        )

        return [
            {
                "id": results["ids"][0][i],
                "document": results["documents"][0][i] if results["documents"] else None,
                "distance": results["distances"][0][i] if results.get("distances") else None,
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else None
            }
            for i in range(len(results["ids"][0]))
        ]

    # File Operations
    async def store_file(self, filename: str, content: bytes):
        """Store a file"""
        if self._file_store_path:
            file_path = self._file_store_path / filename
            file_path.write_bytes(content)

    async def retrieve_file(self, filename: str) -> Optional[bytes]:
        """Retrieve a file"""
        if self._file_store_path:
            file_path = self._file_store_path / filename
            if file_path.exists():
                return file_path.read_bytes()
        return None

    async def list_files(self) -> List[str]:
        """List stored files"""
        if self._file_store_path:
            return [f.name for f in self._file_store_path.iterdir() if f.is_file()]
        return []

    def get_status(self) -> Dict[str, Any]:
        """Get data store status"""
        return {
            "kv_entries": len(self._kv_store),
            "vector_store": self._vector_store is not None,
            "file_store": str(self._file_store_path) if self._file_store_path else None
        }
