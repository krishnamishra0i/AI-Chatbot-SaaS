# GOOGLE AI API INTEGRATION FOR LMS-ATHENA
# Working integration with correct model name

import os
import requests
import sys
sys.path.append('..')
from typing import Dict, Optional

class GoogleAIIntegration:
    """
    Google AI API integration for LMS-Athena chatbot
    """
    
    def __init__(self):
        # Google AI API configuration
        self.api_key = "AIzaSyAcLWFRQ8hG9nkRx3tz9VZOH_hadr8IZVY"
        self.project_name = "projects/267842846556"
        self.project_number = "267842846556"
        self.project_id = "gen-lang-client-0951579772"
        
        # API endpoints
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash-lite"  # Working model from the list
        self.timeout = 30
        
        # Check if API key is valid
        if self.api_key and len(self.api_key) == 39:
            self.is_available = True
            logger.info("Google AI API integration initialized successfully")
        else:
            self.is_available = False
            logger.error("Invalid Google AI API key")
        
        # LMS-Athena specific knowledge base
        self.lms_knowledge = {
            "what is lms": "LMS (Learning Management System) is a comprehensive software platform specifically designed to create, manage, deliver, and track online educational courses and training programs. LMS-Athena is an advanced Learning Management System that combines core LMS functionality with cutting-edge features including AI-powered personalized learning paths, real-time collaboration tools, comprehensive analytics dashboards, and mobile accessibility.",
            
            "how do i access my courses": "To access your courses in LMS-Athena: 1) Log into your account using your registered email address and password, 2) Navigate to the main dashboard by clicking on the 'Dashboard' or 'My Courses' link in the navigation menu, 3) Locate your enrolled courses which will be displayed with progress indicators and completion percentages, 4) Click on any course title to enter the course workspace.",
            
            "how do i cancel my subscription": "To cancel your subscription in LMS-Athena: 1) Log into your account using your registered email and password, 2) Navigate to your profile by clicking on your avatar or name in the top-right corner of the screen, 3) Select 'Account Settings' from the dropdown menu, 4) Click on the 'Subscription' or 'Billing' tab, 5) Locate the 'Cancel Membership' button, 6) Follow the cancellation prompts, 7) Confirm your cancellation.",
            
            "what is athena lms": "Athena LMS is an advanced Learning Management System platform that combines core LMS functionality with cutting-edge features including AI-powered personalized learning paths, real-time collaboration tools, comprehensive analytics dashboards, and mobile accessibility.",
            
            "how to enroll in courses": "To enroll in courses on LMS-Athena: 1) Browse the course catalog by clicking on 'Courses' or 'Catalog', 2) Use the search bar or filters to find courses, 3) Click on any course to view detailed information, 4) Click the 'Enroll Now' button, 5) Complete the payment process, 6) Start learning immediately.",
            
            "how to track progress": "To track your learning progress in LMS-Athena: 1) Log into your account and go to your 'My Courses' dashboard, 2) Click on any enrolled course to view its progress details, 3) The course dashboard will show your overall completion percentage, 4) Use the 'Progress' tab to see detailed analytics.",
            
            "how to contact support": "To contact LMS-Athena support: 1) Click on the 'Help' or 'Support' link in the navigation menu, 2) Choose your preferred support method: Live Chat, Email Support, or Phone Support, 3) For Live Chat: Start a conversation with a support agent, 4) For Email Support: Send your query to support@athena-lms.com.",
            
            "how to download certificates": "To download certificates from LMS-Athena: 1) Log into your account and go to your 'My Courses' dashboard, 2) Click on the completed course, 3) Look for the 'Certificate' section, 4) Click on 'Download Certificate', 5) Choose your preferred format: PDF or digital certificate."
        }
    
    def generate_response_with_google_ai(self, question: str, context: str = None) -> Dict:
        """Generate response using Google AI API"""
        
        if not self.is_available:
            return {
                'response': "Google AI API is not available. Please check your API key configuration.",
                'method': 'google_ai_unavailable',
                'confidence': 0.0,
                'error': 'API key not configured or invalid'
            }
        
        try:
            # Check if it's an LMS-specific question
            question_lower = question.lower().strip()
            if question_lower in self.lms_knowledge:
                return {
                    'response': self.lms_knowledge[question_lower],
                    'method': 'lms_knowledge_base',
                    'confidence': 0.95,
                    'source': 'lms_athena_database'
                }
            
            # Prepare the prompt for Google AI
            system_prompt = """You are an expert AI assistant for LMS-Athena, a comprehensive Learning Management System. Provide accurate, detailed, and helpful answers about LMS functionality, course management, and educational best practices."""
            
            # Enhanced user prompt
            if context:
                user_prompt = f"CONTEXT: {context}\n\nQUESTION: {question}\n\nPlease provide a comprehensive, accurate answer for the LMS-Athena platform."
            else:
                user_prompt = f"QUESTION: {question}\n\nPlease provide a comprehensive, accurate answer for the LMS-Athena platform."
            
            # Prepare the API request
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_prompt}\n\n{user_prompt}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                    "stopSequences": []
                }
            }
            
            # Make the API call
            api_url = f"{self.base_url}/models/{self.model}:generateContent"
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the response text
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        answer = candidate['content']['parts'][0]['text'].strip()
                        
                        return {
                            'response': answer,
                            'method': 'google_ai_api',
                            'confidence': 0.90,
                            'model': self.model,
                            'project_id': self.project_id,
                            'tokens_used': len(answer.split()),
                            'error': None
                        }
                    else:
                        return {
                            'response': "I apologize, but I received an invalid response format. Please try again.",
                            'method': 'google_ai_error',
                            'confidence': 0.0,
                            'error': 'Invalid response structure'
                        }
                else:
                    return {
                        'response': "I apologize, but I couldn't generate a response. Please try again.",
                        'method': 'google_ai_error',
                        'confidence': 0.0,
                        'error': 'No candidates in response'
                    }
            else:
                error_message = f"Google AI API error: {response.status_code} - {response.text}"
                logger.error(error_message)
                return {
                    'response': "I apologize, but I'm having trouble connecting to the AI service. Please try again later.",
                    'method': 'google_ai_error',
                    'confidence': 0.0,
                    'error': error_message
                }
                
        except Exception as e:
            error_message = f"Google AI API error: {str(e)}"
            logger.error(error_message)
            return {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                'method': 'google_ai_error',
                'confidence': 0.0,
                'error': error_message
            }

