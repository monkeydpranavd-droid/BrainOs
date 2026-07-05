"""
app/middleware/logging.py
─────────────────────────────────────────────────────────────────────────────
Structured access log middleware.

Logs every request with:
  - Method, path, status code
  - Duration in milliseconds
  - Request ID (requires RequestIDMiddleware to run first)

In production, replace the Python logger with structlog or send to
a log aggregator (Datadog, Loki, CloudWatch) by swapping the handler.
"""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("brainos.access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        request_id = getattr(request.state, "request_id", "-")

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s %d %.1fms req_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )
        return response
