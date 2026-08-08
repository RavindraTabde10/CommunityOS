"""
Request / Response Logging Middleware
Logs every request with method, path, client IP, status code, and latency.
Also attaches X-Request-ID and X-Process-Time headers for traceability.
"""
import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("api.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs all incoming requests and their responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )

        logger.info(
            "[%s] --> %s %s  ip=%s",
            request_id,
            request.method,
            request.url.path,
            client_ip,
        )

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "[%s] <-- %s %s  status=%d  %.2fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"

        return response
