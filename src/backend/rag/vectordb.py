"""
Vector Database for RAG (Retrieval-Augmented Generation) using ChromaDB
"""
import json
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class SimpleVectorDB:
    """Vector database using ChromaDB"""
    
    def __init__(self, db_path: Optional[str] = None, collection_name: str = "documents"):
        """
        Initialize vector database
        
        Args:
            db_path: Path to save/load database
            collection_name: Name of the ChromaDB collection
        """
        self.db_path = db_path or "./data/merged_chroma_db"
        self.collection_name = collection_name
        
        # Initialize ChromaDB client (local persistent)
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection '{self.collection_name}'")
        except ValueError:
            self.collection = self.client.create_collection(name=self.collection_name)
            logger.info(f"Created new collection '{self.collection_name}'")
    
    def add(self, text: str, embedding: np.ndarray, metadata: Optional[dict] = None):
        """Add document with embedding"""
        doc_id = str(len(self.collection.get()['ids']) + 1)  # Simple ID generation
        self.collection.add(
            documents=[text],
            embeddings=[embedding.tolist()],
            metadatas=[metadata] if metadata else None,
            ids=[doc_id]
        )
        logger.info(f"Added document with ID {doc_id}")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (document, similarity) tuples
        """
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=['documents', 'distances']
        )
        
        if not results['documents']:
            return []
        
        # ChromaDB returns cosine distance, convert to similarity
        similarities = []
        for doc, distance in zip(results['documents'][0], results['distances'][0]):
            similarity = 1 - distance  # Convert distance to similarity
            similarities.append((doc, similarity))
        
        return similarities
    
    def save(self, filepath: str):
        """Save is handled automatically by ChromaDB PersistentClient"""
        logger.info("ChromaDB handles persistence automatically")
    
    def load(self, filepath: str):
        """Load is handled automatically by ChromaDB PersistentClient"""
        logger.info("ChromaDB handles loading automatically")
