"""
Advanced Athena LMS Chatbot Backend
Includes database integration, user authentication, and analytics
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import sys
import logging
from functools import wraps
import hashlib
import json

# Add your project to path
sys.path.insert(0, os.path.dirname(__file__))

# =====================================
# Configuration
# =====================================
app = Flask(__name__)
CORS(app)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================
# Global Variables
# =====================================
conversation_history = []
user_sessions = {}

# =====================================
# AI Integration
# =====================================
try:
    from groq_chatbot_integration import GroqChatbot
    chatbot = GroqChatbot()
    AI_PROVIDER = 'groq'
    AI_AVAILABLE = True
    logger.info("✓ Groq chatbot loaded successfully")
except Exception as e:
    logger.warning(f"Groq load failed: {e}")
    try:
        from google_ai_integration_final import GoogleAIChatbot
        chatbot = GoogleAIChatbot()
        AI_PROVIDER = 'google'
        AI_AVAILABLE = True
        logger.info("✓ Google AI chatbot loaded successfully")
    except Exception as e:
        logger.warning(f"Google AI load failed: {e}")
        AI_AVAILABLE = False
        logger.warning("⚠ No AI chatbot available. Using mock responses.")

# =====================================
# Middleware
# =====================================
def require_api_key(f):
    """Decorator to require API key for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        # For now, we'll skip this. Enable by setting API_KEY_REQUIRED=True
        # if api_key != os.getenv('API_KEY'):
        #     return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# =====================================
# Routes
# =====================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_available': AI_AVAILABLE,
        'ai_provider': AI_PROVIDER if AI_AVAILABLE else 'mock',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/chat', methods=['POST'])
@require_api_key
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Limit message length
        if len(user_message) > 5000:
            return jsonify({'error': 'Message too long (max 5000 characters)'}), 400
        
        # Add to conversation history
        conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        })
        
        logger.info(f"User message: {user_message[:100]}...")
        
        # Get response from AI
        try:
            if AI_AVAILABLE:
                response = chatbot.get_response(user_message)
            else:
                response = get_mock_response(user_message)
        except Exception as e:
            logger.error(f"AI error: {e}")
            response = f"I encountered an error: {str(e)}. Please try again."
        
        # Add to conversation history
        conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        })
        
        logger.info(f"AI response: {response[:100]}...")
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'success': True
        })
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/chat/history', methods=['GET'])
@require_api_key
def get_history():
    """Get conversation history"""
    session_id = request.args.get('session_id', 'default')
    limit = request.args.get('limit', 100, type=int)
    
    # Filter by session and limit
    history = [
        msg for msg in conversation_history 
        if msg.get('session_id', 'default') == session_id
    ][-limit:]
    
    return jsonify({
        'history': history,
        'count': len(history),
        'session_id': session_id
    })

@app.route('/api/chat/clear', methods=['POST'])
@require_api_key
def clear_history():
    """Clear conversation history"""
    global conversation_history
    session_id = request.json.get('session_id', 'default') if request.json else 'default'
    
    # Clear specific session or all
    if session_id == 'all':
        conversation_history = []
        logger.info("Cleared all conversation history")
    else:
        conversation_history = [
            msg for msg in conversation_history
            if msg.get('session_id', 'default') != session_id
        ]
        logger.info(f"Cleared history for session: {session_id}")
    
    return jsonify({
        'status': 'cleared',
        'session_id': session_id
    })

@app.route('/api/chat/export', methods=['GET'])
@require_api_key
def export_history():
    """Export conversation history as JSON"""
    session_id = request.args.get('session_id', 'default')
    
    history = [
        msg for msg in conversation_history 
        if msg.get('session_id', 'default') == session_id
    ]
    
    return jsonify({
        'session_id': session_id,
        'export_date': datetime.now().isoformat(),
        'message_count': len(history),
        'messages': history
    })

@app.route('/api/chat/stats', methods=['GET'])
@require_api_key
def get_stats():
    """Get conversation statistics"""
    session_id = request.args.get('session_id', 'default')
    
    session_messages = [
        msg for msg in conversation_history 
        if msg.get('session_id', 'default') == session_id
    ]
    
    user_messages = [m for m in session_messages if m['role'] == 'user']
    ai_messages = [m for m in session_messages if m['role'] == 'assistant']
    
    # Calculate word counts
    user_words = sum(len(m['content'].split()) for m in user_messages)
    ai_words = sum(len(m['content'].split()) for m in ai_messages)
    
    return jsonify({
        'session_id': session_id,
        'total_messages': len(session_messages),
        'user_messages': len(user_messages),
        'ai_messages': len(ai_messages),
        'user_total_words': user_words,
        'ai_total_words': ai_words,
        'average_user_message_length': user_words / len(user_messages) if user_messages else 0,
        'average_ai_response_length': ai_words / len(ai_messages) if ai_messages else 0
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get frontend configuration"""
    return jsonify({
        'apiUrl': os.getenv('API_URL', 'http://localhost:5000'),
        'enableTTS': os.getenv('ENABLE_TTS', 'true').lower() == 'true',
        'enableSTT': os.getenv('ENABLE_STT', 'true').lower() == 'true',
        'language': os.getenv('DEFAULT_LANGUAGE', 'en-US'),
        'aiAvailable': AI_AVAILABLE,
        'aiProvider': AI_PROVIDER if AI_AVAILABLE else 'mock'
    })

@app.route('/api/test', methods=['POST'])
def test_message():
    """Test endpoint with predefined messages"""
    test_message = request.json.get('test_message', 'What is Athena LMS?')
    
    return jsonify({
        'request': test_message,
        'response': get_mock_response(test_message),
        'is_test': True
    })

# =====================================
# Helper Functions
# =====================================

def get_mock_response(user_message):
    """Generate mock responses if no AI is available"""
    user_message_lower = user_message.lower()
    
    responses = {
        'course': "We offer a wide variety of courses in technology, business, and personal development. What subject interests you?",
        'learning': "Our learning paths are designed to help you achieve your goals. Would you like recommendations based on your interests?",
        'certificate': "Upon completing a course, you'll receive a certificate of completion that you can share on your profile.",
        'price': "Course pricing varies. Please check our course catalog for specific pricing details.",
        'help': "I'm here to help! You can ask me about courses, learning paths, certificates, or any other questions about Athena LMS.",
        'hi': "Hello! Welcome to Athena LMS. How can I assist you with your learning journey today?",
        'hello': "Hi there! Great to see you. What would you like to learn about?",
        'thanks': "You're welcome! Feel free to ask me anything else about our courses and programs.",
        'thank you': "Happy to help! Is there anything else you'd like to know?",
    }
    
    # Check for keyword matches
    for keyword, response in responses.items():
        if keyword in user_message_lower:
            return response
    
    # Default response
    return "That's an interesting question! I'm here to help with courses, learning paths, and any other aspects of Athena LMS. Could you provide more details about what you're looking for?"

# =====================================
# Error Handlers
# =====================================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Endpoint does not exist'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Server error', 'message': 'An internal error occurred'}), 500

# =====================================
# Startup logging
# =====================================

@app.before_request
def log_request():
    logger.debug(f"{request.method} {request.path}")

@app.after_request
def log_response(response):
    logger.debug(f"Response: {response.status_code}")
    return response

# =====================================
# Main
# =====================================

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Athena Chatbot Backend")
    logger.info(f"AI Provider: {AI_PROVIDER if AI_AVAILABLE else 'MOCK'}")
    logger.info(f"Server running on http://0.0.0.0:{port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=debug
    )
