"""
app/repositories/workspace_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for database access related to Workspaces.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember


class WorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, ws_id: uuid.UUID) -> Optional[Workspace]:
        return self._db.get(Workspace, ws_id)

    def get_by_id_and_org(self, ws_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Workspace]:
        stmt = select(Workspace).where(Workspace.id == ws_id).where(Workspace.organization_id == org_id)
        return self._db.scalar(stmt)

    def create(
        self,
        organization_id: uuid.UUID,
        name: str,
        created_by: uuid.UUID,
        description: Optional[str] = None,
        visibility: str = "private",
    ) -> Workspace:
        ws = Workspace(
            organization_id=organization_id,
            name=name,
            description=description,
            visibility=visibility,
            created_by=created_by,
        )
        self._db.add(ws)
        self._db.flush()
        return ws

    def update(self, ws: Workspace) -> Workspace:
        self._db.flush()
        return ws

    def delete(self, ws: Workspace) -> None:
        self._db.delete(ws)
        self._db.flush()

    def list_by_org(self, org_id: uuid.UUID) -> Sequence[Workspace]:
        stmt = select(Workspace).where(Workspace.organization_id == org_id)
        return self._db.scalars(stmt).all()

    def list_for_user_in_org(self, user_id: uuid.UUID, org_id: uuid.UUID) -> Sequence[Workspace]:
        # A user can view a workspace if:
        # 1. It is public within the organization.
        # 2. Or the user is an explicit member of the workspace.
        stmt = (
            select(Workspace)
            .outerjoin(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(Workspace.organization_id == org_id)
            .where(
                or_(
                    Workspace.visibility == "public",
                    WorkspaceMember.user_id == user_id,
                )
            )
            .distinct()
        )
        return self._db.scalars(stmt).all()

    def list_all_for_user(self, user_id: uuid.UUID) -> Sequence[Workspace]:
        # Workspaces across all orgs that this user is a member of, or public workspaces in orgs the user is a member of
        # Wait, let's simplify to: workspaces where user is explicitly a member.
        stmt = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
        )
        return self._db.scalars(stmt).all()
