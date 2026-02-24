"""
Advanced Answer Optimization Module
Improves chatbot answer accuracy through multiple scoring and ranking mechanisms
"""

import re
from typing import List, Tuple, Dict, Optional
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class AnswerQualityScorer:
    """
    Scores answer quality across multiple dimensions:
    - Relevance to question
    - Information completeness
    - Clarity and structure
    - Knowledge base alignment
    """
    
    def __init__(self):
        self.min_quality_score = 0.75  # Increased from 0.65 for stricter filtering
        self.quality_weights = {
            'relevance': 0.45,  # Increased from 0.40 - prioritize relevance even more
            'completeness': 0.25,
            'clarity': 0.20,
            'kb_alignment': 0.10  # Reduced from 0.15 to focus on user question
        }
    
    def score_answer(self, question: str, answer: str, context: Optional[str] = None) -> Tuple[float, Dict]:
        """
        Calculate comprehensive answer quality score (0-1)
        Returns: (score, details_dict)
        """
        scores = {}
        
        # 1. Relevance scoring
        scores['relevance'] = self._score_relevance(question, answer)
        
        # 2. Completeness scoring
        scores['completeness'] = self._score_completeness(answer, question)
        
        # 3. Clarity scoring
        scores['clarity'] = self._score_clarity(answer)
        
        # 4. KB alignment scoring
        scores['kb_alignment'] = self._score_kb_alignment(answer, context) if context else 0.5
        
        # Calculate weighted score
        final_score = sum(scores[key] * self.quality_weights[key] 
                         for key in scores.keys())
        
        logger.debug(f"Answer quality score: {final_score:.3f} | Details: {scores}")
        
        return final_score, scores
    
    def _score_relevance(self, question: str, answer: str) -> float:
        """Score 0-1: Does answer address the question?"""
        if not answer or len(answer.split()) < 5:
            return 0.0
        
        q_tokens = set(self._tokenize(question))
        a_tokens = set(self._tokenize(answer))
        
        # Calculate multiple relevance metrics
        if len(q_tokens) == 0:
            return 0.5
        
        # Word overlap (must be 60%+ for basic relevance - increased from 50%)
        overlap = len(q_tokens & a_tokens) / len(q_tokens)
        
        # Check for key question words mapping
        key_questions = ['what', 'how', 'when', 'where', 'why', 'do', 'can', 'is', 'are']
        q_key_words = [w for w in q_tokens if w in key_questions]
        
        # Enhanced question type checking
        if q_key_words:
            # "how" questions should have instructions/steps
            if 'how' in q_tokens:
                action_indicators = ['step', 'follow', 'click', 'go', 'navigate', 'select', 'enter']
                has_actions = any(indicator in a_tokens for indicator in action_indicators)
                if not has_actions:
                    overlap *= 0.6  # Stronger penalty for missing actions
            
            # "what" questions should have definitions/descriptions
            elif 'what' in q_tokens:
                definition_indicators = ['is', 'are', 'refers', 'means', 'defined']
                has_definition = any(indicator in a_tokens for indicator in definition_indicators)
                if not has_definition:
                    overlap *= 0.7
            
            # "when" questions should have time references
            elif 'when' in q_tokens:
                time_indicators = ['date', 'time', 'day', 'month', 'year', 'schedule', 'period']
                has_time = any(indicator in a_tokens for indicator in time_indicators)
                if not has_time:
                    overlap *= 0.7
        
        # Penalize very low overlap (less than 40% - increased from 30%)
        if overlap < 0.40:
            return overlap * 0.4  # Heavy penalty for low overlap
        
        return min(overlap, 1.0)  # Cap at 1.0
    
    def _score_completeness(self, answer: str, question: str) -> float:
        """Score 0-1: Is the answer complete and detailed?"""
        sentences = re.split(r'[.!?]+', answer.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) == 0:
            return 0.0
        
        # More sentences = better (but even 2-3 sentences is weak)
        sentence_score = min(len(sentences) / 3.0, 1.0)  # Need 3+ sentences for full score (reduced from 4)
        
        # Reward concise answers - penalize overly short ones more heavily
        if len(sentences) == 1:
            sentence_score *= 0.5  # Increased penalty for single sentence (was 0.7)
        elif len(sentences) == 2:
            sentence_score *= 0.7  # Increased penalty for 2 sentences (was 0.8)
        elif len(sentences) > 6:
            sentence_score *= 0.95  # Very slight penalty for longer answers
        
        # Enhanced action items checking
        action_words = ['click', 'go', 'select', 'enter', 'check', 'visit', 'navigate', 'open', 'login', 'access', 'find', 'locate']
        has_actions = any(word in answer.lower() for word in action_words)
        action_score = 0.95 if has_actions else 0.4  # Even stronger preference for actionable answers
        
        # Check for specific details (numbers, names, dates)
        has_specifics = bool(re.search(r'\d+|[A-Z][a-z]+\s+[A-Z][a-z]+|\b\w+\s+\d{1,2}\b', answer))
        specifics_score = 0.9 if has_specifics else 0.6
        
        # Combine scores with weights
        return (sentence_score * 0.4) + (action_score * 0.4) + (specifics_score * 0.2)
    
    def _score_clarity(self, answer: str) -> float:
        """Score 0-1: Is the answer clear and well-structured?"""
        # Check structure indicators
        clarity_score = 0.5  # Default
        
        # Points for structure
        if '\n' in answer or '•' in answer or '-' in answer:
            clarity_score += 0.2  # Has structure/list
        
        if '**' in answer or '__' in answer:  # Bold/emphasis
            clarity_score += 0.1  # Highlights important info
        
        # Check readability
        words = answer.split()
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
        
        # Penalize very long words (5+ chars on average = harder to read)
        if avg_word_len > 6:
            clarity_score *= 0.9
        
        # Penalize if too short (less than 30 words = not enough detail)
        if len(words) < 30:
            clarity_score *= 0.8
        
        return min(clarity_score, 1.0)
    
    def _score_kb_alignment(self, answer: str, context: str) -> float:
        """Score 0-1: Does answer align with KB content?"""
        if not context:
            return 0.5
        
        # Check if answer references KB appropriately
        has_kb_reference = any(phrase in answer.lower() for phrase in 
                              ['based on', 'knowledge base', 'our', 'according to', 'from'])
        
        if has_kb_reference:
            kb_score = 0.9
        else:
            # Check semantic alignment - do answer tokens appear in context?
            answer_tokens = set(self._tokenize(answer))
            context_tokens = set(self._tokenize(context))
            
            if len(answer_tokens) == 0:
                kb_score = 0.5
            else:
                token_overlap = len(answer_tokens & context_tokens) / len(answer_tokens)
                kb_score = 0.4 + (token_overlap * 0.6)  # 0.4-1.0 range
        
        return kb_score
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple tokenization"""
        # Remove punctuation and lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return [w for w in text.split() if len(w) > 2]  # Skip very short words


class AnswerRanker:
    """
    Ranks multiple answer candidates and selects the best
    """
    
    def __init__(self, scorer: AnswerQualityScorer):
        self.scorer = scorer
    
    def rank_answers(self, question: str, candidates: List[Dict], 
                    context: Optional[str] = None) -> List[Tuple[Dict, float]]:
        """
        Rank answer candidates by quality
        Returns: List of (candidate, score) tuples, highest score first
        """
        ranked = []
        
        for candidate in candidates:
            # Get the actual answer text
            answer_text = candidate.get('answer') or candidate.get('text') or ''
            
            # Score the answer
            score, details = self.scorer.score_answer(question, answer_text, context)
            
            # Store with metadata
            ranked.append({
                'candidate': candidate,
                'score': score,
                'details': details
            })
        
        # Sort by score (highest first)
        ranked.sort(key=lambda x: x['score'], reverse=True)
        
        logger.debug(f"Ranked {len(ranked)} answers. Top score: {ranked[0]['score']:.3f if ranked else 0}")
        
        return [(r['candidate'], r['score']) for r in ranked]
    
    def select_best_answer(self, question: str, candidates: List[Dict],
                          context: Optional[str] = None) -> Optional[Tuple[Dict, float]]:
        """
        Select single best answer from candidates
        Returns: (best_candidate, confidence_score) or None
        """
        if not candidates:
            return None
        
        ranked = self.rank_answers(question, candidates, context)
        
        if not ranked:
            return None
        
        best_candidate, best_score = ranked[0]
        
        # Only return if meets minimum quality
        if best_score >= self.scorer.min_quality_score:
            return (best_candidate, best_score)
        
        logger.warning(f"Best candidate score {best_score:.3f} below minimum {self.scorer.min_quality_score}")
        return None


class AnswerEnhancer:
    """
    Enhances answers with better structure and formatting
    """
    
    @staticmethod
    def enhance_structure(answer: str, question: str) -> str:
        """
        Improve answer structure for clarity while keeping it concise
        """
        # Keep answers short - only add structure if absolutely needed
        if len(answer) < 400:  # Increased threshold for even more conciseness
            return answer  # Don't over-structure short answers
        
        # For longer answers, add minimal structure
        if '\n' not in answer and len(answer) > 300:
            # Split into 2-3 logical chunks max
            sentences = re.split(r'([.!?]+)', answer)
            chunks = [''.join(sentences[i:i+2]).strip() 
                     for i in range(0, len(sentences)-1, 2)]
            
            # Only use first 2-3 chunks to keep it short
            if len(chunks) > 2:
                answer = '\n'.join(chunks[:2])
        
        return answer
    
    @staticmethod
    def add_actionability(answer: str) -> str:
        """
        Ensure answer has clear next steps, but keep it concise
        """
        action_phrases = [
            'You can', 'You should', 'Here\'s how', 'Follow these steps',
            'To do this', 'Contact us', 'Visit'
        ]
        
        # Only add action orientation if the answer is very short and lacks it
        has_action = any(phrase.lower() in answer.lower() for phrase in action_phrases)
        
        if not has_action and len(answer) < 80 and ('how' in answer.lower() or 'what' in answer.lower()):  # Reduced threshold
            # Prepend minimal action-oriented intro
            answer = f"Here's what you need to know: {answer}"
        
        return answer


class AnswerValidator:
    """
    Final validation before returning answers
    """
    
    def __init__(self, scorer: AnswerQualityScorer):
        self.scorer = scorer
    
    def validate(self, question: str, answer: str, 
                context: Optional[str] = None) -> Tuple[bool, float, str]:
        """
        Enhanced validation check with stricter criteria
        Returns: (is_valid, confidence, reason)
        """
        # Check length - stricter requirements
        if len(answer) < 20:
            return False, 0.05, "Answer too short (insufficient detail)"
        
        if len(answer) > 2000:
            return False, 0.15, "Answer too long (possible hallucination)"
        
        # Check relevance with stricter threshold
        score, details = self.scorer.score_answer(question, answer, context)
        
        if score < 0.6:  # Increased from 0.5
            return False, score, "Low quality score - below acceptable threshold"
        
        # Enhanced error pattern detection
        answer_lower = answer.lower()
        
        # Check for uncertainty indicators
        uncertainty_phrases = ['i think', 'maybe', 'perhaps', 'possibly', 'not sure', 'unclear']
        has_uncertainty = any(phrase in answer_lower for phrase in uncertainty_phrases)
        if has_uncertainty and score < 0.8:
            return False, score, "Answer contains uncertainty without high confidence"
        
        # Check for generic filler responses
        filler_phrases = ['thank you for asking', 'that is a good question', 'i understand your concern']
        has_filler = any(phrase in answer_lower for phrase in filler_phrases)
        if has_filler and len(answer) < 100:
            return False, score, "Generic filler response without substance"
        
        # Check for avoidance patterns
        avoidance_phrases = ['i cannot help', 'unable to assist', 'cannot provide', 'not able to']
        has_avoidance = any(phrase in answer_lower for phrase in avoidance_phrases)
        if has_avoidance and 'contact support' not in answer_lower:
            return False, score, "Avoidance without proper guidance"
        
        # Check for common error patterns
        if "i don't know" in answer_lower and score < 0.75:
            return False, score, "Answer indicates lack of knowledge without proper guidance"
        
        if "error" in answer_lower or "sorry" in answer_lower:
            if score < 0.7:  # Increased from 0.6
                return False, score, "Answer contains error/apology without good content"
        
        # Final quality gate
        if score < self.scorer.min_quality_score:
            return False, score, "Answer below minimum quality threshold"
        
        return True, score, "Valid - meets quality standards"
