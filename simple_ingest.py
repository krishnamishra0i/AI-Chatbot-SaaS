#!/usr/bin/env python3
"""
Simple ChromaDB ingestion script
"""
import json
import os
import sys

# Add user site-packages to path
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python314', 'site-packages'))

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

def load_json_knowledge_base(filepath):
    """Load Q&A data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    documents = []

    # Handle different JSON structures
    if isinstance(data, list):
        # Direct list format (creditor_academy_qa.json)
        items = data
    elif isinstance(data, dict) and 'documents' in data:
        # Wrapped format (qa_knowledge_base.json)
        items = data['documents']
    else:
        raise ValueError(f"Unknown JSON structure in {filepath}")

    for item in items:
        # Combine question and answer for better context
        text = f"Question: {item['question']}\nAnswer: {item['answer']}"

        # Convert metadata to ChromaDB compatible format (strings only)
        metadata = {
            'id': str(item.get('id', '')),
            'question': item['question'],
            'category': item.get('category', ''),
            'subject': item.get('subject', ''),
        }

        # Handle tags/keywords - convert list to string
        tags = item.get('tags') or item.get('keywords', [])
        if isinstance(tags, list):
            metadata['tags'] = ', '.join(tags)
        else:
            metadata['tags'] = str(tags)

        documents.append({
            'text': text,
            'metadata': metadata
        })

    return documents

def main():
    print("🚀 Starting simple ChromaDB ingestion...")

    try:
        # Initialize ChromaDB
        client = chromadb.PersistentClient(path="./data/chroma_db")

        # Get or create collection
        collection_name = "documents"
        try:
            collection = client.get_collection(name=collection_name)
            print(f"✅ Loaded existing collection '{collection_name}'")
        except ValueError:
            collection = client.create_collection(name=collection_name)
            print(f"✅ Created new collection '{collection_name}'")

        # Initialize embedding model
        print("🤖 Loading embedding model...")
        model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        print("✅ Embedding model loaded")

        # Load and ingest knowledge bases
        knowledge_files = [
            "data/qa_knowledge_base.json",
            "data/creditor_academy_qa.json",
            "data/support_tickets.json"
        ]

        total_ingested = 0

        for file_path in knowledge_files:
            if os.path.exists(file_path):
                print(f"📖 Loading {file_path}...")
                try:
                    documents = load_json_knowledge_base(file_path)

                    for doc in documents:
                        # Generate embedding
                        embedding = model.encode(doc['text'], convert_to_numpy=True)

                        # Add to collection
                        doc_id = f"doc_{total_ingested + 1}"
                        collection.add(
                            documents=[doc['text']],
                            embeddings=[embedding.tolist()],
                            metadatas=[doc['metadata']],
                            ids=[doc_id]
                        )
                        total_ingested += 1

                    print(f"✅ Ingested {len(documents)} documents from {file_path}")
                except Exception as e:
                    print(f"❌ Error loading {file_path}: {e}")
            else:
                print(f"⚠️ File not found: {file_path}")

        print(f"🎉 Total documents ingested: {total_ingested}")
        print("✅ ChromaDB ingestion complete!")

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")

if __name__ == "__main__":
    main()