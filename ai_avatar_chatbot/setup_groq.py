#!/usr/bin/env python
"""
Setup script to configure Groq API key for better chatbot responses
"""
import os
import sys
from pathlib import Path

def setup_groq_api():
    """Setup Groq API key for enhanced chatbot responses"""

    print("🤖 AI Avatar Chatbot - Groq API Setup")
    print("=" * 50)
    print()
    print("To get better answers from your chatbot, you need a Groq API key.")
    print()
    print("Steps to get your Groq API key:")
    print("1. Go to: https://console.groq.com/")
    print("2. Sign up for a free account")
    print("3. Create an API key")
    print("4. Copy the API key")
    print()

    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"

    if not env_file.exists():
        print("❌ .env file not found!")
        return False

    # Read current .env content
    with open(env_file, 'r') as f:
        content = f.read()

    # Check if GROQ_API_KEY is already set
    if "GROQ_API_KEY=your_groq_api_key_here" in content or "GROQ_API_KEY=" in content:
        api_key = input("Enter your Groq API key: ").strip()

        if not api_key:
            print("❌ No API key provided. Setup cancelled.")
            return False

        # Update the .env file
        new_content = content.replace("GROQ_API_KEY=your_groq_api_key_here", f"GROQ_API_KEY={api_key}")
        new_content = new_content.replace("GROQ_API_KEY=", f"GROQ_API_KEY={api_key}")

        with open(env_file, 'w') as f:
            f.write(new_content)

        print("✅ Groq API key configured successfully!")
        print()
        print("Next steps:")
        print("1. Restart your backend server: python run.py")
        print("2. Your chatbot will now give much better answers!")
        print("3. The model has been upgraded to llama-3.1-70b-versatile for enhanced responses")

        return True
    else:
        print("✅ Groq API key appears to be already configured!")
        return True

if __name__ == "__main__":
    success = setup_groq_api()
    if success:
        print("\n🎉 Setup complete! Your chatbot is now ready for better conversations.")
    else:
        print("\n❌ Setup failed. Please try again.")
        sys.exit(1)