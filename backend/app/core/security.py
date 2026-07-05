"""
app/auth/security.py
─────────────────────────────────────────────────────────────────────────────
Low-level security utilities.

Kept separate from jwt.py (which handles Supabase tokens specifically) so
this module can house future security primitives without polluting JWT logic:
  - API key hashing (for programmatic access tokens)
  - Rate-limit key generation
  - Constant-time string comparison
  - HMAC signing for webhooks

Nothing in this file makes network calls.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets


def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key pair: (raw_key, hashed_key).

    The raw_key is shown to the user exactly once.
    The hashed_key is stored in the database.

    Returns:
        (raw_key, hashed_key)
    """
    raw_key = secrets.token_urlsafe(40)
    hashed_key = _hash_api_key(raw_key)
    return raw_key, hashed_key


def _hash_api_key(raw_key: str) -> str:
    """SHA-256 hash an API key for storage."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """
    Constant-time comparison of a submitted API key against its stored hash.

    Using hmac.compare_digest prevents timing attacks.
    """
    submitted_hash = _hash_api_key(raw_key)
    return hmac.compare_digest(submitted_hash, stored_hash)


def generate_webhook_signature(payload: bytes, secret: str) -> str:
    """
    Sign a webhook payload with HMAC-SHA256.

    Used to sign outgoing webhooks so receivers can verify authenticity.
    """
    return hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
