#!/usr/bin/env python3
"""Test ChromaDB persistence"""
import chromadb
from chromadb.config import Settings
from pathlib import Path

CHROMA_DIR = Path("/home/mavrick/Projects/Secondbrain/chroma_db")

print(f"Testing ChromaDB with: {CHROMA_DIR}")

# Initialize client
client = chromadb.Client(Settings(
    persist_directory=str(CHROMA_DIR),
    anonymized_telemetry=False
))

# Get or create collection
collection = client.get_or_create_collection(
    name="obsidian_notes",
    metadata={"description": "Second brain notes"}
)

# Check current count
count_before = collection.count()
print(f"Notes before: {count_before}")

# Add a test note
collection.add(
    ids=["test_1"],
    documents=["This is a test note about domain controller migration and Azure VHD export"],
    metadatas=[{"title": "Test Note", "tags": "test"}]
)

# Check count after add
count_after = collection.count()
print(f"Notes after add: {count_after}")

# Try to query
results = collection.query(
    query_texts=["domain controller"],
    n_results=5
)

print(f"\nQuery results: {len(results['ids'][0]) if results['ids'] else 0} found")
if results['ids'] and results['ids'][0]:
    print(f"First result: {results['documents'][0][0][:100]}")
