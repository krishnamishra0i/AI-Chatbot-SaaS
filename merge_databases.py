#!/usr/bin/env python3
"""
Merge ChromaDB databases - combine original knowledge base with support tickets
"""
import chromadb
from sentence_transformers import SentenceTransformer
import json
import os

def merge_databases():
    """Merge data from both ChromaDB databases into one"""

    # Initialize new merged database
    merged_db_path = "data/merged_chroma_db"
    client = chromadb.PersistentClient(path=merged_db_path)

    # Create collection
    collection_name = "documents"
    collection = client.create_collection(name=collection_name)
    print(f"🆕 Created merged collection: {collection_name}")

    # Load embedding model
    model = SentenceTransformer('BAAI/bge-base-en-v1.5')

    # Load and merge original knowledge base
    print("📚 Loading original knowledge base...")
    with open('data/qa_knowledge_base.json', 'r', encoding='utf-8') as f:
        kb_data = json.load(f)

    kb_documents = []
    for item in kb_data['documents']:
        text = f"Question: {item['question']}\nAnswer: {item['answer']}"
        metadata = {
            'id': str(item.get('id', '')),
            'question': str(item['question']),
            'category': str(item.get('category', '')),
            'subject': str(item.get('subject', '')),
            'type': 'knowledge_base'
        }

        tags = item.get('tags') or item.get('keywords', [])
        if isinstance(tags, list):
            metadata['tags'] = ', '.join(str(tag) for tag in tags)
        else:
            metadata['tags'] = str(tags)

        kb_documents.append({
            'id': item['id'],
            'text': text,
            'metadata': metadata
        })

    # Load support tickets
    print("🎫 Loading support tickets...")
    with open('data/support_tickets.json', 'r', encoding='utf-8') as f:
        st_data = json.load(f)

    st_documents = []
    for item in st_data['documents']:
        if item['question'] == 'Questions' and item['answer'] == 'Answers':
            continue

        text = f"Question: {item['question']}\nAnswer: {item['answer']}"
        metadata = {
            'id': str(item.get('id', '')),
            'question': str(item['question']),
            'category': str(item.get('category', '')),
            'type': 'support_ticket'
        }

        tags = item.get('tags', [])
        if isinstance(tags, list):
            metadata['tags'] = ', '.join(str(tag) for tag in tags)
        else:
            metadata['tags'] = str(tags)

        st_documents.append({
            'id': item['id'],
            'text': text,
            'metadata': metadata
        })

    # Combine all documents
    all_documents = kb_documents + st_documents
    print(f"📊 Total documents to merge: {len(all_documents)} ({len(kb_documents)} KB + {len(st_documents)} ST)")

    # Prepare for ingestion
    ids = [doc['id'] for doc in all_documents]
    texts = [doc['text'] for doc in all_documents]
    metadatas = [doc['metadata'] for doc in all_documents]

    # Generate embeddings
    print("🔄 Generating embeddings for merged data...")
    embeddings = model.encode(texts, show_progress_bar=True)

    # Add to collection
    print("💾 Adding merged data to ChromaDB...")
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("✅ Successfully merged all data into ChromaDB!")

    # Verify
    total_count = collection.count()
    print(f"📊 Total documents in merged collection: {total_count}")

    # Test retrieval
    print("\n🔍 Testing retrieval...")
    results = collection.query(
        query_texts=["how to improve credit score"],
        n_results=2
    )

    print("Knowledge Base Results:")
    for i, (doc, metadata) in enumerate(zip(results['documents'][0][:1], results['metadatas'][0][:1]), 1):
        print(f"  {i}. {metadata['question'][:50]}...")

    results = collection.query(
        query_texts=["cancel membership"],
        n_results=2
    )

    print("Support Ticket Results:")
    for i, (doc, metadata) in enumerate(zip(results['documents'][0][:1], results['metadatas'][0][:1]), 1):
        print(f"  {i}. {metadata['question'][:50]}...")

if __name__ == "__main__":
    merge_databases()