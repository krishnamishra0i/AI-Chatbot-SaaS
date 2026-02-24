"""
Enhanced RAG Retriever Wrapper
Integrates the enhanced Q&A knowledge base with the chatbot
"""
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict

# Add parent directory to path to import enhanced_rag_system
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class EnhancedRetriever:
    """Wrapper for enhanced RAG system compatible with chatbot interface"""
    
    def __init__(self):
        """Initialize the enhanced RAG system"""
        self.chatbot = None
        self.is_loaded = False
        self._initialize()
    
    def _initialize(self):
        """Load the enhanced RAG system"""
        try:
            # Import the enhanced RAG system
            # from enhanced_rag_system import OpenSourceRAGChatbot  # TODO: Implement if needed

            # For now, fall back to simple retriever
            logger.warning("Enhanced RAG system not implemented, using fallback")
            self.is_loaded = False
            return
            
            if not kb_dir.exists():
                logger.warning(f"⚠️  Knowledge base not found at {kb_dir}")
                logger.info("💡 Run 'python setup_rag_system.py' to create the knowledge base")
                return
            
            # Initialize the chatbot
            logger.info("Loading enhanced RAG knowledge base...")
            self.chatbot = OpenSourceRAGChatbot(str(kb_dir))
            self.is_loaded = True
            
            # Get stats
            total_pairs = len(self.chatbot.qa_data)
            categories = self.chatbot.get_category_distribution()
            logger.info(f"✅ Enhanced RAG loaded: {total_pairs} Q&A pairs")
            logger.info(f"📂 Categories: {list(categories.keys())}")
            
        except ImportError as e:
            logger.warning(f"⚠️  Enhanced RAG system not available: {e}")
            logger.info("💡 Using simple fallback mode")
        except Exception as e:
            logger.warning(f"⚠️  Failed to load enhanced RAG: {e}")
            logger.info("💡 Run 'python setup_rag_system.py' to set up the knowledge base")
    
    def get_context(self, query: str, top_k: int = 3) -> Optional[str]:
        """
        Get relevant context for a query
        
        Args:
            query: User's question
            top_k: Number of top results to return
            
        Returns:
            Formatted context string with relevant Q&A pairs
        """
        if not self.is_loaded or not self.chatbot:
            return None
        
        try:
            # Search for relevant Q&A pairs
            results = self.chatbot.search_similar_qa(query, top_k=top_k)
            
            if not results:
                return None
            
            # Format context
            context_parts = []
            for i, (qa, score) in enumerate(results, 1):
                # Only include high-confidence matches
                if score < 0.3:
                    continue
                
                context_parts.append(
                    f"[Relevant Q&A {i}]\n"
                    f"Question: {qa['question']}\n"
                    f"Answer: {qa['answer']}\n"
                    f"Category: {qa.get('category', 'general')}"
                )
            
            if not context_parts:
                return None
            
            logger.info(f"📚 Found {len(context_parts)} relevant Q&A pairs for query")
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Error retrieving context: {e}")
            return None
    
    def get_answer(self, question: str) -> Dict:
        """
        Get a direct answer for a question
        
        Args:
            question: User's question
            
        Returns:
            Dict with answer, confidence, category, matched_question, and context
        """
        if not self.is_loaded or not self.chatbot:
            return {
                'answer': None,
                'confidence': 0.0,
                'category': 'general',
                'matched_question': None,
                'used_kb': False
            }
        
        try:
            # Get answer from chatbot
            response = self.chatbot.generate_rag_response(question)
            
            # Extract matched question from sources
            matched_question = None
            sources = response.get('sources', [])
            if sources and len(sources) > 0:
                # Sources are QA dicts, get the first one's question
                matched_question = sources[0].get('question') if isinstance(sources[0], dict) else None
            
            return {
                'answer': response.get('answer'),
                'confidence': response.get('confidence', 0.0),
                'category': response.get('category', 'general'),
                'matched_question': matched_question,
                'sources': sources,
                'used_kb': True
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting answer: {e}")
            return {
                'answer': None,
                'confidence': 0.0,
                'category': 'general',
                'matched_question': None,
                'used_kb': False
            }
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        if not self.is_loaded or not self.chatbot:
            return {
                'total_qa_pairs': 0,
                'categories': {},
                'is_loaded': False
            }
        
        try:
            return {
                'total_qa_pairs': len(self.chatbot.qa_data),
                'categories': self.chatbot.get_category_distribution(),
                'is_loaded': True
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {
                'total_qa_pairs': 0,
                'categories': {},
                'is_loaded': False
            }
