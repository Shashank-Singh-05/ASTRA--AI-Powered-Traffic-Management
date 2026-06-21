"""ASTRA ML Configuration."""

import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "processed_events.csv"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "raw").mkdir(exist_ok=True)
(DATA_DIR / "processed").mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Random Seed for Reproducibility
RANDOM_STATE = 42

# Timezone config
TIMEZONE = 'Asia/Kolkata'

# Peak hours (IST)
MORNING_PEAK_START = 8
MORNING_PEAK_END = 10
EVENING_PEAK_START = 17
EVENING_PEAK_END = 20

# Feature Mappings
EVENT_CAUSE_SEVERITY = {
    'vip_movement': 10,
    'protest': 9,
    'public_event': 8,
    'procession': 7,
    'accident': 7,
    'tree_fall': 6,
    'congestion': 6,
    'construction': 5,
    'water_logging': 5,
    'road_conditions': 4,
    'pot_holes': 3,
    'vehicle_breakdown': 3,
    'debris': 4,
    'Debris': 4,
    'Fog / Low Visibility': 5,
    'test_demo': 1,
    'others': 3
}

CORRIDOR_IMPORTANCE = {
    'CBD 1': 10,
    'CBD 2': 10,
    'Bellary Road 1': 9,
    'Bellary Road 2': 9,
    'Hosur Road': 8,
    'ORR North 1': 7,
    'ORR North 2': 7,
    'ORR East 1': 7,
    'ORR East 2': 7,
    'ORR West 1': 7,
    'Mysore Road': 7,
    'Tumkur Road': 6,
    'Old Madras Road': 6,
    'Bannerghata Road': 6,
    'West of Chord Road': 6,
    'Magadi Road': 5,
    'Old Airport Road': 5,
    'Hennur Main Road': 4,
    'Airport New South Road': 4,
    'IRR(Thanisandra road)': 4,
    'Varthur Road': 4,
    'Non-corridor': 3
}

# Target column names
TARGET_RISK_SCORE = 'risk_score'
TARGET_RESOLUTION_MINUTES = 'resolution_minutes'
TARGET_RESOLUTION_CATEGORY = 'resolution_category'
