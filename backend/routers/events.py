"""ASTRA Events Router."""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.event import Event
from backend.models.user import User
from backend.schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from backend.middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("", response_model=EventListResponse)
async def list_events(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    event_cause: Optional[str] = None,
    corridor: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List events with pagination and filtering."""
    query = db.query(Event)
    
    if status:
        query = query.filter(Event.status == status)
    if event_cause:
        query = query.filter(Event.event_cause == event_cause)
    if corridor:
        query = query.filter(Event.corridor == corridor)
    if priority:
        query = query.filter(Event.priority == priority)
        
    total = query.count()
    events = query.order_by(Event.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    return EventListResponse(
        events=[EventResponse.model_validate(e) for e in events],
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("", response_model=EventResponse)
async def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new traffic event."""
    db_event = Event(
        event_type=event_in.event_type,
        event_cause=event_in.event_cause,
        priority=event_in.priority,
        latitude=event_in.latitude,
        longitude=event_in.longitude,
        address=event_in.address,
        corridor=event_in.corridor,
        zone=event_in.zone,
        junction=event_in.junction,
        police_station=event_in.police_station,
        description=event_in.description,
        requires_road_closure=event_in.requires_road_closure,
        start_datetime=event_in.start_datetime,
        end_datetime=event_in.end_datetime,
        vehicle_type=event_in.vehicle_type,
        direction=event_in.direction,
        status="active",
        created_at=datetime.now(timezone.utc),
        created_by_id=current_user.id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return EventResponse.model_validate(db_event)

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get event details by ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse.model_validate(event)

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    update_data = event_in.model_dump(exclude_unset=True)
    
    # If marking as resolved/closed
    if update_data.get("status") in ["resolved", "closed"]:
        if not event.closed_at and "closed_at" not in update_data:
            update_data["closed_at"] = datetime.now(timezone.utc)
            
    for key, value in update_data.items():
        setattr(event, key, value)
        
    db.commit()
    db.refresh(event)
    return EventResponse.model_validate(event)
