#!/usr/bin/env python3
"""
Simple Test - Show API vs Comprehensive Answer Generation
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("ANSWER GENERATION TEST - showing when APIs are used")
print("="*80 + "\n")

# Check which APIs are available
google_key = os.getenv('GOOGLE_API_KEY')
groq_key = os.getenv('GROQ_API_KEY')

print(f"Available APIs:")
print(f"  Google Gemini: {'YES' if google_key else 'NO'}")
print(f"  Groq Mixtral: {'YES' if groq_key else 'NO'}\n")

# Load comprehensive system
from comprehensive_answer_system import ComprehensiveAnswerSystem
system = ComprehensiveAnswerSystem()

print("="*80)
print("TEST 1: QUESTION IN 81-ANSWER DATABASE")
print("="*80 + "\n")

result = system.get_answer("what is creditor academy")
print(f"Q: What is Creditor Academy?")
print(f"Confidence: {result['confidence']}")
print(f"Source: Comprehensive System (instant, no API)")
print(f"Answer: {result['answer'][:100]}...\n")

print("="*80)
print("TEST 2: UNKNOWN QUESTION - Should trigger API fallback")
print("="*80 + "\n")

result = system.get_answer("write me a funny story about a robot")
print(f"Q: Write me a funny story about a robot")
print(f"Confidence: {result['confidence']}")
print(f"Source: {result.get('source', 'Fallback')}")

if result['confidence'] < 0.7:
    print("\n[API WOULD BE TRIGGERED HERE]")
    print("This low-confidence question would:")
    print("  1. Try ChromaDB Cloud (semantic search)")
    print("  2. Use Groq API if configured")
    print("  3. Fall back to Google API")
    print("  4. Return default message if all fail")
else:
    print(f"Answer: {result['answer'][:100]}...\n")

print("\n" + "="*80)
print("WHY YOU'RE NOT SEEING API GENERATION:")
print("="*80)
print("""
REASON 1: Comprehensive System Works Well
  - 81 pre-written answers cover most common questions
  - These return 0.99 confidence instantly
  - No need to call APIs (cheaper & faster!)

REASON 2: Questions Must Be Unknown
  - "What is Creditor Academy?" -> Uses Comprehensive (0.99)
  - "What's your favorite pizza?" -> Falls back to API
  - "Write a poem" -> Falls back to API

REASON 3: System Design is Intentional
  - APIs are FALLBACK, not primary
  - This saves money and improves speed
  - You get instant answers for 81 common questions
  - APIs handle edge cases

SOLUTION: Test with Unknown Questions
  - Ask creative questions
  - Ask about random topics
  - Ask for content generation (poems, stories)
  These WILL trigger your Groq/Google APIs!
""")

print("="*80)
print("EXAMPLE QUESTIONS THAT WILL USE APIs:")
print("="*80)
print("""
- "Tell me a joke"
- "Write a poem about love"
- "Create a story about a dragon"
- "What is the meaning of life?"
- "Tell me about space exploration"
- "Write Python code for..."
- "Summarize the history of AI"
""")

print("\n" + "="*80 + "\n")
