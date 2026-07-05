"""
app/repositories/member_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for managing Organization and Workspace membership links.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization_member import OrganizationMember
from app.models.workspace_member import WorkspaceMember


class MemberRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Organization Members ──────────────────────────────────────────────────

    def get_org_member(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Optional[OrganizationMember]:
        stmt = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == org_id)
            .where(OrganizationMember.user_id == user_id)
        )
        return self._db.scalar(stmt)

    def add_org_member(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str = "member",
        invited_by: Optional[uuid.UUID] = None,
    ) -> OrganizationMember:
        member = OrganizationMember(
            organization_id=org_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
        )
        self._db.add(member)
        self._db.flush()
        return member

    def remove_org_member(self, member: OrganizationMember) -> None:
        self._db.delete(member)
        self._db.flush()

    def list_org_members(self, org_id: uuid.UUID) -> Sequence[OrganizationMember]:
        stmt = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == org_id)
            .order_by(OrganizationMember.joined_at.asc())
        )
        return self._db.scalars(stmt).all()

    # ── Workspace Members ─────────────────────────────────────────────────────

    def get_workspace_member(self, ws_id: uuid.UUID, user_id: uuid.UUID) -> Optional[WorkspaceMember]:
        stmt = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == ws_id)
            .where(WorkspaceMember.user_id == user_id)
        )
        return self._db.scalar(stmt)

    def add_workspace_member(
        self,
        ws_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str = "viewer",
    ) -> WorkspaceMember:
        member = WorkspaceMember(
            workspace_id=ws_id,
            user_id=user_id,
            role=role,
        )
        self._db.add(member)
        self._db.flush()
        return member

    def remove_workspace_member(self, member: WorkspaceMember) -> None:
        self._db.delete(member)
        self._db.flush()

    def list_workspace_members(self, ws_id: uuid.UUID) -> Sequence[WorkspaceMember]:
        stmt = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == ws_id)
            .order_by(WorkspaceMember.joined_at.asc())
        )
        return self._db.scalars(stmt).all()
