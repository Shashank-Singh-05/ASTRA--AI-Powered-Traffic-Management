"""ASTRA Explainable AI Module."""

import shap
import pandas as pd
import numpy as np

def generate_shap_explanation(model, features_dict, feature_names):
    """
    Generate SHAP values for a single prediction to explain model reasoning.
    Uses TreeExplainer for tree-based models (RF, XGBoost, LightGBM).
    """
    df = pd.DataFrame([features_dict])
    df = df.reindex(columns=feature_names, fill_value=0)
    
    # We use TreeExplainer for the trained ensemble models
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(df)
        
        # Format the output for the API
        # Handle different return types from SHAP (sometimes list for multiclass/multioutput)
        if isinstance(shap_values, list):
            sv = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        else:
            sv = shap_values[0]
            
        contributions = []
        for i, feature in enumerate(feature_names):
            impact = float(sv[i])
            contributions.append({
                "feature": feature,
                "impact": impact,
                "direction": "positive" if impact > 0 else "negative"
            })
            
        # Sort by absolute impact
        contributions.sort(key=lambda x: abs(x["impact"]), reverse=True)
        return contributions
        
    except Exception as e:
        print(f"Explainability Error: {e}")
        # Fallback to simple rules if SHAP fails
        return [{"feature": "error", "impact": 0.0, "direction": "unknown"}]
