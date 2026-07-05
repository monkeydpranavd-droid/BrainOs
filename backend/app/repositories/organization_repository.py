"""
app/repositories/organization_repository.py
─────────────────────────────────────────────────────────────────────────────
Repository for database access related to Organizations.
"""

from __future__ import annotations

import uuid
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, org_id: uuid.UUID) -> Optional[Organization]:
        return self._db.get(Organization, org_id)

    def get_by_slug(self, slug: str) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.slug == slug.lower().strip())
        return self._db.scalar(stmt)

    def create(
        self,
        name: str,
        slug: str,
        logo_url: Optional[str] = None,
        industry: Optional[str] = None,
        website: Optional[str] = None,
        description: Optional[str] = None,
        plan: str = "free",
        status: str = "active",
    ) -> Organization:
        org = Organization(
            name=name,
            slug=slug.lower().strip(),
            logo_url=logo_url,
            industry=industry,
            website=website,
            description=description,
            plan=plan,
            status=status,
        )
        self._db.add(org)
        self._db.flush()
        return org

    def update(self, org: Organization) -> Organization:
        self._db.flush()
        return org

    def delete(self, org: Organization) -> None:
        self._db.delete(org)
        self._db.flush()

    def list_for_user(self, user_id: uuid.UUID) -> Sequence[Organization]:
        stmt = (
            select(Organization)
            .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
            .where(OrganizationMember.user_id == user_id)
            .where(Organization.status != "deleted")
        )
        return self._db.scalars(stmt).all()
