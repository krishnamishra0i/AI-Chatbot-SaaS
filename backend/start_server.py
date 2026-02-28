#!/usr/bin/env python3
"""Start Athena Flask backend with TTS/STT support (no auto-reload)."""
import subprocess
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("[INFO] Starting Athena Flask Backend (TTS/STT enabled)")
print("[INFO] Disabling auto-reload to prevent import issues...")
print("[INFO] Running: python -m flask run --no-reload\n")

# Run Flask with no-reload to prevent watchdog import issues
result = subprocess.run(
    [sys.executable, "-m", "flask", "run", "--no-reload"],
    env={**os.environ, "FLASK_APP": "app.py"}
)

sys.exit(result.returncode)
