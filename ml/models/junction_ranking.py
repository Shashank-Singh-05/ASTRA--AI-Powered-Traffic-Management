"""Model 3: Junction Risk Ranking."""

import pandas as pd
import joblib
from ml import config

def calculate_junction_rankings(df: pd.DataFrame):
    """
    Rank junctions based on historical event frequency and severity.
    """
    print("\n--- Calculating Junction Rankings ---")
    
    if 'junction' not in df.columns:
        print("No junction data available.")
        return None
        
    junction_data = df.dropna(subset=['junction'])
    
    if len(junction_data) == 0:
        return None
        
    # Calculate frequency
    freq = junction_data['junction'].value_counts()
    
    # Calculate average risk
    if config.TARGET_RISK_SCORE in junction_data.columns:
        risk = junction_data.groupby('junction')[config.TARGET_RISK_SCORE].mean()
    else:
        risk = pd.Series(50, index=freq.index)
        
    # Calculate road closures
    if 'closure_impact' in junction_data.columns:
        closures = junction_data.groupby('junction')['closure_impact'].sum()
    else:
        closures = pd.Series(0, index=freq.index)
        
    # Combine
    rankings = pd.DataFrame({
        'frequency': freq,
        'avg_risk': risk,
        'total_closures': closures
    }).fillna(0)
    
    # Composite ranking score
    # Normalize frequency
    norm_freq = (rankings['frequency'] / rankings['frequency'].max()) * 100
    
    rankings['ranking_score'] = (
        norm_freq * 0.4 +
        rankings['avg_risk'] * 0.4 +
        (rankings['total_closures'] * 5) * 0.2  # Arbitrary weight for closures
    )
    
    rankings = rankings.sort_values('ranking_score', ascending=False)
    
    # Save
    rankings_path = config.MODELS_DIR / "junction_rankings.joblib"
    joblib.dump(rankings, rankings_path)
    print(f"Saved junction rankings to {rankings_path}")
    
    return rankings

def get_top_junctions(n: int = 10):
    """Retrieve top N risky junctions."""
    rankings_path = config.MODELS_DIR / "junction_rankings.joblib"
    try:
        rankings = joblib.load(rankings_path)
        # Format as list of dicts for API
        top = rankings.head(n).reset_index()
        top.rename(columns={'junction': 'name'}, inplace=True)
        return top.to_dict('records')
    except (FileNotFoundError, KeyError):
        return []
