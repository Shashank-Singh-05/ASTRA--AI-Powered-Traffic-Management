"""Resource Optimization Engine."""

import numpy as np
from scipy.optimize import linprog
from typing import List, Dict, Any

class ResourceOptimizer:
    """Optimizes resource allocation across multiple concurrent events."""
    
    def __init__(self):
        pass
        
    def optimize_allocation(self, 
                            events: List[Dict[str, Any]], 
                            total_officers_available: int, 
                            total_barricades_available: int) -> Dict[str, Any]:
        """
        Allocate officers and barricades to minimize overall risk.
        Uses a greedy approach for simplicity and robustness in real-time.
        """
        if not events:
            return {"allocations": [], "remaining_officers": total_officers_available, "remaining_barricades": total_barricades_available}
            
        # Sort events by risk score descending
        sorted_events = sorted(events, key=lambda x: x.get('risk_score', 0), reverse=True)
        
        allocations = []
        rem_officers = total_officers_available
        rem_barricades = total_barricades_available
        
        # Minimum requirements based on risk
        for event in sorted_events:
            risk = event.get('risk_score', 0)
            
            # Determine ideal allocation
            if risk > 80:
                ideal_off = 6
                ideal_bar = 6
            elif risk > 50:
                ideal_off = 4
                ideal_bar = 4
            elif risk > 20:
                ideal_off = 2
                ideal_bar = 2
            else:
                ideal_off = 1
                ideal_bar = 0
                
            # Allocate what's available
            alloc_off = min(ideal_off, rem_officers)
            rem_officers -= alloc_off
            
            alloc_bar = min(ideal_bar, rem_barricades)
            rem_barricades -= alloc_bar
            
            allocations.append({
                "event_id": event.get('id', 'unknown'),
                "event_cause": event.get('event_cause', 'unknown'),
                "risk_score": risk,
                "allocated_officers": alloc_off,
                "allocated_barricades": alloc_bar,
                "deficit_officers": ideal_off - alloc_off,
                "deficit_barricades": ideal_bar - alloc_bar
            })
            
        # If resources remaining, distribute to highest risk events first
        idx = 0
        while (rem_officers > 0 or rem_barricades > 0) and idx < len(allocations):
            # Give max 2 extra officers/barricades to top events
            if rem_officers > 0:
                extra_off = min(2, rem_officers)
                allocations[idx]["allocated_officers"] += extra_off
                rem_officers -= extra_off
                
            if rem_barricades > 0:
                extra_bar = min(2, rem_barricades)
                allocations[idx]["allocated_barricades"] += extra_bar
                rem_barricades -= extra_bar
                
            idx += 1
            
        return {
            "allocations": allocations,
            "remaining_officers": rem_officers,
            "remaining_barricades": rem_barricades,
            "total_deficit": sum(a["deficit_officers"] + a["deficit_barricades"] for a in allocations)
        }

if __name__ == "__main__":
    optimizer = ResourceOptimizer()
    test_events = [
        {"id": 1, "event_cause": "accident", "risk_score": 85},
        {"id": 2, "event_cause": "vehicle_breakdown", "risk_score": 30},
        {"id": 3, "event_cause": "vip_movement", "risk_score": 95},
        {"id": 4, "event_cause": "water_logging", "risk_score": 60}
    ]
    
    # Constrained resources
    print("Testing with constrained resources (10 officers, 10 barricades):")
    result = optimizer.optimize_allocation(test_events, 10, 10)
    for a in result["allocations"]:
        print(f"  Event {a['event_id']} (Risk {a['risk_score']}): Officers={a['allocated_officers']} (Deficit: {a['deficit_officers']})")
        
    print("\nTesting with abundant resources (30 officers, 30 barricades):")
    result2 = optimizer.optimize_allocation(test_events, 30, 30)
    for a in result2["allocations"]:
        print(f"  Event {a['event_id']} (Risk {a['risk_score']}): Officers={a['allocated_officers']} (Deficit: {a['deficit_officers']})")
