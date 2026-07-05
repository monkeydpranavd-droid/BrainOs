"""
app/services/organization_service.py
─────────────────────────────────────────────────────────────────────────────
Service layer for Organization and membership business logic.
"""

from __future__ import annotations

import re
import uuid
from typing import Sequence, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    OrganizationNotFoundError,
    OrganizationSlugTakenError,
)
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.audit_repository import AuditRepository


def slugify(text: str) -> str:
    """Simple slugify implementation for URL-safe slugs."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


class OrganizationService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._org_repo = OrganizationRepository(db)
        self._member_repo = MemberRepository(db)
        self._audit_repo = AuditRepository(db)

    def create_organization(
        self,
        name: str,
        creator_user_id: uuid.UUID,
        slug: Optional[str] = None,
        logo_url: Optional[str] = None,
        industry: Optional[str] = None,
        website: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Organization:
        # Generate slug if not provided
        org_slug = slugify(slug or name)
        if not org_slug:
            org_slug = "org-" + str(uuid.uuid4())[:8]

        # Check for slug uniqueness
        existing = self._org_repo.get_by_slug(org_slug)
        if existing:
            raise OrganizationSlugTakenError(f"Slug '{org_slug}' is already taken.")

        # Create organization
        org = self._org_repo.create(
            name=name,
            slug=org_slug,
            logo_url=logo_url,
            industry=industry,
            website=website,
            description=description,
        )

        # Creator automatically becomes Organization 'owner'
        self._member_repo.add_org_member(
            org_id=org.id,
            user_id=creator_user_id,
            role="owner",
        )

        # Log Audit event
        self._audit_repo.create(
            organization_id=org.id,
            user_id=creator_user_id,
            action="Organization Created",
            entity_type="organization",
            entity_id=str(org.id),
            action_metadata={"name": name, "slug": org_slug},
        )

        self._db.commit()
        self._db.refresh(org)
        return org

    def get_organization(self, org_id: uuid.UUID) -> Organization:
        org = self._org_repo.get_by_id(org_id)
        if not org or org.status == "deleted":
            raise OrganizationNotFoundError()
        return org

    def update_organization(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        name: Optional[str] = None,
        logo_url: Optional[str] = None,
        industry: Optional[str] = None,
        website: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Organization:
        org = self.get_organization(org_id)

        if name is not None:
            org.name = name
        if logo_url is not None:
            org.logo_url = logo_url
        if industry is not None:
            org.industry = industry
        if website is not None:
            org.website = website
        if description is not None:
            org.description = description

        self._org_repo.update(org)

        # Log Audit event
        self._audit_repo.create(
            organization_id=org.id,
            user_id=user_id,
            action="Organization Updated",
            entity_type="organization",
            entity_id=str(org.id),
            action_metadata={"name": name} if name else None,
        )

        self._db.commit()
        self._db.refresh(org)
        return org

    def delete_organization(self, org_id: uuid.UUID, user_id: uuid.UUID) -> None:
        org = self.get_organization(org_id)
        
        # Soft delete by setting status
        org.status = "deleted"
        self._org_repo.update(org)

        # Log Audit event
        self._audit_repo.create(
            organization_id=org.id,
            user_id=user_id,
            action="Organization Deleted",
            entity_type="organization",
            entity_id=str(org.id),
        )

        self._db.commit()

    def get_user_organizations(self, user_id: uuid.UUID) -> Sequence[Organization]:
        return self._org_repo.list_for_user(user_id)

    def list_members(self, org_id: uuid.UUID) -> Sequence[OrganizationMember]:
        # Verify organization exists
        self.get_organization(org_id)
        return self._member_repo.list_org_members(org_id)
