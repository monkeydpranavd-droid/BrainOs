"""
app/schemas/invitation.py
─────────────────────────────────────────────────────────────────────────────
Pydantic schemas for Invitation model.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr

try:
    from enum import StrEnum
except ImportError:
    # Python < 3.11
    class StrEnum(str, Enum):
        pass


class InvitationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class InvitationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: EmailStr
    role: str
    token: str
    status: str
    expires_at: datetime
    invited_by: Optional[uuid.UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class InvitationAcceptRequest(BaseModel):
    token: str
