from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from backend.database import get_db
from backend.models import AuditEvent
from backend.auth.rbac import RequireRole

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

class AuditEventResponse(BaseModel):
    id: int
    action: str
    user_id: int | None
    resource_type: str | None
    resource_id: str | None
    ip_address: str | None
    user_agent: str | None
    payload_json: dict | None = None
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

@router.get("/events", response_model=List[AuditEventResponse])
def get_audit_events(limit: int = 100, db: Session = Depends(get_db), current_user = Depends(RequireRole(["admin"]))):
    events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit).all()
    return events
