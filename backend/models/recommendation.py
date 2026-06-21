"""ASTRA Recommendation Model - Decision Intelligence Engine outputs."""

from sqlalchemy import (
    Column, Integer, Float, String, Boolean, DateTime, Text, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Recommendation(Base):
    """Stores deployment recommendations from the Decision Intelligence Engine."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)

    # Strategy Identification
    strategy_label = Column(String(10), nullable=False)  # A, B, C
    is_recommended = Column(Boolean, default=False)

    # Resource Allocation
    officers_required = Column(Integer, default=0)
    barricades_required = Column(Integer, default=0)
    diversion_needed = Column(Boolean, default=False)
    diversion_route = Column(Text, nullable=True)

    # Expected Impact
    expected_risk_reduction = Column(Float, nullable=True)  # percentage
    expected_improvement = Column(Float, nullable=True)  # percentage
    estimated_cost_score = Column(Float, nullable=True)  # relative cost 0-100

    # Intervention Timing
    deploy_before = Column(DateTime(timezone=True), nullable=True)
    intervention_window = Column(String(20), nullable=True)  # Low/Rising/High/Critical

    # Reasoning
    reasoning = Column(Text, nullable=True)
    rules_fired = Column(JSON, nullable=True)
    # Format: ["rule_1: VIP + high_risk", "rule_2: peak_hour_deployment"]

    # Approval workflow
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_status = Column(String(20), default="pending")  # pending/approved/rejected/modified

    # Outcome tracking (for learning)
    actions_taken = Column(JSON, nullable=True)
    # Format: {"officers_deployed": 6, "barricades_placed": 3, "diversion_activated": true}
    outcome_success = Column(Boolean, nullable=True)
    outcome_notes = Column(Text, nullable=True)
    actual_improvement = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    event = relationship("Event", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(id={self.id}, strategy='{self.strategy_label}', recommended={self.is_recommended})>"
