#!/usr/bin/env python3
"""
Test script to demonstrate RAG + LLM functionality
"""
import sys
import os
import json

# Add user site-packages to path
user_site = os.path.expanduser(r'~\AppData\Roaming\Python\Python314\site-packages')
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import requests

# Add user site-packages to path
user_site = os.path.expanduser(r'~\AppData\Roaming\Python\Python314\site-packages')
if user_site not in sys.path:
    sys.path.insert(0, user_site)

def test_chatbot(question):
    """Test the chatbot with a question using RAG + LLM"""
    try:
        # API endpoint for chat
        url = "http://localhost:8000/api/chat"

        # Prepare the request payload
        payload = {
            "message": question,
            "use_rag": True,
            "use_llm": True
        }

        print(f"🤖 Asking: {question}")
        print("🔍 Searching knowledge base (RAG) + generating response (LLM)...")

        # Make the request
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✅ Response received!")
            print(f"💬 Answer: {result.get('response', 'No response')}")
            if 'sources' in result and result['sources']:
                print(f"📚 Sources used: {len(result['sources'])} documents")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🚀 AI Avatar Chatbot - RAG + LLM Demo")
    print("=" * 50)
    print("Backend: http://localhost:8000 (Running)")
    print("Frontend: http://localhost:3000 (Running)")
    print("=" * 50)

    # Test questions that should use both RAG and LLM
    test_questions = [
        "How can I improve my credit score?",
        "What are the best ways to pay off debt?",
        "How do I cancel my membership?",
        "What is the difference between credit cards and debit cards?",
        "How can I dispute a charge on my account?"
    ]

    print("Testing RAG + LLM functionality...\n")

    for i, question in enumerate(test_questions, 1):
        print(f"Test {i}/{len(test_questions)}:")
        success = test_chatbot(question)
        print("-" * 50)

        if not success:
            print("⚠️  Some tests failed. Make sure the backend is running and configured properly.")
            break

    print("🎯 Demo complete! You can now ask your own questions through:")
    print("   🌐 Web interface: http://localhost:3000")
    print("   🤖 API endpoint: http://localhost:8000/chat")

if __name__ == "__main__":
    main()