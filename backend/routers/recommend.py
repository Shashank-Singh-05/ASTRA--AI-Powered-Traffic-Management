"""ASTRA Recommendation Router."""

from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.prediction import RecommendationRequest, RecommendationResponse
from backend.services.recommendation_service import RecommendationService
from backend.middleware.auth import get_current_active_user
from backend.models.user import User

router = APIRouter(prefix="/api/recommend", tags=["Recommendations"])
rec_service = RecommendationService()

@router.post("", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Get deployment strategies and intervention windows for an event."""
    try:
        return rec_service.generate_recommendations(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
