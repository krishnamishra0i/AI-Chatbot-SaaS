#!/usr/bin/env python3
"""
Check ChromaDB contents
"""
import sqlite3
import os

def check_chromadb_contents():
    """Check what's stored in ChromaDB database"""
    db_path = "./data/support_tickets_db/chroma.sqlite3"

    if not os.path.exists(db_path):
        print("❌ ChromaDB database not found!")
        return

    print("🔍 Checking ChromaDB database contents...")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check collections
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Database tables: {[t[0] for t in tables]}")

        # Check embeddings table
        cursor.execute("SELECT COUNT(*) FROM embeddings;")
        embedding_count = cursor.fetchone()[0]
        print(f"📊 Total embeddings: {embedding_count}")

        # Check collections table
        cursor.execute("SELECT id, name FROM collections;")
        collections = cursor.fetchall()
        print(f"📂 Collections: {collections}")

        # Check documents
        if collections:
            collection_id = collections[0][0]  # First collection
            cursor.execute("SELECT COUNT(*) FROM documents WHERE collection_id = ?;", (collection_id,))
            doc_count = cursor.fetchone()[0]
            print(f"📄 Documents in first collection: {doc_count}")

            # Sample some documents
            cursor.execute("""
                SELECT d.content, m.key, m.string_value
                FROM documents d
                LEFT JOIN metadata m ON d.id = m.document_id
                WHERE d.collection_id = ?
                LIMIT 5;
            """, (collection_id,))
            samples = cursor.fetchall()

            print("\n📝 Sample documents:")
            for i, sample in enumerate(samples[:3], 1):
                content = sample[0][:100] + "..." if len(sample[0]) > 100 else sample[0]
                print(f"  {i}. {content}")

        conn.close()

    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_chromadb_contents()