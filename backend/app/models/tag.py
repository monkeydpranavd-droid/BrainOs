"""
app/models/tag.py
─────────────────────────────────────────────────────────────────────────────
Tag model for organization-wide document categorization.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.document_tag import DocumentTag


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_tags_org_name"),
        Index("ix_tags_organization_id", "organization_id"),
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
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    color: Mapped[str] = mapped_column(
        String(16), nullable=False, default="#6366F1", server_default="#6366F1",
        comment="Hex color code for tags (e.g., '#6366F1')",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship("Organization")
    document_tags: Mapped[List["DocumentTag"]] = relationship(
        "DocumentTag", back_populates="tag", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Tag name={self.name!r} org={self.organization_id}>"
