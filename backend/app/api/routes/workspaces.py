"""
app/api/routes/workspaces.py
─────────────────────────────────────────────────────────────────────────────
API routes for Workspace resource management and workspace memberships.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import (
    get_current_user,
    get_current_organization,
    get_current_workspace,
)
from app.models.workspace import Workspace
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceMemberResponse,
    WorkspaceMemberAddRequest,
)
from app.schemas.user import CurrentUser
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workspace",
)
async def create_workspace(
    body: WorkspaceCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    # Verify user belongs to the org they are creating the workspace in
    await get_current_organization(body.organization_id, current_user, db)
    
    service = WorkspaceService(db)
    ws = service.create_workspace(
        organization_id=body.organization_id,
        name=body.name,
        created_by=current_user.id,
        description=body.description,
        visibility=body.visibility,
    )
    return WorkspaceResponse.model_validate(ws)


@router.get(
    "",
    response_model=List[WorkspaceResponse],
    summary="List workspaces in organization",
)
async def list_workspaces(
    org_id: uuid.UUID = Query(..., description="The ID of the organization to list workspaces for"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WorkspaceResponse]:
    # Verify user belongs to the organization
    await get_current_organization(org_id, current_user, db)

    service = WorkspaceService(db)
    workspaces = service.list_workspaces_for_user(current_user.id, org_id)
    return [WorkspaceResponse.model_validate(w) for w in workspaces]


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Get workspace details",
)
async def get_workspace(
    ws: Workspace = Depends(get_current_workspace),
) -> WorkspaceResponse:
    return WorkspaceResponse.model_validate(ws)


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update workspace details",
)
async def update_workspace(
    workspace_id: uuid.UUID,
    body: WorkspaceUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    # Ensure current user has workspace access
    ws = await get_current_workspace(workspace_id, current_user, db)
    
    service = WorkspaceService(db)
    updated = service.update_workspace(
        ws_id=workspace_id,
        org_id=ws.organization_id,
        user_id=current_user.id,
        name=body.name,
        description=body.description,
        visibility=body.visibility,
    )
    return WorkspaceResponse.model_validate(updated)


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workspace",
)
async def delete_workspace(
    workspace_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    # Ensure current user has workspace access
    ws = await get_current_workspace(workspace_id, current_user, db)

    service = WorkspaceService(db)
    service.delete_workspace(
        ws_id=workspace_id,
        org_id=ws.organization_id,
        user_id=current_user.id,
    )


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    summary="Add member to workspace",
)
async def add_workspace_member(
    workspace_id: uuid.UUID,
    body: WorkspaceMemberAddRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceMemberResponse:
    # Ensure current user has workspace access
    ws = await get_current_workspace(workspace_id, current_user, db)

    service = WorkspaceService(db)
    member = service.add_workspace_member(
        ws_id=workspace_id,
        org_id=ws.organization_id,
        target_user_id=body.user_id,
        role=body.role,
        user_id=current_user.id,
    )
    return WorkspaceMemberResponse.model_validate(member)
