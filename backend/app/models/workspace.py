"""
app/models/workspace.py
─────────────────────────────────────────────────────────────────────────────
Workspace is a scoped work area within an organization.

Examples: "Engineering", "Marketing", "Q4 Planning", "Client: Acme".

Future features that are workspace-scoped:
  - Documents, knowledge bases, vector indexes
  - AI Agents and conversations
  - Google Drive / Notion / Slack integrations
  - Workflows and automations
  - MCP tool connections

All future models that belong to a workspace MUST include both
organization_id and workspace_id for fast, indexed tenant filtering.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.workspace_member import WorkspaceMember
    from app.models.user import User


class Workspace(Base):
    __tablename__ = "workspaces"
    __table_args__ = (
        Index("ix_workspaces_organization_id", "organization_id"),
        Index("ix_workspaces_created_by", "created_by"),
        Index("ix_workspaces_visibility", "visibility"),
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
        comment="Tenant key. Every query MUST filter by this.",
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visibility: Mapped[str] = mapped_column(
        String(32), nullable=False, default="private", server_default="private",
        comment="One of: public (org-wide), private (members only)",
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.users.id", ondelete="SET NULL"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="workspaces",
    )
    creator: Mapped["User"] = relationship(
        "User", foreign_keys=[created_by],
    )
    members: Mapped[List["WorkspaceMember"]] = relationship(
        "WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Workspace id={self.id} name={self.name!r} org={self.organization_id}>"
