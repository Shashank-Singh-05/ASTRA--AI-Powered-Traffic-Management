"""
ASTRA - Sprint 1: Comprehensive Exploratory Data Analysis
Analyzes the ASTraM Bengaluru Traffic Event Dataset
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# ===== Configuration =====
DATA_PATH = Path(r"d:\AA\Projects\ASTRA\data\raw\Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv")
OUTPUT_DIR = Path(r"d:\AA\Projects\ASTRA\data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("ASTRA - Dataset Exploratory Data Analysis")
print("=" * 80)

# ===== 1. Load Dataset =====
print("\n[1/10] Loading dataset...")
df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"  Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"  Memory Usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

# ===== 2. Column Overview =====
print("\n[2/10] Column Overview:")
print("-" * 100)
print(f"{'Column':<35} {'Dtype':<15} {'Non-Null':<12} {'Missing%':<10} {'Unique':<10} {'Sample Value'}")
print("-" * 100)

column_info = []
for col in df.columns:
    non_null = df[col].notna().sum()
    missing_pct = (df[col].isna().sum() / len(df)) * 100
    n_unique = df[col].nunique()
    sample = str(df[col].dropna().iloc[0])[:50] if non_null > 0 else "N/A"
    print(f"  {col:<33} {str(df[col].dtype):<15} {non_null:<12} {missing_pct:<10.1f} {n_unique:<10} {sample}")
    column_info.append({
        "column": col,
        "dtype": str(df[col].dtype),
        "non_null_count": int(non_null),
        "missing_pct": round(missing_pct, 2),
        "n_unique": int(n_unique),
        "sample": sample
    })

# ===== 3. Data Types Classification =====
print("\n[3/10] Data Type Classification:")
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
print(f"  Categorical columns ({len(categorical_cols)}): {categorical_cols}")
print(f"  Numerical columns ({len(numerical_cols)}): {numerical_cols}")

# ===== 4. Key Feature Analysis =====
print("\n[4/10] Key Feature Distributions:")

# Event Type
print("\n  === event_type ===")
print(df['event_type'].value_counts().to_string())

# Event Cause
print("\n  === event_cause ===")
print(df['event_cause'].value_counts().to_string())

# Status
print("\n  === status ===")
print(df['status'].value_counts().to_string())

# Priority
print("\n  === priority ===")
print(df['priority'].value_counts().to_string())

# Requires Road Closure
print("\n  === requires_road_closure ===")
print(df['requires_road_closure'].value_counts().to_string())

# Corridor
print("\n  === corridor (top 20) ===")
print(df['corridor'].value_counts().head(20).to_string())

# Vehicle Type
print("\n  === veh_type (top 15) ===")
print(df['veh_type'].value_counts().head(15).to_string())

# Zone
print("\n  === zone ===")
print(df['zone'].value_counts().to_string())

# Junction (top 20)
print("\n  === junction (top 20) ===")
junction_counts = df['junction'].dropna()
if len(junction_counts) > 0:
    print(df['junction'].value_counts().head(20).to_string())
else:
    print("  No junction data available")

# Police Station
print("\n  === police_station (top 20) ===")
print(df['police_station'].value_counts().head(20).to_string())

# ===== 5. Temporal Analysis =====
print("\n[5/10] Temporal Analysis:")

# Parse timestamps
for col in ['start_datetime', 'end_datetime', 'created_date', 'modified_datetime', 'closed_datetime', 'resolved_datetime']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)

if 'start_datetime' in df.columns:
    valid_dates = df['start_datetime'].dropna()
    print(f"  Date Range: {valid_dates.min()} to {valid_dates.max()}")
    print(f"  Total span: {(valid_dates.max() - valid_dates.min()).days} days")
    
    # Hour distribution
    hours = valid_dates.dt.hour
    print(f"\n  Hour Distribution:")
    hour_counts = hours.value_counts().sort_index()
    for h, c in hour_counts.items():
        bar = "█" * (c // 20)
        print(f"    {h:02d}:00  {c:>5}  {bar}")
    
    # Day of week
    dow = valid_dates.dt.day_name()
    print(f"\n  Day of Week Distribution:")
    for d, c in dow.value_counts().items():
        print(f"    {d:<12} {c:>5}")
    
    # Monthly
    monthly = valid_dates.dt.to_period('M')
    print(f"\n  Monthly Distribution (top 10):")
    for m, c in monthly.value_counts().sort_index().head(10).items():
        print(f"    {m}  {c:>5}")

# ===== 6. Spatial Analysis =====
print("\n[6/10] Spatial Analysis:")
if 'latitude' in df.columns and 'longitude' in df.columns:
    lat = pd.to_numeric(df['latitude'], errors='coerce')
    lng = pd.to_numeric(df['longitude'], errors='coerce')
    
    valid_gps = (lat > 0) & (lng > 0) & (lat < 90) & (lng < 180)
    print(f"  Valid GPS coordinates: {valid_gps.sum()} / {len(df)} ({valid_gps.sum()/len(df)*100:.1f}%)")
    print(f"  Latitude range: {lat[valid_gps].min():.6f} to {lat[valid_gps].max():.6f}")
    print(f"  Longitude range: {lng[valid_gps].min():.6f} to {lng[valid_gps].max():.6f}")
    
    # Check end coordinates
    end_lat = pd.to_numeric(df['endlatitude'], errors='coerce')
    end_lng = pd.to_numeric(df['endlongitude'], errors='coerce')
    valid_end = (end_lat > 0) & (end_lng > 0)
    print(f"  Valid end GPS coordinates: {valid_end.sum()} / {len(df)} ({valid_end.sum()/len(df)*100:.1f}%)")

# ===== 7. Duration Analysis =====
print("\n[7/10] Event Duration Analysis:")
if 'start_datetime' in df.columns and 'end_datetime' in df.columns:
    has_both = df['start_datetime'].notna() & df['end_datetime'].notna()
    print(f"  Events with both start AND end time: {has_both.sum()} / {len(df)}")
    
    if has_both.sum() > 0:
        duration = (df.loc[has_both, 'end_datetime'] - df.loc[has_both, 'start_datetime']).dt.total_seconds() / 60
        duration_positive = duration[duration > 0]
        print(f"  Duration stats (minutes, positive only, n={len(duration_positive)}):")
        print(f"    Min:    {duration_positive.min():.1f}")
        print(f"    25th:   {duration_positive.quantile(0.25):.1f}")
        print(f"    Median: {duration_positive.median():.1f}")
        print(f"    75th:   {duration_positive.quantile(0.75):.1f}")
        print(f"    Max:    {duration_positive.max():.1f}")
        print(f"    Mean:   {duration_positive.mean():.1f}")

    # Alternative: created_date to closed_datetime
    has_resolution = df['created_date'].notna() & df['closed_datetime'].notna()
    print(f"\n  Events with created + closed time: {has_resolution.sum()} / {len(df)}")
    if has_resolution.sum() > 0:
        resolution_time = (df.loc[has_resolution, 'closed_datetime'] - df.loc[has_resolution, 'created_date']).dt.total_seconds() / 60
        resolution_positive = resolution_time[resolution_time > 0]
        print(f"  Resolution time stats (minutes, n={len(resolution_positive)}):")
        print(f"    Min:    {resolution_positive.min():.1f}")
        print(f"    25th:   {resolution_positive.quantile(0.25):.1f}")
        print(f"    Median: {resolution_positive.median():.1f}")
        print(f"    75th:   {resolution_positive.quantile(0.75):.1f}")
        print(f"    Max:    {resolution_positive.max():.1f}")
        print(f"    Mean:   {resolution_positive.mean():.1f}")

    # created_date to resolved_datetime
    has_resolved = df['created_date'].notna() & df['resolved_datetime'].notna()
    print(f"\n  Events with created + resolved time: {has_resolved.sum()} / {len(df)}")
    if has_resolved.sum() > 0:
        resolved_time = (df.loc[has_resolved, 'resolved_datetime'] - df.loc[has_resolved, 'created_date']).dt.total_seconds() / 60
        resolved_positive = resolved_time[resolved_time > 0]
        print(f"  Resolution time stats (minutes, n={len(resolved_positive)}):")
        print(f"    Min:    {resolved_positive.min():.1f}")
        print(f"    25th:   {resolved_positive.quantile(0.25):.1f}")
        print(f"    Median: {resolved_positive.median():.1f}")
        print(f"    75th:   {resolved_positive.quantile(0.75):.1f}")
        print(f"    Max:    {resolved_positive.max():.1f}")
        print(f"    Mean:   {resolved_positive.mean():.1f}")

# ===== 8. Missing Values Summary =====
print("\n[8/10] Missing Values Summary (sorted by % missing):")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({'Missing Count': missing, 'Missing %': missing_pct})
missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing %', ascending=False)
print(missing_df.to_string())

# ===== 9. Duplicate Analysis =====
print("\n[9/10] Duplicate Analysis:")
print(f"  Exact duplicates: {df.duplicated().sum()}")
print(f"  Duplicate IDs: {df['id'].duplicated().sum()}")

# ===== 10. Cross-Feature Analysis =====
print("\n[10/10] Cross-Feature Analysis:")

# Event cause by event type
print("\n  Event Cause by Event Type:")
cross = pd.crosstab(df['event_cause'], df['event_type'])
print(cross.to_string())

# Priority by event cause
print("\n  Priority by Event Cause:")
cross2 = pd.crosstab(df['event_cause'], df['priority'])
print(cross2.to_string())

# Road closure by event cause
print("\n  Road Closure by Event Cause:")
cross3 = pd.crosstab(df['event_cause'], df['requires_road_closure'])
print(cross3.to_string())

# ===== Save Column Documentation =====
print("\n" + "=" * 80)
print("SAVING RESULTS...")

# Save column info as JSON for programmatic use
with open(OUTPUT_DIR / "column_documentation.json", "w") as f:
    json.dump(column_info, f, indent=2)

print(f"  Saved column documentation to {OUTPUT_DIR / 'column_documentation.json'}")

# ===== Summary =====
print("\n" + "=" * 80)
print("DATASET SUMMARY FOR ASTRA")
print("=" * 80)
print(f"""
Dataset: ASTraM Bengaluru Traffic Event Data (Anonymized)
Records: {len(df):,}
Columns: {len(df.columns)}
Event Types: {df['event_type'].nunique()} ({', '.join(df['event_type'].unique())})
Event Causes: {df['event_cause'].nunique()}
Corridors: {df['corridor'].nunique()}
Police Stations: {df['police_station'].nunique()}
Zones: {df['zone'].nunique()}
Junctions: {df['junction'].nunique()}

KEY OBSERVATIONS:
1. This is a REAL operational dataset from Bengaluru Traffic Police (ASTraM system)
2. Contains both planned and unplanned events
3. GPS coordinates available for start (and sometimes end) locations
4. Multiple timestamps: created, start, end, modified, closed, resolved
5. Rich categorical features: corridor, zone, junction, police_station
6. Vehicle information for breakdown events
7. Descriptions in both English and Kannada
8. Priority levels present (High/Low)
9. Road closure requirement tracked
10. Authentication and user tracking present

PREDICTION TARGET RECOMMENDATION:
- Primary: Resolution Time (minutes from creation to closure/resolution)
- This maps to "Impact Duration" in the proposal
- Can derive risk scores from event cause + corridor + time features
- The Decision Intelligence Engine will recommend deployments based on predictions

MISSING DATA STRATEGY:
- end_datetime: Mostly NULL for unplanned events → use closed_datetime instead
- Vehicle fields: Only relevant for breakdown events → conditional features
- Zone/Junction: Some NULL → can be geocoded from GPS coordinates
""")

print("\nEDA COMPLETE!")
