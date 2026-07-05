"""
app/repositories/user_repository.py
─────────────────────────────────────────────────────────────────────────────
Data access layer for the User model.

Repository pattern: all raw SQL / ORM queries live here.
No business logic. No HTTP concerns. No Pydantic schemas.
Services call repositories; routes call services.

The session is always injected — never imported directly.
This makes every method trivially testable with an in-memory DB.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """CRUD operations for the User model."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._db.get(User, user_id)

    def get_by_supabase_id(self, supabase_user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.supabase_user_id == supabase_user_id)
        return self._db.scalar(stmt)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower().strip())
        return self._db.scalar(stmt)

    def list_active(self, limit: int = 100, offset: int = 0) -> Sequence[User]:
        stmt = (
            select(User)
            .where(User.is_active == True)  # noqa: E712
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self._db.scalars(stmt).all()

    # ── Write ─────────────────────────────────────────────────────────────────

    def create(
        self,
        *,
        supabase_user_id: uuid.UUID,
        email: str,
        full_name: str | None = None,
        avatar_url: str | None = None,
        role: str = "member",
    ) -> User:
        user = User(
            supabase_user_id=supabase_user_id,
            email=email.lower().strip(),
            full_name=full_name,
            avatar_url=avatar_url,
            role=role,
        )
        self._db.add(user)
        self._db.flush()   # get DB-generated id without committing
        return user

    def update_last_login(self, user: User) -> User:
        user.last_login = datetime.now(tz=timezone.utc)
        self._db.flush()
        return user

    def update_profile(
        self,
        user: User,
        *,
        full_name: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        if full_name is not None:
            user.full_name = full_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        self._db.flush()
        return user

    def update_role(self, user: User, role: str) -> User:
        user.role = role
        self._db.flush()
        return user

    def deactivate(self, user: User) -> User:
        user.is_active = False
        self._db.flush()
        return user

    def reactivate(self, user: User) -> User:
        user.is_active = True
        self._db.flush()
        return user
