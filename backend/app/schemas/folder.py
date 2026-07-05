"""
app/schemas/folder.py
─────────────────────────────────────────────────────────────────────────────
Pydantic schemas for Folder models.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FolderCreate(BaseModel):
    organization_id: uuid.UUID
    workspace_id: uuid.UUID
    parent_folder_id: Optional[uuid.UUID] = None
    name: str = Field(..., max_length=256)


class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=256)


class FolderResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    workspace_id: uuid.UUID
    parent_folder_id: Optional[uuid.UUID]
    name: str
    path: str
    created_at: datetime

    model_config = {"from_attributes": True}
