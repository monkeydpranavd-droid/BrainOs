"""
app/repositories/folder_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for database access related to Folders.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.folder import Folder


class FolderRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, folder_id: uuid.UUID) -> Optional[Folder]:
        return self._db.get(Folder, folder_id)

    def get_by_id_and_org(self, folder_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Folder]:
        stmt = select(Folder).where(Folder.id == folder_id).where(Folder.organization_id == org_id)
        return self._db.scalar(stmt)

    def create(
        self,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        name: str,
        path: str,
        parent_folder_id: Optional[uuid.UUID] = None,
    ) -> Folder:
        folder = Folder(
            organization_id=organization_id,
            workspace_id=workspace_id,
            name=name,
            path=path,
            parent_folder_id=parent_folder_id,
        )
        self._db.add(folder)
        self._db.flush()
        return folder

    def update(self, folder: Folder) -> Folder:
        self._db.flush()
        return folder

    def delete(self, folder: Folder) -> None:
        self._db.delete(folder)
        self._db.flush()

    def list_by_workspace(self, workspace_id: uuid.UUID) -> Sequence[Folder]:
        stmt = select(Folder).where(Folder.workspace_id == workspace_id).order_by(Folder.path.asc())
        return self._db.scalars(stmt).all()
