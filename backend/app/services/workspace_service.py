"""
app/services/workspace_service.py
─────────────────────────────────────────────────────────────────────────────
Service layer for Workspace and membership business logic.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    WorkspaceNotFoundError,
    InsufficientPermissionsError,
    AlreadyMemberError,
)
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.audit_repository import AuditRepository


class WorkspaceService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._ws_repo = WorkspaceRepository(db)
        self._member_repo = MemberRepository(db)
        self._audit_repo = AuditRepository(db)

    def create_workspace(
        self,
        organization_id: uuid.UUID,
        name: str,
        created_by: uuid.UUID,
        description: Optional[str] = None,
        visibility: str = "private",
        commit: bool = True,
    ) -> Workspace:
        # Create workspace
        ws = self._ws_repo.create(
            organization_id=organization_id,
            name=name,
            created_by=created_by,
            description=description,
            visibility=visibility,
        )

        # Creator automatically becomes Workspace 'owner' member
        self._member_repo.add_workspace_member(
            ws_id=ws.id,
            user_id=created_by,
            role="owner",
        )

        # Log Audit event
        self._audit_repo.create(
            organization_id=organization_id,
            user_id=created_by,
            action="Workspace Created",
            entity_type="workspace",
            entity_id=str(ws.id),
            action_metadata={"name": name, "visibility": visibility},
        )

        if commit:
            self._db.commit()
            self._db.refresh(ws)
        else:
            self._db.flush()
        return ws

    def get_workspace(self, ws_id: uuid.UUID) -> Workspace:
        ws = self._ws_repo.get_by_id(ws_id)
        if not ws:
            raise WorkspaceNotFoundError()
        return ws

    def get_workspace_in_org(self, ws_id: uuid.UUID, org_id: uuid.UUID) -> Workspace:
        ws = self._ws_repo.get_by_id_and_org(ws_id, org_id)
        if not ws:
            raise WorkspaceNotFoundError()
        return ws

    def update_workspace(
        self,
        ws_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> Workspace:
        ws = self.get_workspace_in_org(ws_id, org_id)

        if name is not None:
            ws.name = name
        if description is not None:
            ws.description = description
        if visibility is not None:
            ws.visibility = visibility

        self._ws_repo.update(ws)

        # Log Audit event
        self._audit_repo.create(
            organization_id=org_id,
            user_id=user_id,
            action="Workspace Updated",
            entity_type="workspace",
            entity_id=str(ws.id),
        )

        self._db.commit()
        self._db.refresh(ws)
        return ws

    def delete_workspace(self, ws_id: uuid.UUID, org_id: uuid.UUID, user_id: uuid.UUID) -> None:
        ws = self.get_workspace_in_org(ws_id, org_id)
        
        self._ws_repo.delete(ws)

        # Log Audit event
        self._audit_repo.create(
            organization_id=org_id,
            user_id=user_id,
            action="Workspace Deleted",
            entity_type="workspace",
            entity_id=str(ws_id),
            action_metadata={"name": ws.name},
        )

        self._db.commit()

    def add_workspace_member(
        self,
        ws_id: uuid.UUID,
        org_id: uuid.UUID,
        target_user_id: uuid.UUID,
        role: str,
        user_id: uuid.UUID,
    ) -> WorkspaceMember:
        # Verify workspace exists in org
        ws = self.get_workspace_in_org(ws_id, org_id)

        # Check if already a member
        existing = self._member_repo.get_workspace_member(ws_id, target_user_id)
        if existing:
            raise AlreadyMemberError("User is already a member of this workspace.")

        # Create member link
        member = self._member_repo.add_workspace_member(
            ws_id=ws_id,
            user_id=target_user_id,
            role=role,
        )

        # Log Audit event
        self._audit_repo.create(
            organization_id=org_id,
            user_id=user_id,
            action="Workspace Member Added",
            entity_type="workspace_member",
            entity_id=str(target_user_id),
            action_metadata={"workspace_id": str(ws_id), "role": role},
        )

        self._db.commit()
        return member

    def remove_workspace_member(
        self,
        ws_id: uuid.UUID,
        org_id: uuid.UUID,
        target_user_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        # Verify workspace exists in org
        self.get_workspace_in_org(ws_id, org_id)

        # Get workspace member link
        member = self._member_repo.get_workspace_member(ws_id, target_user_id)
        if not member:
            raise WorkspaceNotFoundError("User is not a member of this workspace.")

        self._member_repo.remove_workspace_member(member)

        # Log Audit event
        self._audit_repo.create(
            organization_id=org_id,
            user_id=user_id,
            action="Workspace Member Removed",
            entity_type="workspace_member",
            entity_id=str(target_user_id),
            action_metadata={"workspace_id": str(ws_id)},
        )

        self._db.commit()

    def list_workspaces_for_user(self, user_id: uuid.UUID, org_id: uuid.UUID) -> Sequence[Workspace]:
        return self._ws_repo.list_for_user_in_org(user_id, org_id)

    def list_all_user_workspaces(self, user_id: uuid.UUID) -> Sequence[Workspace]:
        return self._ws_repo.list_all_for_user(user_id)
