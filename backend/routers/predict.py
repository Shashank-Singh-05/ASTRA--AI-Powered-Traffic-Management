"""ASTRA Prediction Router."""

from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.prediction import PredictionRequest, PredictionResponse, RiskScoreResponse
from backend.services.prediction_service import PredictionService
from backend.middleware.auth import get_current_active_user
from backend.models.user import User

router = APIRouter(prefix="/api/predict", tags=["Predictions"])
pred_service = PredictionService()

@router.post("", response_model=PredictionResponse)
async def predict_event_impact(
    request: PredictionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Run full ML prediction pipeline for an event."""
    try:
        response = pred_service.generate_full_prediction(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk", response_model=RiskScoreResponse)
async def get_quick_risk(
    request: PredictionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Get a quick risk score without running the full pipeline."""
    try:
        return pred_service.get_quick_risk_score(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
