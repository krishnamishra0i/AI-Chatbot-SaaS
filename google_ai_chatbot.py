"""
Google Generative AI Integration for ATHENA Chatbot
Provides real-time intelligent responses using Google's Gemini API
"""

import google.generativeai as genai
import os
from typing import Optional

class GoogleAIChatbot:
    """
    Google Generative AI (Gemini) powered chatbot for ATHENA
    Provides intelligent, real-time responses
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google AI Chatbot
        
        Args:
            api_key: Google API key (from environment if not provided)
        """
        try:
            # Get API key from parameter or environment
            self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
            
            if not self.api_key:
                raise ValueError("Google API key not found. Set GOOGLE_API_KEY environment variable.")
            
            # Configure Google AI
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Conversation history for context
            self.chat_history = []
            
            # System prompt for the chatbot
            self.system_prompt = """You are Ambassador Paul, an AI Learning Expert for ATHENA AI - a cutting-edge learning platform.

Your role:
- Provide helpful, accurate information about ATHENA AI, courses, and e-learning
- Be friendly, professional, and engaging
- Answer questions about learning paths, course enrollment, certificates, and platform features
- Offer personalized learning recommendations when appropriate
- Help resolve technical issues and provide support

Key Information about ATHENA AI:
- ATHENA is an enterprise-grade learning platform with AI-powered features
- We offer courses in technology, business, and personal development
- All users get certificates upon course completion
- Real-time collaboration and interactive learning experiences
- Mobile-friendly and accessible from anywhere
- 24/7 support available

Always:
- Be concise but informative
- Use friendly, conversational language
- Ask clarifying questions if needed
- Suggest relevant courses or learning paths when appropriate
- Maintain context from previous messages

Remember: You're here to help users succeed in their learning journey!"""
            
            print("✓ Google AI Chatbot initialized successfully")
            
        except Exception as e:
            print(f"✗ Error initializing Google AI Chatbot: {str(e)}")
            self.model = None
    
    def get_response(self, user_message: str) -> str:
        """
        Get an AI-powered response to the user's message
        
        Args:
            user_message: The user's question or message
            
        Returns:
            AI-generated response string
        """
        try:
            if not self.model:
                return "I'm currently unavailable. Please try again later."
            
            # Add user message to history
            self.chat_history.append({
                "role": "user",
                "parts": [user_message]
            })
            
            try:
                # Create chat session with history
                chat = self.model.start_chat(history=self.chat_history)
                
                # Generate response with system prompt
                prompt = f"{self.system_prompt}\n\nUser: {user_message}"
                response = chat.send_message(prompt, stream=False)
                
                bot_response = response.text
                
                # Add bot response to history
                self.chat_history.append({
                    "role": "model",
                    "parts": [bot_response]
                })
                
                # Keep history to last 10 exchanges (for context and API efficiency)
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
                
                return bot_response
                
            except Exception as e:
                error_msg = str(e)
                if "API key" in error_msg or "authentication" in error_msg.lower():
                    return "Authentication error: Please check your Google API key configuration."
                elif "overloaded" in error_msg.lower():
                    return "The service is temporarily overloaded. Please try again in a moment."
                else:
                    return f"I encountered an issue: {error_msg}. Please try again."
        
        except Exception as e:
            print(f"Error in get_response: {str(e)}")
            return f"An unexpected error occurred: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.chat_history = []
        print("Conversation history cleared")


# Simple test function
def test_chatbot():
    """Test the chatbot integration"""
    try:
        chatbot = GoogleAIChatbot()
        
        # Test messages
        test_messages = [
            "What is ATHENA AI?",
            "How do I enroll in a course?",
            "Do I get certificates?"
        ]
        
        print("\n=== Testing Google AI Chatbot ===\n")
        
        for msg in test_messages:
            print(f"User: {msg}")
            response = chatbot.get_response(msg)
            print(f"Bot: {response}\n")
        
        print("✓ Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")


if __name__ == "__main__":
    test_chatbot()
