"""
ASTRA - Sprint 1: Remaining EDA Analysis (temporal + duration + cross-feature)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_PATH = Path(r"d:\AA\Projects\ASTRA\data\raw\Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv")
df = pd.read_csv(DATA_PATH, low_memory=False)

# Parse timestamps
for col in ['start_datetime', 'end_datetime', 'created_date', 'modified_datetime', 'closed_datetime', 'resolved_datetime']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)

# ===== TEMPORAL =====
print("TEMPORAL ANALYSIS")
print("=" * 60)

valid_dates = df['start_datetime'].dropna()
print(f"Date Range: {valid_dates.min()} to {valid_dates.max()}")
print(f"Span: {(valid_dates.max() - valid_dates.min()).days} days")

hours = valid_dates.dt.hour
print(f"\nHour Distribution:")
hour_counts = hours.value_counts().sort_index()
for h, c in hour_counts.items():
    bar = "#" * (c // 20)
    print(f"  {h:02d}:00  {c:>5}  {bar}")

dow = valid_dates.dt.day_name()
print(f"\nDay of Week:")
for d in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:
    c = (dow == d).sum()
    print(f"  {d:<12} {c:>5}")

monthly = valid_dates.dt.to_period('M')
print(f"\nMonthly:")
for m, c in monthly.value_counts().sort_index().items():
    print(f"  {m}  {c:>5}")

# ===== DURATION =====
print("\nDURATION ANALYSIS")
print("=" * 60)

# Method 1: start to end
has_both = df['start_datetime'].notna() & df['end_datetime'].notna()
print(f"Events with start + end: {has_both.sum()} / {len(df)}")
if has_both.sum() > 0:
    dur = (df.loc[has_both, 'end_datetime'] - df.loc[has_both, 'start_datetime']).dt.total_seconds() / 60
    dur_pos = dur[dur > 0]
    print(f"  Duration (minutes, n={len(dur_pos)}):")
    print(f"    Min={dur_pos.min():.1f}, Median={dur_pos.median():.1f}, Mean={dur_pos.mean():.1f}, Max={dur_pos.max():.1f}")

# Method 2: created to closed
has_closed = df['created_date'].notna() & df['closed_datetime'].notna()
print(f"\nEvents with created + closed: {has_closed.sum()} / {len(df)}")
if has_closed.sum() > 0:
    res = (df.loc[has_closed, 'closed_datetime'] - df.loc[has_closed, 'created_date']).dt.total_seconds() / 60
    res_pos = res[(res > 0) & (res < 100000)]  # Filter extreme outliers
    print(f"  Resolution time (minutes, n={len(res_pos)}):")
    print(f"    Min={res_pos.min():.1f}, 25th={res_pos.quantile(0.25):.1f}, Median={res_pos.median():.1f}")
    print(f"    75th={res_pos.quantile(0.75):.1f}, Max={res_pos.max():.1f}, Mean={res_pos.mean():.1f}")
    
    # Distribution buckets
    print(f"\n  Resolution Time Buckets:")
    bins = [0, 15, 30, 60, 120, 240, 480, 1440, float('inf')]
    labels = ['<15min', '15-30min', '30-60min', '1-2hr', '2-4hr', '4-8hr', '8-24hr', '>24hr']
    buckets = pd.cut(res_pos, bins=bins, labels=labels)
    for label, count in buckets.value_counts().sort_index().items():
        pct = count / len(res_pos) * 100
        print(f"    {label:<12} {count:>5}  ({pct:.1f}%)")

# Method 3: created to resolved
has_resolved = df['created_date'].notna() & df['resolved_datetime'].notna()
print(f"\nEvents with created + resolved: {has_resolved.sum()} / {len(df)}")

# ===== CROSS-FEATURE =====
print("\nCROSS-FEATURE ANALYSIS")
print("=" * 60)

# Resolution time by event cause
if has_closed.sum() > 0:
    df_closed = df[has_closed].copy()
    df_closed['resolution_min'] = (df_closed['closed_datetime'] - df_closed['created_date']).dt.total_seconds() / 60
    df_closed = df_closed[(df_closed['resolution_min'] > 0) & (df_closed['resolution_min'] < 100000)]
    
    print("\nMedian Resolution Time by Event Cause:")
    cause_res = df_closed.groupby('event_cause')['resolution_min'].agg(['median', 'mean', 'count'])
    cause_res = cause_res.sort_values('median', ascending=False)
    for cause, row in cause_res.iterrows():
        print(f"  {cause:<25} median={row['median']:>8.1f}min  mean={row['mean']:>8.1f}min  n={int(row['count'])}")

    print("\nMedian Resolution Time by Priority:")
    pri_res = df_closed.groupby('priority')['resolution_min'].agg(['median', 'mean', 'count'])
    for pri, row in pri_res.iterrows():
        print(f"  {pri:<10} median={row['median']:>8.1f}min  mean={row['mean']:>8.1f}min  n={int(row['count'])}")

    print("\nMedian Resolution Time by Corridor (top 15):")
    corr_res = df_closed.groupby('corridor')['resolution_min'].agg(['median', 'mean', 'count'])
    corr_res = corr_res[corr_res['count'] >= 10].sort_values('median', ascending=False).head(15)
    for corr, row in corr_res.iterrows():
        print(f"  {corr:<25} median={row['median']:>8.1f}min  mean={row['mean']:>8.1f}min  n={int(row['count'])}")

    print("\nRoad Closure by Event Cause:")
    closure = pd.crosstab(df['event_cause'], df['requires_road_closure'], normalize='index') * 100
    if 'True' in closure.columns or True in closure.columns:
        col = True if True in closure.columns else 'True'
        closure_sorted = closure.sort_values(col, ascending=False)
        for cause, row in closure_sorted.iterrows():
            pct = row.get(col, row.get('True', 0))
            print(f"  {cause:<25} {pct:.1f}% require closure")

# ===== FEATURE IMPORTANCE ASSESSMENT =====
print("\n\nFEATURE IMPORTANCE ASSESSMENT FOR ASTRA")
print("=" * 60)
print("""
FEATURE                         IMPORTANCE    REASON
-----------------------------------------------------------
event_cause                     CRITICAL      Primary driver of risk level
corridor                        CRITICAL      Location-based risk assessment
requires_road_closure           HIGH          Direct impact indicator
priority                        HIGH          Expert-assigned importance
event_type (planned/unplanned)  HIGH          Predictability of event
start_datetime (hour, dow)      HIGH          Temporal patterns
police_station                  MEDIUM        Spatial clustering
zone                            MEDIUM        Area-level risk
junction                        MEDIUM        Intersection-specific risk
latitude/longitude              MEDIUM        Spatial features
veh_type                        LOW-MEDIUM    Only for breakdown events
description                     LOW           Free text, needs NLP
direction                       LOW           Sparse data (99.5% missing)
map_file                        NONE          100% missing
comment                         NONE          100% missing
meta_data                       NONE          100% missing
""")

# Unique corridors and junctions for reference
print("\nALL CORRIDORS:")
for c in sorted(df['corridor'].dropna().unique()):
    count = (df['corridor'] == c).sum()
    print(f"  {c}: {count}")

print("\nTOP 30 JUNCTIONS:")
for j, c in df['junction'].value_counts().head(30).items():
    print(f"  {j}: {c}")

print("\nDONE!")
