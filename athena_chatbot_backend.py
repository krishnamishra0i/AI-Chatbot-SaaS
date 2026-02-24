from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import sys

# Add your project to path
sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

# Import your existing chatbot/AI integration
try:
    from google_ai_chatbot import GoogleAIChatbot
    chatbot = GoogleAIChatbot(api_key="AIzaSyDBx4_5GdBC0bUfVkW6_Ub02PorVlm1uls")
    AI_AVAILABLE = True
    print("✓ Google AI integration loaded")
except ImportError:
    try:
        from groq_chatbot_integration import GroqChatbot
        chatbot = GroqChatbot()
        AI_AVAILABLE = True
        print("✓ Groq AI integration loaded")
    except ImportError:
        AI_AVAILABLE = False
        print("⚠ No AI chatbot available. Using mock responses. Install google-generativeai or groq")
except Exception as e:
    AI_AVAILABLE = False
    print(f"⚠ Error loading AI integration: {str(e)}. Using mock responses.")

# Store conversation history
conversation_history = []

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Add to history
        conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get response from AI
        if AI_AVAILABLE:
            try:
                response = chatbot.get_response(user_message)
            except Exception as e:
                response = f"I encountered an error: {str(e)}. Please try again."
        else:
            # Mock response if no AI available
            response = get_mock_response(user_message)
        
        # Add to history
        conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    return jsonify(conversation_history)

@app.route('/api/chat/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({'status': 'cleared'})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_available': AI_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

def get_mock_response(user_message):
    """Generate mock responses if no AI is available"""
    user_message_lower = user_message.lower()
    
    responses = {
        'course': "We offer a wide variety of courses in technology, business, and personal development. What subject interests you?",
        'learning': "Our learning paths are designed to help you achieve your goals. Would you like recommendations based on your interests?",
        'certificate': "Upon completing a course, you'll receive a certificate of completion that you can share on your profile.",
        'price': "Course pricing varies. Please check our course catalog for specific pricing details.",
        'certificate': "All completed courses come with a certificate of completion.",
        'help': "I'm here to help! You can ask me about courses, learning paths, certificates, or any other questions about Athena LMS.",
    }
    
    for keyword, response in responses.items():
        if keyword in user_message_lower:
            return response
    
    return "That's an interesting question! I'm here to help with courses, learning paths, and any other aspects of Athena LMS. Could you provide more details?"

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
