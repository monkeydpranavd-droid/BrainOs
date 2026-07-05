"""
app/api/routes/chat.py
─────────────────────────────────────────────────────────────────────────────
API routes for chat conversation memory and RAG semantic searches.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, status, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import get_current_user
from app.schemas.user import CurrentUser
from app.schemas.chat import (
    NewConversationRequest,
    ConversationResponse,
    ChatMessageResponse,
    ChatQueryRequest,
    ChatResponse
)
from app.services.llm.ChatService import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/new",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new chat conversation thread",
)
def create_conversation(
    payload: NewConversationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationResponse:
    service = ChatService(db)
    convo = service.create_conversation(payload.organization_id, payload.workspace_id, payload.title)
    return ConversationResponse.model_validate(convo)


@router.get(
    "/history",
    response_model=List[ConversationResponse],
    summary="Get conversation history in workspace",
)
def get_conversations(
    workspace_id: uuid.UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ConversationResponse]:
    service = ChatService(db)
    convos = service.list_conversations(workspace_id)
    return [ConversationResponse.model_validate(c) for c in convos]


@router.get(
    "/{convo_id}/messages",
    response_model=List[ChatMessageResponse],
    summary="Get message history for a conversation thread",
)
def get_messages(
    convo_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ChatMessageResponse]:
    service = ChatService(db)
    convo = service.get_conversation(convo_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation thread not found")
        
    return [ChatMessageResponse.model_validate(msg) for msg in convo.messages]


@router.delete(
    "/history",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation thread",
)
def delete_conversation(
    conversation_id: uuid.UUID = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service = ChatService(db)
    service.delete_conversation(conversation_id)


@router.post(
    "",
    response_model=ChatResponse,
    summary="Send a message and get grounded RAG response",
)
def chat_query(
    payload: ChatQueryRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    service = ChatService(db)
    try:
        res = service.generate_chat_response(payload.conversation_id, payload.query, payload.document_ids)
        return ChatResponse.model_validate(res)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/stream",
    summary="Stream grounded RAG response using Server-Sent Events (SSE)",
)
def chat_stream(
    payload: ChatQueryRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    service = ChatService(db)
    generator = service.stream_chat_response(payload.conversation_id, payload.query, payload.document_ids)
    return StreamingResponse(generator, media_type="text/event-stream")
