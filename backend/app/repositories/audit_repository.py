"""
app/repositories/audit_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for database access related to AuditLogs.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID],
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        action_metadata: Optional[Dict] = None,
    ) -> AuditLog:
        log = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            action_metadata=action_metadata,
        )
        self._db.add(log)
        self._db.flush()
        return log

    def list_by_org(self, org_id: uuid.UUID, limit: int = 100, offset: int = 0) -> Sequence[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.organization_id == org_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self._db.scalars(stmt).all()
