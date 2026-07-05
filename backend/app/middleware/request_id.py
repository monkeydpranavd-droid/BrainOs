"""
app/middleware/request_id.py
─────────────────────────────────────────────────────────────────────────────
Request ID middleware.

Assigns a unique UUID to every incoming request and attaches it to:
  - The request state (request.state.request_id)
  - The response header (X-Request-ID)

Why:
  - Distributed tracing: correlate logs across services
  - Support tickets: "give us your X-Request-ID" is more useful than a timestamp
  - If the client sends X-Request-ID, we echo it back (idempotent retry pattern)
"""

from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Honour client-supplied ID (e.g., for retry deduplication)
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
