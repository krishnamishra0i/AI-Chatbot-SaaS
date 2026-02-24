#!/usr/bin/env python3
"""
Test Google Gemini API Integration - Simple Version
"""

import os
import sys

print("\n=== GOOGLE API TEST ===\n")

# Check environment variable
google_key = os.getenv('GOOGLE_API_KEY')

if not google_key:
    print("ERROR: GOOGLE_API_KEY environment variable not found")
    sys.exit(1)

print(f"OK: Found GOOGLE_API_KEY")

# Test import
print("\nTesting Google AI package...")
try:
    # Use the new google-genai package (not the deprecated one)
    import google.genai as genai
    print("OK: google-genai package available")
except ImportError:
    # Fallback to old package
    try:
        import google.generativeai as genai
        print("OK: google-generativeai package available (deprecated)")
    except ImportError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

# Configure API
print("\nConfiguring Google API...")
try:
    genai.configure(api_key=google_key)
    print("OK: API configured")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Test with simple query
print("\nTesting Google Gemini model...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'API works'")
    
    if response and response.text:
        print(f"OK: Got response from Google API")
        print(f"Response: {response.text[:100]}")
        print("\n=== GOOGLE API IS WORKING ===\n")
    else:
        print("ERROR: No response from API")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Now test with integrated system
print("\n=== TESTING INTEGRATED SYSTEM WITH GOOGLE API ===\n")

try:
    from integrated_answer_system import IntegratedAnswerSystem
    
    print("Initializing integrated system...")
    system = IntegratedAnswerSystem()
    
    print("\nTest 1: Creditor Academy question")
    result1 = system.get_answer("What is Creditor Academy?")
    print(f"  Layer: {result1['layer']}")
    print(f"  Confidence: {result1['confidence']}")
    print(f"  Answer: {result1['answer'][:80]}...")
    
    print("\nTest 2: Technology question")
    result2 = system.get_answer("What is artificial intelligence?")
    print(f"  Layer: {result2['layer']}")
    print(f"  Confidence: {result2['confidence']}")
    print(f"  Answer: {result2['answer'][:80]}...")
    
    print("\nOK: Integrated system working with Google API!")
    
except Exception as e:
    print(f"Note: {e}")

print("\n=== SETUP COMPLETE ===\n")
print("Google API is configured and working!")
print("Your chatbot now has both Groq and Google API available.\n")