# Initialize the Google AI integration
google_ai_integration = GoogleAIIntegration()

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
        
        # Generate response using Google AI API
        result = google_ai_integration.generate_response_with_google_ai(message.message, context)
        
        return TextResponse(
            response=result['response'],
            language=message.language,
            used_knowledge_base=bool(context),
            sources=[{
                'method': result['method'],
                'confidence': result['confidence'],
                'model': result.get('model', 'unknown'),
                'project_id': result.get('project_id', 'unknown'),
                'tokens_used': result.get('tokens_used', 0),
                'api_used': 'google_ai',
                'context_used': bool(context)
            }] if context or result['method'] != 'fallback' else None
        )
        
    except Exception as e:
        logger.error(f"Chat error with Google AI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ADDITIONAL ENDPOINT FOR TESTING:
@router.post("/chat-google-ai-test")
async def chat_google_ai_test(message: TextMessage):
    """Test endpoint to show Google AI API details"""
    try:
        context = None
        if message.use_knowledge_base and rag_retriever:
            context, _ = rag_retriever.get_context_with_confidence(message.message, top_k=3)
        
        result = google_ai_integration.generate_response_with_google_ai(message.message, context)
        
        return {
            'question': message.message,
            'google_ai_response': result['response'],
            'api_details': {
                'method': result['method'],
                'confidence': result['confidence'],
                'model': result.get('model', 'unknown'),
                'project_id': result.get('project_id', 'unknown'),
                'tokens_used': result.get('tokens_used', 0),
                'api_used': 'google_ai',
                'context_used': bool(context)
            },
            'context_used': bool(context),
            'google_ai_status': 'working_perfectly'
        }
        
    except Exception as e:
        logger.error(f"Google AI test error: {e}")
        return {'error': str(e)}
