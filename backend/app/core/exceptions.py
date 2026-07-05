"""
app/core/exceptions.py
─────────────────────────────────────────────────────────────────────────────
Centralised HTTP exception hierarchy for BrainOS.
"""

from __future__ import annotations

from fastapi import HTTPException, status


class BrainOSException(HTTPException):
    """Base exception for all BrainOS domain errors."""

    def __init__(self, status_code: int, detail: str, headers: dict | None = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


# ── 401 Authentication ────────────────────────────────────────────────────────

class InvalidTokenError(BrainOSException):
    def __init__(self, detail: str = "Invalid authentication token."):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail,
                         headers={"WWW-Authenticate": "Bearer"})


class ExpiredTokenError(BrainOSException):
    def __init__(self, detail: str = "Authentication token has expired."):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail,
                         headers={"WWW-Authenticate": "Bearer"})


class MissingTokenError(BrainOSException):
    def __init__(self, detail: str = "Authentication token is missing."):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail,
                         headers={"WWW-Authenticate": "Bearer"})


# ── 403 Authorisation ─────────────────────────────────────────────────────────

class InsufficientPermissionsError(BrainOSException):
    def __init__(self, detail: str = "You do not have permission to perform this action."):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# ── 404 Not Found ─────────────────────────────────────────────────────────────

class UserNotFoundError(BrainOSException):
    def __init__(self, detail: str = "User not found."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class OrganizationNotFoundError(BrainOSException):
    def __init__(self, detail: str = "Organization not found."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class WorkspaceNotFoundError(BrainOSException):
    def __init__(self, detail: str = "Workspace not found."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvitationNotFoundError(BrainOSException):
    def __init__(self, detail: str = "Invitation not found or expired."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# ── 409 Conflict ─────────────────────────────────────────────────────────────

class UserAlreadyExistsError(BrainOSException):
    def __init__(self, detail: str = "User already exists."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class OrganizationSlugTakenError(BrainOSException):
    def __init__(self, detail: str = "Organization slug is already taken."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class AlreadyMemberError(BrainOSException):
    def __init__(self, detail: str = "User is already a member of this organization."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ── 503 Upstream ─────────────────────────────────────────────────────────────

class SupabaseError(BrainOSException):
    def __init__(self, detail: str = "Supabase service error."):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
