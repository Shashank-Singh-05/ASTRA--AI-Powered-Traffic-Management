"""Opportunity Window Predictor Module."""

from datetime import datetime, timedelta
from typing import Dict, Any

class OpportunityWindowPredictor:
    """Predicts the optimal time window for interventions."""
    
    def __init__(self):
        # IST peak hours
        self.morning_peak = (8, 10)
        self.evening_peak = (17, 20)
        
    def predict_window(self, event_data: Dict[str, Any], start_time: datetime = None) -> Dict[str, Any]:
        """
        Calculate intervention windows and deadline.
        """
        if start_time is None:
            # Assume now if not provided, for demo purposes we just use a generic time
            start_time = datetime.now()
            
        risk_score = event_data.get('risk_score', 50)
        hour = start_time.hour
        
        # Determine current phase
        is_peak = (self.morning_peak[0] <= hour <= self.morning_peak[1]) or \
                  (self.evening_peak[0] <= hour <= self.evening_peak[1])
                  
        is_pre_peak = (self.morning_peak[0] - 1 <= hour < self.morning_peak[0]) or \
                      (self.evening_peak[0] - 1 <= hour < self.evening_peak[0])
                      
        # Calculate time until critical
        # Base time: 60 mins. High risk reduces it. Peak hour reduces it.
        base_mins = 60
        if risk_score > 80:
            base_mins -= 30
        elif risk_score > 60:
            base_mins -= 15
            
        if is_peak:
            base_mins -= 15
            
        time_until_critical = max(10, base_mins) # Minimum 10 mins
        
        # Determine Window Status
        if risk_score > 85:
            window = "Critical"
        elif risk_score > 65 or (risk_score > 50 and is_peak):
            window = "High"
        elif is_pre_peak:
            window = "Rising"
        else:
            window = "Low"
            
        deploy_before = start_time + timedelta(minutes=time_until_critical)
        
        return {
            "intervention_window": window,
            "time_until_critical_mins": time_until_critical,
            "deploy_before": deploy_before.isoformat(),
            "reasoning": f"Current risk phase is {window}. Deploy within {time_until_critical} mins before situation escalates."
        }

if __name__ == "__main__":
    predictor = OpportunityWindowPredictor()
    
    # Test 1: High risk during pre-peak
    dt1 = datetime(2024, 6, 17, 16, 30) # 4:30 PM (pre-evening peak)
    res1 = predictor.predict_window({"risk_score": 75}, dt1)
    print(f"Test 1 (16:30, Risk 75): Window={res1['intervention_window']}, Critical in {res1['time_until_critical_mins']}m")
    
    # Test 2: Low risk off-peak
    dt2 = datetime(2024, 6, 17, 13, 0) # 1:00 PM (off peak)
    res2 = predictor.predict_window({"risk_score": 30}, dt2)
    print(f"Test 2 (13:00, Risk 30): Window={res2['intervention_window']}, Critical in {res2['time_until_critical_mins']}m")
