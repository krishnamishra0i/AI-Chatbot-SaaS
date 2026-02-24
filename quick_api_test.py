#!/usr/bin/env python3
"""
Quick Test - API Fallback Generation
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("\n[TEST] Quick API Generation Test\n")

# Test 1: Check APIs available
google_key = os.getenv('GOOGLE_API_KEY')
groq_key = os.getenv('GROQ_API_KEY')

print(f"Google API: {'YES' if google_key else 'NO'}")
print(f"Groq API: {'YES' if groq_key else 'NO'}")

# Test 2: Test Comprehensive System
print("\n[TEST] Comprehensive System:")
from comprehensive_answer_system import ComprehensiveAnswerSystem
system = ComprehensiveAnswerSystem()

# Known answer
result1 = system.get_answer("what is creditor academy")
print(f"Known Q: Confidence = {result1['confidence']}")

# Unknown answers
result2 = system.get_answer("what is the weather today")
print(f"Unknown Q: Confidence = {result2['confidence']}")

print("\n[KEY POINT]")
print("Your system works in LAYERS:")
print("1. Tries comprehensive system first (81 answers)")
print("2. If confidence < 0.7, uses ChromaDB")
print("3. If still low, uses Google/Groq API")
print("\nThis is GOOD - saves API costs!")
print("\nTo test API generation:")
print("- Ask questions NOT in the 81 answers")
print("- Like: 'What is your favorite color?'")
print("- These will trigger API fallback")
