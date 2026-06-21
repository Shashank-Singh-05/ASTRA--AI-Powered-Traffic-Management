"""ASTRA Prediction & Recommendation Schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== Prediction Schemas =====

class PredictionRequest(BaseModel):
    """Input for prediction API - can predict for a new or existing event."""
    # Event details (for new prediction)
    event_type: str = Field(default="unplanned", pattern="^(planned|unplanned)$")
    event_cause: str = Field(..., description="Event cause category")
    corridor: str = Field(default="Non-corridor")
    zone: Optional[str] = None
    junction: Optional[str] = None
    police_station: Optional[str] = None
    requires_road_closure: bool = False
    priority: str = Field(default="Low", pattern="^(High|Low)$")
    latitude: float = Field(default=12.97, ge=12.0, le=14.0)
    longitude: float = Field(default=77.59, ge=76.0, le=79.0)
    start_datetime: Optional[datetime] = None
    vehicle_type: Optional[str] = None
    description: Optional[str] = None

    # Optional: predict for existing event
    event_id: Optional[int] = None


class RiskScoreResponse(BaseModel):
    """Quick risk score response."""
    risk_score: float = Field(..., ge=0, le=100)
    risk_category: str  # Low / Medium / High / Critical
    confidence: float


class PredictionResponse(BaseModel):
    """Full prediction response with all model outputs."""
    prediction_id: int

    # Model 1: Risk Score
    risk_score: float
    risk_category: str  # Low / Medium / High / Critical

    # Model 2: Corridor Stress
    corridor_stress: float
    corridor_name: str

    # Model 3: Junction Rankings
    junction_rankings: List[Dict[str, Any]]
    # [{"junction": "SilkBoardJunc", "risk_score": 85, "rank": 1}, ...]

    # Model 4: Impact Duration
    predicted_resolution_minutes: float
    resolution_category: str  # Quick / Medium / Long

    # Explainability
    contributing_factors: List[Dict[str, Any]]
    # [{"feature": "road_closure", "impact_pct": 32, "direction": "increases risk"}, ...]

    # Metadata
    model_version: str
    predicted_at: datetime


# ===== Recommendation Schemas =====

class RecommendationRequest(BaseModel):
    """Input for recommendation API."""
    event_id: Optional[int] = None
    prediction_id: Optional[int] = None
    # Or provide event details directly
    risk_score: Optional[float] = None
    event_cause: Optional[str] = None
    corridor: Optional[str] = None
    requires_road_closure: Optional[bool] = None
    is_peak_hour: Optional[bool] = None

    # Available resources (optional, for optimization)
    available_officers: int = Field(default=20)
    available_barricades: int = Field(default=12)


class StrategyResponse(BaseModel):
    """Single deployment strategy."""
    strategy_label: str  # A, B, C
    is_recommended: bool
    officers: int
    barricades: int
    diversion_needed: bool
    diversion_route: Optional[str]
    expected_risk_reduction: float  # percentage
    expected_improvement: float  # percentage
    cost_score: float  # 0-100 (lower = cheaper)
    reasoning: str


class RecommendationResponse(BaseModel):
    """Full recommendation response with multiple strategies."""
    event_id: Optional[int]
    risk_score: float
    risk_category: str

    # Multiple strategies
    strategies: List[StrategyResponse]
    recommended_strategy: str  # A, B, or C

    # Intervention timing
    deploy_before: Optional[datetime]
    intervention_window: str  # Low / Rising / High / Critical
    time_until_critical: Optional[float]  # minutes

    # Reasoning
    overall_reasoning: str
    rules_fired: List[str]


# ===== Explainability Schemas =====

class ExplainRequest(BaseModel):
    """Request explanation for a prediction."""
    prediction_id: int


class FeatureContribution(BaseModel):
    """Single feature's contribution to prediction."""
    feature: str
    display_name: str
    impact_percentage: float
    direction: str  # "increases risk" / "decreases risk"
    value: Any  # actual feature value


class ExplainResponse(BaseModel):
    """Explainability response with SHAP/LIME breakdown."""
    prediction_id: int
    risk_score: float
    risk_category: str

    # Feature contributions (sorted by impact)
    contributions: List[FeatureContribution]

    # Human-readable summary
    summary: str
    # e.g., "Risk is HIGH (87%) primarily due to Road Closure (32%), Event Attendance (21%), Peak Hour (18%)"


# ===== Dashboard Schemas =====

class DashboardKPIs(BaseModel):
    """Dashboard key performance indicators."""
    active_events: int
    high_risk_events: int
    officers_deployed: int
    avg_risk_score: float
    events_today: int
    events_this_week: int
    avg_resolution_minutes: float
    top_corridors: List[Dict[str, Any]]
    # [{"corridor": "Bellary Road 1", "active_events": 5, "stress_score": 78}, ...]
    recent_predictions: List[Dict[str, Any]]
    risk_distribution: Dict[str, int]
    # {"Low": 45, "Medium": 30, "High": 15, "Critical": 10}


# ===== Chat Schemas =====

class ChatRequest(BaseModel):
    """AI Copilot chat request."""
    message: str = Field(..., max_length=2000)
    context: Optional[Dict[str, Any]] = None  # optional context like current event


class ChatResponse(BaseModel):
    """AI Copilot chat response."""
    response: str
    similar_events: Optional[List[Dict[str, Any]]] = None
    suggested_actions: Optional[List[str]] = None
    confidence: Optional[float] = None


# ===== History Schemas =====

class HistorySearchRequest(BaseModel):
    """Search historical events."""
    query: Optional[str] = None
    event_cause: Optional[str] = None
    corridor: Optional[str] = None
    zone: Optional[str] = None
    priority: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class HistoryOutcomeRecord(BaseModel):
    """Record the actual outcome of an event."""
    prediction_id: int
    actual_resolution_minutes: Optional[float] = None
    actual_risk_category: Optional[str] = None
    actions_taken: Optional[Dict[str, Any]] = None
    outcome_success: Optional[bool] = None
    outcome_notes: Optional[str] = None
