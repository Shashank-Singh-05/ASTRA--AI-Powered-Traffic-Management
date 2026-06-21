"""ASTRA Feature Engineering."""

import pandas as pd
import numpy as np
from ml import config
from sklearn.preprocessing import LabelEncoder

def create_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and create time-based features from start_datetime."""
    if 'start_datetime' not in df.columns:
        return df

    # Create safe copy of datetime
    dt = df['start_datetime']
    
    # Basic temporal
    df['hour_ist'] = dt.dt.hour
    df['day_of_week'] = dt.dt.dayofweek
    df['month'] = dt.dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Peak hour boolean
    is_morning_peak = (df['hour_ist'] >= config.MORNING_PEAK_START) & (df['hour_ist'] < config.MORNING_PEAK_END)
    is_evening_peak = (df['hour_ist'] >= config.EVENING_PEAK_START) & (df['hour_ist'] < config.EVENING_PEAK_END)
    df['is_peak_hour'] = (is_morning_peak | is_evening_peak).astype(int)
    
    # Cyclical hour features
    df['hour_sin'] = np.sin(2 * np.pi * df['hour_ist'] / 24.0)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_ist'] / 24.0)
    
    return df

def create_spatial_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create spatial and location-based features."""
    
    # Encode Corridor Importance
    df['corridor_importance'] = df['corridor'].map(config.CORRIDOR_IMPORTANCE).fillna(3)
    
    # Categorical encodings
    categorical_cols = ['corridor', 'zone', 'police_station']
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            # Fill NA before encoding
            filled_col = df[col].fillna('Unknown')
            df[f'{col}_encoded'] = le.fit_transform(filled_col)
            
    # Has junction indicator
    if 'junction' in df.columns:
        df['has_junction'] = df['junction'].notna().astype(int)
        
    return df

def create_event_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create event-specific features."""
    
    # Cause Severity
    df['cause_severity'] = df['event_cause'].map(config.EVENT_CAUSE_SEVERITY).fillna(3)
    
    # Event Type
    if 'event_type' in df.columns:
        df['is_planned'] = (df['event_type'] == 'planned').astype(int)
        
    # Closure impact (binary from bool)
    if 'requires_road_closure' in df.columns:
        df['closure_impact'] = df['requires_road_closure'].astype(int)
        
    # Priority
    if 'priority' in df.columns:
        df['is_high_priority'] = (df['priority'] == 'High').astype(int)
        
    return df

def create_target_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Create target variables for prediction."""
    
    # 1. Composite Risk Score (Target 1)
    # Weights: Cause 30%, Closure 20%, Corridor 20%, Peak Hour 15%, Priority 15%
    
    # Normalize components to 0-1 range before weighting
    norm_cause = df['cause_severity'] / 10.0
    norm_closure = df['closure_impact']
    norm_corridor = df['corridor_importance'] / 10.0
    norm_peak = df['is_peak_hour']
    norm_priority = df['is_high_priority']
    
    raw_risk = (
        norm_cause * 0.30 +
        norm_closure * 0.20 +
        norm_corridor * 0.20 +
        norm_peak * 0.15 +
        norm_priority * 0.15
    )
    
    # Scale to 0-100
    df[config.TARGET_RISK_SCORE] = raw_risk * 100.0
    
    # 2. Resolution Time Category (Target 2 classification)
    if 'resolution_minutes' in df.columns:
        conditions = [
            (df['resolution_minutes'] < 30),
            (df['resolution_minutes'] >= 30) & (df['resolution_minutes'] <= 120),
            (df['resolution_minutes'] > 120)
        ]
        choices = ['Quick', 'Medium', 'Long']
        df[config.TARGET_RESOLUTION_CATEGORY] = np.select(conditions, choices, default='Unknown')
        
    return df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run all feature engineering steps."""
    print("Engineering features...")
    df = create_temporal_features(df)
    df = create_spatial_features(df)
    df = create_event_features(df)
    df = create_target_variables(df)
    return df

if __name__ == "__main__":
    from ml.data_pipeline import load_and_clean_data
    df = load_and_clean_data()
    df_engineered = engineer_features(df)
    print(f"Engineered Data Shape: {df_engineered.shape}")
    print(df_engineered[[config.TARGET_RISK_SCORE, 'resolution_minutes', config.TARGET_RESOLUTION_CATEGORY]].head())
