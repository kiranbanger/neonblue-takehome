"""
Events router for the experimentation platform
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models import Event
from app.auth import verify_token
from app.database import get_db

router = APIRouter(prefix="/events", tags=["events"])


class EventInput(BaseModel):
    """Event input model"""
    user_id: str
    type: str
    timestamp: str
    properties: Optional[Dict[str, Any]] = None


@router.post("/", status_code=201)
async def record_event(
    data: EventInput,
    client_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Record an event"""
    
    try:
        # Parse timestamp
        event_timestamp = datetime.fromisoformat(data.timestamp)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid timestamp format. Use ISO format (e.g., 2025-10-24T04:31:32.819790)"
        )

    # Create event
    event = Event(
        id=str(uuid.uuid4()),
        user_id=data.user_id,
        client_id=client_id,
        event_type=data.type,
        timestamp=event_timestamp,
        properties=data.properties or {}
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "id": event.id,
        "user_id": event.user_id,
        "client_id": event.client_id,
        "event_type": event.event_type,
        "timestamp": event.timestamp.isoformat(),
        "properties": event.properties,
        "created_at": event.created_at.isoformat(),
        "updated_at": event.updated_at.isoformat()
    }

