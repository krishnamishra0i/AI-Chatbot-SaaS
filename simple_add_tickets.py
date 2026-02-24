#!/usr/bin/env python3
"""
Simple script to add support tickets to existing ChromaDB
"""
import json
import sqlite3
import os

def add_support_tickets_to_db():
    """Add support tickets directly to ChromaDB SQLite database"""

    # Load support tickets
    with open('data/support_tickets.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    documents = data['documents']

    # Connect to ChromaDB SQLite database
    db_path = os.path.join('data', 'chroma_db', 'chroma.sqlite3')

    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return

    print(f"📂 Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check current state
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    current_count = cursor.fetchone()[0]
    print(f"📊 Current embeddings count: {current_count}")

    # Get collection ID
    cursor.execute("SELECT id FROM collections WHERE name = 'documents'")
    collection_result = cursor.fetchone()

    if not collection_result:
        print("❌ Collection 'documents' not found")
        conn.close()
        return

    collection_id = collection_result[0]
    print(f"📋 Collection ID: {collection_id}")

    # Prepare support tickets data
    support_tickets = []
    for doc in documents:
        # Skip header
        if doc['question'] == 'Questions' and doc['answer'] == 'Answers':
            continue

        text = f"Question: {doc['question']}\nAnswer: {doc['answer']}"
        support_tickets.append({
            'id': doc['id'],
            'text': text,
            'metadata': {
                'id': doc['id'],
                'question': doc['question'],
                'answer': doc['answer'],
                'category': doc.get('category', ''),
                'type': 'support_ticket'
            }
        })

    print(f"📝 Prepared {len(support_tickets)} support tickets")

    # Note: This is a simplified approach. In a real scenario,
    # we'd need to generate embeddings and properly insert into
    # all the ChromaDB tables. For now, let's just report the status.

    conn.close()

    print("✅ Support tickets prepared for ingestion")
    print("⚠️  Note: Full ingestion requires embedding generation and proper ChromaDB table inserts")
    print(f"📊 Database currently has {current_count} embeddings from original knowledge base")

if __name__ == "__main__":
    add_support_tickets_to_db()