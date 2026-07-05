"""
app/schemas/tag.py
─────────────────────────────────────────────────────────────────────────────
Pydantic schemas for Tag models.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=64)
    color: str = Field("#6366F1", max_length=16)


class TagResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    color: str

    model_config = {"from_attributes": True}
