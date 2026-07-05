"""
app/models/organization.py
─────────────────────────────────────────────────────────────────────────────
Organization is the top-level tenant boundary in BrainOS.

Every piece of data (workspaces, documents, conversations, agents, knowledge)
is scoped under an organization_id. No query ever crosses this boundary.

Design:
  - slug: URL-safe unique identifier (e.g. "acme-corp"). Used in API paths
    and future subdomain routing (acme-corp.brainos.ai).
  - plan: free/pro/enterprise — referenced by billing and feature gates.
  - status: active/suspended/deleted — soft-delete pattern.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.organization_member import OrganizationMember
    from app.models.invitation import Invitation
    from app.models.audit_log import AuditLog


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_organizations_slug"),
        Index("ix_organizations_slug", "slug"),
        Index("ix_organizations_status", "status"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="URL-safe unique identifier. Used in routing and future subdomains.",
    )
    logo_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan: Mapped[str] = mapped_column(
        String(32), nullable=False, default="free", server_default="free",
        comment="One of: free, pro, enterprise",
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="active", server_default="active",
        comment="One of: active, suspended, deleted",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    workspaces: Mapped[List["Workspace"]] = relationship(
        "Workspace", back_populates="organization", cascade="all, delete-orphan",
    )
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="organization", cascade="all, delete-orphan",
    )
    invitations: Mapped[List["Invitation"]] = relationship(
        "Invitation", back_populates="organization", cascade="all, delete-orphan",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="organization", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} slug={self.slug!r} plan={self.plan!r}>"
