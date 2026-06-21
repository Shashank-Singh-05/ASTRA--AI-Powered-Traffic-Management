"""ASTRA Data Cleaning Pipeline."""

import pandas as pd
import numpy as np
from ml import config

def load_and_clean_data(file_path: str = config.RAW_DATA_PATH) -> pd.DataFrame:
    """
    Load raw CSV data and perform initial cleaning.
    """
    print(f"Loading data from {file_path}")
    df = pd.read_csv(file_path, low_memory=False)

    # 1. Drop 100% missing columns
    cols_to_drop = ['map_file', 'comment', 'meta_data']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')

    # 2. Handle missing values
    df['corridor'] = df['corridor'].fillna('Non-corridor')
    df['priority'] = df['priority'].fillna('Low')
    df['requires_road_closure'] = df['requires_road_closure'].fillna(False)

    # Combine 'Debris' and 'debris'
    df['event_cause'] = df['event_cause'].replace({'Debris': 'debris'})

    # 3. Handle Timestamps (Convert to IST)
    datetime_cols = ['start_datetime', 'end_datetime', 'created_date', 'closed_datetime', 'resolved_datetime']
    for col in datetime_cols:
        if col in df.columns:
            # Convert to UTC then to IST
            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
            df[col] = df[col].dt.tz_convert(config.TIMEZONE)

    # 4. Calculate Resolution Minutes
    # Use closed_datetime if end_datetime is null
    if 'closed_datetime' in df.columns and 'created_date' in df.columns:
        resolution_delta = df['closed_datetime'] - df['created_date']
        df['resolution_minutes'] = resolution_delta.dt.total_seconds() / 60.0
        
        # Filter negative or extremely long resolution times (outliers)
        # keeping values between 0 and 100000 minutes as seen in EDA
        df.loc[(df['resolution_minutes'] <= 0) | (df['resolution_minutes'] > 100000), 'resolution_minutes'] = np.nan

    # 5. Filter invalid GPS coordinates (Bengaluru roughly 12-14 Lat, 76-79 Lng)
    if 'latitude' in df.columns and 'longitude' in df.columns:
        valid_gps = (df['latitude'] >= 12.0) & (df['latitude'] <= 14.0) & \
                    (df['longitude'] >= 76.0) & (df['longitude'] <= 79.0)
        df.loc[~valid_gps, ['latitude', 'longitude']] = np.nan
        
    return df

if __name__ == "__main__":
    df = load_and_clean_data()
    print(f"Data cleaned. Shape: {df.shape}")
    # print(df.head())
