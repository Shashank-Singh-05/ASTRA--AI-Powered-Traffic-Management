"""ASTRA Recommendation Service."""

from backend.schemas.prediction import RecommendationRequest, RecommendationResponse
from engine.recommendation import RecommendationEngine
from engine.opportunity_window import OpportunityWindowPredictor
from datetime import datetime

class RecommendationService:
    def __init__(self):
        self.rec_engine = RecommendationEngine()
        self.opp_window = OpportunityWindowPredictor()
        
    def generate_recommendations(self, req: RecommendationRequest) -> RecommendationResponse:
        """Generate A/B/C deployment strategies."""
        
        # Build event dict for engine
        event_data = {
            "risk_score": req.risk_score or 50,
            "event_cause": req.event_cause or "unknown",
            "corridor": req.corridor or "Non-corridor",
            "requires_road_closure": req.requires_road_closure or False,
            "is_peak_hour": req.is_peak_hour or False
        }
        
        # Get strategies
        strat_result = self.rec_engine.generate_strategies(event_data)
        
        # Get opportunity window
        win_result = self.opp_window.predict_window(event_data)
        
        # Determine category
        score = event_data["risk_score"]
        if score > 85: cat = "Critical"
        elif score > 65: cat = "High"
        elif score > 35: cat = "Medium"
        else: cat = "Low"
        
        return RecommendationResponse(
            event_id=req.event_id,
            risk_score=score,
            risk_category=cat,
            strategies=strat_result["strategies"],
            recommended_strategy=strat_result["recommended_strategy"],
            deploy_before=datetime.fromisoformat(win_result["deploy_before"]),
            intervention_window=win_result["intervention_window"],
            time_until_critical=win_result["time_until_critical_mins"],
            overall_reasoning=strat_result["overall_reasoning"],
            rules_fired=strat_result["rules_fired"]
        )
