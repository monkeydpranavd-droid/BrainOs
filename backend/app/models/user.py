"""
app/models/user.py
─────────────────────────────────────────────────────────────────────────────
SQLAlchemy 2.0 User model — Python 3.9 compatible.

Uses Optional[X] instead of X | None because SQLAlchemy 2.0 evaluates
mapped_column annotations at class creation time, which breaks on Python
3.9 even with `from __future__ import annotations`.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("supabase_user_id", name="uq_users_supabase_user_id"),
        UniqueConstraint("email", name="uq_users_email"),
        Index("ix_users_supabase_user_id", "supabase_user_id"),
        Index("ix_users_email", "email"),
        Index("ix_users_is_active", "is_active"),
        {"schema": "public"},
    )

    # ── Identity ──────────────────────────────────────────────────────────────

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    supabase_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        comment="References auth.users.id in Supabase. Never store credentials here.",
    )

    # ── Profile ───────────────────────────────────────────────────────────────

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    full_name: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(2048),
        nullable=True,
    )

    # ── Access control ────────────────────────────────────────────────────────

    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="member",
        server_default="member",
        comment="One of: owner, admin, member, viewer",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    # ── Timestamps ────────────────────────────────────────────────────────────

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"
