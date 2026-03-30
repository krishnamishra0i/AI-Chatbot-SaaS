"""
Athena AI — FastAPI Server Entrypoint
Run with: python run.py
"""

import os
import sys
import socket
import urllib.request
import urllib.error
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


def _is_port_available(port: int) -> bool:
    """Return True when localhost:port is not currently listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def _is_athena_running(port: int) -> bool:
    """Best-effort check whether Athena backend is already serving on the given port."""
    health_url = f"http://127.0.0.1:{port}/api/health"
    try:
        with urllib.request.urlopen(health_url, timeout=1.0) as response:
            body = response.read().decode("utf-8", errors="ignore")
            return response.status == 200 and "healthy" in body
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


def _resolve_port(primary_port: int) -> int | None:
    """
    Resolve which port should be used.
    Returns:
      - int: port to start the server on
      - None: Athena already running on primary port
    """
    if _is_port_available(primary_port):
        return primary_port

    if _is_athena_running(primary_port):
        print(f"[INFO] Athena backend is already running on port {primary_port}.")
        print("[INFO] Reuse the existing server process; startup skipped.")
        return None

    alt_port_raw = os.getenv("ALT_PORT", "").strip()
    if alt_port_raw:
        try:
            alt_port = int(alt_port_raw)
        except ValueError:
            raise RuntimeError(f"Invalid ALT_PORT value: {alt_port_raw!r}") from None

        if alt_port != primary_port and _is_port_available(alt_port):
            print(f"[WARN] Port {primary_port} is in use by another process.")
            print(f"[INFO] Falling back to ALT_PORT={alt_port}.")
            return alt_port

    raise RuntimeError(
        f"Port {primary_port} is already in use and no valid free ALT_PORT is available. "
        "Stop the existing process or set ALT_PORT in backend/.env."
    )

if __name__ == "__main__":
    # Keep reload disabled by default for stable local startup.
    # Enable only when explicitly requested: UVICORN_RELOAD=true
    reload_enabled = _parse_bool_env("UVICORN_RELOAD", default=False)

    try:
        selected_port = _resolve_port(settings.PORT)
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    if selected_port is None:
        sys.exit(0)

    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=selected_port,
        reload=reload_enabled,
        reload_dirs=[_backend_dir] if reload_enabled else None,
        log_level="debug" if settings.DEBUG else "info",
    )
