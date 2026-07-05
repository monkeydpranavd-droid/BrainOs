"""
app/auth/dependencies.py
─────────────────────────────────────────────────────────────────────────────
FastAPI dependency functions for authentication and multi-tenant authorisation.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import InsufficientPermissionsError, MissingTokenError
from app.schemas.user import CurrentUser, UserRole
from app.services.auth_service import AuthService
from app.services.organization_service import OrganizationService
from app.services.workspace_service import WorkspaceService
from app.repositories.member_repository import MemberRepository
from app.models.organization import Organization
from app.models.workspace import Workspace
from app.models.organization_member import OrganizationMember
from app.models.workspace_member import WorkspaceMember

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


# ── Primary dependency (Bypassed for Dev Mode) ────────────────────────────────

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    from app.services.auth_service import AuthService
    from app.schemas.auth import TokenPayload

    # Static developer user payload — JIT provisions organization & workspace if missing
    dev_payload = TokenPayload(
        sub="00000000-0000-0000-0000-000000000000",
        email="developer@brainos.ai",
        role="owner",
        user_metadata={"full_name": "Developer Owner"},
        iss="developer",
        aud="authenticated"
    )
    service = AuthService(db)
    user = service.get_or_create_user(dev_payload)

    logger.debug("Authenticated bypass user %s (role=%s)", user.id, user.role)
    return CurrentUser.model_validate(user)


# ── Optional dependency (Bypassed for Dev Mode) ───────────────────────────────

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[CurrentUser]:
    try:
        return await get_current_user(credentials, db)
    except Exception:
        return None


# ── Global system-level roles ─────────────────────────────────────────────────

async def require_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not current_user.is_admin:
        raise InsufficientPermissionsError("This action requires admin or owner privileges.")
    return current_user


async def require_owner(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not current_user.is_owner:
        raise InsufficientPermissionsError("This action requires owner privileges.")
    return current_user


# ── Multi-tenant dependencies ─────────────────────────────────────────────────

async def get_current_organization(
    org_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Organization:
    """Verifies that the user is a member of the organization and returns it."""
    member_repo = MemberRepository(db)
    member = member_repo.get_org_member(org_id, current_user.id)
    if not member:
        raise InsufficientPermissionsError("You are not a member of this organization.")
    
    service = OrganizationService(db)
    return service.get_organization(org_id)


async def require_org_admin(
    org_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMember:
    """Verifies that the user has admin or owner privileges within the organization."""
    member_repo = MemberRepository(db)
    member = member_repo.get_org_member(org_id, current_user.id)
    if not member or member.role not in ("admin", "owner"):
        raise InsufficientPermissionsError("This action requires organization admin privileges.")
    return member


async def require_org_owner(
    org_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMember:
    """Verifies that the user is the owner of the organization."""
    member_repo = MemberRepository(db)
    member = member_repo.get_org_member(org_id, current_user.id)
    if not member or member.role != "owner":
        raise InsufficientPermissionsError("This action requires organization owner privileges.")
    return member


async def get_current_workspace(
    workspace_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Workspace:
    """Verifies workspace access based on visibility and memberships."""
    service = WorkspaceService(db)
    ws = service.get_workspace(workspace_id)
    
    # 1. User must be a member of the workspace's organization
    member_repo = MemberRepository(db)
    org_member = member_repo.get_org_member(ws.organization_id, current_user.id)
    if not org_member:
        raise InsufficientPermissionsError("You are not a member of the organization containing this workspace.")

    # 2. If private, user must be a member of the workspace
    if ws.visibility == "private":
        ws_member = member_repo.get_workspace_member(workspace_id, current_user.id)
        if not ws_member:
            raise InsufficientPermissionsError("You do not have access to this private workspace.")

    return ws


async def require_workspace_member(
    workspace_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceMember:
    """Requires the user to be a formal member of the workspace."""
    member_repo = MemberRepository(db)
    ws_member = member_repo.get_workspace_member(workspace_id, current_user.id)
    if not ws_member:
        raise InsufficientPermissionsError("You are not a member of this workspace.")
    return ws_member
