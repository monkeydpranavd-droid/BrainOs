"""
app/services/knowledge_base_service.py
─────────────────────────────────────────────────────────────────────────────
Service layer for KnowledgeBase business logic.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFoundError
from app.models.knowledge_base import KnowledgeBase
from app.repositories.knowledge_repository import KnowledgeRepository


class KnowledgeBaseService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = KnowledgeRepository(db)

    def create_knowledge_base(
        self,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        visibility: str = "private",
    ) -> KnowledgeBase:
        kb = self._repo.create(
            organization_id=organization_id,
            workspace_id=workspace_id,
            name=name,
            description=description,
            visibility=visibility,
        )
        self._db.commit()
        return kb

    def get_knowledge_base(self, kb_id: uuid.UUID) -> KnowledgeBase:
        kb = self._repo.get_by_id(kb_id)
        if not kb:
            raise UserNotFoundError("KnowledgeBase not found")
        return kb

    def update_knowledge_base(
        self,
        kb_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> KnowledgeBase:
        kb = self.get_knowledge_base(kb_id)
        if name is not None:
            kb.name = name
        if description is not None:
            kb.description = description
        if visibility is not None:
            kb.visibility = visibility

        self._repo.update(kb)
        self._db.commit()
        self._db.refresh(kb)
        return kb

    def delete_knowledge_base(self, kb_id: uuid.UUID) -> None:
        kb = self.get_knowledge_base(kb_id)
        self._repo.delete(kb)
        self._db.commit()

    def list_knowledge_bases(self, workspace_id: uuid.UUID) -> Sequence[KnowledgeBase]:
        return self._repo.list_by_workspace(workspace_id)
