"""
app/models/document_tag.py
─────────────────────────────────────────────────────────────────────────────
Junction table mapping Documents to Tags.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.tag import Tag


class DocumentTag(Base):
    __tablename__ = "document_tags"
    __table_args__ = (
        UniqueConstraint("document_id", "tag_id", name="uq_document_tags_doc_tag"),
        Index("ix_document_tags_document_id", "document_id"),
        Index("ix_document_tags_tag_id", "tag_id"),
        {"schema": "public"},
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.tags.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    document: Mapped["Document"] = relationship("Document", back_populates="document_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="document_tags")

    def __repr__(self) -> str:
        return f"<DocumentTag doc={self.document_id} tag={self.tag_id}>"
