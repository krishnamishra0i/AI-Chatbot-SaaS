# FINAL INTEGRATION CODE FOR chat_routes.py
# Copy this into your ai_avatar_chatbot/backend/api/chat_routes.py

# IMPORTS - Add these at the top with your other imports
import sys
sys.path.append('..')
from clean_optimized_chatbot import CleanOptimizedChatbot

# INITIALIZATION - Add this near your other initializations
clean_chatbot = CleanOptimizedChatbot()

# REPLACE your chat endpoint with this clean, optimized version:
@router.post("/chat")
async def chat(message: TextMessage):
    try:
        # Get accurate answer from clean chatbot
        result = clean_chatbot.get_accurate_answer(message.message)
        
        return TextResponse(
            response=result['answer'],
            language=message.language,
            used_knowledge_base=True,
            sources=[{
                'confidence': result['confidence'],
                'method': result['method'],
                'source': result['source']
            }]
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ADDITIONAL ENDPOINT FOR TESTING (optional)
@router.post("/chat-test")
async def chat_test(message: TextMessage):
    """Test endpoint to show chatbot details"""
    try:
        result = clean_chatbot.get_accurate_answer(message.message)
        
        return {
            'question': message.message,
            'answer': result['answer'],
            'confidence': result['confidence'],
            'method': result['method'],
            'source': result['source'],
            'status': 'working_perfectly'
        }
        
    except Exception as e:
        logger.error(f"Chat test error: {e}")
        return {'error': str(e)}
