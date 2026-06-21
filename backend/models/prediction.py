"""ASTRA Prediction Model - ML prediction results stored for audit and learning."""

from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Text, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Prediction(Base):
    """Stores ML prediction results for every event."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)

    # Model 1: Event Impact / Risk Score
    risk_score = Column(Float, nullable=False)  # 0-100
    risk_category = Column(String(20), nullable=True)  # Low/Medium/High/Critical

    # Model 2: Corridor Stress
    corridor_stress_score = Column(Float, nullable=True)  # 0-100
    corridor_name = Column(String(100), nullable=True)

    # Model 3: Junction Rankings (stored as JSON list)
    junction_rankings = Column(JSON, nullable=True)
    # Format: [{"junction": "SilkBoardJunc", "risk_score": 85}, ...]

    # Model 4: Impact Duration
    predicted_resolution_minutes = Column(Float, nullable=True)
    resolution_category = Column(String(20), nullable=True)  # Quick/Medium/Long

    # Explainability
    shap_values = Column(JSON, nullable=True)
    # Format: {"road_closure": 0.32, "attendance": 0.21, "peak_hour": 0.18, ...}

    top_contributing_factors = Column(JSON, nullable=True)
    # Format: [{"feature": "road_closure", "impact": 32, "direction": "positive"}, ...]

    # Model metadata
    model_version = Column(String(50), nullable=True)
    model_name = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Actual outcome (for learning)
    actual_resolution_minutes = Column(Float, nullable=True)
    actual_risk_category = Column(String(20), nullable=True)
    outcome_recorded_at = Column(DateTime(timezone=True), nullable=True)
    outcome_notes = Column(Text, nullable=True)

    # Relationships
    event = relationship("Event", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction(id={self.id}, event_id={self.event_id}, risk={self.risk_score})>"
