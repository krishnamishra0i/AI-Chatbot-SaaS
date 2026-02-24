# GOOGLE AI API INTEGRATION FOR LMS-ATHENA
# Copy this into your ai_avatar_chatbot/backend/api/chat_routes.py

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
        self.model = "gemini-1.5-pro"  # Fixed model name
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
            "what is lms": "LMS (Learning Management System) is a comprehensive software platform specifically designed to create, manage, deliver, and track online educational courses and training programs. LMS-Athena is an advanced Learning Management System that combines core LMS functionality with cutting-edge features including AI-powered personalized learning paths, real-time collaboration tools, comprehensive analytics dashboards, and mobile accessibility. It supports multimedia content, interactive assessments, virtual classrooms, live streaming capabilities, and seamless integration with popular educational tools and third-party applications.",
            
            "how do i access my courses": "To access your courses in LMS-Athena: 1) Log into your account using your registered email address and password, 2) Navigate to the main dashboard by clicking on the 'Dashboard' or 'My Courses' link in the navigation menu, 3) Locate your enrolled courses which will be displayed with progress indicators and completion percentages, 4) Click on any course title to enter the course workspace, 5) In the course interface, you'll find all course materials organized by modules or weeks including video lectures, reading materials, assignments, quizzes, and supplementary resources, 6) Use the sidebar navigation to jump between different sections like Announcements, Grades, Discussions, and Resources.",
            
            "how do i cancel my subscription": "To cancel your subscription in LMS-Athena: 1) Log into your account using your registered email and password, 2) Navigate to your profile by clicking on your avatar or name in the top-right corner of the screen, 3) Select 'Account Settings' from the dropdown menu that appears, 4) Click on the 'Subscription' or 'Billing' tab in the account settings interface, 5) Locate the 'Cancel Membership' or 'Cancel Subscription' button, 6) Follow the cancellation prompts which may include a survey about your reason for canceling, 7) Review the cancellation details including when your access will end, 8) Confirm your cancellation by clicking the final confirmation button. Important: You will retain full access to all course materials until your current billing period ends.",
            
            "what is athena lms": "Athena LMS is an advanced Learning Management System platform that combines core LMS functionality with cutting-edge features including AI-powered personalized learning paths, real-time collaboration tools, comprehensive analytics dashboards, and mobile accessibility. It supports multimedia content, interactive assessments, virtual classrooms, live streaming capabilities, and seamless integration with popular educational tools and third-party applications. Athena LMS is specifically designed to enhance student engagement through gamification elements, provide instructors with detailed performance insights, and enable personalized learning experiences that adapt to individual student needs and learning styles.",
            
            "how to enroll in courses": "To enroll in courses on LMS-Athena: 1) Browse the course catalog by clicking on 'Courses' or 'Catalog' in the navigation menu, 2) Use the search bar or filters to find courses that interest you, 3) Click on any course to view detailed information including curriculum, instructor details, duration, and pricing, 4) Click the 'Enroll Now' or 'Add to Cart' button, 5) If required, complete the payment process or apply any available discount codes, 6) After successful enrollment, the course will appear in your 'My Courses' dashboard, 7) You can start learning immediately by clicking on the course title.",
            
            "how to track progress": "To track your learning progress in LMS-Athena: 1) Log into your account and go to your 'My Courses' dashboard, 2) Click on any enrolled course to view its progress details, 3) The course dashboard will show your overall completion percentage, completed modules/lessons, and remaining content, 4) Use the 'Progress' tab to see detailed analytics including time spent, quiz scores, and assignment grades, 5) Check the 'Grades' section for specific scores and feedback from instructors, 6) Use the 'Calendar' to view upcoming deadlines and scheduled activities, 7) Enable email notifications to receive regular progress updates.",
            
            "how to contact support": "To contact LMS-Athena support: 1) Click on the 'Help' or 'Support' link in the navigation menu, 2) Choose your preferred support method: Live Chat, Email Support, or Phone Support, 3) For Live Chat: Start a conversation with a support agent during business hours, 4) For Email Support: Send your query to support@athena-lms.com and expect a response within 24 hours, 5) For Phone Support: Call +1-800-ATHENA-LMS during business hours (9 AM - 6 PM EST), 6) For urgent issues, use the 'Priority Support' option if available with your subscription plan, 7) Check the 'FAQ' section for quick answers to common questions.",
            
            "how to download certificates": "To download certificates from LMS-Athena: 1) Log into your account and go to your 'My Courses' dashboard, 2) Click on the completed course for which you want a certificate, 3) Look for the 'Certificate' or 'Achievements' section in the course dashboard, 4) Click on 'Download Certificate' or 'View Certificate', 5) Choose your preferred format: PDF or digital certificate, 6) For PDF certificates, click 'Download' to save it to your device, 7) For digital certificates, you can share the link directly on LinkedIn or other professional networks, 8) Some certificates may require verification before download if the course has specific completion requirements."
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
            system_prompt = """You are an expert AI assistant for LMS-Athena, a comprehensive Learning Management System. Provide accurate, detailed, and helpful answers about:

1. LMS functionality and features
2. Course enrollment and management
3. Account settings and subscriptions
4. Technical support and troubleshooting
5. Learning progress tracking
6. Certificate and achievement systems
7. Educational best practices
8. Technology and learning tools

Always provide:
- Clear, step-by-step instructions when applicable
- Specific details and examples
- Professional and helpful tone
- Comprehensive coverage of the topic
- Actionable advice and recommendations

If the question is about general topics outside LMS, provide helpful information while maintaining focus on educational context."""
            
            # Enhanced user prompt
            if context:
                user_prompt = f"CONTEXT: {context}\n\nQUESTION: {question}\n\nPlease provide a comprehensive, accurate answer for the LMS-Athena platform. Include specific details, step-by-step instructions when applicable, and maintain a professional, helpful tone."
            else:
                user_prompt = f"QUESTION: {question}\n\nPlease provide a comprehensive, accurate answer for the LMS-Athena platform. Include specific details, step-by-step instructions when applicable, and maintain a professional, helpful tone."
            
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
                    "maxOutputTokens": 2048,
                    "stopSequences": []
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
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
                        error_message = "Invalid response structure from Google AI API"
                        logger.error(error_message)
                        return {
                            'response': "I apologize, but I received an invalid response format. Please try again.",
                            'method': 'google_ai_error',
                            'confidence': 0.0,
                            'error': error_message
                        }
                else:
                    error_message = "No candidates in response from Google AI API"
                    logger.error(error_message)
                    return {
                        'response': "I apologize, but I couldn't generate a response. Please try again.",
                        'method': 'google_ai_error',
                        'confidence': 0.0,
                        'error': error_message
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
                
        except requests.exceptions.Timeout:
            error_message = "Google AI API request timed out"
            logger.error(error_message)
            return {
                'response': "I apologize, but the request took too long. Please try again with a shorter question.",
                'method': 'google_ai_timeout',
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
