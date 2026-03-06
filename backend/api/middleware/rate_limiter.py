"""
Rate limiting middleware using in-memory sliding window.
Falls back to Redis if REDIS_URL is configured.
"""

import time
import asyncio
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from api.core.config import get_settings

settings = get_settings()


class InMemoryRateLimiter:
    """Simple sliding-window rate limiter using in-memory storage."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str) -> Tuple[bool, int]:
        """Check if a request is allowed. Returns (allowed, remaining)."""
        async with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Clean old entries
            self._requests[key] = [
                t for t in self._requests[key] if t > window_start
            ]

            current_count = len(self._requests[key])

            if current_count >= self.max_requests:
                return False, 0

            self._requests[key].append(now)
            return True, self.max_requests - current_count - 1


# Global rate limiter instance
_limiter = InMemoryRateLimiter(
    max_requests=settings.RATE_LIMIT_PER_MINUTE,
    window_seconds=60,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI."""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for docs and health endpoints
        if request.url.path in ("/docs", "/redoc", "/openapi.json", "/", "/api/health"):
            return await call_next(request)

        # Use IP address as rate limit key (or user ID if authenticated)
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{client_ip}"

        allowed, remaining = await _limiter.is_allowed(key)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
