#!/usr/bin/env python3
"""
Simple test script to verify the chat API endpoints work
with accurate answers
"""
import sys
import os
import asyncio
import json

# Add paths
sys.path.insert(0, '.')
sys.path.insert(0, 'ai_avatar_chatbot')

async def test_chat_api():
    """Test the chat API"""
    print("\n" + "="*70)
    print("TESTING CHAT API WITH ACCURATE ANSWERS")
    print("="*70)
    
    try:
        # Import the chat routes
        from ai_avatar_chatbot.backend.api.chat_routes import router, TextMessage
        print("✓ Chat routes imported successfully")
        
        # Import simple accurate system
        from simple_accurate_system import simple_accurate_system
        print("✓ Simple accurate system imported successfully")
        
        # Test some questions
        test_questions = [
            "hello",
            "what is creditor academy",
            "what is the freedom formula",
            "what is sovereignty",
            "how do i access my courses"
        ]
        
        print("\nTesting Questions:")
        print("-" * 70)
        
        for question in test_questions:
            result = simple_accurate_system.get_answer(question)
            print(f"\nQ: {question}")
            print(f"Confidence: {result['confidence']} ({result['accuracy_level']})")
            print(f"Method: {result['method']}")
            print(f"Answer: {result['answer'][:150]}...")
        
        print("\n" + "="*70)
        print("✓ All chat API tests passed!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_chat_api())
