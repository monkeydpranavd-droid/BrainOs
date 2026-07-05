"""
app/services/invitation_service.py
─────────────────────────────────────────────────────────────────────────────
Service layer for Invitation business logic.
"""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Sequence, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    InvitationNotFoundError,
    AlreadyMemberError,
)
from app.models.invitation import Invitation
from app.models.organization_member import OrganizationMember
from app.repositories.invitation_repository import InvitationRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository


class InvitationService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._inv_repo = InvitationRepository(db)
        self._member_repo = MemberRepository(db)
        self._audit_repo = AuditRepository(db)
        self._user_repo = UserRepository(db)

    def create_invitation(
        self,
        org_id: uuid.UUID,
        email: str,
        role: str,
        invited_by: uuid.UUID,
    ) -> Invitation:
        # Check if user is already a member
        email = email.lower().strip()
        user = self._user_repo.get_by_email(email)
        if user:
            member = self._member_repo.get_org_member(org_id, user.id)
            if member:
                raise AlreadyMemberError("User with this email is already a member.")

        # Check for existing active pending invitation
        existing = self._inv_repo.get_by_org_and_email(org_id, email)
        if existing and existing.status == "pending" and existing.expires_at > datetime.now(timezone.utc):
            existing.status = "revoked"
            self._inv_repo.update(existing)

        # Generate unique secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        # Create invitation
        inv = self._inv_repo.create(
            organization_id=org_id,
            email=email,
            role=role,
            token=token,
            expires_at=expires_at,
            invited_by=invited_by,
        )

        # Log Audit event
        self._audit_repo.create(
            organization_id=org_id,
            user_id=invited_by,
            action="Invitation Sent",
            entity_type="invitation",
            entity_id=str(inv.id),
            action_metadata={"email": email, "role": role},
        )

        self._db.commit()
        return inv

    def accept_invitation(self, token: str, user_id: uuid.UUID) -> OrganizationMember:
        inv = self._inv_repo.get_by_token(token)
        if not inv or inv.status != "pending":
            raise InvitationNotFoundError("Invitation is invalid or has already been used.")

        if inv.expires_at < datetime.now(timezone.utc):
            inv.status = "expired"
            self._inv_repo.update(inv)
            self._db.commit()
            raise InvitationNotFoundError("Invitation has expired.")

        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise InvitationNotFoundError("User not found.")

        # Check if already org member
        existing_member = self._member_repo.get_org_member(inv.organization_id, user.id)
        if existing_member:
            inv.status = "accepted"
            self._inv_repo.update(inv)
            self._db.commit()
            raise AlreadyMemberError("You are already a member of this organization.")

        # Add member to organization
        member = self._member_repo.add_org_member(
            org_id=inv.organization_id,
            user_id=user.id,
            role=inv.role,
            invited_by=inv.invited_by,
        )

        # Update status
        inv.status = "accepted"
        self._inv_repo.update(inv)

        # Log Audit event
        self._audit_repo.create(
            organization_id=inv.organization_id,
            user_id=user.id,
            action="Member Added",
            entity_type="organization_member",
            entity_id=str(user.id),
            action_metadata={"role": inv.role, "invited_by": str(inv.invited_by) if inv.invited_by else None},
        )

        self._db.commit()
        return member

    def list_invitations(self, org_id: uuid.UUID) -> Sequence[Invitation]:
        return self._inv_repo.list_by_org(org_id)
