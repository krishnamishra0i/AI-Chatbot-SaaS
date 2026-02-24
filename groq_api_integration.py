#!/usr/bin/env python3
"""
GROQ API INTEGRATION
Use Groq API for chatbot answer generation
"""

import sys
sys.path.insert(0, 'ai_avatar_chatbot')

import os
import requests
import json
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqAPIIntegration:
    """
    Groq API integration for chatbot responses
    """
    
    def __init__(self):
        # Groq API configuration
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"  # Fast and efficient model
        self.timeout = 30
        
        # Check if API key is available
        if not self.api_key or not self.api_key.startswith("gsk_"):
            logger.warning("Groq API key not found or invalid. Please set GROQ_API_KEY environment variable.")
            self.is_available = False
        else:
            self.is_available = True
            logger.info("Groq API integration initialized successfully")
    
    def generate_response_with_groq(self, question: str, context: str = None) -> Dict:
        """
        Generate response using Groq API with dynamic parameters based on question context
        """
        if not self.is_available:
            return {
                'response': "Groq API is not configured. Please set GROQ_API_KEY environment variable.",
                'method': 'groq_unavailable',
                'confidence': 0.0,
                'error': 'API key not configured'
            }
        
        try:
            # Analyze question for dynamic parameters
            analysis = self._analyze_question_context(question)
            max_tokens = analysis['max_tokens']
            temperature = analysis['temperature']
            
            # Prepare the prompt
            system_prompt = """You are a helpful AI assistant providing accurate, detailed answers to user questions. Be comprehensive, clear, and helpful. If you don't know something, say so honestly."""
            
            # Add context if available
            if context:
                user_prompt = f"""Context: {context}

Question: {question}

Please provide a comprehensive and accurate answer based on the context and your knowledge."""
            else:
                user_prompt = f"""Question: {question}

Please provide a comprehensive and accurate answer."""
            
            # Prepare the request
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
                "max_tokens": max_tokens,  # DYNAMIC based on question context
                "temperature": temperature,  # DYNAMIC based on emotion and context
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
                    'dynamic_params': analysis,
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
    
    def _analyze_question_context(self, question: str) -> Dict:
        """
        Analyze question to determine emotional context and response requirements
        Returns dynamic parameters for token limits and creativity
        """
        question_lower = question.lower().strip()
        
        # Emotion and context detection
        emotional_indicators = {
            'greetings': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy', 'hiya'],
            'excited': ['wow', 'amazing', 'awesome', 'fantastic', 'incredible', 'brilliant', 'excellent'],
            'frustrated': ['why', 'what the hell', 'this sucks', 'terrible', 'awful', 'horrible', 'stupid'],
            'urgent': ['urgent', 'emergency', 'asap', 'immediately', 'right now', 'quickly'],
            'confused': ['confused', 'lost', 'don\'t understand', 'help me', 'stuck', 'not sure'],
            'grateful': ['thank you', 'thanks', 'appreciate', 'grateful', 'helpful']
        }
        
        # Question complexity indicators
        complexity_indicators = {
            'simple': ['what is', 'define', 'explain simply', 'basic', 'introduction to'],
            'detailed': ['how does', 'explain in detail', 'comprehensive', 'step by step', 'thorough'],
            'technical': ['algorithm', 'implementation', 'code', 'programming', 'technical'],
            'comparative': ['vs', 'versus', 'compare', 'difference between', 'better than']
        }
        
        # Length-based analysis
        question_length = len(question.split())
        
        # Detect emotion
        detected_emotions = []
        for emotion, keywords in emotional_indicators.items():
            if any(keyword in question_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        # Detect complexity
        detected_complexity = []
        for complexity, keywords in complexity_indicators.items():
            if any(keyword in question_lower for keyword in keywords):
                detected_complexity.append(complexity)
        
        # Determine response parameters based on analysis
        base_tokens = 50  # Ultra conservative minimum tokens
        temperature = 0.3  # Conservative default
        
        # Adjust for emotions - extremely short responses
        if 'greetings' in detected_emotions:
            base_tokens = 20   # Ultra short, friendly responses
            temperature = 0.8  # More creative for friendly chat
        elif 'excited' in detected_emotions:
            base_tokens = 80
            temperature = 0.7  # Enthusiastic but controlled
        elif 'frustrated' in detected_emotions:
            base_tokens = 120
            temperature = 0.4  # More factual, less creative
        elif 'urgent' in detected_emotions:
            base_tokens = 40
            temperature = 0.2  # Quick, direct answers
        elif 'confused' in detected_emotions:
            base_tokens = 140
            temperature = 0.5  # Clear, explanatory
        elif 'grateful' in detected_emotions:
            base_tokens = 30
            temperature = 0.6  # Warm, appreciative
        
        # Adjust for complexity - extremely reduced
        if 'simple' in detected_complexity:
            base_tokens = min(base_tokens, 60)
            temperature = min(temperature, 0.4)
        elif 'detailed' in detected_complexity:
            base_tokens = max(base_tokens, 160)
            temperature = 0.3  # More precise for detailed explanations
        elif 'technical' in detected_complexity:
            base_tokens = max(base_tokens, 140)
            temperature = 0.2  # Very precise for technical content
        elif 'comparative' in detected_complexity:
            base_tokens = max(base_tokens, 130)
            temperature = 0.4  # Balanced for comparisons
        
        # Adjust for question length - very conservative
        if question_length < 5:  # Very short questions
            base_tokens = min(base_tokens, 35)
        elif question_length > 20:  # Long, complex questions
            base_tokens = max(base_tokens, 120)
        
        # Context-based adjustments for specific domains - extremely short
        if any(word in question_lower for word in ['lms', 'learning', 'course', 'education']):
            base_tokens = max(base_tokens, 100)  # Educational content - very concise
            temperature = 0.3  # More factual for educational content
        elif any(word in question_lower for word in ['code', 'programming', 'algorithm', 'debug']):
            base_tokens = max(base_tokens, 120)  # Code explanations - focused and brief
            temperature = 0.2  # Very precise for code
        elif any(word in question_lower for word in ['financial', 'money', 'budget', 'credit']):
            base_tokens = max(base_tokens, 110)  # Financial advice - concise
            temperature = 0.3  # Balanced but conservative
        
        # Ensure reasonable bounds - extremely conservative maximum
        max_tokens = max(15, min(base_tokens, 200))  # Between 15-200 tokens (ultra short!)
        temperature = max(0.1, min(temperature, 0.9))  # Between 0.1-0.9
        
        return {
            'max_tokens': max_tokens,
            'temperature': temperature,
            'detected_emotions': detected_emotions,
            'detected_complexity': detected_complexity,
            'question_length': question_length,
            'context_type': 'educational' if 'lms' in question_lower else 
                           'technical' if any(word in question_lower for word in ['code', 'programming']) else
                           'financial' if any(word in question_lower for word in ['financial', 'money']) else
                           'general'
        }
    
    def test_groq_api(self) -> Dict:
        """Test the Groq API connection"""
        
        print("🧪 TESTING GROQ API CONNECTION")
        print("-" * 40)
        
        if not self.is_available:
            print("❌ Groq API key not configured")
            return {'status': 'error', 'message': 'API key not configured'}
        
        test_questions = [
            "What is an LMS?",
            "How do I cancel a subscription?",
            "What are the best credit cards?",
            "How should I budget my money?"
        ]
        
        results = []
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 Test {i}/{len(test_questions)}")
            print(f"Q: {question}")
            
            result = self.generate_response_with_groq(question)
            
            print(f"🤖 Method: {result['method']}")
            print(f"📊 Confidence: {result['confidence']:.2f}")
            print(f"📝 Answer: {result['response'][:150]}...")
            
            if result['error']:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success")
                if 'tokens_used' in result:
                    print(f"🔢 Tokens used: {result['tokens_used']}")
            
            print("-" * 30)
            results.append(result)
        
        # Summary
        successful_tests = sum(1 for r in results if not r['error'])
        print(f"\n📊 Test Summary: {successful_tests}/{len(test_questions)} successful")
        
        return {
            'status': 'success' if successful_tests > 0 else 'error',
            'successful_tests': successful_tests,
            'total_tests': len(test_questions),
            'results': results
        }

def setup_groq_integration():
    """Setup Groq API integration"""
    
    print("="*80)
    print("🤖 GROQ API INTEGRATION SETUP")
    print("="*80)
    
    # Check environment
    api_key = os.getenv("GROQ_API_KEY", "")
    
    if not api_key:
        print("\n❌ GROQ_API_KEY not found in environment variables")
        print("\n📝 To set up Groq API:")
        print("1. Get your Groq API key from https://console.groq.com/")
        print("2. Set environment variable: export GROQ_API_KEY='your-api-key-here'")
        print("3. Or create .env file with: GROQ_API_KEY=your-api-key-here")
        print("4. Restart your chatbot server")
        return False
    elif not api_key.startswith("gsk_"):
        print(f"\n❌ Invalid GROQ_API_KEY format: {api_key[:10]}...")
        print("Groq API keys should start with 'gsk_'")
        return False
    else:
        print(f"\n✅ GROQ_API_KEY found: {api_key[:10]}...")
    
    # Test the integration
    print("\n🧪 Testing Groq API integration...")
    groq_integration = GroqAPIIntegration()
    test_results = groq_integration.test_groq_api()
    
    if test_results['status'] == 'success':
        print(f"\n✅ Groq API integration successful!")
        print(f"📊 Test results: {test_results['successful_tests']}/{test_results['total_tests']} tests passed")
        return True
    else:
        print(f"\n❌ Groq API integration failed")
        print(f"📊 Test results: {test_results['successful_tests']}/{test_results['total_tests']} tests passed")
        return False

def create_groq_integration_code():
    """Create the integration code for chat_routes.py"""
    
    integration_code = '''
# GROQ API INTEGRATION FOR chat_routes.py
# Add this to your ai_avatar_chatbot/backend/api/chat_routes.py

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
                'response': "Groq API is not configured. Please set GROQ_API_KEY environment variable.",
                'method': 'groq_unavailable',
                'confidence': 0.0
            }
        
        try:
            system_prompt = "You are a helpful AI assistant providing accurate, detailed answers. Be comprehensive and clear."
            
            if context:
                user_prompt = f"Context: {context}\\n\\nQuestion: {question}\\n\\nPlease provide a comprehensive answer."
            else:
                user_prompt = f"Question: {question}\\n\\nPlease provide a comprehensive answer."
            
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
'''
    
    with open('groq_api_integration.py', 'w') as f:
        f.write(integration_code)
    
    print("✅ Created groq_api_integration.py")
    return integration_code

if __name__ == '__main__':
    print("="*80)
    print("🤖 GROQ API INTEGRATION FOR CHATBOT")
    print("="*80)
    
    # Step 1: Setup check
    setup_success = setup_groq_integration()
    
    if setup_success:
        # Step 2: Create integration code
        print("\n📝 Creating integration code...")
        create_groq_integration_code()
        
        print("\n" + "="*80)
        print("🎉 GROQ API INTEGRATION READY!")
        print("="*80)
        print("""
✅ SETUP COMPLETED:
   • Groq API key validated
   • API connection tested successfully
   • Integration code generated

✅ FEATURES:
   • Fast responses using Groq's Llama 3.1 model
   • Context-aware responses with knowledge base
   • Error handling and fallbacks
   • Token usage tracking

✅ TO INTEGRATE:
   1. Copy code from groq_api_integration.py
   2. Paste into ai_avatar_chatbot/backend/api/chat_routes.py
   3. Replace your existing chat endpoint
   4. Restart your server
   5. Test with /chat-groq-test endpoint

✅ EXPECTED RESULTS:
   • Fast, accurate responses from Groq API
   • Context-aware answers with knowledge base
   • Professional, helpful tone
   • Reliable performance

🚀 YOUR CHATBOT WILL USE GROQ API FOR ANSWERS!
""")
    else:
        print("\n" + "="*80)
        print("❌ GROQ API SETUP FAILED")
        print("="*80)
        print("""
❌ SETUP FAILED:
   • Groq API key not found or invalid
   • Please configure GROQ_API_KEY environment variable

📝 TO FIX:
   1. Get API key from https://console.groq.com/
   2. Set environment: export GROQ_API_KEY='your-key'
   3. Or create .env file with GROQ_API_KEY=your-key
   4. Restart and run this script again

🔧 Once configured, your chatbot will use Groq API for responses!
""")
