"""
app/schemas/workspace.py
─────────────────────────────────────────────────────────────────────────────
Pydantic schemas for Workspace and WorkspaceMember models.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field

try:
    from enum import StrEnum
except ImportError:
    # Python < 3.11
    class StrEnum(str, Enum):
        pass


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class WorkspaceVisibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class WorkspaceCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=256)
    description: Optional[str] = None
    visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = None
    visibility: Optional[WorkspaceVisibility] = None


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: Optional[str]
    visibility: str
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceMemberResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    role: WorkspaceRole
    joined_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceMemberAddRequest(BaseModel):
    user_id: uuid.UUID
    role: WorkspaceRole = WorkspaceRole.VIEWER
