"""
Document ingestion for RAG
"""
import os
from pathlib import Path
from typing import List, Optional
from backend.utils.logger import setup_logger
from backend.rag.vectordb import SimpleVectorDB
import numpy as np

logger = setup_logger(__name__)

class DocumentIngestor:
    """Ingest documents into vector database"""
    
    def __init__(self, vector_db: SimpleVectorDB, embedding_model: Optional[str] = None):
        """
        Initialize ingestor
        
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
            logger.info("Embedding model loaded for ingestion")
        except ImportError:
            logger.error("sentence-transformers not installed")
            self.model = None
    
    def ingest_text(self, text: str, metadata: Optional[dict] = None):
        """
        Ingest plain text
        
        Args:
            text: Text to ingest
            metadata: Optional metadata dictionary
        """
        if not self.model:
            logger.error("Embedding model not available")
            return
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            self.vector_db.add(text, embedding, metadata)
            logger.info(f"Ingested text: {text[:50]}...")
        except Exception as e:
            logger.error(f"Error ingesting text: {e}")
    
    def ingest_file(self, filepath: str):
        """
        Ingest text from file
        
        Args:
            filepath: Path to text file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Split into chunks
            chunks = self._chunk_text(text, chunk_size=500)
            
            for chunk in chunks:
                self.ingest_text(chunk)
            
            logger.info(f"Ingested file: {filepath} ({len(chunks)} chunks)")
        except Exception as e:
            logger.error(f"Error ingesting file: {e}")
    
    def ingest_directory(self, directory: str, extensions: Optional[List[str]] = None):
        """
        Ingest all text files in directory
        
        Args:
            directory: Directory path
            extensions: File extensions to process (default: ['.txt', '.md'])
        """
        if extensions is None:
            extensions = ['.txt', '.md']
        
        directory_path = Path(directory)
        
        for file_path in directory_path.rglob('*'):
            if file_path.suffix in extensions:
                self.ingest_file(str(file_path))
    
    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Chunk size in characters
            overlap: Overlap size in characters
            
        Returns:
            List of chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks
