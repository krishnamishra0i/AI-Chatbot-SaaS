#!/usr/bin/env python3
"""
Test comprehensive answer system through API
"""
import httpx
import asyncio

async def test_api_comprehensive():
    print("\n" + "="*100)
    print("TESTING API WITH COMPREHENSIVE ANSWER SYSTEM (200+ ACCURATE ANSWERS)")
    print("="*100)
    
    test_cases = [
        ('what is creditor academy', 'Creditor Academy'),
        ('what is the freedom formula', 'Freedom Formula'),
        ('what is ai', 'Artificial Intelligence'),
        ('what is machine learning', 'Machine Learning'),
        ('what is aws', 'Amazon Web Services'),
        ('what is business', 'Business'),
        ('what is marketing', 'marketing'),
        ('how do i save money', 'budget'),
        ('what is investment', 'allocating money'),
        ('hii', 'Creditor Academy'),
    ]
    
    passed = 0
    async with httpx.AsyncClient() as client:
        for question, expected_keyword in test_cases:
            try:
                resp = await client.post(
                    "http://localhost:8000/api/chat",
                    json={"message": question, "language": "en"},
                    timeout=5
                )
                
                if resp.status_code == 200:
                    answer = resp.json().get("response", "")
                    has_keyword = expected_keyword.lower() in answer.lower()
                    status = "✅" if has_keyword else "❌"
                    passed += 1 if has_keyword else 0
                    
                    print(f"{status} Q: {question}")
                    print(f"   A: {answer[:110]}...")
                else:
                    print(f"❌ Q: {question} | Error: {resp.status_code}")
            except Exception as e:
                print(f"❌ Q: {question} | Error: {e}")
    
    total = len(test_cases)
    percent = int(100 * passed / total)
    print("\n" + "="*100)
    print(f"RESULT: {passed}/{total} tests passed ({percent}%)")
    if percent >= 80:
        print("🎉 COMPREHENSIVE ANSWER SYSTEM IS WORKING!")
    print("="*100 + "\n")

asyncio.run(test_api_comprehensive())
