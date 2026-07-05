"""
app/auth/jwt.py
─────────────────────────────────────────────────────────────────────────────
Supabase JWT verification.

Verifies the signature, audience, issuer and expiration of Supabase-issued asymmetric
or symmetric JWTs server-side using JWKS endpoints.
"""

from __future__ import annotations

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

# Initialize PyJWKClient globally to leverage key caching.
# We pass settings.SUPABASE_KEY as the apikey header to authenticate against Supabase Gateway.
_jwks_uri = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
_jwk_client = PyJWKClient(_jwks_uri, headers={"apikey": settings.SUPABASE_KEY})


def verify_supabase_jwt(token: str) -> TokenPayload:
    """
    Verify a Supabase-issued JWT and return its decoded payload.

    Raises:
        MissingTokenError  – if token is empty
        ExpiredTokenError  – if token has expired
        InvalidTokenError  – if signature, audience, issuer or structure is invalid
    """
    if not token or not token.strip():
        raise MissingTokenError()

    try:
        # Retrieve the public key matching kid of JWT from cached JWKS keys
        signing_key = _jwk_client.get_signing_key_from_jwt(token)
        verification_key = signing_key.key
    except Exception as exc:
        # Fallback to local symmetric secret verification for legacy HS256 tokens
        # if JWKS does not contain matching key or is unavailable.
        verification_key = settings.SUPABASE_JWT_SECRET

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
