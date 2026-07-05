"""
app/repositories/document_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for database access related to Documents and DocumentChunks.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_tag import DocumentTag


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, doc_id: uuid.UUID) -> Optional[Document]:
        return self._db.get(Document, doc_id)

    def get_by_id_and_org(self, doc_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Document]:
        stmt = select(Document).where(Document.id == doc_id).where(Document.organization_id == org_id)
        return self._db.scalar(stmt)

    def get_by_checksum(self, checksum: str, org_id: uuid.UUID) -> Optional[Document]:
        stmt = (
            select(Document)
            .where(Document.checksum == checksum)
            .where(Document.organization_id == org_id)
        )
        return self._db.scalar(stmt)

    def create(
        self,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        uploaded_by: uuid.UUID,
        title: str,
        original_filename: str,
        storage_path: str,
        mime_type: str,
        file_size: int,
        checksum: str,
        folder_id: Optional[uuid.UUID] = None,
        knowledge_base_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        language: Optional[str] = None,
        page_count: Optional[int] = None,
    ) -> Document:
        doc = Document(
            organization_id=organization_id,
            workspace_id=workspace_id,
            uploaded_by=uploaded_by,
            title=title,
            original_filename=original_filename,
            storage_path=storage_path,
            mime_type=mime_type,
            file_size=file_size,
            checksum=checksum,
            folder_id=folder_id,
            knowledge_base_id=knowledge_base_id,
            description=description,
            language=language,
            page_count=page_count,
            status="pending",
        )
        self._db.add(doc)
        self._db.flush()
        return doc

    def update(self, doc: Document) -> Document:
        self._db.flush()
        return doc

    def delete(self, doc: Document) -> None:
        self._db.delete(doc)
        self._db.flush()

    def list_by_workspace(
        self,
        workspace_id: uuid.UUID,
        folder_id: Optional[uuid.UUID] = None,
        kb_id: Optional[uuid.UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Document]:
        stmt = (
            select(Document)
            .where(Document.workspace_id == workspace_id)
        )
        if folder_id is not None:
            stmt = stmt.where(Document.folder_id == folder_id)
        if kb_id is not None:
            stmt = stmt.where(Document.knowledge_base_id == kb_id)
            
        stmt = stmt.order_by(Document.created_at.desc()).limit(limit).offset(offset)
        return self._db.scalars(stmt).all()

    # ── Chunks ────────────────────────────────────────────────────────────────

    def create_chunk(
        self,
        document_id: uuid.UUID,
        chunk_index: int,
        content: str,
        page: Optional[int] = None,
        token_count: int = 0,
        chunk_metadata: Optional[dict] = None,
        embedding: Optional[List[float]] = None,
    ) -> DocumentChunk:
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            page=page,
            token_count=token_count,
            chunk_metadata=chunk_metadata,
            embedding_status="completed" if embedding else "pending",
            embedding=embedding,
        )
        self._db.add(chunk)
        self._db.flush()
        return chunk

    def list_chunks(self, document_id: uuid.UUID) -> Sequence[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        return self._db.scalars(stmt).all()

    def search_documents_metadata(
        self,
        org_id: uuid.UUID,
        workspace_id: uuid.UUID,
        query: str,
        limit: int = 50,
    ) -> Sequence[Document]:
        """Perform metadata text search on documents in a workspace."""
        search_pattern = f"%{query.lower()}%"
        stmt = (
            select(Document)
            .where(Document.organization_id == org_id)
            .where(Document.workspace_id == workspace_id)
            .where(
                or_(
                    Document.title.ilike(search_pattern),
                    Document.original_filename.ilike(search_pattern),
                    Document.summary.ilike(search_pattern),
                )
            )
            .limit(limit)
        )
        return self._db.scalars(stmt).all()

    def search_chunks_vector(
        self,
        workspace_id: uuid.UUID,
        query_vector: list[float],
        limit: int = 10,
    ) -> Sequence[DocumentChunk]:
        """Query similar chunks in a workspace using pgvector cosine distance."""
        stmt = (
            select(DocumentChunk)
            .join(Document)
            .where(Document.workspace_id == workspace_id)
            .where(DocumentChunk.embedding != None)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(limit)
        )
        return self._db.scalars(stmt).all()

    def search_chunks_vector_filtered(
        self,
        org_id: uuid.UUID,
        workspace_id: uuid.UUID,
        query_vector: list[float],
        document_ids: Optional[list[uuid.UUID]] = None,
        limit: int = 10,
    ) -> Sequence[DocumentChunk]:
        """Query similar chunks with metadata filtering and document narrowing."""
        stmt = (
            select(DocumentChunk)
            .join(Document)
            .where(Document.organization_id == org_id)
            .where(Document.workspace_id == workspace_id)
            .where(DocumentChunk.embedding != None)
        )
        if document_ids:
            stmt = stmt.where(Document.id.in_(document_ids))
            
        stmt = stmt.order_by(DocumentChunk.embedding.cosine_distance(query_vector)).limit(limit)
        return self._db.scalars(stmt).all()
