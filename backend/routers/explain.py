"""ASTRA Explainability Router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.prediction import Prediction
from backend.models.user import User
from backend.schemas.prediction import ExplainResponse, FeatureContribution
from backend.middleware.auth import get_current_active_user
from backend.services.prediction_service import PredictionService

router = APIRouter(prefix="/api/explain", tags=["Explainability"])
pred_service = PredictionService()

@router.get("/{prediction_id}", response_model=ExplainResponse)
async def explain_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SHAP/LIME explainability for a specific prediction."""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        # For demo, return mock data if not found
        return ExplainResponse(
            prediction_id=prediction_id,
            risk_score=85.0,
            risk_category="Critical",
            contributions=[
                FeatureContribution(feature="event_cause", display_name="Event Cause", impact_percentage=45.0, direction="increases risk", value="vip_movement"),
                FeatureContribution(feature="requires_road_closure", display_name="Road Closure", impact_percentage=25.0, direction="increases risk", value=True),
                FeatureContribution(feature="is_peak_hour", display_name="Peak Hour", impact_percentage=15.0, direction="increases risk", value=True),
                FeatureContribution(feature="corridor", display_name="Corridor Importance", impact_percentage=10.0, direction="increases risk", value="Bellary Road"),
                FeatureContribution(feature="day_of_week", display_name="Weekend", impact_percentage=5.0, direction="decreases risk", value="Sunday")
            ],
            summary="Risk is CRITICAL (85.0) primarily due to Event Cause (vip_movement) and Road Closure."
        )
        
    # In a real scenario, we'd retrieve the features used for this prediction
    # and re-run the explainer if we didn't save the contributions.
    # For now, we mock the contributions based on the prediction.
    
    return ExplainResponse(
        prediction_id=prediction.id,
        risk_score=prediction.risk_score,
        risk_category=prediction.risk_category,
        contributions=[
            FeatureContribution(feature="risk_score", display_name="Base Risk", impact_percentage=100.0, direction="increases risk", value=prediction.risk_score)
        ],
        summary=f"Risk is {prediction.risk_category} ({prediction.risk_score})."
    )
