"""
app/schemas/organization.py
─────────────────────────────────────────────────────────────────────────────
Pydantic schemas for Organization and OrganizationMember models.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr

try:
    from enum import StrEnum
except ImportError:
    # Python < 3.11
    class StrEnum(str, Enum):
        pass


class OrgRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class OrgPlan(StrEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class OrgStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class OrganizationCreate(BaseModel):
    name: str = Field(..., max_length=256)
    slug: Optional[str] = Field(None, max_length=64)
    logo_url: Optional[str] = Field(None, max_length=2048)
    industry: Optional[str] = Field(None, max_length=128)
    website: Optional[str] = Field(None, max_length=2048)
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=256)
    logo_url: Optional[str] = Field(None, max_length=2048)
    industry: Optional[str] = Field(None, max_length=128)
    website: Optional[str] = Field(None, max_length=2048)
    description: Optional[str] = None
    plan: Optional[OrgPlan] = None
    status: Optional[OrgStatus] = None


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    logo_url: Optional[str]
    industry: Optional[str]
    website: Optional[str]
    description: Optional[str]
    plan: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrganizationMemberResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role: OrgRole
    invited_by: Optional[uuid.UUID]
    joined_at: datetime

    model_config = {"from_attributes": True}


class OrganizationInviteRequest(BaseModel):
    email: EmailStr
    role: OrgRole = OrgRole.MEMBER
