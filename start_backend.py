#!/usr/bin/env python3
"""
Simple Backend Starter - No Unicode Issues
"""

import sys
import os
from pathlib import Path

print("[INFO] Starting Backend...")

# Add paths
user_site = os.path.expanduser(r'~\AppData\Roaming\Python\Python314\site-packages')
if user_site not in sys.path:
    sys.path.insert(0, user_site)

src_path = os.path.join(os.getcwd(), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Environment loaded from .env")
except:
    print("[WARNING] .env not found or dotenv not installed")

# Start server
try:
    print("[INFO] Importing FastAPI app...")
    from backend.main_enhanced import app
    import uvicorn
    
    print("[OK] Backend loaded successfully")
    print("[INFO] Starting server on http://localhost:8000")
    print("[INFO] Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Server error: {e}")
    sys.exit(1)
