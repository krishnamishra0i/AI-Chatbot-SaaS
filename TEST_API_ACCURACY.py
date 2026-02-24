#!/usr/bin/env python3
"""
Test the Chat API with accurate answers
"""
import httpx
import json
import asyncio

async def test_chat_api():
    """Test chat API endpoints"""
    print("\n" + "="*70)
    print("TESTING CHAT API - ACCURATE ANSWER SYSTEM")
    print("="*70)
    
    base_url = "http://localhost:8000"
    
    test_questions = [
        "hii",  # The problem case from the screenshot
        "hello",
        "what is creditor academy",
        "what is the freedom formula",
        "what is sovereignty"
    ]
    
    async with httpx.AsyncClient() as client:
        for question in test_questions:
            try:
                print(f"\n{'─'*70}")
                print(f"Q: {question}")
                
                response = await client.post(
                    f"{base_url}/api/chat",
                    json={
                        "message": question,
                        "language": "en",
                        "use_knowledge_base": True
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("response", "No answer")
                    sources = data.get("sources", [])
                    
                    print(f"A: {answer[:150]}...")
                    if sources:
                        print(f"Source: {sources[0].get('accuracy', sources[0].get('method', 'unknown'))}")
                    print("✅ Success")
                else:
                    print(f"Error: Status {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"Connection error: {e}")
    
    print("\n" + "="*70)
    print("Testing complete! Check if answers are about Creditor Academy")
    print("="*70 + "\n")

asyncio.run(test_chat_api())
