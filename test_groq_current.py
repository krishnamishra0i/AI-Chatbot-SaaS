#!/usr/bin/env python3
"""
GROQ API INTEGRATION - WORKING VERSION
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
            logger.warning("Groq API key not found or invalid.")
            self.is_available = False
        else:
            self.is_available = True
            logger.info("Groq API integration initialized successfully")
    
    def generate_response_with_groq(self, question: str, context: str = None) -> Dict:
        """
        Generate response using Groq API
        """
        if not self.is_available:
            return {
                'response': "Groq API is not configured. Please check your GROQ_API_KEY.",
                'method': 'groq_unavailable',
                'confidence': 0.0,
                'error': 'API key not configured'
            }
        
        try:
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

def test_current_groq():
    """Test the current Groq API setup"""
    
    print("="*80)
    print("🤖 TESTING CURRENT GROQ API SETUP")
    print("="*80)
    
    # Check environment
    api_key = os.getenv("GROQ_API_KEY", "")
    
    if not api_key:
        print("\n❌ GROQ_API_KEY not found in environment variables")
        return False
    elif not api_key.startswith("gsk_"):
        print(f"\n❌ Invalid GROQ_API_KEY format: {api_key[:10]}...")
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

if __name__ == '__main__':
    test_current_groq()
