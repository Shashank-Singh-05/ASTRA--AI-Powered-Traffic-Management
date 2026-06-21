"""Model 1: Event Impact / Risk Score Predictor."""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from ml import config

# Features used for training
FEATURES = [
    'hour_ist', 'day_of_week', 'is_weekend', 'is_peak_hour',
    'corridor_encoded', 'zone_encoded', 'police_station_encoded', 'has_junction',
    'cause_severity', 'is_planned', 'closure_impact', 'is_high_priority'
]

def train_event_impact_models(df: pd.DataFrame):
    """Train and compare models for Event Impact (Risk Score)."""
    print("\n--- Training Event Impact Models ---")
    
    # Prepare data
    X = df[FEATURES]
    y = df[config.TARGET_RISK_SCORE]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=config.RANDOM_STATE
    )
    
    # Initialize models
    models = {
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=config.RANDOM_STATE),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=config.RANDOM_STATE),
        'LightGBM': LGBMRegressor(n_estimators=100, random_state=config.RANDOM_STATE, verbose=-1)
    }
    
    results = {}
    best_model = None
    best_r2 = -float('inf')
    best_name = ""
    
    # Train and evaluate
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        mse = mean_squared_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        
        results[name] = {'MSE': mse, 'R2': r2, 'model': model}
        print(f"{name} - R2: {r2:.4f}, MSE: {mse:.4f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            best_name = name
            
    print(f"Best Model: {best_name} (R2: {best_r2:.4f})")
    
    # Save the best model
    model_path = config.MODELS_DIR / "event_impact_model.joblib"
    joblib.dump(best_model, model_path)
    print(f"Saved best model to {model_path}")
    
    return best_model, results

def predict_risk_score(model, features_dict):
    """Make a single prediction using the trained model."""
    df = pd.DataFrame([features_dict])
    # Ensure columns match FEATURES exactly
    df = df.reindex(columns=FEATURES, fill_value=0)
    score = model.predict(df)[0]
    return np.clip(score, 0, 100) # Ensure between 0 and 100
