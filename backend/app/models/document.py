"""
app/models/document.py
─────────────────────────────────────────────────────────────────────────────
Document model representing metadata and processing status of uploaded items.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.workspace import Workspace
    from app.models.user import User
    from app.models.folder import Folder
    from app.models.knowledge_base import KnowledgeBase
    from app.models.document_version import DocumentVersion
    from app.models.document_chunk import DocumentChunk
    from app.models.document_tag import DocumentTag


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_organization_id", "organization_id"),
        Index("ix_documents_workspace_id", "workspace_id"),
        Index("ix_documents_folder_id", "folder_id"),
        Index("ix_documents_knowledge_base_id", "knowledge_base_id"),
        Index("ix_documents_checksum", "checksum"),
        Index("ix_documents_status", "status"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.users.id", ondelete="SET NULL"),
        nullable=False,
    )
    folder_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.folders.id", ondelete="SET NULL"),
        nullable=True,
    )
    knowledge_base_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.knowledge_bases.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_path: Mapped[str] = mapped_column(
        String(2048), nullable=False,
        comment="Supabase Storage path within the bucket",
    )
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending", server_default="pending",
        comment="One of: pending, processing, processed, failed",
    )
    checksum: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="SHA-256 hash of the original file bytes to prevent duplication",
    )
    current_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1",
    )
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship("Organization")
    workspace: Mapped["Workspace"] = relationship("Workspace")
    uploader: Mapped["User"] = relationship("User")
    folder: Mapped[Optional["Folder"]] = relationship("Folder", back_populates="documents")
    knowledge_base: Mapped[Optional["KnowledgeBase"]] = relationship("KnowledgeBase", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion", back_populates="document", cascade="all, delete-orphan",
    )
    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan",
    )
    document_tags: Mapped[List["DocumentTag"]] = relationship(
        "DocumentTag", back_populates="document", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} title={self.title!r} version={self.current_version}>"
