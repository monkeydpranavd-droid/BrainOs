"""
app/schemas/knowledge_base.py
─────────────────────────────────────────────────────────────────────────────
Pydantic schemas for KnowledgeBase models.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        pass


class KBVisibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class KnowledgeBaseCreate(BaseModel):
    organization_id: uuid.UUID
    workspace_id: uuid.UUID
    name: str = Field(..., max_length=256)
    description: Optional[str] = None
    visibility: KBVisibility = KBVisibility.PRIVATE


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = None
    visibility: Optional[KBVisibility] = None


class KnowledgeBaseResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: Optional[str]
    visibility: str
    created_at: datetime

    model_config = {"from_attributes": True}
