"""
app/api/routes/documents.py
─────────────────────────────────────────────────────────────────────────────
API routes for document upload, update, deletion, versions, and tags.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    status,
    File,
    UploadFile,
    Form,
    BackgroundTasks,
    Query,
)
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import (
    get_current_user,
    get_current_organization,
    get_current_workspace,
)
from app.repositories.member_repository import MemberRepository
from app.core.exceptions import InsufficientPermissionsError, UserNotFoundError
from app.schemas.document import (
    DocumentResponse,
    DocumentUpdate,
    DocumentVersionResponse,
    DocumentChunkResponse,
)
from app.schemas.user import CurrentUser
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document or a new version",
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    organization_id: uuid.UUID = Form(...),
    workspace_id: uuid.UUID = Form(...),
    folder_id: Optional[uuid.UUID] = Form(None),
    knowledge_base_id: Optional[uuid.UUID] = Form(None),
    change_notes: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    # 1. Verify organization and workspace membership access
    await get_current_organization(organization_id, current_user, db)
    await get_current_workspace(workspace_id, current_user, db)

    # 2. Check RBAC: Guests cannot upload documents
    member_repo = MemberRepository(db)
    org_member = member_repo.get_org_member(organization_id, current_user.id)
    if not org_member or org_member.role == "guest":
        raise InsufficientPermissionsError("Guests are not permitted to upload files.")

    # 3. Read file contents in memory
    file_bytes = await file.read()

    # 4. Invoke service layer
    service = DocumentService(db)
    doc = service.upload_document(
        organization_id=organization_id,
        workspace_id=workspace_id,
        uploaded_by=current_user.id,
        filename=file.filename,
        file_bytes=file_bytes,
        mime_type=file.content_type or "application/octet-stream",
        background_tasks=background_tasks,
        folder_id=folder_id,
        knowledge_base_id=knowledge_base_id,
        change_notes=change_notes,
    )
    return DocumentResponse.model_validate(doc)


@router.get(
    "",
    response_model=List[DocumentResponse],
    summary="List documents in workspace",
)
async def list_documents(
    workspace_id: uuid.UUID = Query(...),
    folder_id: Optional[uuid.UUID] = Query(None),
    kb_id: Optional[uuid.UUID] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentResponse]:
    # Verify access to workspace
    await get_current_workspace(workspace_id, current_user, db)

    service = DocumentService(db)
    docs = service.list_documents(workspace_id, folder_id, kb_id)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get(
    "/{doc_id}",
    response_model=DocumentResponse,
    summary="Get document details",
)
async def get_document(
    doc_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    service = DocumentService(db)
    doc = service.get_document(doc_id)
    
    # Check access to workspace
    await get_current_workspace(doc.workspace_id, current_user, db)
    return DocumentResponse.model_validate(doc)


@router.patch(
    "/{doc_id}",
    response_model=DocumentResponse,
    summary="Update document fields",
)
async def update_document(
    doc_id: uuid.UUID,
    body: DocumentUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    service = DocumentService(db)
    doc = service.get_document(doc_id)
    
    # Check access to workspace
    await get_current_workspace(doc.workspace_id, current_user, db)
    
    # Check editor role
    member_repo = MemberRepository(db)
    org_member = member_repo.get_org_member(doc.organization_id, current_user.id)
    if not org_member or org_member.role == "guest":
        raise InsufficientPermissionsError("Guest users cannot modify document details.")

    updated = service.update_document(
        doc_id=doc_id,
        title=body.title,
        description=body.description,
        folder_id=body.folder_id,
        knowledge_base_id=body.knowledge_base_id,
        summary=body.summary,
        language=body.language,
    )
    return DocumentResponse.model_validate(updated)


@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
)
async def delete_document(
    doc_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service = DocumentService(db)
    doc = service.get_document(doc_id)
    
    # Ensure workspace access
    await get_current_workspace(doc.workspace_id, current_user, db)
    
    # Check owner role
    member_repo = MemberRepository(db)
    org_member = member_repo.get_org_member(doc.organization_id, current_user.id)
    if not org_member or org_member.role not in ("owner", "admin"):
        raise InsufficientPermissionsError("Only organization owners or admins may delete documents.")

    service.delete_document(doc_id)


@router.get(
    "/{doc_id}/versions",
    response_model=List[DocumentVersionResponse],
    summary="List document versions",
)
async def list_document_versions(
    doc_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentVersionResponse]:
    service = DocumentService(db)
    doc = service.get_document(doc_id)
    await get_current_workspace(doc.workspace_id, current_user, db)

    versions = service.list_versions(doc_id)
    return [DocumentVersionResponse.model_validate(v) for v in versions]


@router.get(
    "/{doc_id}/preview",
    summary="Generate temporary preview URL",
)
async def get_document_preview(
    doc_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    doc = service.get_document(doc_id)
    await get_current_workspace(doc.workspace_id, current_user, db)

    url = service.get_preview_url(doc_id)
    return {"preview_url": url}


@router.post(
    "/{doc_id}/tags",
    response_model=DocumentResponse,
    summary="Assign tag to document",
)
async def assign_tag(
    doc_id: uuid.UUID,
    tag_name: str = Query(...),
    color: str = Query("#6366F1"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    service = DocumentService(db)
    doc = service.get_document(doc_id)
    await get_current_workspace(doc.workspace_id, current_user, db)

    updated = service.assign_tag(doc_id, tag_name, color)
    return DocumentResponse.model_validate(updated)


@router.post(
    "/upload-chunk",
    status_code=status.HTTP_200_OK,
    summary="Upload a single file chunk",
)
async def upload_chunk(
    session_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...),
) -> dict:
    import os
    from pathlib import Path

    chunks_dir = Path(__file__).resolve().parent.parent.parent.parent / "uploads" / "chunks" / session_id
    chunks_dir.mkdir(parents=True, exist_ok=True)

    chunk_file = chunks_dir / f"{chunk_index}"
    with open(chunk_file, "wb") as f:
        f.write(await file.read())

    return {"message": f"Chunk {chunk_index} uploaded successfully."}


@router.post(
    "/assemble-chunks",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assemble uploaded chunks and process document",
)
async def assemble_chunks(
    background_tasks: BackgroundTasks,
    session_id: str = Form(...),
    total_chunks: int = Form(...),
    organization_id: uuid.UUID = Form(...),
    workspace_id: uuid.UUID = Form(...),
    filename: str = Form(...),
    mime_type: str = Form(...),
    folder_id: Optional[uuid.UUID] = Form(None),
    knowledge_base_id: Optional[uuid.UUID] = Form(None),
    change_notes: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    import shutil
    from pathlib import Path
    from fastapi import HTTPException

    await get_current_organization(organization_id, current_user, db)
    await get_current_workspace(workspace_id, current_user, db)

    member_repo = MemberRepository(db)
    org_member = member_repo.get_org_member(organization_id, current_user.id)
    if not org_member or org_member.role == "guest":
        raise InsufficientPermissionsError("Guests are not permitted to upload files.")

    chunks_dir = Path(__file__).resolve().parent.parent.parent.parent / "uploads" / "chunks" / session_id
    if not chunks_dir.exists():
        raise HTTPException(status_code=400, detail="Upload session not found.")

    assembled_bytes = bytearray()
    for idx in range(total_chunks):
        chunk_file = chunks_dir / f"{idx}"
        if not chunk_file.exists():
            raise HTTPException(status_code=400, detail=f"Missing chunk {idx}.")
        with open(chunk_file, "rb") as f:
            assembled_bytes.extend(f.read())

    shutil.rmtree(chunks_dir, ignore_errors=True)

    service = DocumentService(db)
    doc = service.upload_document(
        organization_id=organization_id,
        workspace_id=workspace_id,
        uploaded_by=current_user.id,
        filename=filename,
        file_bytes=bytes(assembled_bytes),
        mime_type=mime_type or "application/octet-stream",
        background_tasks=background_tasks,
        folder_id=folder_id,
        knowledge_base_id=knowledge_base_id,
        change_notes=change_notes,
    )
    return DocumentResponse.model_validate(doc)


@router.get(
    "/{doc_id}/chunks",
    response_model=List[DocumentChunkResponse],
    summary="Get document chunks",
)
async def get_document_chunks(
    doc_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentChunkResponse]:
    service = DocumentService(db)
    doc = service.get_document(doc_id)
    await get_current_workspace(doc.workspace_id, current_user, db)

    from app.repositories.document_repository import DocumentRepository
    repo = DocumentRepository(db)
    chunks = repo.list_chunks(doc_id)
    return [DocumentChunkResponse.model_validate(c) for c in chunks]


@router.get(
    "/local-preview",
    summary="Serve local document files in local-development fallback mode",
    include_in_schema=False,
)
def serve_local_preview(
    bucket: str,
    path: str,
):
    from fastapi.responses import FileResponse
    from pathlib import Path
    
    local_file = Path(__file__).resolve().parent.parent.parent.parent / "uploads" / bucket / path
    if not local_file.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(local_file)
