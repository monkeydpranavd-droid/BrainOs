"""
app/api/routes/knowledge_bases.py
─────────────────────────────────────────────────────────────────────────────
API routes for KnowledgeBase partitions.
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
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseResponse
from app.schemas.user import CurrentUser
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(prefix="/knowledge-bases", tags=["Knowledge Bases"])


@router.post(
    "",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new knowledge base in workspace",
)
async def create_knowledge_base(
    body: KnowledgeBaseCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    # Verify access to org and workspace
    await get_current_organization(body.organization_id, current_user, db)
    await get_current_workspace(body.workspace_id, current_user, db)

    service = KnowledgeBaseService(db)
    kb = service.create_knowledge_base(
        organization_id=body.organization_id,
        workspace_id=body.workspace_id,
        name=body.name,
        description=body.description,
        visibility=body.visibility,
    )
    return KnowledgeBaseResponse.model_validate(kb)


@router.get(
    "",
    response_model=List[KnowledgeBaseResponse],
    summary="List knowledge bases in workspace",
)
async def list_knowledge_bases(
    workspace_id: uuid.UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[KnowledgeBaseResponse]:
    # Verify access to workspace
    await get_current_workspace(workspace_id, current_user, db)

    service = KnowledgeBaseService(db)
    kbs = service.list_knowledge_bases(workspace_id)
    return [KnowledgeBaseResponse.model_validate(k) for k in kbs]
