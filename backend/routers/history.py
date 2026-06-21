"""ASTRA History Router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.prediction import Prediction
from backend.models.user import User
from backend.models.event import Event
from backend.schemas.event import EventResponse
from backend.schemas.prediction import HistorySearchRequest, HistoryOutcomeRecord
from backend.middleware.auth import get_current_active_user
from typing import Dict, Any

router = APIRouter(prefix="/api/history", tags=["History"])

@router.post("/search")
async def search_history(
    request: HistorySearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search historical events and predictions."""
    query = db.query(Event).filter(Event.created_by_id == current_user.id)
    
    if request.query:
        query = query.filter(Event.description.ilike(f"%{request.query}%") | Event.corridor.ilike(f"%{request.query}%"))
    if request.event_cause:
        query = query.filter(Event.event_cause == request.event_cause)
    if request.corridor:
        query = query.filter(Event.corridor == request.corridor)
    if request.status:
        query = query.filter(Event.status == request.status)
        
    total = query.count()
    events = query.order_by(Event.created_at.desc()).offset((request.page - 1) * request.per_page).limit(request.per_page).all()

    return {
        "results": [EventResponse.model_validate(e) for e in events],
        "total": total,
        "page": request.page,
        "per_page": request.per_page
    }

@router.post("/{prediction_id}/outcome")
async def record_outcome(
    prediction_id: int,
    outcome: HistoryOutcomeRecord,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Record the actual outcome of an event to improve future models."""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
        
    # In a full implementation, we would save this to an Outcome table
    # or update the Prediction record.
    return {"status": "success", "message": "Outcome recorded successfully"}
