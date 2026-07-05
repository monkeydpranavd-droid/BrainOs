import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings

# Resolve the .env file relative to THIS file, not the CWD.
ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "BrainOS"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── Supabase ──────────────────────────────────────────────────────────────
    SUPABASE_URL: str
    SUPABASE_KEY: str                   # anon/publishable key (safe for clients)
    SUPABASE_JWT_SECRET: str            # used to verify JWTs server-side
    SUPABASE_SERVICE_ROLE_KEY: str      # admin key — never send to frontend

    # ── Auth ──────────────────────────────────────────────────────────────────
    # Supabase issues JWTs with audience "authenticated"
    JWT_AUDIENCE: str = "authenticated"
    # Supabase JWT algorithm
    JWT_ALGORITHM: str = "HS256"
    # How many seconds of clock skew to tolerate during token verification
    JWT_LEEWAY_SECONDS: int = 10

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins; override in production
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"


settings = Settings()