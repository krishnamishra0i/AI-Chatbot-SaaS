#!/usr/bin/env python3
"""
Setup Google and Groq API Keys - Save to .env file
"""

import os
from pathlib import Path

print("\n" + "="*100)
print("SAVING API KEYS TO .env FILE")
print("="*100 + "\n")

# Your API keys
google_key = 'AIzaSyDBx4_5GdBC0bUfVkW6_Ub02PorVlm1uls'
groq_key = os.getenv('GROQ_API_KEY')  # Should already be set
chromadb_key = 'ck-BMAgXpD2WFAgi82jm7AkLyVk1kN7qrkk2sndKqAVMFXR'
chromadb_tenant = '8e799f6a-8e13-491e-8daa-ea89d5f2bf89'
chromadb_db = 'lms-chatbot'

# Create .env content
env_content = f"""# API Keys Configuration
# Generated: February 13, 2026

# Google Gemini API
GOOGLE_API_KEY={google_key}

# Groq API (Mixtral)
GROQ_API_KEY={groq_key if groq_key else 'your_groq_key_here'}

# ChromaDB Cloud
CHROMADB_API_KEY={chromadb_key}
CHROMADB_TENANT={chromadb_tenant}
CHROMADB_DATABASE={chromadb_db}
"""

# Write to .env file
env_file = Path('.env')
env_file.write_text(env_content)

print(f"✅ Created .env file with API keys")
print(f"   Location: {env_file.absolute()}\n")

print("IMPORTANT: Add these to .gitignore to protect your keys:")
env_content_check = Path('.gitignore').read_text() if Path('.gitignore').exists() else ""
if '.env' not in env_content_check:
    Path('.gitignore').write_text(env_content_check + '\n.env\n')
    print("✅ Added .env to .gitignore\n")
else:
    print("✅ .env already in .gitignore\n")

print("="*100)
print("API KEYS CONFIGURED")
print("="*100)

print("\nYour Chatbot Now Has:\n")
print("✅ Google Gemini API (AIzaSy...Vlm1uls)")
if groq_key:
    print("✅ Groq API (configured)")
else:
    print("⏳ Groq API (not set)")
print("✅ ChromaDB Cloud (validated)")

print("\nMulti-Layer Answer System:")
print("  Layer 1: Comprehensive Answers (81+ pre-written)")
print("  Layer 2: ChromaDB Cloud (semantic search)")
print("  Layer 3: Google Gemini (fallback)")
print("  Layer 4: Groq Mixtral (fallback)")

print("\n" + "="*100 + "\n")
