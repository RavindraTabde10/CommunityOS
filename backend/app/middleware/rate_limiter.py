"""
Rate Limiting Middleware
Sliding-window per-IP rate limiter backed by in-memory storage.
For production deployments with multiple workers, replace the in-memory store
with a Redis backend (e.g. via redis-py or aioredis).
"""
import time
import asyncio
from collections import defaultdict, deque
from typing import Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

# Paths excluded from rate limiting
_EXEMPT_PATHS = {"/", "/health", "/api/docs", "/api/redoc", "/openapi.json"}


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window rate limiter: allows `requests_per_minute` requests per IP
    in any rolling 60-second window.
    """

    def __init__(self, app, requests_per_minute: int | None = None) -> None:
        super().__init__(app)
        self._limit = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self._window = 60  # seconds
        self._store: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _client_ip(request: Request) -> str:
        for header in ("X-Forwarded-For", "X-Real-IP"):
            value = request.headers.get(header)
            if value:
                return value.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    # ------------------------------------------------------------------
    # Middleware entry point
    # ------------------------------------------------------------------

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        ip = self._client_ip(request)
        now = time.monotonic()
        window_start = now - self._window

        async with self._lock:
            timestamps = self._store[ip]

            # Evict timestamps outside the current window
            while timestamps and timestamps[0] < window_start:
                timestamps.popleft()

            if len(timestamps) >= self._limit:
                oldest = timestamps[0]
                retry_after = int(self._window - (now - oldest)) + 1
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please slow down."},
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(self._limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                    },
                )

            timestamps.append(now)
            remaining = self._limit - len(timestamps)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self._limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
