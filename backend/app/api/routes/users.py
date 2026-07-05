"""
app/api/routes/users.py
─────────────────────────────────────────────────────────────────────────────
User profile management and user-centric listing routes.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.repositories.user_repository import UserRepository
from app.schemas.user import AdminUserUpdate, CurrentUser, UserResponse, UserUpdate
from app.schemas.organization import OrganizationResponse
from app.schemas.workspace import WorkspaceResponse
from app.services.organization_service import OrganizationService
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_my_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Return the full profile of the authenticated user."""
    repo = UserRepository(db)
    user = repo.get_by_id(current_user.id)
    return UserResponse.model_validate(user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_my_profile(
    body: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update the authenticated user's own profile (name, avatar)."""
    repo = UserRepository(db)
    user = repo.get_by_id(current_user.id)
    updated = repo.update_profile(
        user,
        full_name=body.full_name,
        avatar_url=body.avatar_url,
    )
    db.commit()
    db.refresh(updated)
    return UserResponse.model_validate(updated)


@router.get(
    "/me/organizations",
    response_model=List[OrganizationResponse],
    summary="Get current user's organizations",
)
async def get_my_organizations(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[OrganizationResponse]:
    """Return a list of organizations the current user belongs to."""
    service = OrganizationService(db)
    orgs = service.get_user_organizations(current_user.id)
    return [OrganizationResponse.model_validate(o) for o in orgs]


@router.get(
    "/me/workspaces",
    response_model=List[WorkspaceResponse],
    summary="Get current user's workspaces",
)
async def get_my_workspaces(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WorkspaceResponse]:
    """Return a list of workspaces the current user belongs to."""
    service = WorkspaceService(db)
    workspaces = service.list_all_user_workspaces(current_user.id)
    return [WorkspaceResponse.model_validate(w) for w in workspaces]


# ── Admin routes ──────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List all users (admin only)",
)
async def list_users(
    limit: int = 50,
    offset: int = 0,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> List[UserResponse]:
    """Return all active users. Requires admin or owner role."""
    repo = UserRepository(db)
    users = repo.list_active(limit=limit, offset=offset)
    return [UserResponse.model_validate(u) for u in users]


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update any user (admin only)",
)
async def admin_update_user(
    user_id: uuid.UUID,
    body: AdminUserUpdate,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Admin can update role, active status, name, avatar of any user."""
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if body.full_name is not None or body.avatar_url is not None:
        repo.update_profile(user, full_name=body.full_name, avatar_url=body.avatar_url)

    if body.role is not None:
        repo.update_role(user, body.role)

    if body.is_active is not None:
        if body.is_active:
            repo.reactivate(user)
        else:
            repo.deactivate(user)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)
