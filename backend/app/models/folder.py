"""
app/models/folder.py
─────────────────────────────────────────────────────────────────────────────
Folder model for hierarchical structure within Workspaces.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.workspace import Workspace
    from app.models.document import Document


class Folder(Base):
    __tablename__ = "folders"
    __table_args__ = (
        Index("ix_folders_organization_id", "organization_id"),
        Index("ix_folders_workspace_id", "workspace_id"),
        Index("ix_folders_parent_folder_id", "parent_folder_id"),
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
    parent_folder_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.folders.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    path: Mapped[str] = mapped_column(
        String(2048), nullable=False,
        comment="Computed or materialized path hierarchy for rapid query (e.g. '/HR/Policies')",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship("Organization")
    workspace: Mapped["Workspace"] = relationship("Workspace")
    parent: Mapped[Optional["Folder"]] = relationship(
        "Folder", remote_side=[id], back_populates="subfolders",
    )
    subfolders: Mapped[List["Folder"]] = relationship(
        "Folder", back_populates="parent", cascade="all, delete-orphan",
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="folder",
    )

    def __repr__(self) -> str:
        return f"<Folder id={self.id} path={self.path!r}>"
