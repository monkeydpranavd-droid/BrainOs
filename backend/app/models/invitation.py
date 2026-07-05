"""
app/models/invitation.py
─────────────────────────────────────────────────────────────────────────────
Organization invitation model.

Flow:
  1. Admin creates invitation (email + role + token + expiry)
  2. System emails the token URL (placeholder — email service plugs in here)
  3. Invited user clicks link → backend validates token → OrganizationMember created
  4. Invitation status → accepted

Token is a secrets.token_urlsafe(32) value, stored hashed in production.
For now we store it plain (dev mode) — hash it before production.
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


class Invitation(Base):
    __tablename__ = "invitations"
    __table_args__ = (
        UniqueConstraint("token", name="uq_invitations_token"),
        Index("ix_invitations_organization_id", "organization_id"),
        Index("ix_invitations_email", "email"),
        Index("ix_invitations_status", "status"),
        Index("ix_invitations_token", "token"),
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
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    role: Mapped[str] = mapped_column(
        String(32), nullable=False, default="member", server_default="member",
        comment="Role the invited user will receive on acceptance.",
    )
    token: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="One-time token sent in the invitation email.",
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending", server_default="pending",
        comment="One of: pending, accepted, expired, revoked",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        comment="UTC datetime when this invitation can no longer be accepted.",
    )
    invited_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="invitations",
    )
    inviter: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<Invitation org={self.organization_id} "
            f"email={self.email!r} status={self.status!r}>"
        )
