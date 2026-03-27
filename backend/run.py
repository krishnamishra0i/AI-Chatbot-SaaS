"""
Athena AI — FastAPI Server Entrypoint
Run with: python run.py
"""

import os
import sys
import uvicorn

from api.core.config import get_settings

# Ensure the working directory is the backend folder
# so that `api.main:app` is importable regardless of where python is invoked from.
_backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_backend_dir)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

settings = get_settings()


def _parse_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

if __name__ == "__main__":
    # Keep reload disabled by default for stable local startup.
    # Enable only when explicitly requested: UVICORN_RELOAD=true
    reload_enabled = _parse_bool_env("UVICORN_RELOAD", default=False)

    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=reload_enabled,
        reload_dirs=[_backend_dir] if reload_enabled else None,
        log_level="debug" if settings.DEBUG else "info",
    )
