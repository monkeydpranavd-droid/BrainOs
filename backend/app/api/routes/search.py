"""
app/api/routes/search.py
─────────────────────────────────────────────────────────────────────────────
API routes for document metadata searching.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import (
    get_current_user,
    get_current_workspace,
)
from app.schemas.document import DocumentResponse
from app.schemas.user import CurrentUser
from app.services.document_service import DocumentService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "/documents",
    response_model=List[DocumentResponse],
    summary="Search document metadata in workspace",
)
async def search_documents(
    workspace_id: uuid.UUID = Query(...),
    query: str = Query(..., min_length=1, description="Text string query to search"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentResponse]:
    # Verify access to workspace
    ws = await get_current_workspace(workspace_id, current_user, db)

    service = DocumentService(db)
    docs = service.search_documents(ws.organization_id, workspace_id, query)
    return [DocumentResponse.model_validate(d) for d in docs]
