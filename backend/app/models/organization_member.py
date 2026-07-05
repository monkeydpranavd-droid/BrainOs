"""
app/models/organization_member.py
─────────────────────────────────────────────────────────────────────────────
Junction table connecting users to organizations with a role.

A user can belong to many organizations (multi-tenant SaaS pattern).
Role controls what actions they can perform within that organization.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class OrganizationMember(Base):
    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_members_org_user"),
        Index("ix_org_members_organization_id", "organization_id"),
        Index("ix_org_members_user_id", "user_id"),
        Index("ix_org_members_role", "role"),
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
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(32), nullable=False, default="member", server_default="member",
        comment="One of: owner, admin, member, guest",
    )
    invited_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who sent the invitation. NULL if the org creator.",
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="members",
    )
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id],
    )
    inviter: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[invited_by],
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizationMember org={self.organization_id} "
            f"user={self.user_id} role={self.role!r}>"
        )
