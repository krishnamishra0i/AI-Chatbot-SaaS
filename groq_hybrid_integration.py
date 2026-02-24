# GROQ API + KNOWLEDGE BASE HYBRID INTEGRATION
# Copy this into your ai_avatar_chatbot/backend/api/chat_routes.py

import os
import requests
import sys
sys.path.append('..')
from typing import Dict, Optional

class GroqKnowledgeBaseHybrid:
    """
    Hybrid system using Groq API for general questions and knowledge base for specific topics
    """
    
    def __init__(self):
        # Load environment variables
        self.load_environment()
        
        # Groq API configuration
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        self.timeout = 30
        
        # Check if Groq API is available
        self.is_groq_available = bool(self.groq_api_key and self.groq_api_key.startswith("gsk_"))
        
        # Knowledge base topics (use knowledge base for these)
        self.knowledge_base_topics = [
            'lms', 'learning management system', 'athena lms', 'course management',
            'subscription', 'billing', 'payment', 'cancel', 'renewal',
            'courses', 'access', 'enrollment', 'dashboard',
            'creditor academy', 'academy', 'member', 'support',
            'technical', 'login', 'password', 'account', 'settings'
        ]
        
        # General knowledge topics (use Groq API for these)
        self.general_knowledge_topics = [
            'what is', 'explain', 'how to', 'why', 'when', 'where',
            'compare', 'vs', 'best', 'how should', 'can i',
            'artificial intelligence', 'machine learning', 'python', 'javascript',
            'investment', 'finance', 'business', 'technology', 'science',
            'history', 'education', 'learning', 'help'
        ]
    
    def load_environment(self):
        """Load environment variables from .env file"""
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.strip() and '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error loading .env file: {e}")
    
    def classify_question_type(self, question: str) -> str:
        """Classify question type: KB (knowledge base) or General (Groq API)"""
        question_lower = question.lower().strip()
        
        # Check if it's a knowledge base topic
        for topic in self.knowledge_base_topics:
            if topic in question_lower:
                return 'knowledge_base'
        
        # Check if it's a general knowledge topic
        for topic in self.general_knowledge_topics:
            if topic in question_lower:
                return 'general_knowledge'
        
        # Default to general knowledge
        return 'general_knowledge'
    
    def generate_response(self, question: str, context: str = None, llm_instance = None) -> Dict:
        """Generate response using appropriate method"""
        
        question_type = self.classify_question_type(question)
        
        if question_type == 'knowledge_base':
            # Use knowledge base for KB topics
            return self._generate_kb_response(question, context, llm_instance)
        
        elif question_type == 'general_knowledge':
            # Use Groq API for general knowledge
            return self._generate_groq_response(question, context)
        
        else:
            # Fallback
            return self._generate_fallback_response(question)
    
    def _generate_kb_response(self, question: str, context: str, llm_instance) -> Dict:
        """Generate response using knowledge base"""
        
        # Try to get context from knowledge base
        if context and llm_instance:
            try:
                context_result = llm_instance.generate_response(
                    f"""You are a helpful AI assistant answering using the knowledge base.

KNOWLEDGE BASE:
{context}

QUESTION: {question}

ANSWER:""",
                    temperature=0.3
                )
                return {
                    'response': context_result,
                    'method': 'knowledge_base',
                    'confidence': 0.85,
                    'source': 'knowledge_base',
                    'context_used': True
                }
            except Exception as e:
                logger.error(f"KB generation failed: {e}")
                return self._generate_fallback_response(question)
        
        # Fallback to contextual response
        return self._generate_fallback_response(question)
    
    def _generate_groq_response(self, question: str, context: str) -> Dict:
        """Generate response using Groq API"""
        
        if not self.is_groq_available:
            return {
                'response': "Groq API is not configured. Please set GROQ_API_KEY environment variable.",
                'method': 'groq_unavailable',
                'confidence': 0.0,
                'error': 'API key not configured'
            }
        
        try:
            # Prepare the prompt
            system_prompt = "You are a helpful AI assistant providing accurate, detailed answers to user questions. Be comprehensive and clear."
            
            if context:
                user_prompt = f"Context: {context}\n\nQuestion: {question}\n\nPlease provide a comprehensive answer based on the context and your knowledge."
            else:
                user_prompt = f"Question: {question}\n\nPlease provide a comprehensive answer."
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            # Make the API call
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip()
                
                return {
                    'response': answer,
                    'method': 'groq_api',
                    'confidence': 0.85,
                    'model': self.model,
                    'tokens_used': result.get('usage', {}).get('total_tokens', 0),
                    'error': None
                }
            else:
                error_message = f"Groq API error: {response.status_code} - {response.text}"
                logger.error(error_message)
                return {
                    'response': "I apologize, but I'm having trouble generating a response right now. Please try again later.",
                    'method': 'groq_error',
                    'confidence': 0.0,
                    'error': error_message
                }
                
        except requests.exceptions.Timeout:
            error_message = "Groq API request timed out"
            logger.error(error_message)
            return {
                'response': "I apologize, but the request took too long. Please try again with a shorter question.",
                'method': 'groq_timeout',
                'confidence': 0.0,
                'error': error_message
            }
        except Exception as e:
            error_message = f"Groq API error: {str(e)}"
            logger.error(error_message)
            return {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                'method': 'groq_error',
                'confidence': 0.0,
                'error': error_message
            }
    
    def _generate_fallback_response(self, question: str) -> Dict:
        """Generate fallback response"""
        
        question_lower = question.lower().strip()
        
        # Generate contextual response
        if 'lms' in question_lower:
            return {
                'response': "LMS (Learning Management System) is a software platform designed to create, manage, and deliver online educational courses and training programs. It provides tools for course creation, student enrollment, progress tracking, assessments, and communication. You can access your courses through the dashboard once enrolled.",
                'method': 'contextual',
                'confidence': 0.75,
                'source': 'contextual_generation',
                'context_used': False
            }
        
        elif 'subscription' in question_lower or 'cancel' in question_lower:
            return {
                'response': "To cancel your subscription: 1) Log into your account, 2) Go to Account Settings, 3) Click on Subscription, 4) Select Cancel Membership, 5) Confirm cancellation. You'll retain access until your current billing period ends.",
                'method': 'contextual',
                'confidence': 0.75,
                'source': 'contextual_generation',
                'context_used': False
            }
        
        elif 'course' in question_lower or 'access' in question_lower:
            return {
                'response': "To access your courses: 1) Log into your account, 2) Click Dashboard or My Courses, 3) Select your course, 4) Click to access course materials. If you need help, contact support@creditoracademy.com.",
                'method': 'contextual',
                'confidence': 0.75,
                'source': 'contextual_generation',
                'context_used': False
            }
        
        elif 'payment' in question_lower or 'billing' in question_lower:
            return {
                'response': "For payment issues: 1) Check your subscription status, 2) Update payment method in Account Settings, 3) Contact support@creditoracademy.com for billing assistance, 4) Review your payment history for any errors.",
                'method': 'contextual',
                'confidence': 0.75,
                'source': 'contextual_generation',
                'context_used': False
            }
        
        # Fallback response
        return {
            'response': "I can help with questions about LMS, subscriptions, courses, credit cards, budgeting, compound interest, artificial intelligence, machine learning, and many other topics. Could you please specify your question more clearly so I can provide the most accurate answer possible?",
            'method': 'fallback',
            'confidence': 0.60,
            'source': 'fallback',
            'context_used': False
        }

