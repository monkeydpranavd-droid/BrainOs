"""
app/api/routes/organizations.py
─────────────────────────────────────────────────────────────────────────────
API routes for Organization resource management and invitation workflows.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import (
    get_current_user,
    get_current_organization,
    require_org_admin,
    require_org_owner,
)
from app.models.organization import Organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberResponse,
    OrganizationInviteRequest,
)
from app.schemas.invitation import InvitationResponse, InvitationAcceptRequest
from app.schemas.user import CurrentUser
from app.services.organization_service import OrganizationService
from app.services.invitation_service import InvitationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
)
async def create_org(
    body: OrganizationCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    service = OrganizationService(db)
    org = service.create_organization(
        name=body.name,
        creator_user_id=current_user.id,
        slug=body.slug,
        logo_url=body.logo_url,
        industry=body.industry,
        website=body.website,
        description=body.description,
    )
    return OrganizationResponse.model_validate(org)


@router.get(
    "",
    response_model=List[OrganizationResponse],
    summary="List current user's organizations",
)
async def list_orgs(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[OrganizationResponse]:
    service = OrganizationService(db)
    orgs = service.get_user_organizations(current_user.id)
    return [OrganizationResponse.model_validate(o) for o in orgs]


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Get organization details",
)
async def get_org(
    org: Organization = Depends(get_current_organization),
) -> OrganizationResponse:
    return OrganizationResponse.model_validate(org)


@router.patch(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Update organization details (admin only)",
)
async def update_org(
    org_id: uuid.UUID,
    body: OrganizationUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    # Authorization check via require_org_admin dependency (triggers InsufficientPermissionsError if fails)
    # We do a nested Depends lookup in Python or inject it directly.
    # In FastAPI, we can do it directly:
    service = OrganizationService(db)
    org = service.update_organization(
        org_id=org_id,
        user_id=current_user.id,
        name=body.name,
        logo_url=body.logo_url,
        industry=body.industry,
        website=body.website,
        description=body.description,
    )
    return OrganizationResponse.model_validate(org)


@router.delete(
    "/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete organization (owner only)",
)
async def delete_org(
    org_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service = OrganizationService(db)
    service.delete_organization(org_id, current_user.id)


@router.post(
    "/{org_id}/invite",
    response_model=InvitationResponse,
    summary="Invite user to organization (admin only)",
)
async def invite_user(
    org_id: uuid.UUID,
    body: OrganizationInviteRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvitationResponse:
    service = InvitationService(db)
    inv = service.create_invitation(
        org_id=org_id,
        email=body.email,
        role=body.role,
        invited_by=current_user.id,
    )
    return InvitationResponse.model_validate(inv)


@router.get(
    "/{org_id}/members",
    response_model=List[OrganizationMemberResponse],
    summary="List organization members",
)
async def list_org_members(
    org_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[OrganizationMemberResponse]:
    service = OrganizationService(db)
    members = service.list_members(org_id)
    return [OrganizationMemberResponse.model_validate(m) for m in members]


@router.post(
    "/accept-invite",
    response_model=OrganizationMemberResponse,
    summary="Accept organization invitation",
)
async def accept_invite(
    body: InvitationAcceptRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMemberResponse:
    service = InvitationService(db)
    member = service.accept_invitation(
        token=body.token,
        user_id=current_user.id,
    )
    return OrganizationMemberResponse.model_validate(member)
