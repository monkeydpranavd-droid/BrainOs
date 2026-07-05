"""
app/repositories/knowledge_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for database access related to KnowledgeBases.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeBase


class KnowledgeRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, kb_id: uuid.UUID) -> Optional[KnowledgeBase]:
        return self._db.get(KnowledgeBase, kb_id)

    def get_by_id_and_org(self, kb_id: uuid.UUID, org_id: uuid.UUID) -> Optional[KnowledgeBase]:
        stmt = (
            select(KnowledgeBase)
            .where(KnowledgeBase.id == kb_id)
            .where(KnowledgeBase.organization_id == org_id)
        )
        return self._db.scalar(stmt)

    def create(
        self,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        visibility: str = "private",
    ) -> KnowledgeBase:
        kb = KnowledgeBase(
            organization_id=organization_id,
            workspace_id=workspace_id,
            name=name,
            description=description,
            visibility=visibility,
        )
        self._db.add(kb)
        self._db.flush()
        return kb

    def update(self, kb: KnowledgeBase) -> KnowledgeBase:
        self._db.flush()
        return kb

    def delete(self, kb: KnowledgeBase) -> None:
        self._db.delete(kb)
        self._db.flush()

    def list_by_workspace(self, workspace_id: uuid.UUID) -> Sequence[KnowledgeBase]:
        stmt = select(KnowledgeBase).where(KnowledgeBase.workspace_id == workspace_id).order_by(KnowledgeBase.created_at.desc())
        return self._db.scalars(stmt).all()
