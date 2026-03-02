"""
Athena AI — FastAPI Server Entrypoint
Run with: python run.py
"""

import os
import sys

# Ensure the working directory is the backend folder
# so that `api.main:app` is importable regardless of where python is invoked from.
_backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_backend_dir)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

import uvicorn
from api.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[_backend_dir] if settings.DEBUG else None,
        log_level="debug" if settings.DEBUG else "info",
    )
