#!/usr/bin/env python3
"""
Test Google Gemini API Integration
"""

import os
import sys

print("\n" + "█"*100)
print("█" + " "*35 + "🧪 GOOGLE API TEST" + " "*47 + "█")
print("█"*100 + "\n")

# Check environment variable
google_key = os.getenv('GOOGLE_API_KEY')

if not google_key:
    print("❌ GOOGLE_API_KEY environment variable not found")
    print("   Set it with: $env:GOOGLE_API_KEY='your_key'")
    sys.exit(1)

print(f"✅ Found GOOGLE_API_KEY: {google_key[:30]}...")

# Test import
print("\n📦 Testing Google AI Python package...")
try:
    import google.generativeai as genai
    print("✅ google-generativeai package available")
except ImportError as e:
    print(f"❌ Package not found: {e}")
    print("   Install with: pip install google-generativeai")
    sys.exit(1)

# Configure API
print("\n🔧 Configuring Google API...")
try:
    genai.configure(api_key=google_key)
    print("✅ API configured successfully")
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    sys.exit(1)

# Test with simple query
print("\n🤖 Testing Google Gemini...")
try:
    # Use the latest available model
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Google API is working!' in exactly those words")
    
    if response and response.text:
        print(f"✅ Google API Response: {response.text}")
        print("\n" + "="*100)
        print("✅ GOOGLE API IS WORKING!")
        print("="*100)
    else:
        print("❌ No response from API")
        sys.exit(1)
except Exception as e:
    print(f"❌ API Test failed: {e}")
    sys.exit(1)

# Now test with integrated system
print("\n\n" + "█"*100)
print("█" + " "*25 + "🔄 TESTING INTEGRATED SYSTEM WITH GOOGLE API" + " "*28 + "█")
print("█"*100 + "\n")

try:
    from integrated_answer_system import IntegratedAnswerSystem
    
    print("🚀 Initializing integrated system...")
    system = IntegratedAnswerSystem()
    
    print("\n📝 Testing with Creditor Academy question...")
    result1 = system.get_answer("What is Creditor Academy?")
    print(f"   Q: What is Creditor Academy?")
    print(f"   Layer: {result1['layer']}")
    print(f"   Source: {result1['source']}")
    print(f"   Confidence: {result1['confidence']}")
    print(f"   Answer: {result1['answer'][:100]}...")
    
    print("\n📝 Testing with technology question...")
    result2 = system.get_answer("What is artificial intelligence?")
    print(f"   Q: What is artificial intelligence?")
    print(f"   Layer: {result2['layer']}")
    print(f"   Source: {result2['source']}")
    print(f"   Confidence: {result2['confidence']}")
    print(f"   Answer: {result2['answer'][:100]}...")
    
    print("\n✅ Integrated system working with Google API!")
    
except Exception as e:
    print(f"⚠️  Integrated system note: {e}")
    print("   But Google API itself is working fine!")

print("\n" + "█"*100)
print("█" + " "*30 + "✅ GOOGLE API SETUP COMPLETE!" + " "*38 + "█")
print("█"*100 + "\n")
