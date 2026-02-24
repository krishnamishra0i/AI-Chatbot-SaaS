#!/usr/bin/env python3
"""
Interactive chatbot tester - Ask questions and get RAG + LLM responses
"""
import sys
import os
import json

# Add user site-packages to path
user_site = os.path.expanduser(r'~\AppData\Roaming\Python\Python314\site-packages')
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import requests

def ask_question(question):
    """Ask a question to the chatbot using RAG + LLM"""
    try:
        url = "http://localhost:8000/api/chat"

        payload = {
            "message": question,
            "language": "en",
            "use_knowledge_base": True
        }

        print(f"\n🤖 You: {question}")
        print("🔍 Searching knowledge base (RAG) + generating response (LLM)...")

        response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print("✅ Response received!")
            print(f"💬 AI Avatar: {result.get('response', 'No response')}")
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
    print("🎯 AI Avatar Chatbot - Interactive RAG + LLM Demo")
    print("=" * 60)
    print("Backend: http://localhost:8000 (Running)")
    print("Frontend: http://localhost:3000 (Running)")
    print("=" * 60)
    print("Ask any question and get answers using both RAG and LLM!")
    print("Type 'quit' or 'exit' to stop.")
    print("-" * 60)

    while True:
        try:
            question = input("\n❓ Your question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Thanks for testing the AI Avatar Chatbot.")
                break

            if not question:
                print("⚠️ Please enter a question.")
                continue

            success = ask_question(question)
            if not success:
                print("💡 Tip: Make sure both backend (port 8000) and frontend (port 3000) are running.")

        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for testing the AI Avatar Chatbot.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()