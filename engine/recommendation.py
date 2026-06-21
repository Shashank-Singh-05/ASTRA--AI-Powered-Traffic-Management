"""Recommendation Engine Module."""

from typing import Dict, Any, List
from engine.rule_engine import RuleEngine

class RecommendationEngine:
    """Generates multiple deployment strategies (A/B/C) based on event data and rules."""
    
    def __init__(self):
        self.rule_engine = RuleEngine()

    def generate_strategies(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate multiple deployment strategies.
        Returns the strategies and the recommended one.
        """
        # Get baseline actions from rules
        matched_actions = self.rule_engine.evaluate(event_data)
        
        # Determine baseline resource needs (take max from matched rules)
        base_officers = max([a.get('officers', 0) for a in matched_actions] + [1])
        base_barricades = max([a.get('barricades', 0) for a in matched_actions] + [0])
        base_diversion = any([a.get('diversion', False) for a in matched_actions])
        
        rules_fired = [a.get('rule_id') for a in matched_actions]
        reasonings = [a.get('reasoning') for a in matched_actions]
        overall_reasoning = " | ".join(reasonings) if reasonings else "Standard deployment based on event parameters."
        
        risk_score = event_data.get('risk_score', 0)
        
        # Strategy A: Minimum Deployment (Cost Optimized)
        strategy_a = {
            "strategy_label": "A",
            "is_recommended": False,
            "officers": max(1, int(base_officers * 0.6)),
            "barricades": max(0, int(base_barricades * 0.5)),
            "diversion_needed": base_diversion and risk_score > 70, # Only divert if high risk
            "diversion_route": "Nearest alternate parallel road" if base_diversion and risk_score > 70 else None,
            "expected_risk_reduction": 15.0 + (risk_score * 0.1),
            "expected_improvement": 10.0,
            "cost_score": 30.0,
            "reasoning": "Minimal resource allocation. Sufficient for observation but may struggle if situation escalates."
        }
        
        # Strategy B: Balanced Deployment (Usually Recommended)
        strategy_b = {
            "strategy_label": "B",
            "is_recommended": True,
            "officers": base_officers,
            "barricades": base_barricades,
            "diversion_needed": base_diversion,
            "diversion_route": "Standard planned detour" if base_diversion else None,
            "expected_risk_reduction": 40.0 + (risk_score * 0.2),
            "expected_improvement": 32.0,
            "cost_score": 60.0,
            "reasoning": "Optimal balance of resources. Expected to contain the incident efficiently."
        }
        
        # Strategy C: Maximum Deployment (Risk Optimized)
        strategy_c = {
            "strategy_label": "C",
            "is_recommended": False,
            "officers": int(base_officers * 1.5) + 2,
            "barricades": int(base_barricades * 1.5) + 2,
            "diversion_needed": base_diversion or risk_score > 60,
            "diversion_route": "Wide area cordon and re-routing" if (base_diversion or risk_score > 60) else None,
            "expected_risk_reduction": 60.0 + (risk_score * 0.3),
            "expected_improvement": 45.0,
            "cost_score": 95.0,
            "reasoning": "Maximum resource deployment. Ensures highest safety and fastest resolution at high resource cost."
        }
        
        # Adjust recommendation based on risk
        if risk_score > 85:
            strategy_b["is_recommended"] = False
            strategy_c["is_recommended"] = True
            recommended_strategy = "C"
        elif risk_score < 30:
            strategy_b["is_recommended"] = False
            strategy_a["is_recommended"] = True
            recommended_strategy = "A"
        else:
            recommended_strategy = "B"
            
        # Cap reductions at 99%
        for s in [strategy_a, strategy_b, strategy_c]:
            s["expected_risk_reduction"] = min(99.0, s["expected_risk_reduction"])
            
        return {
            "strategies": [strategy_a, strategy_b, strategy_c],
            "recommended_strategy": recommended_strategy,
            "overall_reasoning": overall_reasoning,
            "rules_fired": rules_fired
        }

if __name__ == "__main__":
    engine = RecommendationEngine()
    test_event = {
        "event_cause": "accident",
        "risk_score": 75,
        "requires_road_closure": True,
        "is_peak_hour": True,
        "corridor": "Hosur Road"
    }
    
    result = engine.generate_strategies(test_event)
    print(f"Recommended Strategy: {result['recommended_strategy']}")
    print(f"Reasoning: {result['overall_reasoning']}")
    print("\nStrategies:")
    for s in result['strategies']:
        print(f"  [{s['strategy_label']}] Recommended: {s['is_recommended']}")
        print(f"      Officers: {s['officers']}, Barricades: {s['barricades']}")
        print(f"      Diversion: {s['diversion_needed']}")
        print(f"      Expected Reduction: {s['expected_risk_reduction']:.1f}%")
