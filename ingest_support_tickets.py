#!/usr/bin/env python3
"""
Ingest support tickets into ChromaDB
"""
import json
import os
import sys

# Don't add user site-packages to avoid conflicts
# Use current environment packages

import chromadb
from sentence_transformers import SentenceTransformer

def load_support_tickets(filepath):
    """Load support tickets from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    documents = []

    # Handle JSON structure
    if isinstance(data, dict) and 'documents' in data:
        items = data['documents']
    else:
        raise ValueError(f"Unknown JSON structure in {filepath}")

    for item in items:
        # Skip header row
        if item['question'] == 'Questions' and item['answer'] == 'Answers':
            continue

        # Combine question and answer for better context
        text = f"Question: {item['question']}\nAnswer: {item['answer']}"

        # Convert metadata to ChromaDB compatible format (strings only)
        metadata = {
            'id': str(item.get('id', '')),
            'question': str(item['question']),
            'category': str(item.get('category', '')),
            'type': 'support_ticket'
        }

        # Handle tags - ensure it's always a string
        tags = item.get('tags', [])
        if isinstance(tags, list):
            metadata['tags'] = ', '.join(str(tag) for tag in tags)
        else:
            metadata['tags'] = str(tags)

        documents.append({
            'id': item['id'],
            'text': text,
            'metadata': metadata
        })

    return documents

def main():
    # Load support tickets
    support_file = 'data/support_tickets.json'
    documents = load_support_tickets(support_file)

    print(f"📥 Loaded {len(documents)} support tickets")

    # Initialize ChromaDB with a new path for support tickets
    db_path = "data/support_tickets_db"
    client = chromadb.PersistentClient(path=db_path)

    # Get or create collection
    collection_name = "documents"
    try:
        collection = client.get_collection(name=collection_name)
        print(f"✅ Using existing collection: {collection_name}")
    except:
        collection = client.create_collection(name=collection_name)
        print(f"🆕 Created new collection: {collection_name}")

    # Initialize embedding model (same as working setup)
    model = SentenceTransformer('BAAI/bge-base-en-v1.5')

    # Prepare data for ingestion
    ids = [doc['id'] for doc in documents]
    texts = [doc['text'] for doc in documents]
    metadatas = [doc['metadata'] for doc in documents]

    print(f"🔄 Generating embeddings for {len(texts)} documents...")

    # Generate embeddings
    embeddings = model.encode(texts, show_progress_bar=True)

    # Add to database
    print("💾 Adding support tickets to ChromaDB...")
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("✅ Support tickets successfully ingested into ChromaDB!")

    # Verify
    total_count = collection.count()
    print(f"📊 Total documents in collection: {total_count}")

    # Test retrieval
    print("\n🔍 Testing retrieval with a sample query...")
    results = collection.query(
        query_texts=["how to cancel membership"],
        n_results=3
    )

    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        print(f"\n--- Result {i} ---")
        print(f"Question: {metadata['question']}")
        print(f"Answer: {metadata['answer'][:200]}...")

if __name__ == "__main__":
    main()