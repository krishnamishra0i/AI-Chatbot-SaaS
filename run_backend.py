#!/usr/bin/env python3
"""
Script to run the AI Avatar Chatbot backend
"""
import sys
import os

# Add user site-packages to path
user_site = os.path.expanduser(r'~\AppData\Roaming\Python\Python314\site-packages')
if user_site not in sys.path:
    sys.path.insert(0, user_site)

# Add src directory to path for backend imports
src_path = os.path.join(os.getcwd(), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print("Starting AI Avatar Chatbot Backend...")
print(f"Python path includes: {user_site}")
print(f"Source path includes: {src_path}")

try:
    from backend.main_enhanced import app
    import uvicorn

    print("✓ Backend loaded successfully!")
    print("Starting server on http://localhost:8000")

    uvicorn.run(app, host="0.0.0.0", port=8000)

except ImportError as e:
    print(f"✗ Failed to import backend: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error starting server: {e}")
    sys.exit(1)