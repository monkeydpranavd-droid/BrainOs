"""
app/auth/supabase.py
─────────────────────────────────────────────────────────────────────────────
Supabase Admin client — server-side only.

Used for admin operations that cannot be done with the anon key:
  - Fetching user metadata from auth.users
  - Inviting users by email (future)
  - Deleting users (future)

SECURITY: This module uses the service_role key. It must NEVER be imported
from any code path that is reachable by the frontend or by unauthenticated
requests. Only the auth service layer and admin-gated routes may use it.
"""

from __future__ import annotations

import logging

from supabase import Client, create_client

from app.core.config import settings

logger = logging.getLogger(__name__)

# Module-level singleton — avoids creating a new HTTP client per request.
# Supabase client is thread-safe.
_admin_client: Client | None = None


def get_supabase_admin() -> Client:
    """
    Return the Supabase admin client (service_role key).

    Lazy-initialised on first call so startup is fast and the client is
    not created during tests that mock config.
    """
    global _admin_client
    if _admin_client is None:
        _admin_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
        logger.debug("Supabase admin client initialised.")
    return _admin_client


def get_supabase_user_metadata(supabase_user_id: str) -> dict | None:
    """
    Fetch Supabase auth user metadata by UUID.

    Returns the user metadata dict, or None if the user does not exist.
    Raises SupabaseError on API failure.
    """
    from app.core.exceptions import SupabaseError

    try:
        client = get_supabase_admin()
        response = client.auth.admin.get_user_by_id(supabase_user_id)
        if response and response.user:
            user = response.user
            return {
                "id": str(user.id),
                "email": user.email,
                "full_name": (user.user_metadata or {}).get("full_name"),
                "avatar_url": (user.user_metadata or {}).get("avatar_url"),
            }
        return None
    except Exception as exc:
        logger.error("Supabase admin API error: %s", exc)
        raise SupabaseError(f"Failed to fetch user from Supabase: {exc}")
