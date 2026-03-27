#!/usr/bin/env python3
"""Start Athena FastAPI backend with stable local settings."""
import subprocess
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("[INFO] Starting Athena FastAPI Backend on port 5000")
print("[INFO] Auto-reload disabled for stable local runtime")
print(f"[INFO] Running: {sys.executable} run.py\n")

env = {**os.environ, "UVICORN_RELOAD": "false"}
result = subprocess.run([sys.executable, "run.py"], env=env)
sys.exit(result.returncode)
