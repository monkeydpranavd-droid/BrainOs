"""
app/schemas/auth.py — Python 3.9 compatible
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    role: Optional[str] = None
    aud: Optional[Union[str, List[str]]] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    app_metadata: Optional[Dict] = None
    user_metadata: Optional[Dict] = None

    @property
    def user_uuid(self) -> uuid.UUID:
        return uuid.UUID(self.sub)


class SessionInfo(BaseModel):
    supabase_user_id: uuid.UUID
    email: Optional[str]
    role: Optional[str]
    issued_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_valid: bool = True


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully."
