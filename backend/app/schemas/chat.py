"""
app/schemas/chat.py
─────────────────────────────────────────────────────────────────────────────
Pydantic schemas for Chat Conversations, Message items, and Query requests.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class NewConversationRequest(BaseModel):
    organization_id: uuid.UUID
    workspace_id: uuid.UUID
    title: Optional[str] = "New Conversation"


class ConversationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    token_count: int
    message_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatQueryRequest(BaseModel):
    conversation_id: uuid.UUID
    query: str
    document_ids: Optional[List[uuid.UUID]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
