#!/usr/bin/env python3
"""
Test ChromaDB Cloud connection
"""
import sys
import os

# Add user site-packages to path
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python313', 'site-packages'))

import chromadb

def test_chroma_cloud():
    print("Testing ChromaDB Cloud connection...")

    try:
        client = chromadb.HttpClient(
            host="https://api.trychroma.com",
            api_key="ck-2BmLntY81Xwqh1P2pwD18A5NM3nWKjBxNtb8DQX2MD2V",
            tenant="default",
            database="lms-chatbot-database"
        )

        # Test creating a collection
        collection = client.create_collection(name="test_collection")
        print("✅ Successfully connected to ChromaDB Cloud!")
        print("✅ Created test collection")

        # Clean up
        client.delete_collection(name="test_collection")
        print("✅ Cleaned up test collection")

    except Exception as e:
        print(f"❌ Error connecting to ChromaDB Cloud: {e}")

if __name__ == "__main__":
    test_chroma_cloud()