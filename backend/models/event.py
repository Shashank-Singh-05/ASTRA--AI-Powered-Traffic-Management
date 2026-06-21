"""ASTRA Event Model - Traffic events from ASTraM system."""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    Enum as SQLEnum, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum


class EventType(str, enum.Enum):
    PLANNED = "planned"
    UNPLANNED = "unplanned"


class EventCause(str, enum.Enum):
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    ACCIDENT = "accident"
    CONSTRUCTION = "construction"
    WATER_LOGGING = "water_logging"
    TREE_FALL = "tree_fall"
    POT_HOLES = "pot_holes"
    ROAD_CONDITIONS = "road_conditions"
    CONGESTION = "congestion"
    PUBLIC_EVENT = "public_event"
    PROCESSION = "procession"
    VIP_MOVEMENT = "vip_movement"
    PROTEST = "protest"
    DEBRIS = "debris"
    FOG = "fog"
    OTHERS = "others"


class EventStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    RESOLVED = "resolved"


class Priority(str, enum.Enum):
    HIGH = "High"
    LOW = "Low"


class Event(Base):
    """Traffic event model - core entity for ASTRA predictions."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(50), unique=True, index=True, nullable=True)

    # Event Classification
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    event_cause = Column(SQLEnum(EventCause), nullable=False, index=True)
    priority = Column(SQLEnum(Priority), nullable=False, default=Priority.LOW)
    status = Column(SQLEnum(EventStatus), nullable=False, default=EventStatus.ACTIVE, index=True)

    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    end_latitude = Column(Float, nullable=True)
    end_longitude = Column(Float, nullable=True)
    address = Column(Text, nullable=True)
    end_address = Column(Text, nullable=True)

    # Spatial Classification
    corridor = Column(String(100), nullable=True, index=True)
    zone = Column(String(50), nullable=True, index=True)
    junction = Column(String(100), nullable=True, index=True)
    police_station = Column(String(100), nullable=True, index=True)

    # Event Details
    description = Column(Text, nullable=True)
    requires_road_closure = Column(Boolean, default=False)
    direction = Column(String(20), nullable=True)

    # Vehicle Information (for breakdown events)
    vehicle_type = Column(String(50), nullable=True)
    vehicle_number = Column(String(50), nullable=True)

    # ML Results
    risk_score = Column(Float, nullable=True)
    strategy_used = Column(String(100), nullable=True)

    # Timestamps
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Tracking
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    created_by = relationship("User", back_populates="created_events")
    predictions = relationship("Prediction", back_populates="event")
    recommendations = relationship("Recommendation", back_populates="event")

    def __repr__(self):
        return f"<Event(id={self.id}, type='{self.event_type}', cause='{self.event_cause}', corridor='{self.corridor}')>"

    @property
    def resolution_minutes(self):
        """Calculate resolution time in minutes."""
        end = self.closed_at or self.resolved_at or self.end_datetime
        if end and self.created_at:
            delta = end - self.created_at
            return delta.total_seconds() / 60
        return None
