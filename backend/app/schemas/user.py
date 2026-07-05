"""
app/schemas/user.py — Python 3.9 compatible
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import auto
from typing import Optional

try:
    from enum import StrEnum
except ImportError:
    # Python < 3.11
    from enum import Enum
    class StrEnum(str, Enum):  # type: ignore[no-redef]
        pass

from pydantic import BaseModel, Field


class UserRole(StrEnum):
    OWNER   = "owner"
    ADMIN   = "admin"
    MEMBER  = "member"
    VIEWER  = "viewer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    model_config = {"from_attributes": True}


class CurrentUser(BaseModel):
    id: uuid.UUID
    supabase_user_id: uuid.UUID
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}

    @property
    def is_admin(self) -> bool:
        return self.role in (UserRole.ADMIN, UserRole.OWNER)

    @property
    def is_owner(self) -> bool:
        return self.role == UserRole.OWNER


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=256)
    avatar_url: Optional[str] = Field(None, max_length=2048)


class AdminUserUpdate(UserUpdate):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
