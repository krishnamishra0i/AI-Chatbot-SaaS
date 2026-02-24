# GROQ API INTEGRATION FOR chat_routes.py
# Copy this into your ai_avatar_chatbot/backend/api/chat_routes.py

import os
import requests
from typing import Dict, Optional

# Groq API integration class
class GroqAPIIntegration:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        self.timeout = 30
        self.is_available = bool(self.api_key and self.api_key.startswith("gsk_"))
    
    def generate_response_with_groq(self, question: str, context: str = None) -> Dict:
        if not self.is_available:
            return {
                'response': "Groq API is not configured. Please check your GROQ_API_KEY.",
                'method': 'groq_unavailable',
                'confidence': 0.0
            }
        
        try:
            system_prompt = "You are a helpful AI assistant providing accurate, detailed answers. Be comprehensive and clear."
            
            if context:
                user_prompt = f"Context: {context}\n\nQuestion: {question}\n\nPlease provide a comprehensive answer."
            else:
                user_prompt = f"Question: {question}\n\nPlease provide a comprehensive answer."
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip()
                return {
                    'response': answer,
                    'method': 'groq_api',
                    'confidence': 0.85,
                    'model': self.model
                }
            else:
                return {
                    'response': "I apologize, but I'm having trouble generating a response right now.",
                    'method': 'groq_error',
                    'confidence': 0.0
                }
        except Exception as e:
            return {
                'response': "I apologize, but I'm experiencing technical difficulties.",
                'method': 'groq_error',
                'confidence': 0.0
            }

# Initialize Groq integration
groq_integration = GroqAPIIntegration()

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
        
        # Generate response using Groq API
        result = groq_integration.generate_response_with_groq(message.message, context)
        
        return TextResponse(
            response=result['response'],
            language=message.language,
            used_knowledge_base=bool(context),
            sources=[{
                'method': result['method'],
                'confidence': result['confidence'],
                'model': result.get('model', 'unknown'),
                'api_used': 'groq'
            }] if context else None
        )
        
    except Exception as e:
        logger.error(f"Chat error with Groq API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ADDITIONAL ENDPOINT FOR TESTING:
@router.post("/chat-groq-test")
async def chat_groq_test(message: TextMessage):
    """Test Groq API integration"""
    try:
        context = None
        if message.use_knowledge_base and rag_retriever:
            context, _ = rag_retriever.get_context_with_confidence(message.message, top_k=3)
        
        result = groq_integration.generate_response_with_groq(message.message, context)
        
        return {
            'question': message.message,
            'groq_response': result['response'],
            'method': result['method'],
            'confidence': result['confidence'],
            'model': result.get('model', 'unknown'),
            'context_used': bool(context),
            'api_status': 'working' if not result.get('error') else 'error'
        }
        
    except Exception as e:
        logger.error(f"Groq test error: {e}")
        return {'error': str(e)}
