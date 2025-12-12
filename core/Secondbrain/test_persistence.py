#!/usr/bin/env python3
"""Test ChromaDB persistence across sessions"""
import chromadb
from chromadb.config import Settings
from pathlib import Path

CHROMA_DIR = Path("/home/mavrick/Projects/Secondbrain/test_chroma_db")
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

print("=== Session 1: Adding data ===")
client1 = chromadb.Client(Settings(
    persist_directory=str(CHROMA_DIR),
    anonymized_telemetry=False
))
collection1 = client1.get_or_create_collection(name="test_collection")
print(f"Count before add: {collection1.count()}")

collection1.add(
    ids=["note_1"],
    documents=["This is about domain controller migration"],
    metadatas=[{"title": "DC Migration"}]
)
print(f"Count after add: {collection1.count()}")

# Try to explicitly persist if method exists
if hasattr(client1, 'persist'):
    print("Calling persist()...")
    client1.persist()
else:
    print("No persist() method found")

# Delete client reference
del client1
del collection1

print("\n=== Session 2: Reopening ===")
client2 = chromadb.Client(Settings(
    persist_directory=str(CHROMA_DIR),
    anonymized_telemetry=False
))
collection2 = client2.get_or_create_collection(name="test_collection")
print(f"Count in new session: {collection2.count()}")

if collection2.count() > 0:
    print("✓ Persistence works!")
else:
    print("✗ Persistence failed - data was not saved")
