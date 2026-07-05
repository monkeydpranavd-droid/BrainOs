"""
app/api/routes/auth.py — Python 3.9 compatible
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import get_current_user
from app.schemas.auth import LogoutResponse, SessionInfo
from app.schemas.user import CurrentUser, UserResponse
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

_bearer = HTTPBearer(auto_error=False)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated user profile",
)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    service = AuthService(db)
    user = service.get_user_by_id(current_user.id)
    return UserResponse.model_validate(user)


@router.get(
    "/session",
    response_model=SessionInfo,
    summary="Get decoded session metadata",
)
async def get_session(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> SessionInfo:
    token_header = f"Bearer {credentials.credentials}" if credentials else None
    service = AuthService(db)
    payload = service.verify_token_from_header(token_header)
    return service.build_session_info(payload)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Server-side logout hook",
)
async def logout(
    current_user: CurrentUser = Depends(get_current_user),
) -> LogoutResponse:
    logger.info("User %s logged out.", current_user.id)
    return LogoutResponse()
