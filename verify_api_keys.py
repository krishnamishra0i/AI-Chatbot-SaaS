#!/usr/bin/env python3
"""
API KEY VERIFICATION SCRIPT
Tests if Google API and Groq API keys are working
"""

import os
import sys
from pathlib import Path

def check_google_api():
    """Check if Google API key is configured and working"""
    print("\n" + "="*100)
    print("🔍 TESTING GOOGLE API")
    print("="*100)
    
    try:
        # Check environment variable
        google_api_key = os.getenv('GOOGLE_API_KEY')
        
        if not google_api_key:
            print("❌ GOOGLE_API_KEY environment variable not set")
            print("   To set it: set GOOGLE_API_KEY=your_key_here")
            return False
        
        print(f"✅ Found GOOGLE_API_KEY: {google_api_key[:20]}...")
        
        # Try importing Google AI module
        try:
            import google.generativeai as genai
            print("✅ Google AI Python package installed")
            
            # Configure API
            genai.configure(api_key=google_api_key)
            print("✅ Google API configured successfully")
            
            # Test with simple request
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Say 'Google API is working'")
            
            if response.text:
                print(f"✅ Google API working! Response: '{response.text}'")
                return True
            else:
                print("❌ Google API returned empty response")
                return False
                
        except ImportError as e:
            print(f"❌ Google AI package not installed: {e}")
            print("   Install with: pip install google-generativeai")
            return False
        except Exception as e:
            print(f"❌ Google API test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Google API: {e}")
        return False


def check_groq_api():
    """Check if Groq API key is configured and working"""
    print("\n" + "="*100)
    print("🔍 TESTING GROQ API")
    print("="*100)
    
    try:
        # Check environment variable
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if not groq_api_key:
            print("❌ GROQ_API_KEY environment variable not set")
            print("   To set it: set GROQ_API_KEY=your_key_here")
            return False
        
        print(f"✅ Found GROQ_API_KEY: {groq_api_key[:20]}...")
        
        # Try importing Groq module
        try:
            from groq import Groq
            print("✅ Groq Python package installed")
            
            # Initialize client
            client = Groq(api_key=groq_api_key)
            print("✅ Groq client initialized successfully")
            
            # Test with simple request
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "user", "content": "Say 'Groq API is working'"}
                ],
                max_tokens=100
            )
            
            if response.choices[0].message.content:
                print(f"✅ Groq API working! Response: '{response.choices[0].message.content}'")
                return True
            else:
                print("❌ Groq API returned empty response")
                return False
                
        except ImportError as e:
            print(f"❌ Groq package not installed: {e}")
            print("   Install with: pip install groq")
            return False
        except Exception as e:
            print(f"❌ Groq API test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Groq API: {e}")
        return False


def check_required_env_variables():
    """Check all environment variables"""
    print("\n" + "="*100)
    print("🔐 CHECKING ENVIRONMENT VARIABLES")
    print("="*100)
    
    variables_to_check = {
        'GOOGLE_API_KEY': 'Google Generative AI',
        'GROQ_API_KEY': 'Groq LLM',
        'CHROMADB_API_KEY': 'ChromaDB Cloud',
        'OPENAI_API_KEY': 'OpenAI (optional)',
        'ANTHROPIC_API_KEY': 'Claude API (optional)'
    }
    
    found_vars = {}
    missing_vars = []
    
    for var_name, description in variables_to_check.items():
        value = os.getenv(var_name)
        if value:
            found_vars[var_name] = (description, value[:20] + "...")
            print(f"✅ {var_name}: SET ({description})")
        else:
            missing_vars.append((var_name, description))
            print(f"❌ {var_name}: NOT SET ({description})")
    
    return found_vars, missing_vars


def main():
    """Main verification function"""
    
    print("\n" + "█"*100)
    print("█" + " "*98 + "█")
    print("█" + " "*30 + "🔑 API KEY VERIFICATION 🔑" + " "*41 + "█")
    print("█" + " "*98 + "█")
    print("█"*100)
    
    # Check environment variables
    found, missing = check_required_env_variables()
    
    # Test Google API
    google_working = check_google_api()
    
    # Test Groq API
    groq_working = check_groq_api()
    
    # Summary
    print("\n" + "="*100)
    print("📊 VERIFICATION SUMMARY")
    print("="*100)
    
    print("\n🔑 API Status:")
    print(f"   Google API: {'✅ WORKING' if google_working else '❌ NOT WORKING'}")
    print(f"   Groq API:   {'✅ WORKING' if groq_working else '❌ NOT WORKING'}")
    
    print("\n📝 Environment Variables:")
    print(f"   Found: {len(found)} variables")
    for var, (desc, val) in found.items():
        print(f"      ✅ {var}")
    
    if missing:
        print(f"   Missing: {len(missing)} variables")
        for var, desc in missing:
            print(f"      ❌ {var} ({desc})")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if not google_working and not groq_working:
        print("   ⚠️  Both APIs are not working. Please:")
        print("      1. Set GOOGLE_API_KEY in environment")
        print("      2. Set GROQ_API_KEY in environment")
        print("      3. Install required packages: pip install google-generativeai groq")
        print("      4. Run this script again to verify")
    elif not google_working:
        print("   ⚠️  Google API not working. Please set GOOGLE_API_KEY")
    elif not groq_working:
        print("   ⚠️  Groq API not working. Please set GROQ_API_KEY")
    else:
        print("   ✅ Both APIs are working! Your chatbot can use both services.")
        print("   ✅ For maximum accuracy, the system uses:")
        print("      1. Comprehensive Answer System (200+ hardcoded answers) - ALWAYS")
        print("      2. ChromaDB Cloud (semantic search) - ENHANCED")
        print("      3. Google API (when needed)")
        print("      4. Groq API (when needed)")
    
    print("\n" + "█"*100 + "\n")
    
    return google_working, groq_working


if __name__ == "__main__":
    google_ok, groq_ok = main()
    sys.exit(0 if (google_ok and groq_ok) else 1)
