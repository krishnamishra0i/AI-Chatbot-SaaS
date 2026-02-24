#!/usr/bin/env python3
"""
Test the API with updated tech answers
"""
import httpx
import asyncio

async def test_api():
    print("\n" + "="*80)
    print("TESTING API - AFTER FIXING TECH QUESTIONS")
    print("="*80)
    
    questions = [
        'what is ai',
        'what is deep learning',
        'what is aws',
        'what is creditor academy'
    ]
    
    async with httpx.AsyncClient() as client:
        for q in questions:
            try:
                resp = await client.post(
                    "http://localhost:8000/api/chat",
                    json={"message": q, "language": "en", "use_knowledge_base": True},
                    timeout=5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    ans = data.get("response", "No answer")
                    print(f"\nQ: {q}")
                    print(f"A: {ans[:130]}...")
                else:
                    print(f"\nQ: {q}")
                    print(f"Error: {resp.status_code}")
            except Exception as e:
                print(f"\nQ: {q}")
                print(f"Connection error: {e}")

    print("\n" + "="*80 + "\n")

asyncio.run(test_api())
