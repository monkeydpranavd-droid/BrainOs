"""
app/repositories/tag_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for database access related to Tags and DocumentTags.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.models.document_tag import DocumentTag


class TagRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, tag_id: uuid.UUID) -> Optional[Tag]:
        return self._db.get(Tag, tag_id)

    def get_by_id_and_org(self, tag_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Tag]:
        stmt = select(Tag).where(Tag.id == tag_id).where(Tag.organization_id == org_id)
        return self._db.scalar(stmt)

    def get_by_name(self, org_id: uuid.UUID, name: str) -> Optional[Tag]:
        stmt = (
            select(Tag)
            .where(Tag.organization_id == org_id)
            .where(Tag.name == name.strip())
        )
        return self._db.scalar(stmt)

    def create(self, organization_id: uuid.UUID, name: str, color: str = "#6366F1") -> Tag:
        tag = Tag(organization_id=organization_id, name=name.strip(), color=color)
        self._db.add(tag)
        self._db.flush()
        return tag

    def delete(self, tag: Tag) -> None:
        self._db.delete(tag)
        self._db.flush()

    def list_by_org(self, org_id: uuid.UUID) -> Sequence[Tag]:
        stmt = select(Tag).where(Tag.organization_id == org_id).order_by(Tag.name.asc())
        return self._db.scalars(stmt).all()

    # ── Document Tags ─────────────────────────────────────────────────────────

    def get_document_tag(self, doc_id: uuid.UUID, tag_id: uuid.UUID) -> Optional[DocumentTag]:
        stmt = (
            select(DocumentTag)
            .where(DocumentTag.document_id == doc_id)
            .where(DocumentTag.tag_id == tag_id)
        )
        return self._db.scalar(stmt)

    def add_tag_to_document(self, doc_id: uuid.UUID, tag_id: uuid.UUID) -> DocumentTag:
        doc_tag = DocumentTag(document_id=doc_id, tag_id=tag_id)
        self._db.add(doc_tag)
        self._db.flush()
        return doc_tag

    def remove_tag_from_document(self, doc_tag: DocumentTag) -> None:
        self._db.delete(doc_tag)
        self._db.flush()

    def list_tags_for_document(self, doc_id: uuid.UUID) -> Sequence[Tag]:
        stmt = (
            select(Tag)
            .join(DocumentTag, DocumentTag.tag_id == Tag.id)
            .where(DocumentTag.document_id == doc_id)
            .order_by(Tag.name.asc())
        )
        return self._db.scalars(stmt).all()
