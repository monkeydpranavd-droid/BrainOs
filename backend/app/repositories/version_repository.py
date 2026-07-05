"""
app/repositories/version_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for database access related to DocumentVersions.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_version import DocumentVersion


class VersionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, ver_id: uuid.UUID) -> Optional[DocumentVersion]:
        return self._db.get(DocumentVersion, ver_id)

    def create(
        self,
        document_id: uuid.UUID,
        version: int,
        storage_path: str,
        checksum: str,
        uploaded_by: uuid.UUID,
        change_notes: Optional[str] = None,
    ) -> DocumentVersion:
        ver = DocumentVersion(
            document_id=document_id,
            version=version,
            storage_path=storage_path,
            checksum=checksum,
            uploaded_by=uploaded_by,
            change_notes=change_notes,
        )
        self._db.add(ver)
        self._db.flush()
        return ver

    def list_by_document(self, document_id: uuid.UUID) -> Sequence[DocumentVersion]:
        stmt = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version.desc())
        )
        return self._db.scalars(stmt).all()
