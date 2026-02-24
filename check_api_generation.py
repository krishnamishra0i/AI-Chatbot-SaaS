#!/usr/bin/env python3
"""
Test LLM/API Answer Generation - Debug Why APIs Aren't Being Used
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "="*100)
print("TESTING LLM/API ANSWER GENERATION")
print("="*100 + "\n")

# Check API keys
print("[1] Checking API Keys Available:")
google_key = os.getenv('GOOGLE_API_KEY')
groq_key = os.getenv('GROQ_API_KEY')

if google_key:
    print(f"    [OK] Google API Key: {google_key[:20]}...")
else:
    print("    [MISSING] Google API Key")

if groq_key:
    print(f"    [OK] Groq API Key: {groq_key[:20]}...")
else:
    print("    [MISSING] Groq API Key")

# Test Comprehensive System
print("\n[2] Testing Comprehensive Answer System:")
try:
    from comprehensive_answer_system import ComprehensiveAnswerSystem
    system = ComprehensiveAnswerSystem()
    
    # Test with a question NOT in the database
    unknown_question = "What is the meaning of life according to philosophers?"
    result = system.get_answer(unknown_question)
    
    print(f"    Question: {unknown_question}")
    print(f"    Confidence: {result['confidence']}")
    print(f"    Method: {result.get('method', 'N/A')}")
    
    if result['confidence'] < 0.7:
        print("    [NOTE] Low confidence - should use API fallback")
    
except Exception as e:
    print(f"    [ERROR] {e}")

# Test Integrated System
print("\n[3] Testing Integrated Answer System (with API fallback):")
try:
    from integrated_answer_system import IntegratedAnswerSystem
    system = IntegratedAnswerSystem()
    
    # Test with various questions
    test_questions = [
        "What is Creditor Academy?",  # Should be Layer 1 (Comprehensive)
        "What is the weather?",  # Should fall back to API
        "Tell me about quantum computing",  # Might be API
    ]
    
    for q in test_questions:
        result = system.get_answer(q)
        print(f"\n    Q: {q}")
        print(f"    Layer: {result['layer']}")
        print(f"    Source: {result['source']}")
        print(f"    Confidence: {result['confidence']}")
        print(f"    Answer: {result['answer'][:70]}...")
        
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Test Groq API Directly
print("\n[4] Testing Groq API Directly:")
try:
    from groq import Groq
    
    if groq_key:
        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "user", "content": "What is quantum computing in 2 sentences?"}
            ],
            max_tokens=200
        )
        
        print(f"    [OK] Groq API Working")
        print(f"    Response: {response.choices[0].message.content[:100]}...")
    else:
        print("    [SKIPPED] No Groq API key")
        
except Exception as e:
    print(f"    [ERROR] {e}")

# Test Google API Directly
print("\n[5] Testing Google API Directly:")
try:
    if google_key:
        import google.genai as genai
        client = genai.Client(api_key=google_key)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="What is artificial intelligence in 2 sentences?"
        )
        
        print(f"    [OK] Google API Working")
        print(f"    Response: {response.text[:100]}...")
    else:
        print("    [SKIPPED] No Google API key")
        
except Exception as e:
    if "quota" in str(e).lower() or "429" in str(e):
        print(f"    [OK] Google API Key Valid (quota/billing issue - expected)")
        print(f"    Note: Add billing to Google Cloud Console to use")
    else:
        print(f"    [ERROR] {e}")

print("\n" + "="*100)
print("DIAGNOSIS SUMMARY")
print("="*100)

print("\nWhy Answers Might Not Be Generated Through LLM/API:\n")

print("[1] Comprehensive System Returns High Confidence:")
print("    - If answer found in database (81 answers), it returns immediately")
print("    - This is GOOD - it's faster and more accurate")
print("    - APIs are only used if confidence < 0.7")

print("\n[2] APIs Not Configured:")
print(f"    - Google API: {'YES' if google_key else 'NO'}")
print(f"    - Groq API: {'YES' if groq_key else 'NO'}")

print("\n[3] To Force API Usage:")
print("    - Ask questions NOT in the 81-answer database")
print("    - APIs are fallback for unknown questions")
print("    - This is intentional - reduce API costs & improve speed")

print("\n[4] Current Answer Generator Order:")
print("    1. Comprehensive System (81 answers) - instant")
print("    2. ChromaDB Cloud (semantic search) - fallback")
print("    3. Google/Groq API (LLM) - fallback #2")

print("\n" + "="*100 + "\n")
