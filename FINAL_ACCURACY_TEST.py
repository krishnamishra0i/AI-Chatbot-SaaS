#!/usr/bin/env python3
"""
Full verification of the fix
"""
import httpx
import asyncio

async def test_full():
    print("\n" + "="*100)
    print("CREDITOR ACADEMY CHATBOT - ACCURACY FIX VERIFICATION")
    print("="*100)
    
    test_cases = [
        {
            'question': 'what is ai',
            'should_contain': ['Artificial Intelligence', 'computer systems', 'human intelligence']
        },
        {
            'question': 'what is deep learning',
            'should_contain': ['Deep Learning', 'neural networks', 'layers']
        },
        {
            'question': 'what is aws',
            'should_contain': ['Amazon Web Services', 'cloud computing', 'infrastructure']
        },
        {
            'question': 'what is creditor academy',
            'should_contain': ['Creditor Academy', 'sovereignty education', 'private economy']
        },
        {
            'question': 'hii',
            'should_contain': ['Welcome to Creditor Academy', '👋']
        }
    ]
    
    async with httpx.AsyncClient() as client:
        all_pass = True
        for test in test_cases:
            q = test['question']
            should_have = test['should_contain']
            
            try:
                resp = await client.post(
                    "http://localhost:8000/api/chat",
                    json={"message": q, "language": "en"},
                    timeout=5
                )
                
                if resp.status_code == 200:
                    answer = resp.json().get("response", "")
                    
                    # Check if answer contains expected keywords
                    has_all = all(keyword.lower() in answer.lower() for keyword in should_have)
                    status = "✅ PASS" if has_all else "❌ FAIL"
                    all_pass = all_pass and has_all
                    
                    print(f"\n{status} | Q: {q}")
                    print(f"    A: {answer[:100]}...")
                    if not has_all:
                        print(f"    Missing: {[k for k in should_have if k.lower() not in answer.lower()]}")
                else:
                    print(f"\n❌ FAIL | Q: {q} | Status: {resp.status_code}")
                    all_pass = False
            except Exception as e:
                print(f"\n❌ FAIL | Q: {q} | Error: {e}")
                all_pass = False
    
    print("\n" + "="*100)
    if all_pass:
        print("🎉 ALL TESTS PASSED - CHATBOT ACCURACY IS FIXED!")
    else:
        print("⚠️  SOME TESTS FAILED - CHECK ANSWERS ABOVE")
    print("="*100 + "\n")

asyncio.run(test_full())
