#!/usr/bin/env python3
"""
SETUP GUIDE - Configure API Keys and ChromaDB
Run this to configure your API keys for Google, Groq, and ChromaDB
"""

import os
import sys
from pathlib import Path

def setup_api_keys():
    """Interactive setup for API keys"""
    
    print("\n" + "█"*100)
    print("█" + " "*98 + "█")
    print("█" + " "*35 + "🔑 API KEY SETUP GUIDE 🔑" + " "*38 + "█")
    print("█" + " "*98 + "█")
    print("█"*100)
    
    print("\n📋 SETUP INSTRUCTIONS:\n")
    
    # Google API
    print("1️⃣  GOOGLE API (for Gemini AI)")
    print("   ├─ Get key: https://ai.google.dev/")
    print("   ├─ Copy your API key")
    print("   └─ Set environment variable:")
    print("      • Windows: set GOOGLE_API_KEY=your_key_here")
    print("      • PowerShell: $env:GOOGLE_API_KEY='your_key_here'")
    print("      • Linux/Mac: export GOOGLE_API_KEY=your_key_here")
    
    # Groq API
    print("\n2️⃣  GROQ API (for Mixtral AI)")
    print("   ├─ Get key: https://console.groq.com")
    print("   ├─ Copy your API key")
    print("   └─ Set environment variable:")
    print("      • Windows: set GROQ_API_KEY=your_key_here")
    print("      • PowerShell: $env:GROQ_API_KEY='your_key_here'")
    print("      • Linux/Mac: export GROQ_API_KEY=your_key_here")
    
    # ChromaDB
    print("\n3️⃣  CHROMADB CLOUD (for semantic search)")
    print("   ├─ Your credentials (already valid): ✅")
    print("   ├─ API Key: ck-BMAgXpD2WFAgi82jm7AkLyVk1kN7qrkk2sndKqAVMFXR")
    print("   ├─ Tenant ID: 8e799f6a-8e13-491e-8daa-ea89d5f2bf89")
    print("   └─ Database: lms-chatbot")
    
    print("\n\n📝 OPTION 1: Set Variables in Terminal (Temporary)")
    print("   ─" * 50)
    print("   Run these commands in your terminal:")
    print("   (Values will be reset when terminal closes)")
    
    google_key = input("\n   Enter your Google API Key (or press Enter to skip): ").strip()
    if google_key:
        os.environ['GOOGLE_API_KEY'] = google_key
        print("   ✅ GOOGLE_API_KEY set")
    
    groq_key = input("   Enter your Groq API Key (or press Enter to skip): ").strip()
    if groq_key:
        os.environ['GROQ_API_KEY'] = groq_key
        print("   ✅ GROQ_API_KEY set")
    
    print("\n\n📝 OPTION 2: Set Variables Permanently")
    print("   ─" * 50)
    print("   Create a .env file in your project directory:")
    print("   (Recommended for development)\n")
    
    create_env = input("   Create .env file? (y/n): ").strip().lower()
    
    if create_env == 'y':
        env_file = Path('.env')
        env_content = ""
        
        if google_key:
            env_content += f"GOOGLE_API_KEY={google_key}\n"
        if groq_key:
            env_content += f"GROQ_API_KEY={groq_key}\n"
        
        env_content += """CHROMADB_API_KEY=ck-BMAgXpD2WFAgi82jm7AkLyVk1kN7qrkk2sndKqAVMFXR
CHROMADB_TENANT=8e799f6a-8e13-491e-8daa-ea89d5f2bf89
CHROMADB_DATABASE=lms-chatbot
"""
        
        env_file.write_text(env_content)
        print(f"   ✅ Created .env file with your credentials")
        print(f"   📁 Location: {env_file.absolute()}")
        print(f"   ⚠️  IMPORTANT: Add .env to .gitignore to keep keys private!")
        
        # Add to .gitignore
        gitignore = Path('.gitignore')
        if gitignore.exists():
            content = gitignore.read_text()
            if '.env' not in content:
                gitignore.write_text(content + '\n.env\n')
                print("   ✅ Added .env to .gitignore")
    
    print("\n\n📝 OPTION 3: Windows System Environment Variables (Permanent)")
    print("   ─" * 50)
    print("   1. Open System Properties:")
    print("      • Press Win+R, type: sysdm.cpl, press Enter")
    print("   2. Go to 'Advanced' tab → 'Environment Variables'")
    print("   3. Click 'New' under 'User variables'")
    print("   4. Add:")
    print("      • Variable name: GOOGLE_API_KEY")
    print("      • Variable value: your_google_key_here")
    print("   5. Repeat for GROQ_API_KEY")
    print("   6. Click OK and restart terminal/Python\n")
    
    print("\n" + "█"*100)
    print("█" + " THANK YOU - Your API keys are ready to use!" + " "*49 + "█")
    print("█"*100 + "\n")


def create_env_from_input():
    """Create .env file from user input"""
    
    print("\n\n🚀 QUICK SETUP - Create .env file now?")
    print("─" * 100)
    
    response = input("\nEnter Google API Key (or skip): ").strip()
    google_key = response if response else ""
    
    response = input("Enter Groq API Key (or skip): ").strip()
    groq_key = response if response else ""
    
    if google_key or groq_key:
        env_file = Path('.env')
        content = ""
        
        if google_key:
            content += f"GOOGLE_API_KEY={google_key}\n"
        if groq_key:
            content += f"GROQ_API_KEY={groq_key}\n"
        
        content += """CHROMADB_API_KEY=ck-BMAgXpD2WFAgi82jm7AkLyVk1kN7qrkk2sndKqAVMFXR
CHROMADB_TENANT=8e799f6a-8e13-491e-8daa-ea89d5f2bf89
CHROMADB_DATABASE=lms-chatbot
"""
        
        env_file.write_text(content)
        print("\n✅ .env file created successfully!")
        print(f"📁 Location: {env_file.absolute()}\n")
        
        return True
    
    return False


if __name__ == "__main__":
    setup_api_keys()
    
    # Offer quick setup
    response = input("\nDo you want to quickly create .env file now? (y/n): ").strip().lower()
    if response == 'y':
        create_env_from_input()
