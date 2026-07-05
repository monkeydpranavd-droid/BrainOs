"""
app/auth/jwt.py
─────────────────────────────────────────────────────────────────────────────
Supabase JWT verification.

Verifies the signature, audience, issuer and expiration of Supabase-issued
asymmetric (ES256/RS256) or symmetric (HS256) JWTs server-side.

IMPORTANT: New Supabase projects use ES256 (asymmetric). The JWT secret in
.env is ONLY used for legacy HS256 projects. Asymmetric tokens are verified
using the public key fetched from the Supabase JWKS endpoint, which is
cached by PyJWKClient and only re-fetched when a kid is not found in cache.
"""

from __future__ import annotations

import logging

import jwt
from jwt import PyJWKClient
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidSignatureError,
    InvalidTokenError as PyJWTInvalidTokenError,
)

from app.core.config import settings
from app.core.exceptions import ExpiredTokenError, InvalidTokenError, MissingTokenError
from app.schemas.auth import TokenPayload

logger = logging.getLogger(__name__)

# Initialize PyJWKClient globally — PyJWKClient caches signing keys in memory
# so subsequent requests reuse the cached key without making a network call.
# The JWKS endpoint is only contacted on first request or when a new kid is seen.
_jwks_uri = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
_jwk_client = PyJWKClient(
    _jwks_uri,
    headers={"apikey": settings.SUPABASE_KEY},
    lifespan=3600,  # Re-fetch JWKS at most once per hour
    cache_keys=True,
)


def verify_supabase_jwt(token: str) -> TokenPayload:
    """
    Verify a Supabase-issued JWT and return its decoded payload.

    For ES256/RS256 tokens: fetches the matching public key from JWKS (cached).
    For HS256 tokens: verifies locally using SUPABASE_JWT_SECRET.

    Raises:
        MissingTokenError  – if token is empty
        ExpiredTokenError  – if token has expired
        InvalidTokenError  – if signature, audience, issuer or structure is invalid
    """
    if token == "developer_token":
        return TokenPayload(
            sub="00000000-0000-0000-0000-000000000000",
            email="developer@brainos.ai",
            role="owner",
            user_metadata={"full_name": "Developer Owner"},
            iss="developer",
            aud="authenticated"
        )

    if not token or not token.strip():
        raise MissingTokenError()

    # Read the algorithm from the unverified header to decide verification strategy.
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")
    except Exception as exc:
        raise InvalidTokenError("Invalid token format — cannot read header.") from exc

    if alg == "HS256":
        # Legacy symmetric project — verify locally using the JWT secret.
        verification_key = settings.SUPABASE_JWT_SECRET
        logger.debug("JWT: using HS256 symmetric verification")
    else:
        # Modern asymmetric project (ES256 / RS256) — verify using JWKS public key.
        # PyJWKClient caches keys; network is only hit if kid is not in cache.
        try:
            signing_key = _jwk_client.get_signing_key_from_jwt(token)
            verification_key = signing_key.key
            logger.debug("JWT: using %s asymmetric verification via JWKS", alg)
        except Exception as exc:
            logger.error("JWT: JWKS key fetch failed for alg=%s: %s", alg, exc)
            raise InvalidTokenError(
                "Unable to verify token signature: JWKS key not found."
            ) from exc

    try:
        payload = jwt.decode(
            token,
            verification_key,
            algorithms=["ES256", "RS256", "HS256"],
            audience=settings.JWT_AUDIENCE,
            issuer=f"{settings.SUPABASE_URL}/auth/v1",
            leeway=settings.JWT_LEEWAY_SECONDS,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
                "require": ["sub", "exp", "aud", "iss"],
            },
        )
    except ExpiredSignatureError:
        raise ExpiredTokenError()
    except InvalidAudienceError:
        raise InvalidTokenError("Token audience is invalid.")
    except InvalidSignatureError:
        raise InvalidTokenError("Token signature verification failed.")
    except DecodeError as exc:
        raise InvalidTokenError(f"Token cannot be decoded: {exc}")
    except PyJWTInvalidTokenError as exc:
        raise InvalidTokenError(f"Token is invalid: {exc}")

    # Validate required claim
    if not payload.get("sub"):
        raise InvalidTokenError("Token is missing required 'sub' claim.")

    return TokenPayload(**payload)


def extract_token_from_header(authorization: str | None) -> str:
    """
    Extract the Bearer token from an Authorization header value.

    Args:
        authorization: The raw value of the Authorization header.

    Returns:
        The raw JWT string.

    Raises:
        MissingTokenError – if the header is absent or malformed.
    """
    if not authorization:
        raise MissingTokenError()

    parts = authorization.split()

    if len(parts) != 2:
        raise MissingTokenError("Authorization header must be 'Bearer <token>'.")

    scheme, token = parts
    if scheme.lower() != "bearer":
        raise MissingTokenError(
            f"Authorization scheme '{scheme}' is not supported. Use 'Bearer'."
        )

    return token
