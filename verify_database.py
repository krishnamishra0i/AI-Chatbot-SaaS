#!/usr/bin/env python3
"""
Final verification of merged ChromaDB database
"""
import chromadb
from sentence_transformers import SentenceTransformer

def verify_merged_database():
    """Verify the merged database contains all data"""

    # Connect to merged database
    db_path = "data/merged_chroma_db"
    client = chromadb.PersistentClient(path=db_path)

    # Get collection
    collection = client.get_collection(name="documents")

    total_docs = collection.count()
    print(f"📊 Total documents in merged database: {total_docs}")

    # Test queries
    model = SentenceTransformer('BAAI/bge-base-en-v1.5')

    # Test knowledge base query
    kb_query = "how to improve credit score"
    kb_embedding = model.encode([kb_query])
    kb_results = collection.query(
        query_embeddings=kb_embedding.tolist(),
        n_results=3
    )

    print(f"\n🔍 Query: '{kb_query}'")
    print("Knowledge Base Results:")
    for i, (doc, metadata, score) in enumerate(zip(
        kb_results['documents'][0],
        kb_results['metadatas'][0],
        kb_results['distances'][0]
    ), 1):
        print(f"  {i}. {metadata['question'][:60]}... (Type: {metadata['type']})")

    # Test support ticket query
    st_query = "cancel membership"
    st_embedding = model.encode([st_query])
    st_results = collection.query(
        query_embeddings=st_embedding.tolist(),
        n_results=3
    )

    print(f"\n🔍 Query: '{st_query}'")
    print("Support Ticket Results:")
    for i, (doc, metadata, score) in enumerate(zip(
        st_results['documents'][0],
        st_results['metadatas'][0],
        st_results['distances'][0]
    ), 1):
        print(f"  {i}. {metadata['question'][:60]}... (Type: {metadata['type']})")

    # Count by type
    all_results = collection.get()
    kb_count = sum(1 for m in all_results['metadatas'] if m.get('type') == 'knowledge_base')
    st_count = sum(1 for m in all_results['metadatas'] if m.get('type') == 'support_ticket')

    print("\n📈 Data Summary:")
    print(f"  Knowledge Base documents: {kb_count}")
    print(f"  Support Ticket documents: {st_count}")
    print(f"  Total: {kb_count + st_count}")

    print("\n✅ Database verification complete!")

if __name__ == "__main__":
    verify_merged_database()