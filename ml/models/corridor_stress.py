"""Model 2: Corridor Stress Predictor."""

import pandas as pd
import numpy as np
from ml import config
import joblib

def calculate_corridor_stress(df: pd.DataFrame):
    """
    Calculate base stress scores for corridors.
    Instead of a full ML model, we use an aggregation approach based on
    historical event frequency, average risk, and capacity/importance.
    """
    print("\n--- Calculating Corridor Stress Profiles ---")
    
    # 1. Base frequency score
    corridor_counts = df['corridor'].value_counts()
    max_count = corridor_counts.max()
    freq_score = (corridor_counts / max_count) * 100
    
    # 2. Average risk score per corridor
    if config.TARGET_RISK_SCORE in df.columns:
        avg_risk = df.groupby('corridor')[config.TARGET_RISK_SCORE].mean()
    else:
        avg_risk = pd.Series(50, index=corridor_counts.index)
        
    # 3. Corridor importance factor
    importance = pd.Series(config.CORRIDOR_IMPORTANCE)
    
    # Combine into stress profile
    stress_profiles = pd.DataFrame({
        'freq_score': freq_score,
        'avg_risk': avg_risk,
        'importance': importance
    }).fillna(50) # fill missing with average
    
    # Base stress = 40% freq + 40% risk + 20% importance
    stress_profiles['base_stress'] = (
        stress_profiles['freq_score'] * 0.4 +
        stress_profiles['avg_risk'] * 0.4 +
        (stress_profiles['importance'] * 10) * 0.2
    )
    
    # Cap at 100
    stress_profiles['base_stress'] = np.clip(stress_profiles['base_stress'], 0, 100)
    
    # Save profiles
    profile_path = config.MODELS_DIR / "corridor_stress_profiles.joblib"
    joblib.dump(stress_profiles, profile_path)
    print(f"Saved corridor stress profiles to {profile_path}")
    
    return stress_profiles

def predict_current_corridor_stress(corridor_name: str, current_active_events: int = 0):
    """
    Predict real-time stress based on base profile and current active events.
    """
    profile_path = config.MODELS_DIR / "corridor_stress_profiles.joblib"
    try:
        profiles = joblib.load(profile_path)
        base_stress = profiles.loc[corridor_name, 'base_stress']
    except (FileNotFoundError, KeyError):
        base_stress = 50.0 # Default
        
    # Add stress for current active events (+5 per event)
    current_stress = base_stress + (current_active_events * 5.0)
    return np.clip(current_stress, 0, 100)
