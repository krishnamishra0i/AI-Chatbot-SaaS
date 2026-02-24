"""
Simple Q&A Retriever - Directly loads and searches Q&A pairs
No vector database needed - uses simple keyword matching
"""
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class SimpleQARetriever:
    """Simple Q&A retriever using keyword matching"""
    
    def __init__(self, qa_file_path: Optional[str] = None):
        """
        Initialize retriever with Q&A data
        
        Args:
            qa_file_path: Path to creditor_academy_qa.json file
        """
        self.qa_data = []
        self.is_loaded = False
        
        # Default path to Q&A file
        if not qa_file_path:
            project_root = Path(__file__).parent.parent.parent.parent
            qa_file_path = str(project_root / "data" / "creditor_academy_qa.json")
        
        self.load_qa_data(qa_file_path)
    
    def load_qa_data(self, filepath):
        """Load Q&A data from JSON file"""
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.warning(f"⚠️  Q&A file not found: {filepath}")
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                self.qa_data = json.load(f)
            
            self.is_loaded = True
            logger.info(f"✅ Loaded {len(self.qa_data)} Q&A pairs from {filepath.name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Q&A data: {e}")
    
    def get_context_with_confidence(self, query: str, top_k: int = 3) -> Tuple[Optional[str], float]:
        """
        Get relevant Q&A pairs with confidence score
        
        Args:
            query: User's question
            top_k: Number of results
            
        Returns:
            Tuple of (formatted context string, confidence score)
        """
        if not self.is_loaded or not self.qa_data:
            return None, 0.0
        
        try:
            # Find matching Q&A pairs
            matches = self._search_qa(query, top_k)
            
            if not matches:
                return None, 0.0
            
            # Calculate confidence based on match quality
            confidence = self._calculate_overall_confidence(matches, query)
            
            # Format as context
            context_parts = []
            for i, qa in enumerate(matches, 1):
                context_parts.append(
                    f"Q{i}: {qa['question']}\n"
                    f"A{i}: {qa['answer']}\n"
                )
            
            context = "\n".join(context_parts)
            
            logger.info(f"📚 Found {len(matches)} relevant Q&A pairs with confidence {confidence:.2f}")
            return context, confidence
            
        except Exception as e:
            logger.error(f"❌ Context retrieval error: {e}")
            return None, 0.0
    
    def _calculate_overall_confidence(self, matches: List[Dict], query: str) -> float:
        """Calculate overall confidence score for retrieved matches"""
        if not matches:
            return 0.0
        
        # Base confidence on the quality of matches
        confidence = 0.0
        
        # Higher confidence if we have matches
        confidence += 0.3
        
        # Higher confidence for more matches
        confidence += min(0.3, len(matches) * 0.1)
        
        # Higher confidence if top match has high score
        if matches:
            top_score = self._calculate_score(matches[0], 
                                             [w for w in query.lower().split() if len(w) > 2], 
                                             query.lower())
            # Normalize score to 0-1 confidence
            confidence += min(0.4, top_score / 20.0)  # Assuming max score ~20
        
        return min(1.0, confidence)
    
    def _search_qa(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search Q&A pairs using keyword matching
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of matching Q&A pairs
        """
        query_lower = query.lower()
        
        # Extract keywords from query
        words = re.findall(r'\b\w+\b', query_lower)
        keywords = [w for w in words if len(w) > 2]  # Filter short words
        
        # Score each Q&A pair
        scored_qa = []
        for qa in self.qa_data:
            score = self._calculate_score(qa, keywords, query_lower)
            if score > 0:
                scored_qa.append((score, qa))
        
        # Sort by score and return top results
        scored_qa.sort(reverse=True, key=lambda x: x[0])
        
        return [qa for _, qa in scored_qa[:top_k]]
    
    def _calculate_score(self, qa: Dict, keywords: List[str], query: str) -> float:
        """Calculate relevance score for a Q&A pair"""
        score = 0.0
        
        # Combine searchable text
        question = qa['question'].lower()
        answer = qa.get('answer', '').lower()
        qa_keywords = [k.lower() for k in qa.get('keywords', [])]
        category = qa.get('category', '').lower()
        
        # Check for exact phrase match (highest score)
        if query in question or query in answer:
            score += 10.0
        
        # Check keywords in QA keywords list
        for kw in keywords:
            if kw in qa_keywords:
                score += 3.0
            elif kw in question:
                score += 2.0
            elif kw in answer:
                score += 1.0
        
        # Bonus for category match
        for kw in keywords:
            if kw in category:
                score += 1.5

        # Add fuzzy similarity score between query and question/answer using difflib
        try:
            from difflib import SequenceMatcher
            # similarity to question
            q_sim = SequenceMatcher(None, query, question).ratio()
            a_sim = SequenceMatcher(None, query, answer).ratio() if answer else 0.0
            # weight question similarity higher
            score += q_sim * 5.0
            score += a_sim * 2.0
        except Exception:
            # If difflib unavailable (shouldn't happen), skip fuzzy scoring
            pass
        
        return score
    
    def get_stats(self) -> Dict:
        """Get statistics about loaded Q&A data"""
        if not self.is_loaded:
            return {"error": "No data loaded"}
        
        categories = {}
        for qa in self.qa_data:
            cat = qa.get('category', 'general')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_qa_pairs": len(self.qa_data),
            "categories": categories,
            "is_loaded": self.is_loaded
        }
    
    # Compatibility methods with EnhancedRetriever interface
    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieve documents (for compatibility)"""
        matches = self._search_qa(query, top_k)
        return [f"{qa['question']}\n{qa['answer']}" for qa in matches]

