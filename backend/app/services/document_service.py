"""
app/services/document_service.py
─────────────────────────────────────────────────────────────────────────────
Service layer for Document and versioning business logic.
Integrates Supabase Storage uploads and executes background pipelines.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import Any, List, Optional, Sequence, Tuple
from fastapi import BackgroundTasks

from sqlalchemy.orm import Session

from app.core.exceptions import (
    UserNotFoundError,
    InsufficientPermissionsError,
)
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.repositories.document_repository import DocumentRepository
from app.repositories.version_repository import VersionRepository
from app.repositories.tag_repository import TagRepository
from app.storage.supabase_storage import StorageService
from app.documents.versioning import calculate_sha256
from app.workers.document_processor import SyncDocumentProcessor


class DocumentService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._doc_repo = DocumentRepository(db)
        self._ver_repo = VersionRepository(db)
        self._tag_repo = TagRepository(db)
        self._storage = StorageService()
        self._processor = SyncDocumentProcessor()

    def upload_document(
        self,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        uploaded_by: uuid.UUID,
        filename: str,
        file_bytes: bytes,
        mime_type: str,
        background_tasks: BackgroundTasks,
        folder_id: Optional[uuid.UUID] = None,
        knowledge_base_id: Optional[uuid.UUID] = None,
        change_notes: Optional[str] = None,
    ) -> Document:
        file_size = len(file_bytes)
        checksum = calculate_sha256(file_bytes)

        # 1. Deduplication check: verify if document checksum already exists in organization
        existing_by_checksum = self._doc_repo.get_by_checksum(checksum, organization_id)
        if existing_by_checksum:
            # Prevents duplicate upload of exact same file contents
            return existing_by_checksum

        # 2. Check if a document with same original filename exists in this workspace & folder
        # (If it does, we treat this as a new version)
        # We can implement a helper or query in DB. Let's look up document by filename/folder
        # Let's simple check:
        existing_doc = None
        # We search document by workspace, folder and filename
        # Let's write a simple query directly here:
        from sqlalchemy import select
        stmt = (
            select(Document)
            .where(Document.workspace_id == workspace_id)
            .where(Document.original_filename == filename)
            .where(Document.folder_id == folder_id)
        )
        existing_doc = self._db.scalar(stmt)

        if existing_doc:
            # ── New Version Flow ──────────────────────────────────────────────
            new_version_num = existing_doc.current_version + 1
            storage_path = f"{organization_id}/{workspace_id}/{existing_doc.id}/v{new_version_num}_{filename}"
            
            # Upload version physical file
            self._storage.upload_file("documents", storage_path, file_bytes, mime_type)
            
            # Create Version record
            self._ver_repo.create(
                document_id=existing_doc.id,
                version=new_version_num,
                storage_path=storage_path,
                checksum=checksum,
                uploaded_by=uploaded_by,
                change_notes=change_notes or f"Revision upload to version {new_version_num}",
            )
            
            # Update parent Document
            existing_doc.current_version = new_version_num
            existing_doc.storage_path = storage_path
            existing_doc.file_size = file_size
            existing_doc.checksum = checksum
            existing_doc.mime_type = mime_type
            existing_doc.status = "pending"
            
            self._doc_repo.update(existing_doc)
            self._db.commit()
            self._db.refresh(existing_doc)
            
            # Trigger background processor task asynchronously
            background_tasks.add_task(self._processor.process_document, existing_doc.id)
            return existing_doc

        else:
            # ── New Document Flow ─────────────────────────────────────────────
            doc_uuid = uuid.uuid4()
            storage_path = f"{organization_id}/{workspace_id}/{doc_uuid}/v1_{filename}"
            
            # Upload document physical file
            self._storage.upload_file("documents", storage_path, file_bytes, mime_type)
            
            # Create Document record
            doc = self._doc_repo.create(
                organization_id=organization_id,
                workspace_id=workspace_id,
                uploaded_by=uploaded_by,
                title=filename.rsplit(".", 1)[0], # Remove extension for clean title
                original_filename=filename,
                storage_path=storage_path,
                mime_type=mime_type,
                file_size=file_size,
                checksum=checksum,
                folder_id=folder_id,
                knowledge_base_id=knowledge_base_id,
                description=None,
            )
            
            # Create Version 1 record
            self._ver_repo.create(
                document_id=doc.id,
                version=1,
                storage_path=storage_path,
                checksum=checksum,
                uploaded_by=uploaded_by,
                change_notes="Initial document upload",
            )
            
            self._db.commit()
            self._db.refresh(doc)
            
            # Trigger background processor task asynchronously
            background_tasks.add_task(self._processor.process_document, doc.id)
            return doc

    def get_document(self, doc_id: uuid.UUID) -> Document:
        doc = self._doc_repo.get_by_id(doc_id)
        if not doc:
            from app.core.exceptions import UserNotFoundError
            # Standard error maps to 404
            raise UserNotFoundError("Document not found")
        return doc

    def update_document(
        self,
        doc_id: uuid.UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        folder_id: Optional[uuid.UUID] = None,
        knowledge_base_id: Optional[uuid.UUID] = None,
        summary: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Document:
        doc = self.get_document(doc_id)
        if title is not None:
            doc.title = title
        if description is not None:
            doc.description = description
        if folder_id is not None:
            doc.folder_id = folder_id
        if knowledge_base_id is not None:
            doc.knowledge_base_id = knowledge_base_id
        if summary is not None:
            doc.summary = summary
        if language is not None:
            doc.language = language

        self._doc_repo.update(doc)
        self._db.commit()
        self._db.refresh(doc)
        return doc

    def delete_document(self, doc_id: uuid.UUID) -> None:
        doc = self.get_document(doc_id)
        # Delete from Supabase Storage first
        try:
            self._storage.delete_file("documents", doc.storage_path)
        except Exception:
            pass # Ignore storage deletes if already missing
            
        self._doc_repo.delete(doc)
        self._db.commit()

    def get_preview_url(self, doc_id: uuid.UUID) -> str:
        """Fetch signed URL for secure file preview access."""
        doc = self.get_document(doc_id)
        return self._storage.signed_url("documents", doc.storage_path, expires_in_seconds=3600)

    def list_documents(
        self,
        workspace_id: uuid.UUID,
        folder_id: Optional[uuid.UUID] = None,
        kb_id: Optional[uuid.UUID] = None,
    ) -> Sequence[Document]:
        return self._doc_repo.list_by_workspace(workspace_id, folder_id, kb_id)

    def list_versions(self, doc_id: uuid.UUID) -> Sequence[DocumentVersion]:
        # Validate doc exists
        self.get_document(doc_id)
        return self._ver_repo.list_by_document(doc_id)

    def assign_tag(self, doc_id: uuid.UUID, tag_name: str, color: str = "#6366F1") -> Document:
        doc = self.get_document(doc_id)
        tag = self._tag_repo.get_by_name(doc.organization_id, tag_name)
        if not tag:
            tag = self._tag_repo.create(doc.organization_id, name=tag_name, color=color)
            
        if not self._tag_repo.get_document_tag(doc.id, tag.id):
            self._tag_repo.add_tag_to_document(doc.id, tag.id)
            self._db.commit()
            
        self._db.refresh(doc)
        return doc

    def get_tags(self, doc_id: uuid.UUID) -> Sequence[Any]:
        return self._tag_repo.list_tags_for_document(doc_id)

    def search_documents(self, org_id: uuid.UUID, workspace_id: uuid.UUID, query: str) -> Sequence[Document]:
        return self._doc_repo.search_documents_metadata(org_id, workspace_id, query)
