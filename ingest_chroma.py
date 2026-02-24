#!/usr/bin/env python3
"""
Script to ingest knowledge base data into ChromaDB
"""
import json
import os
import sys
from pathlib import Path

# Add user site-packages to path
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python313', 'site-packages'))

# Add project paths
sys.path.append('ai_avatar_chatbot')

from ai_avatar_chatbot.backend.rag.vectordb import SimpleVectorDB
from ai_avatar_chatbot.backend.rag.ingest import DocumentIngestor

def load_json_knowledge_base(filepath):
    """Load Q&A data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    documents = []
    for item in data.get('documents', []):
        # Combine question and answer for better context
        text = f"Question: {item['question']}\nAnswer: {item['answer']}"
        documents.append({
            'text': text,
            'metadata': {
                'id': item.get('id'),
                'question': item['question'],
                'category': item.get('category'),
                'tags': item.get('tags', [])
            }
        })
    
    return documents

def main():
    print("🚀 Starting ChromaDB ingestion...")
    
    # Initialize ChromaDB
    db_path = "./data/chroma_db"
    vector_db = SimpleVectorDB(db_path=db_path)
    
    # Initialize ingestor
    ingestor = DocumentIngestor(vector_db)
    
    # Load and ingest knowledge bases
    knowledge_files = [
        "data/qa_knowledge_base.json",
        "data/creditor_academy_qa.json"
    ]
    
    total_ingested = 0
    
    for file_path in knowledge_files:
        if os.path.exists(file_path):
            print(f"📖 Loading {file_path}...")
            try:
                documents = load_json_knowledge_base(file_path)
                
                for doc in documents:
                    # Ingest with metadata
                    ingestor.ingest_text(doc['text'], doc['metadata'])
                    total_ingested += 1
                
                print(f"✅ Ingested {len(documents)} documents from {file_path}")
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
        else:
            print(f"⚠️ File not found: {file_path}")
    
    # Also ingest any text files in knowledge_base directory
    kb_dir = "data/knowledge_base"
    if os.path.exists(kb_dir):
        print(f"📁 Ingesting text files from {kb_dir}...")
        ingestor.ingest_directory(kb_dir)
        print(f"✅ Ingested text files from {kb_dir}")
    
    print(f"🎉 Total documents ingested: {total_ingested}")
    print("✅ ChromaDB ingestion complete!")

if __name__ == "__main__":
    main()