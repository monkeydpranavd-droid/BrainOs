"""
app/models/document_chunk.py
─────────────────────────────────────────────────────────────────────────────
DocumentChunk model representing individual chunks of parsed document text.
Prepares the database for future vector storage and semantic search.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional, Dict

from sqlalchemy import ForeignKey, Index, Integer, String, Text, JSON, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.document import Document


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        Index("ix_document_chunks_document_id", "document_id"),
        Index("ix_document_chunks_embedding_status", "embedding_status"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()"),
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    chunk_metadata: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    embedding_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending", server_default="pending",
        comment="One of: pending, processing, completed, failed",
    )
    
    from pgvector.sqlalchemy import Vector
    embedding: Mapped[Optional[list]] = mapped_column(Vector(1536), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk doc={self.document_id} index={self.chunk_index}>"
