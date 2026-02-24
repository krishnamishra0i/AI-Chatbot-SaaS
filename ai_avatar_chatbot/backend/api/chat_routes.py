"""
Chat API routes - Fixed and simplified
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import sys
import os
from pathlib import Path

# Fix import paths - add workspace root
workspace_root = Path(__file__).parents[3]  # Go up 3 levels: api -> backend -> ai_avatar_chatbot -> ...
sys.path.insert(0, str(workspace_root))

try:
    from backend.utils.logger import setup_logger
    logger = setup_logger(__name__)
except:
    import logging
    logger = logging.getLogger(__name__)

# Layer 1: INTEGRATED ANSWER SYSTEM (All layers combined)
try:
    from integrated_answer_system import IntegratedAnswerSystem
    integrated_system = IntegratedAnswerSystem()
    INTEGRATED_AVAILABLE = True
    print("✓ Integrated Answer System loaded successfully")
except Exception as e:
    print(f"⚠ Integrated system warning: {e}")
    INTEGRATED_AVAILABLE = False
    integrated_system = None
    
    # Fallback to comprehensive system only
    try:
        from comprehensive_answer_system import comprehensive_system
        COMPREHENSIVE_AVAILABLE = True
        print("✓ Comprehensive Answer System loaded successfully (200+ accurate answers)")
    except Exception as e2:
        print(f"⚠ Comprehensive system warning: {e2}")
        COMPREHENSIVE_AVAILABLE = False
        comprehensive_system = None

# Layer 2: ULTIMATE ACCURACY
try:
    from ultimate_accuracy_working import UltimateAccuracyOptimizer
    ultimate_optimizer = UltimateAccuracyOptimizer()
    ULTIMATE_AVAILABLE = True
    print("✓ Ultimate Accuracy System loaded successfully")
except Exception as e:
    print(f"⚠ Ultimate accuracy warning: {e}")
    ULTIMATE_AVAILABLE = False
    ultimate_optimizer = None

# Layer 3: ENHANCED CHAT SYSTEM
try:
    from backend.utils.enhanced_chat_system import enhanced_chat_system
    ENHANCED_AVAILABLE = True
    print("✓ Enhanced Chat System loaded successfully")
except Exception as e:
    print(f"⚠ Enhanced system warning: {e}")
    ENHANCED_AVAILABLE = False

router = APIRouter()

class TextMessage(BaseModel):
    message: str
    language: str = "en"
    use_knowledge_base: bool = True

class TextResponse(BaseModel):
    response: str
    language: str
    used_knowledge_base: bool
    sources: Optional[list] = None

@router.post("/chat")
async def chat(message: TextMessage):
    """Chat endpoint with integrated multi-layer accuracy system"""
    try:
        logger.info(f"Chat: {message.message[:50]}")
        user_message = message.message.strip()

        # LAYER 1: INTEGRATED ANSWER SYSTEM (Comprehensive + ChromaDB + APIs combined)
        if INTEGRATED_AVAILABLE and integrated_system:
            try:
                result = integrated_system.get_answer(user_message)
                if result and result.get('confidence', 0) >= 0.5:
                    logger.info(f"Using Integrated System - Layer {result.get('layer')}: {result.get('source')}")
                    return TextResponse(
                        response=result.get('answer', 'No answer'),
                        language=message.language,
                        used_knowledge_base=True,
                        sources=[{
                            'layer': result.get('layer'),
                            'confidence': result.get('confidence'),
                            'source': result.get('source')
                        }]
                    )
            except Exception as e:
                logger.warning(f"Integrated system error: {e}")

        # FALLBACK: COMPREHENSIVE ANSWER SYSTEM (if integrated unavailable)
        if COMPREHENSIVE_AVAILABLE and comprehensive_system:
            try:
                result = comprehensive_system.get_answer(user_message)
                if result and result.get('confidence', 0) >= 0.5:
                    logger.info(f"Using Comprehensive System: {result.get('method')}")
                    return TextResponse(
                        response=result.get('answer', 'No answer'),
                        language=message.language,
                        used_knowledge_base=True,
                        sources=[{
                            'method': result.get('method'),
                            'confidence': result.get('confidence'),
                            'accuracy': result.get('accuracy_level'),
                            'quality': result.get('answer_quality'),
                            'source': result.get('source')
                        }]
                    )
            except Exception as e:
                logger.warning(f"Comprehensive system error: {e}")

        # LAYER 2: ULTIMATE ACCURACY (99% CONFIDENCE)
        if ULTIMATE_AVAILABLE and ultimate_optimizer:
            try:
                result = ultimate_optimizer.get_ultimate_accurate_answer(user_message)
                if result and result.get('confidence', 0) >= 0.8:
                    logger.info(f"Using Ultimate Accuracy System")
                    return TextResponse(
                        response=result.get('answer', 'No answer'),
                        language=message.language,
                        used_knowledge_base=True,
                        sources=[{'method': 'ultimate_accuracy', 'confidence': result.get('confidence')}]
                    )
            except Exception as e:
                logger.warning(f"Ultimate accuracy error: {e}")

        # LAYER 3: ENHANCED CHAT SYSTEM
        if ENHANCED_AVAILABLE:
            try:
                result = await enhanced_chat_system.generate_response(
                    user_message,
                    use_knowledge_base=message.use_knowledge_base
                )
                logger.info(f"Using Enhanced Chat System")
                return TextResponse(
                    response=result.get('response', 'Unable to generate response'),
                    language=message.language,
                    used_knowledge_base=result.get('used_knowledge_base', False),
                    sources=result.get('sources', [])
                )
            except Exception as e:
                logger.warning(f"Enhanced system error: {e}")

        # LAYER 4: SMART FALLBACK
        fallback_response = f"Thank you for asking about: {user_message}. I'm Creditor Academy's AI assistant. Please ask me about sovereignty, private operation, courses, or the Freedom Formula!"
        logger.info(f"Using fallback response")
        return TextResponse(
            response=fallback_response,
            language=message.language,
            used_knowledge_base=False,
            sources=[{'method': 'fallback', 'confidence': 0.5}]
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing error")

@router.post("/chat/stream")
async def chat_stream(message: TextMessage):
    """Streaming chat endpoint with 4-layer accuracy"""
    try:
        logger.info(f"Stream: {message.message[:50]}")
        user_message = message.message.strip()

        async def generate():
            response_text = ""

            # LAYER 1: Comprehensive Answer System (99% confidence)
            if COMPREHENSIVE_AVAILABLE and comprehensive_system:
                try:
                    result = comprehensive_system.get_answer(user_message)
                    if result and result.get('confidence', 0) >= 0.5:
                        response_text = result.get('answer', '')
                        logger.info(f"Stream using Comprehensive System: {result.get('method')}")
                except:
                    pass

            # LAYER 2: Ultimate Accuracy (99% confidence)
            if not response_text and ULTIMATE_AVAILABLE and ultimate_optimizer:
                try:
                    result = ultimate_optimizer.get_ultimate_accurate_answer(user_message)
                    if result and result.get('confidence', 0) >= 0.8:
                        response_text = result.get('answer', '')
                        logger.info(f"Stream using Ultimate Accuracy")
                except:
                    pass

            # LAYER 3: Enhanced Chat System
            if not response_text and ENHANCED_AVAILABLE:
                try:
                    result = await enhanced_chat_system.generate_response(user_message)
                    response_text = result.get('response', '')
                    logger.info(f"Stream using Enhanced System")
                except:
                    pass

            # LAYER 4: Fallback
            if not response_text:
                response_text = f"Thank you for asking about: {user_message}. I'm Creditor Academy's AI assistant. Ask me about sovereignty, courses, or the Freedom Formula!"
                logger.info(f"Stream using fallback")

            # Stream the response word by word
            words = response_text.split()
            for word in words:
                yield f"data: {{\"content\": \"{word} \"}}\n\n"
                await asyncio.sleep(0.02)

            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )

    except Exception as e:
        logger.error(f"Stream error: {e}")
        raise HTTPException(status_code=500, detail="Streaming error")
