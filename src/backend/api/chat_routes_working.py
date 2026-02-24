"""
Chat API routes - Working version with all fixes applied
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from backend.utils.logger import setup_logger
from backend.utils.answer_utils import format_answer
from backend.llm.prompt import ENHANCED_SYSTEM_PROMPT, ENHANCED_RAG_PROMPT, ULTRA_ACCURATE_RAG_PROMPT
from backend.llm.answer_optimizer import AnswerQualityScorer, AnswerRanker, AnswerValidator, AnswerEnhancer
import asyncio
import io
import concurrent.futures
import sys
import os

# Add parent directory to path for imports
sys.path.append('..')
sys.path.append('../../..')

# Try to import the ultimate fix
try:
    from ultimate_chatbot_fix import UltimateChatbotFix
    ultimate_fix = UltimateChatbotFix()
except ImportError:
    ultimate_fix = None
    print("Warning: Ultimate fix not available, using fallback")

logger = setup_logger(__name__)
router = APIRouter()

# Pydantic models
class TextMessage(BaseModel):
    message: str
    language: str = "en"
    use_knowledge_base: bool = True

class TextResponse(BaseModel):
    response: str
    language: str
    used_knowledge_base: bool
    sources: Optional[list] = None

# Initialize components
answer_scorer = AnswerQualityScorer()
answer_ranker = AnswerRanker()
answer_validator = AnswerValidator()
answer_enhancer = AnswerEnhancer()

# Try to initialize RAG retriever
rag_retriever = None
try:
    from backend.rag.simple_qa_retriever import SimpleQARetriever
    rag_retriever = SimpleQARetriever()
except ImportError:
    logger.warning("RAG retriever not available")

# Try to initialize LLM
llm_instance = None
try:
    from backend.llm.llm_interface import LLMInterface
    llm_instance = LLMInterface()
except ImportError:
    logger.warning("LLM interface not available")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Chatbot API is running"}

@router.post("/chat")
async def chat(message: TextMessage):
    """Main chat endpoint with ultimate fix"""
    try:
        # Get context from knowledge base if available
        context = None
        if message.use_knowledge_base and rag_retriever:
            try:
                context, _ = rag_retriever.get_context_with_confidence(message.message, top_k=3)
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
        
        # Use ultimate fix if available
        if ultimate_fix:
            result = ultimate_fix.generate_ultimate_response(message.message, context, llm_instance)
            
            return TextResponse(
                response=result['response'],
                language=message.language,
                used_knowledge_base=bool(context),
                sources=[{
                    'method': result['method'],
                    'confidence': result['confidence'],
                    'model': result.get('model', 'unknown'),
                    'detail_level': result.get('detail_level', 'medium'),
                    'response_time': result.get('response_time', 0.0),
                    'api_used': result.get('method', 'unknown'),
                    'context_used': bool(context)
                }] if context or result['method'] != 'fallback' else None
            )
        
        # Fallback to basic response
        fallback_response = generate_fallback_response(message.message)
        
        return TextResponse(
            response=fallback_response,
            language=message.language,
            used_knowledge_base=False,
            sources=[{
                'method': 'fallback',
                'confidence': 0.5,
                'model': 'fallback',
                'api_used': 'fallback'
            }]
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-ultimate-fix-test")
async def chat_ultimate_fix_test(message: TextMessage):
    """Test endpoint to show ultimate fix details"""
    try:
        context = None
        if message.use_knowledge_base and rag_retriever:
            context, _ = rag_retriever.get_context_with_confidence(message.message, top_k=3)
        
        if ultimate_fix:
            result = ultimate_fix.generate_ultimate_response(message.message, context, llm_instance)
            
            return {
                'question': message.message,
                'ultimate_response': result['response'],
                'fix_details': {
                    'method': result['method'],
                    'confidence': result['confidence'],
                    'model': result.get('model', 'unknown'),
                    'detail_level': result.get('detail_level', 'medium'),
                    'response_time': result.get('response_time', 0.0),
                    'api_used': result.get('method', 'unknown'),
                    'context_used': bool(context)
                },
                'context_used': bool(context),
                'ultimate_fix_status': 'working_perfectly'
            }
        else:
            return {
                'error': 'Ultimate fix not available',
                'message': 'Please ensure ultimate_chatbot_fix.py is in the correct location'
            }
        
    except Exception as e:
        logger.error(f"Ultimate fix test error: {e}")
        return {'error': str(e)}

@router.post("/chat-test")
async def chat_test(message: TextMessage):
    """Test endpoint for basic functionality"""
    try:
        return {
            'question': message.message,
            'response': f"Test response for: {message.message}",
            'language': message.language,
            'use_knowledge_base': message.use_knowledge_base,
            'status': 'working'
        }
    except Exception as e:
        logger.error(f"Chat test error: {e}")
        return {'error': str(e)}

def generate_fallback_response(question: str) -> str:
    """Generate a basic fallback response"""
    
    question_lower = question.lower().strip()
    
    # Basic knowledge base for fallback
    basic_responses = {
        "what is lms": "LMS (Learning Management System) is a software platform for creating, managing, and delivering online educational courses.",
        "how do i access my courses": "To access your courses, log into your account and click on 'My Courses' in the dashboard.",
        "how do i cancel my subscription": "To cancel your subscription, go to Account Settings > Subscription > Cancel Membership.",
        "what is athena lms": "Athena LMS is an advanced Learning Management System with AI-powered features and comprehensive educational tools.",
        "how to enroll in courses": "To enroll, browse the course catalog, select a course, and click 'Enroll Now'.",
        "how to track progress": "Track your progress in the 'My Courses' dashboard where you'll see completion percentages and grades.",
        "how to contact support": "Contact support through the Help menu or email support@athena-lms.com.",
        "how to download certificates": "Download certificates from the completed course page in the 'Certificate' section.",
        "what are the best credit cards": "The best credit cards depend on your credit score. For excellent credit, consider Chase Sapphire Preferred or Citi Double Cash.",
        "how should i budget my money": "Use the 50/30/20 rule: 50% for needs, 30% for wants, 20% for savings and debt repayment.",
        "what is compound interest": "Compound interest is interest earned on both the initial principal and accumulated interest, creating exponential growth.",
        "what is artificial intelligence": "AI is computer science focused on creating intelligent systems that perform tasks requiring human intelligence.",
        "explain machine learning": "Machine Learning enables computers to learn from data without explicit programming, using algorithms to find patterns.",
        "how do i learn": "To learn effectively, set clear goals, break topics into smaller chunks, use multiple learning methods, and practice regularly.",
        "what should i do": "Consider urgency and importance using the Eisenhower Matrix to prioritize tasks effectively."
    }
    
    if question_lower in basic_responses:
        return basic_responses[question_lower]
    
    # Generate contextual response
    if 'lms' in question_lower:
        return "I can help with LMS questions about courses, subscriptions, and platform features. Please ask a more specific question."
    elif 'subscription' in question_lower or 'cancel' in question_lower:
        return "For subscription issues, go to Account Settings > Subscription. You can cancel, upgrade, or update payment methods there."
    elif 'course' in question_lower or 'access' in question_lower:
        return "Access your courses through the dashboard. If you're having trouble, check your enrollment status or contact support."
    elif 'payment' in question_lower or 'billing' in question_lower:
        return "For payment questions, check your billing history in Account Settings or contact support@athena-lms.com."
    elif 'credit' in question_lower or 'card' in question_lower:
        return "Credit card recommendations depend on your credit score and spending habits. Consider rewards, fees, and interest rates."
    elif 'budget' in question_lower or 'money' in question_lower:
        return "Budget effectively using the 50/30/20 rule: 50% needs, 30% wants, 20% savings. Track expenses and automate savings."
    elif 'ai' in question_lower or 'artificial intelligence' in question_lower:
        return "AI involves creating intelligent systems that can learn, reason, and solve problems. It includes machine learning, deep learning, and natural language processing."
    elif 'learn' in question_lower or 'study' in question_lower:
        return "Learn effectively by setting goals, breaking topics into chunks, using multiple methods, practicing regularly, and reviewing frequently."
    else:
        return "I can help with questions about LMS, subscriptions, courses, credit cards, budgeting, AI, and learning strategies. Could you please specify your question more clearly?"
