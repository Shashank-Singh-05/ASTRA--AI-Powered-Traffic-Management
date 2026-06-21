"""ASTRA Event Schemas - Request/Response models for event endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EventCreate(BaseModel):
    """Schema for creating a new traffic event."""
    event_type: str = Field(..., pattern="^(planned|unplanned)$")
    event_cause: str = Field(..., description="Event cause category")
    priority: str = Field(default="Low", pattern="^(High|Low)$")
    latitude: float = Field(..., ge=12.0, le=14.0, description="GPS latitude")
    longitude: float = Field(..., ge=76.0, le=79.0, description="GPS longitude")
    address: Optional[str] = None
    corridor: Optional[str] = None
    zone: Optional[str] = None
    junction: Optional[str] = None
    police_station: Optional[str] = None
    description: Optional[str] = None
    requires_road_closure: bool = False
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    vehicle_type: Optional[str] = None
    direction: Optional[str] = None


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    status: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    requires_road_closure: Optional[bool] = None
    end_datetime: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    risk_score: Optional[float] = None
    strategy_used: Optional[str] = None


class EventResponse(BaseModel):
    """Schema for event response."""
    id: int
    external_id: Optional[str]
    event_type: str
    event_cause: str
    priority: str
    status: str
    latitude: float
    longitude: float
    address: Optional[str]
    corridor: Optional[str]
    zone: Optional[str]
    junction: Optional[str]
    police_station: Optional[str]
    description: Optional[str]
    requires_road_closure: bool
    start_datetime: datetime
    end_datetime: Optional[datetime]
    created_at: Optional[datetime]
    closed_at: Optional[datetime]
    vehicle_type: Optional[str]
    resolution_minutes: Optional[float] = None
    risk_score: Optional[float] = None
    strategy_used: Optional[str] = None

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Paginated event list response."""
    events: List[EventResponse]
    total: int
    page: int
    per_page: int


class EventBulkUpload(BaseModel):
    """Schema for bulk event upload."""
    events: List[EventCreate]
