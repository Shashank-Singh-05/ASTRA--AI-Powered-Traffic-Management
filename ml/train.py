"""ASTRA ML Training Orchestrator."""

from ml.data_pipeline import load_and_clean_data
from ml.feature_engineering import engineer_features
from ml.models.event_impact import train_event_impact_models
from ml.models.corridor_stress import calculate_corridor_stress
from ml.models.junction_ranking import calculate_junction_rankings
from ml.models.impact_duration import train_impact_duration_models
from ml import config

def run_pipeline():
    print("=" * 60)
    print("ASTRA ML Pipeline Execution")
    print("=" * 60)
    
    # 1. Data Cleaning
    df = load_and_clean_data()
    print(f"Data cleaned. Shape: {df.shape}")
    
    # 2. Feature Engineering
    df_engineered = engineer_features(df)
    print(f"Features engineered. Shape: {df_engineered.shape}")
    
    # Save processed data
    df_engineered.to_csv(config.PROCESSED_DATA_PATH, index=False)
    print(f"Saved processed data to {config.PROCESSED_DATA_PATH}")
    
    # 3. Model Training
    print("\n--- Training Models ---")
    
    # Model 1: Event Impact
    best_impact_model, impact_results = train_event_impact_models(df_engineered)
    
    # Model 2: Corridor Stress
    stress_profiles = calculate_corridor_stress(df_engineered)
    
    # Model 3: Junction Ranking
    junction_rankings = calculate_junction_rankings(df_engineered)
    
    # Model 4: Impact Duration
    best_duration_model, duration_results = train_impact_duration_models(df_engineered)
    
    print("\n" + "=" * 60)
    print("ASTRA ML Pipeline Complete!")
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline()
