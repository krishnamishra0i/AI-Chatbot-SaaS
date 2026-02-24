#!/usr/bin/env python3
"""
Direct Chat Implementation - Uses Comprehensive System Directly
This bypasses all the old logic and directly calls the answer system
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os
from pathlib import Path

# Add paths
workspace_root = Path(__file__).parents[3]
sys.path.insert(0, str(workspace_root))

# Load comprehensive system DIRECTLY
print("[INIT] Loading Direct Answer System...")
try:
    from comprehensive_answer_system import ComprehensiveAnswerSystem
    answer_system = ComprehensiveAnswerSystem()
    print(f"[OK] Comprehensive System: {len(answer_system.answers)} answers loaded")
except Exception as e:
    print(f"[ERROR] Failed to load: {e}")
    answer_system = None

# Models
class TextMessage(BaseModel):
    message: str
    language: str = "en"

class TextResponse(BaseModel):
    response: str
    language: str
    confidence: float
    source: str

# Router
router = APIRouter()

@router.post("/chat")
async def chat(message: TextMessage):
    """Direct chat using comprehensive answer system"""
    
    if not answer_system:
        raise HTTPException(status_code=500, detail="Answer system not loaded")
    
    try:
        user_message = message.message.strip()
        print(f"[CHAT] User: {user_message}")
        
        # Get answer directly
        result = answer_system.get_answer(user_message)
        
        print(f"[ANSWER] Confidence: {result.get('confidence')}")
        print(f"[ANSWER] Method: {result.get('method')}")
        
        return TextResponse(
            response=result.get('answer', 'No answer'),
            language=message.language,
            confidence=result.get('confidence', 0),
            source=result.get('source', 'Comprehensive System')
        )
        
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_stream(message: TextMessage):
    """Streaming chat endpoint"""
    
    if not answer_system:
        raise HTTPException(status_code=500, detail="Answer system not loaded")
    
    try:
        user_message = message.message.strip()
        result = answer_system.get_answer(user_message)
        
        return TextResponse(
            response=result.get('answer', 'No answer'),
            language=message.language,
            confidence=result.get('confidence', 0),
            source=result.get('source', 'Comprehensive System')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
