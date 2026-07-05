"""
app/repositories/invitation_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for database access related to Invitations.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invitation import Invitation


class InvitationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, inv_id: uuid.UUID) -> Optional[Invitation]:
        return self._db.get(Invitation, inv_id)

    def get_by_token(self, token: str) -> Optional[Invitation]:
        stmt = select(Invitation).where(Invitation.token == token)
        return self._db.scalar(stmt)

    def get_by_org_and_email(self, org_id: uuid.UUID, email: str) -> Optional[Invitation]:
        stmt = (
            select(Invitation)
            .where(Invitation.organization_id == org_id)
            .where(Invitation.email == email.lower().strip())
        )
        return self._db.scalar(stmt)

    def create(
        self,
        organization_id: uuid.UUID,
        email: str,
        role: str,
        token: str,
        expires_at: datetime,
        invited_by: Optional[uuid.UUID] = None,
    ) -> Invitation:
        inv = Invitation(
            organization_id=organization_id,
            email=email.lower().strip(),
            role=role,
            token=token,
            expires_at=expires_at,
            invited_by=invited_by,
        )
        self._db.add(inv)
        self._db.flush()
        return inv

    def update(self, inv: Invitation) -> Invitation:
        self._db.flush()
        return inv

    def list_by_org(self, org_id: uuid.UUID) -> Sequence[Invitation]:
        stmt = (
            select(Invitation)
            .where(Invitation.organization_id == org_id)
            .order_by(Invitation.created_at.desc())
        )
        return self._db.scalars(stmt).all()
