#!/usr/bin/env python3
"""
Test ChromaDB integration
"""
import sys
import os

# Don't add user site-packages - use virtual environment
# sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python314', 'site-packages'))

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

def test_chromadb():
    print("🧪 Testing ChromaDB integration...")

    try:
        # Initialize ChromaDB
        client = chromadb.PersistentClient(path="./data/chroma_db")

        # Get collection
        collection_name = "documents"
        collection = client.get_collection(name=collection_name)
        print(f"✅ Connected to collection '{collection_name}'")

        # Count documents
        count = collection.count()
        print(f"📊 Current document count: {count}")

        # Test search
        model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        query = "how to cancel membership"
        query_embedding = model.encode(query, convert_to_numpy=True)

        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=3
        )

        print(f"\n🔍 Search results for: '{query}'")
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
            print(f"\n--- Result {i} ---")
            print(f"Text: {doc[:200]}...")
            print(f"Question: {metadata.get('question', 'N/A')}")
            print(f"Category: {metadata.get('category', 'N/A')}")

        print("\n✅ ChromaDB test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chromadb()