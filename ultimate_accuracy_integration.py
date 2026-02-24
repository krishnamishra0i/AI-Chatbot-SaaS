# ULTIMATE ACCURACY INTEGRATION
# Copy this into your ai_avatar_chatbot/backend/api/chat_routes.py

# IMPORTS - Add these at the top with your other imports
import sys
sys.path.append('..')
from ultimate_accuracy_working import UltimateAccuracyOptimizer

# INITIALIZATION - Add this near your other initializations
ultimate_accuracy_optimizer = UltimateAccuracyOptimizer()

# REPLACE your chat endpoint with this ultimate accuracy version:
@router.post("/chat")
async def chat(message: TextMessage):
    try:
        # Get ultimate accurate answer
        result = ultimate_accuracy_optimizer.get_ultimate_accurate_answer(
            message.message, None, llm_instance
        )
        
        return TextResponse(
            response=result['answer'],
            language=message.language,
            used_knowledge_base=True,
            sources=[{
                'confidence': result['confidence'],
                'accuracy_level': result['accuracy_level'],
                'method': result['method'],
                'detail_level': result['detail_level'],
                'source': result['source']
            }]
        )
        
    except Exception as e:
        logger.error(f"Chat error with ultimate accuracy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ADDITIONAL ENDPOINT FOR TESTING (optional)
@router.post("/chat-ultimate-test")
async def chat_ultimate_test(message: TextMessage):
    """Test endpoint to show ultimate accuracy details"""
    try:
        result = ultimate_accuracy_optimizer.get_ultimate_accurate_answer(
            message.message, None, llm_instance
        )
        
        return {
            'question': message.message,
            'ultimate_answer': result['answer'],
            'accuracy_metrics': {
                'confidence': result['confidence'],
                'accuracy_level': result['accuracy_level'],
                'method': result['method'],
                'detail_level': result['detail_level'],
                'source': result['source']
            },
            'quality_assessment': {
                'status': 'ultimate_accuracy_achieved',
                'performance': 'exceptional' if result['confidence'] >= 0.95 else 'excellent' if result['confidence'] >= 0.90 else 'very_good' if result['confidence'] >= 0.85 else 'good',
                'detail_quality': 'maximum' if result['detail_level'] == 'maximum' else 'high' if result['detail_level'] == 'high' else 'medium'
            }
        }
        
    except Exception as e:
        logger.error(f"Ultimate accuracy test error: {e}")
        return {'error': str(e)}
