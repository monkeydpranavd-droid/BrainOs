"""
app/api/routes/folders.py
─────────────────────────────────────────────────────────────────────────────
API routes for nested Folder management.
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
from app.schemas.folder import FolderCreate, FolderResponse
from app.schemas.user import CurrentUser
from app.services.folder_service import FolderService

router = APIRouter(prefix="/folders", tags=["Folders"])


@router.post(
    "",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new folder in workspace",
)
async def create_folder(
    body: FolderCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FolderResponse:
    # Verify access to org and workspace
    await get_current_organization(body.organization_id, current_user, db)
    await get_current_workspace(body.workspace_id, current_user, db)

    service = FolderService(db)
    folder = service.create_folder(
        organization_id=body.organization_id,
        workspace_id=body.workspace_id,
        name=body.name,
        parent_folder_id=body.parent_folder_id,
    )
    return FolderResponse.model_validate(folder)


@router.get(
    "",
    response_model=List[FolderResponse],
    summary="List folders in workspace",
)
async def list_folders(
    workspace_id: uuid.UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[FolderResponse]:
    # Verify access to workspace
    await get_current_workspace(workspace_id, current_user, db)

    service = FolderService(db)
    folders = service.list_folders(workspace_id)
    return [FolderResponse.model_validate(f) for f in folders]
