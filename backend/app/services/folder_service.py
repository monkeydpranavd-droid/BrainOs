"""
app/services/folder_service.py
─────────────────────────────────────────────────────────────────────────────
Service layer for Folder hierarchical organization business logic.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFoundError
from app.models.folder import Folder
from app.repositories.folder_repository import FolderRepository


class FolderService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = FolderRepository(db)

    def create_folder(
        self,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        name: str,
        parent_folder_id: Optional[uuid.UUID] = None,
    ) -> Folder:
        # Determine path path
        if parent_folder_id:
            parent = self._repo.get_by_id(parent_folder_id)
            if not parent:
                raise UserNotFoundError("Parent folder not found")
            path = f"{parent.path}/{name.strip()}"
        else:
            path = f"/{name.strip()}"

        folder = self._repo.create(
            organization_id=organization_id,
            workspace_id=workspace_id,
            name=name.strip(),
            path=path,
            parent_folder_id=parent_folder_id,
        )
        self._db.commit()
        return folder

    def get_folder(self, folder_id: uuid.UUID) -> Folder:
        folder = self._repo.get_by_id(folder_id)
        if not folder:
            raise UserNotFoundError("Folder not found")
        return folder

    def list_folders(self, workspace_id: uuid.UUID) -> Sequence[Folder]:
        return self._repo.list_by_workspace(workspace_id)
