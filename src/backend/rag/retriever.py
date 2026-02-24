"""
Document retriever for RAG
"""
import numpy as np
from typing import List, Optional
from backend.utils.logger import setup_logger
from backend.rag.vectordb import SimpleVectorDB

logger = setup_logger(__name__)

class Retriever:
    """Document retriever using embeddings"""
    
    def __init__(self, vector_db: SimpleVectorDB, embedding_model: Optional[str] = None):
        """
        Initialize retriever
        
        Args:
            vector_db: Vector database instance
            embedding_model: Embedding model name
        """
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self._init_embedding_model()
    
    def _init_embedding_model(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(
                self.embedding_model or "BAAI/bge-base-en-v1.5"
            )
            logger.info("Embedding model loaded")
        except ImportError:
            logger.error("sentence-transformers not installed")
            self.model = None
    
    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """
        Retrieve relevant documents for query
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        if not self.model:
            logger.warning("Embedding model not available")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query, convert_to_numpy=True)
            
            # Search in vector database
            results = self.vector_db.search(query_embedding, top_k)
            
            return [doc for doc, _ in results]
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []
    
    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        Get context string for LLM
        
        Args:
            query: Search query
            top_k: Number of documents
            
        Returns:
            Formatted context string
        """
        docs = self.retrieve(query, top_k)
        
        if not docs:
            return ""
        
        context = "\n".join([f"- {doc}" for doc in docs])
        return context
