"""Model 4: Impact Duration (Resolution Time) Predictor."""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from ml import config

# Features used for training
FEATURES = [
    'hour_ist', 'day_of_week', 'is_weekend', 'is_peak_hour',
    'corridor_encoded', 'zone_encoded', 'police_station_encoded', 'has_junction',
    'cause_severity', 'is_planned', 'closure_impact', 'is_high_priority'
]

def train_impact_duration_models(df: pd.DataFrame):
    """Train classification model for Resolution Time Category."""
    print("\n--- Training Impact Duration Models ---")
    
    # Filter data with resolution target
    df_valid = df.dropna(subset=[config.TARGET_RESOLUTION_CATEGORY]).copy()
    
    if len(df_valid) == 0:
        print("No resolution data available for training.")
        return None, {}
        
    print(f"Training on {len(df_valid)} records with resolution data.")
    
    X = df_valid[FEATURES]
    y = df_valid[config.TARGET_RESOLUTION_CATEGORY]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=config.RANDOM_STATE, stratify=y
    )
    
    # Initialize models
    models = {
        'RandomForest_Clf': RandomForestClassifier(n_estimators=100, random_state=config.RANDOM_STATE, class_weight='balanced'),
        'LightGBM_Clf': LGBMClassifier(n_estimators=100, random_state=config.RANDOM_STATE, class_weight='balanced', verbose=-1)
    }
    
    results = {}
    best_model = None
    best_acc = -float('inf')
    best_name = ""
    
    # Train and evaluate
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        acc = accuracy_score(y_test, preds)
        
        results[name] = {'Accuracy': acc, 'model': model}
        print(f"{name} - Accuracy: {acc:.4f}")
        
        if acc > best_acc:
            best_acc = acc
            best_model = model
            best_name = name
            
    print(f"Best Model: {best_name} (Accuracy: {best_acc:.4f})")
    print("\nClassification Report (Best Model):")
    print(classification_report(y_test, best_model.predict(X_test)))
    
    # Save the best model
    model_path = config.MODELS_DIR / "impact_duration_model.joblib"
    joblib.dump(best_model, model_path)
    print(f"Saved best model to {model_path}")
    
    return best_model, results

def predict_duration_category(model, features_dict):
    """Predict resolution category (Quick/Medium/Long)."""
    df = pd.DataFrame([features_dict])
    df = df.reindex(columns=FEATURES, fill_value=0)
    category = model.predict(df)[0]
    return category
