"""
app/main.py
─────────────────────────────────────────────────────────────────────────────
BrainOS FastAPI application entrypoint.

Startup responsibilities:
  1. Build the FastAPI app with metadata
  2. Register CORS middleware (allows the Next.js frontend)
  3. Register custom middleware (request ID, access logging)
  4. Register exception handlers (typed domain → consistent JSON errors)
  5. Mount all API routers under /api/v1
  6. Expose the root health check

Versioned router prefix (/api/v1) means we can introduce /api/v2 routes
for breaking changes without touching existing clients.
"""

from __future__ import annotations

import logging
import logging.config

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.auth import router as auth_router
from app.api.routes.database import router as database_router
from app.api.routes.health import router as health_router
from app.api.routes.users import router as users_router
from app.api.routes.organizations import router as organizations_router
from app.api.routes.workspaces import router as workspaces_router
from app.api.routes.documents import router as documents_router
from app.api.routes.folders import router as folders_router
from app.api.routes.knowledge_bases import router as knowledge_bases_router
from app.api.routes.search import router as search_router

from app.core.config import settings
from app.core.exceptions import BrainOSException
from app.middleware.logging import AccessLogMiddleware
from app.middleware.request_id import RequestIDMiddleware

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.is_development else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("brainos")

# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="BrainOS API",
    version=settings.APP_VERSION,
    description=(
        "Enterprise AI Operating System — BrainOS Backend API. "
        "All protected routes require a valid Supabase JWT in the "
        "Authorization: Bearer <token> header."
    ),
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
)

# ── Middleware (order matters: first registered = outermost) ──────────────────

# CORS must be before custom middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Request ID before access log so the log can read it
app.add_middleware(RequestIDMiddleware)
app.add_middleware(AccessLogMiddleware)

# ── Exception handlers ────────────────────────────────────────────────────────

@app.exception_handler(BrainOSException)
async def brainos_exception_handler(request: Request, exc: BrainOSException) -> JSONResponse:
    """
    Convert all BrainOSException subclasses to a consistent JSON error shape.

    {
        "error": "Invalid authentication token.",
        "status_code": 401,
        "request_id": "..."
    }
    """
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id,
        },
        headers=exc.headers or {},
    )

# ── Routers ───────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(health_router, prefix=API_PREFIX)
app.include_router(database_router, prefix=API_PREFIX)
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)
app.include_router(organizations_router, prefix=API_PREFIX)
app.include_router(workspaces_router, prefix=API_PREFIX)
app.include_router(documents_router, prefix=API_PREFIX)
app.include_router(folders_router, prefix=API_PREFIX)
app.include_router(knowledge_bases_router, prefix=API_PREFIX)
app.include_router(search_router, prefix=API_PREFIX)

# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    return {
        "message": "BrainOS Backend Running 🚀",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.on_event("startup")
async def on_startup():
    logger.info(
        "BrainOS API starting. env=%s version=%s",
        settings.APP_ENV,
        settings.APP_VERSION,
    )


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("BrainOS API shutting down.")