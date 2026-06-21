"""ASTRA Road Model - Bengaluru road infrastructure data."""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Road(Base):
    """Road/corridor infrastructure reference data."""
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    corridor = Column(String(100), nullable=True, index=True)
    zone = Column(String(50), nullable=True)

    # Importance metrics
    importance_score = Column(Float, default=50.0)  # 0-100
    capacity_score = Column(Float, default=50.0)  # 0-100
    avg_daily_events = Column(Float, nullable=True)

    # Spatial
    start_latitude = Column(Float, nullable=True)
    start_longitude = Column(Float, nullable=True)
    end_latitude = Column(Float, nullable=True)
    end_longitude = Column(Float, nullable=True)
    length_km = Column(Float, nullable=True)

    # Metadata
    road_type = Column(String(50), nullable=True)  # highway, arterial, collector, local
    num_lanes = Column(Integer, nullable=True)
    has_divider = Column(Boolean, default=True)
    speed_limit = Column(Integer, nullable=True)

    # Junction data
    junctions = Column(JSON, nullable=True)
    # Format: [{"name": "MekhriCircle", "lat": 13.01, "lng": 77.58}, ...]

    def __repr__(self):
        return f"<Road(id={self.id}, name='{self.name}', corridor='{self.corridor}')>"


class AuditLog(Base):
    """Audit log for tracking all user actions in the system."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(100), nullable=True)
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user='{self.username}')>"