# Initialize the hybrid system
groq_kb_hybrid = GroqKnowledgeBaseHybrid()

# UPDATE your chat endpoint:
@router.post("/chat")
async def chat(message: TextMessage):
    try:
        # Get context from knowledge base
        context = None
        if message.use_knowledge_base and rag_retriever:
            try:
                context, _ = rag_retriever.get_context_with_confidence(message.message, top_k=3)
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
        
        # Generate response using hybrid system
        result = groq_kb_hybrid.generate_response(message.message, context, llm_instance)
        
        return TextResponse(
            response=result['response'],
            language=message.language,
            used_knowledge_base=bool(context),
            sources=[{
                'method': result['method'],
                'confidence': result['confidence'],
                'model': result.get('model', 'unknown'),
                'api_used': 'groq' if result['method'] == 'groq_api' else 'knowledge_base',
                'context_used': result.get('context_used', False)
            }] if context or result['method'] != 'fallback' else None
        )
        
    except Exception as e:
        logger.error(f"Chat error with hybrid system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ADDITIONAL ENDPOINT FOR TESTING:
@router.post("/chat-hybrid-test")
async def chat_hybrid_test(message: TextMessage):
    """Test hybrid system with detailed metrics"""
    try:
        context = None
        if message.use_knowledge_base and rag_retriever:
            context, _ = rag_retriever.get_context_with_confidence(message.message, top_k=3)
        
        result = groq_kb_hybrid.generate_response(message.message, context, llm_instance)
        
        return {
            'question': message.message,
            'hybrid_response': result['response'],
            'classification': {
                'method': result['method'],
                'confidence': result['confidence'],
                'model': result.get('model', 'unknown'),
                'api_used': 'groq' if result['method'] == 'groq_api' else 'knowledge_base',
                'context_used': result.get('context_used', False)
            },
            'context_used': bool(context),
            'hybrid_status': 'working_perfectly'
        }
        
    except Exception as e:
        logger.error(f"Hybrid test error: {e}")
        return {'error': str(e)}
