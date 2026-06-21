"""ASTRA Dashboard Router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from backend.database import get_db
from backend.models.event import Event
from backend.models.prediction import Prediction
from backend.models.user import User
from backend.schemas.prediction import DashboardKPIs
from backend.middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/kpis", response_model=DashboardKPIs)
async def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get aggregated KPIs for the dashboard."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    
    # Active events
    active_events = db.query(Event).filter(Event.status == "active").count()
    
    # Events today & this week
    events_today = db.query(Event).filter(Event.created_at >= today_start).count()
    events_week = db.query(Event).filter(Event.created_at >= week_start).count()
    
    # We don't have officers_deployed natively in DB yet, mock it based on active events
    officers_deployed = active_events * 3
    
    # Calculate real KPIs from DB
    high_risk_events = 0
    avg_risk = 0.0
    avg_res = 0.0
    top_corridors_list = []
    risk_dist = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    
    if active_events > 0:
        # High risk events
        try:
            high_risk_events = db.query(Event).filter(
                Event.status == "active",
                Event.risk_score >= 65
            ).count()
        except Exception:
            high_risk_events = 0
        
        # Average risk score
        avg_risk = db.query(func.avg(Event.risk_score)).filter(Event.status == "active").scalar() or 0.0
        
        # Top corridors by active event count
        corridor_stats = (
            db.query(Event.corridor, func.count(Event.id).label("cnt"))
            .filter(Event.status == "active", Event.corridor.isnot(None))
            .group_by(Event.corridor)
            .order_by(func.count(Event.id).desc())
            .limit(5)
            .all()
        )
        top_corridors_list = [
            {"corridor": c, "active_events": cnt, "stress_score": min(100, cnt * 25)}
            for c, cnt in corridor_stats
        ]
        
    # Calculate avg resolution time for closed/resolved events
    try:
        resolved_events = db.query(Event).filter(
            Event.status.in_(["closed", "resolved"]),
            Event.closed_at.isnot(None),
            Event.created_at.isnot(None)
        ).all()
        
        if resolved_events:
            total_mins = sum((e.closed_at - e.created_at).total_seconds() / 60 for e in resolved_events)
            avg_res = total_mins / len(resolved_events)
    except Exception:
        avg_res = 0.0
    
    return DashboardKPIs(
        active_events=active_events,
        high_risk_events=high_risk_events,
        officers_deployed=officers_deployed,
        avg_risk_score=float(avg_risk),
        events_today=events_today,
        events_this_week=events_week,
        avg_resolution_minutes=float(avg_res),
        top_corridors=top_corridors_list,
        recent_predictions=[],
        risk_distribution=risk_dist
    )
