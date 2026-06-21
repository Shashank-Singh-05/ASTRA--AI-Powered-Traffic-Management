"""ASTRA Prediction Service. Bridges API and ML Models."""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from backend.schemas.prediction import PredictionRequest, PredictionResponse, RiskScoreResponse
from ml.models.corridor_stress import predict_current_corridor_stress
from ml.models.junction_ranking import get_top_junctions
from ml.explainability import generate_shap_explanation
from ml import config
import joblib

class PredictionService:
    def __init__(self):
        self.models_loaded = False
        self.impact_model = None
        self.duration_model = None
        
    def _load_models(self):
        """Lazy load models."""
        if self.models_loaded:
            return
            
        try:
            impact_path = config.MODELS_DIR / "event_impact_model.joblib"
            duration_path = config.MODELS_DIR / "impact_duration_model.joblib"
            
            if impact_path.exists():
                self.impact_model = joblib.load(impact_path)
            
            if duration_path.exists():
                self.duration_model = joblib.load(duration_path)
                
            self.models_loaded = True
        except Exception as e:
            print(f"Error loading ML models: {e}")

    def _prepare_features(self, req: PredictionRequest) -> Dict[str, Any]:
        """Convert API request to ML feature dictionary."""
        dt = req.start_datetime or datetime.now()
        
        # Mappings
        cause_severity = config.EVENT_CAUSE_SEVERITY.get(req.event_cause, 3)
        corridor_importance = config.CORRIDOR_IMPORTANCE.get(req.corridor, 3)
        
        # Time
        hour = dt.hour
        is_peak = (config.MORNING_PEAK_START <= hour < config.MORNING_PEAK_END) or \
                  (config.EVENING_PEAK_START <= hour < config.EVENING_PEAK_END)
                  
        return {
            'hour_ist': hour,
            'day_of_week': dt.weekday(),
            'is_weekend': 1 if dt.weekday() >= 5 else 0,
            'is_peak_hour': 1 if is_peak else 0,
            'corridor_encoded': 0, # Placeholder, in prod would use actual LabelEncoder
            'zone_encoded': 0,
            'police_station_encoded': 0,
            'has_junction': 1 if req.junction else 0,
            'cause_severity': cause_severity,
            'is_planned': 1 if req.event_type == 'planned' else 0,
            'closure_impact': 1 if req.requires_road_closure else 0,
            'is_high_priority': 1 if req.priority == 'High' else 0
        }
        
    def get_quick_risk_score(self, req: PredictionRequest) -> RiskScoreResponse:
        """Get just the risk score."""
        self._load_models()
        features = self._prepare_features(req)
        
        if self.impact_model:
            # Create a dataframe ensuring column order
            from ml.models.event_impact import FEATURES
            df = pd.DataFrame([features]).reindex(columns=FEATURES, fill_value=0)
            score = float(self.impact_model.predict(df)[0])
        else:
            # Fallback heuristic
            score = (features['cause_severity']/10 * 40) + \
                    (features['closure_impact'] * 30) + \
                    (features['is_peak_hour'] * 20) + \
                    (features['is_high_priority'] * 10)
                    
        score = max(0.0, min(100.0, score))
        
        if score > 85: cat = "Critical"
        elif score > 65: cat = "High"
        elif score > 35: cat = "Medium"
        else: cat = "Low"
        
        return RiskScoreResponse(
            risk_score=score,
            risk_category=cat,
            confidence=0.85
        )

    def generate_full_prediction(self, req: PredictionRequest) -> PredictionResponse:
        """Run all 4 ML models for a complete prediction."""
        self._load_models()
        features = self._prepare_features(req)
        
        # 1. Risk Score
        risk_res = self.get_quick_risk_score(req)
        
        # 2. Corridor Stress
        stress = predict_current_corridor_stress(req.corridor, 1)
        
        # 3. Junctions
        junctions = get_top_junctions(5)
        
        # 4. Duration
        if self.duration_model:
            from ml.models.impact_duration import FEATURES as DUR_FEAT
            df_dur = pd.DataFrame([features]).reindex(columns=DUR_FEAT, fill_value=0)
            dur_cat = str(self.duration_model.predict(df_dur)[0])
            dur_mins = 20 if dur_cat == 'Quick' else 60 if dur_cat == 'Medium' else 180
        else:
            # Fallback
            if risk_res.risk_score > 80:
                dur_cat = "Long"
                dur_mins = 180
            elif risk_res.risk_score > 40:
                dur_cat = "Medium"
                dur_mins = 60
            else:
                dur_cat = "Quick"
                dur_mins = 20
                
        # 5. Explainability
        if self.impact_model:
            from ml.models.event_impact import FEATURES as IMP_FEAT
            contributions = generate_shap_explanation(self.impact_model, features, IMP_FEAT)
            # Map back to API schema
            api_contribs = [
                {
                    "feature": c["feature"],
                    "display_name": c["feature"].replace("_", " ").title(),
                    "impact_percentage": abs(c["impact"]),
                    "direction": c["direction"],
                    "value": features.get(c["feature"], 0)
                }
                for c in contributions[:5]
            ]
        else:
            api_contribs = [
                {"feature": "event_cause", "display_name": "Event Cause", "impact_percentage": 45.0, "direction": "positive", "value": req.event_cause},
                {"feature": "requires_road_closure", "display_name": "Road Closure", "impact_percentage": 25.0, "direction": "positive", "value": req.requires_road_closure}
            ]
            
        return PredictionResponse(
            prediction_id=0, # Will be set by DB
            risk_score=risk_res.risk_score,
            risk_category=risk_res.risk_category,
            corridor_stress=stress,
            corridor_name=req.corridor,
            junction_rankings=junctions,
            predicted_resolution_minutes=dur_mins,
            resolution_category=dur_cat,
            contributing_factors=api_contribs,
            model_version="1.0.0",
            predicted_at=datetime.now()
        )
