"""
app/schemas/document.py
─────────────────────────────────────────────────────────────────────────────
Pydantic schemas for Document, DocumentVersion, and DocumentChunk models.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, Field

from app.schemas.tag import TagResponse


class DocumentChunkResponse(BaseModel):
    id: uuid.UUID
    chunk_index: int
    content: str
    page: Optional[int]
    token_count: int
    embedding_status: str

    model_config = {"from_attributes": True}


class DocumentVersionResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    version: int
    storage_path: str
    checksum: str
    uploaded_by: uuid.UUID
    change_notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    workspace_id: uuid.UUID
    uploaded_by: uuid.UUID
    folder_id: Optional[uuid.UUID]
    knowledge_base_id: Optional[uuid.UUID]
    title: str
    description: Optional[str]
    original_filename: str
    storage_path: str
    mime_type: str
    file_size: int
    status: str
    checksum: str
    current_version: int
    summary: Optional[str]
    language: Optional[str]
    page_count: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    # Optional loaded fields
    versions: Optional[List[DocumentVersionResponse]] = None
    chunks: Optional[List[DocumentChunkResponse]] = None
    tags: Optional[List[TagResponse]] = None

    model_config = {"from_attributes": True}


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=512)
    description: Optional[str] = None
    folder_id: Optional[uuid.UUID] = None
    knowledge_base_id: Optional[uuid.UUID] = None
    summary: Optional[str] = None
    language: Optional[str] = Field(None, max_length=32)
