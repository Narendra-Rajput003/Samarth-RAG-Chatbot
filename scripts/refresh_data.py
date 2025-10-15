# scripts/refresh_data.py
"""Synchronous data refresh script. Run: python scripts/refresh_data.py"""
import os
import pandas as pd
from src.utils.logger import logger

def refresh_crop_data(year):
    """Download/process crop CSV for year. Runs synchronously."""
    # Placeholder URL; replace with real data.gov.in API/endpoint
    url = f"https://data.gov.in/resource/district-wise-crop-production-{year}"
    try:
        df = pd.read_csv(url)
        for state in df['State'].unique():
            chunk = df[df['State'] == state].to_json(orient='records')
            with open(f"data/processed/crop_{state}_{year}.json", 'w') as f:
                f.write(chunk)
        logger.info(f"Refreshed crop data for {year}")
    except Exception as e:
        logger.error(f"Error refreshing {year}: {e}")

if __name__ == "__main__":
    for y in range(2013, 2023):
        refresh_crop_data(y)