"""
app/services/auth_service.py
─────────────────────────────────────────────────────────────────────────────
Authentication business logic.

This layer sits between the HTTP layer (routes/dependencies) and the data
layer (repositories/Supabase). It owns:
  - Token verification
  - First-login user provisioning (auto-create local profile)
  - last_login tracking
  - Session info assembly

It does NOT know about HTTP. It raises domain exceptions (not HTTPException).
Routes catch domain exceptions and convert them via FastAPI exception handlers.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.auth.jwt import extract_token_from_header, verify_supabase_jwt
from app.core.exceptions import InvalidTokenError, UserNotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import SessionInfo, TokenPayload
from app.schemas.user import CurrentUser, UserRole

logger = logging.getLogger(__name__)


class AuthService:
    """
    Encapsulates all authentication operations.

    Designed to be instantiated per-request (stateless).
    Inject the DB session; do not store it beyond the request lifetime.
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = UserRepository(db)

    # ── Token verification ────────────────────────────────────────────────────

    def verify_token_from_header(self, authorization: str | None) -> TokenPayload:
        """
        Extract and verify a JWT from the Authorization header.

        Returns the decoded token payload on success.
        Raises MissingTokenError / InvalidTokenError / ExpiredTokenError.
        """
        raw_token = extract_token_from_header(authorization)
        return verify_supabase_jwt(raw_token)

    # ── User provisioning ─────────────────────────────────────────────────────

    def get_or_create_user(self, payload: TokenPayload) -> User:
        """
        Given a verified JWT payload, return the corresponding local User.

        On first login the user is automatically provisioned in the local DB.
        This is the "just-in-time provisioning" pattern — we don't pre-seed
        users; they appear when they first authenticate.

        Always updates last_login on success.
        """
        supabase_uid = payload.user_uuid

        user = self._repo.get_by_supabase_id(supabase_uid)

        if user is None:
            logger.info(
                "First login for Supabase user %s — provisioning local profile.",
                supabase_uid,
            )
            user = self._provision_new_user(payload)

        if not user.is_active:
            raise InvalidTokenError("Your account has been deactivated.")

        self._repo.update_last_login(user)
        self._db.commit()
        self._db.refresh(user)

        return user

    def _provision_new_user(self, payload: TokenPayload) -> User:
        """Create a new local user from a verified JWT payload."""
        email = payload.email
        if not email:
            raise InvalidTokenError(
                "Cannot provision user: JWT payload is missing 'email' claim."
            )

        # Pull richer metadata from user_metadata if available.
        user_metadata: dict = payload.user_metadata or {}
        full_name: str | None = user_metadata.get("full_name") or user_metadata.get("name")
        avatar_url: str | None = user_metadata.get("avatar_url") or user_metadata.get("picture")

        # 1. Create User
        user = self._repo.create(
            supabase_user_id=payload.user_uuid,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            role=UserRole.MEMBER,
        )

        # 2. Provision Tenant (Organization & Workspace) transactionally
        # Import services locally to avoid circular dependencies
        from app.services.organization_service import OrganizationService
        from app.services.workspace_service import WorkspaceService

        org_name = f"{full_name}'s Org" if full_name else f"{email.split('@')[0].capitalize()}'s Org"
        org_service = OrganizationService(self._db)
        org = org_service.create_organization(
            name=org_name,
            creator_user_id=user.id,
            commit=False
        )

        ws_service = WorkspaceService(self._db)
        ws_service.create_workspace(
            organization_id=org.id,
            name="Default Workspace",
            created_by=user.id,
            commit=False
        )

        return user

    # ── Session info ──────────────────────────────────────────────────────────

    def build_session_info(self, payload: TokenPayload) -> SessionInfo:
        """Assemble a SessionInfo from a decoded token payload."""
        issued_at = (
            datetime.fromtimestamp(payload.iat, tz=timezone.utc)
            if payload.iat
            else None
        )
        expires_at = (
            datetime.fromtimestamp(payload.exp, tz=timezone.utc)
            if payload.exp
            else None
        )
        return SessionInfo(
            supabase_user_id=payload.user_uuid,
            email=payload.email,
            role=payload.role,
            issued_at=issued_at,
            expires_at=expires_at,
            is_valid=True,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def get_user_by_id(self, user_id: uuid.UUID) -> User:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user
