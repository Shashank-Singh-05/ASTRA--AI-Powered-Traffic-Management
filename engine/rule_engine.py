"""Rule Engine Module."""

import yaml
from pathlib import Path
from typing import Dict, Any, List

class RuleEngine:
    """Evaluates event data against configured rules."""
    
    def __init__(self, rules_path: str = None):
        if rules_path is None:
            rules_path = Path(__file__).parent / "rules.yaml"
        self.rules_path = rules_path
        self.rules = self.load_rules()

    def load_rules(self) -> List[Dict]:
        """Load rules from YAML file."""
        try:
            with open(self.rules_path, 'r') as f:
                config = yaml.safe_load(f)
                return sorted(config.get('rules', []), key=lambda x: x.get('priority', 99))
        except Exception as e:
            print(f"Error loading rules: {e}")
            return []

    def evaluate(self, event_data: Dict[str, Any]) -> List[Dict]:
        """
        Evaluate event data against all rules.
        Returns a list of actions from rules that matched, ordered by priority.
        """
        matched_actions = []
        
        for rule in self.rules:
            if self._check_conditions(rule.get('conditions', []), event_data):
                action = rule.get('actions', {}).copy()
                action['rule_id'] = rule.get('id')
                matched_actions.append(action)
                
        return matched_actions

    def _check_conditions(self, conditions: List[Dict], data: Dict[str, Any]) -> bool:
        """Check if all conditions in a rule are met by the data."""
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            data_val = data.get(field)
            
            if data_val is None:
                return False
                
            if operator == "==":
                if data_val != value: return False
            elif operator == "!=":
                if data_val == value: return False
            elif operator == ">":
                if data_val <= value: return False
            elif operator == ">=":
                if data_val < value: return False
            elif operator == "<":
                if data_val >= value: return False
            elif operator == "<=":
                if data_val > value: return False
            else:
                print(f"Unknown operator: {operator}")
                return False
                
        return True

if __name__ == "__main__":
    engine = RuleEngine()
    
    test_event_1 = {
        "event_cause": "vip_movement",
        "risk_score": 85,
        "requires_road_closure": True,
        "is_peak_hour": False,
        "corridor": "Bellary Road 1"
    }
    
    test_event_2 = {
        "event_cause": "vehicle_breakdown",
        "risk_score": 45,
        "requires_road_closure": False,
        "is_peak_hour": True,
        "corridor": "ORR South"
    }
    
    print("Testing Event 1 (VIP):")
    actions = engine.evaluate(test_event_1)
    for a in actions:
        print(f"  Matched Rule: {a['rule_id']} -> {a['reasoning']}")
        
    print("\nTesting Event 2 (Breakdown in peak):")
    actions = engine.evaluate(test_event_2)
    for a in actions:
        print(f"  Matched Rule: {a['rule_id']} -> {a['reasoning']}")
