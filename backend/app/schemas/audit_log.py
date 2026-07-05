"""
app/schemas/audit_log.py
─────────────────────────────────────────────────────────────────────────────
Pydantic schemas for AuditLog model.
Compatible with Python 3.9.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    action: str
    entity_type: str
    entity_id: Optional[str]
    action_metadata: Optional[Dict]
    created_at: datetime

    model_config = {"from_attributes": True}
