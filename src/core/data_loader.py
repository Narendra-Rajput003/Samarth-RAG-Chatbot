# src/core/data_loader.py
"""Enhanced data loader for government datasets with cross-domain integration."""
import pandas as pd
import json
from typing import List, Dict, Tuple
from src.utils.logger import logger
from src.config.settings import settings
from src.core.data_gov_client import DataGovClient

# Crop name standardization
CROP_MAPPING = {
    "PADDY": "Rice",
    "JOWAR": "Sorghum",
    "BAJRA": "Pearl Millet",
    "MAIZE": "Maize",
    "RAGI": "Finger Millet",
    "WHEAT": "Wheat",
    "BARLEY": "Barley",
    "GRAM": "Chickpea",
    "TUR": "Pigeon Pea",
    "MOONG": "Green Gram",
    "URAD": "Black Gram",
    "COTTON": "Cotton",
    "SUGARCANE": "Sugarcane",
    "JUTE": "Jute",
    "MESTA": "Mesta"
}

# State name standardization
STATE_MAPPING = {
    "TAMILNADU": "Tamil Nadu",
    "UTTARPRADESH": "Uttar Pradesh",
    "WESTBENGAL": "West Bengal",
    "MADHYAPRADESH": "Madhya Pradesh",
    "ANDHRAPRADESH": "Andhra Pradesh"
}

def load_and_chunk_data(file_path: str) -> List[Dict[str, str]]:
    """Process CSV: Normalize, chunk by meaningful groups."""
    try:
        df = pd.read_csv(file_path)

        # Standardize column names and values
        df = _standardize_dataframe(df)

        # Create contextual chunks based on data type
        if _is_agricultural_data(df):
            chunks = _create_agricultural_chunks(df, file_path)
        elif _is_climate_data(df):
            chunks = _create_climate_chunks(df, file_path)
        else:
            chunks = _create_generic_chunks(df, file_path)

        logger.info(f"Chunked {len(chunks)} documents from {file_path}")
        return chunks

    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

def _standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names and values."""
    # Standardize state names
    for col in df.columns:
        if 'state' in col.lower():
            df[col] = df[col].replace(STATE_MAPPING)

    # Standardize crop names
    for col in df.columns:
        if 'crop' in col.lower():
            df[col] = df[col].replace(CROP_MAPPING)

    # Fill missing values
    df = df.fillna("N/A")

    return df

def _is_agricultural_data(df: pd.DataFrame) -> bool:
    """Check if dataframe contains agricultural data."""
    agri_keywords = ['crop', 'production', 'yield', 'area', 'season', 'agriculture']
    return any(keyword in col.lower() for col in df.columns for keyword in agri_keywords)

def _is_climate_data(df: pd.DataFrame) -> bool:
    """Check if dataframe contains climate data."""
    climate_keywords = ['rainfall', 'temperature', 'humidity', 'weather', 'climate', 'monsoon']
    return any(keyword in col.lower() for col in df.columns for keyword in climate_keywords)

def _create_agricultural_chunks(df: pd.DataFrame, file_path: str) -> List[Dict]:
    """Create contextual chunks for agricultural data."""
    chunks = []

    # Check if required columns exist
    required_cols = ['State', 'Year']
    if not all(col in df.columns for col in required_cols):
        logger.warning(f"Missing required columns {required_cols} in {file_path}, skipping agricultural chunking")
        return chunks

    # Group by state and year for better context
    for (state, year), group in df.groupby(['State', 'Year']):
        if pd.isna(state) or pd.isna(year):
            continue

        # Create state-year overview
        state_year_data = group.to_dict('records')
        # Use safe column access for production
        prod_col = 'Production_tonnes' if 'Production_tonnes' in group.columns else 'Production_tonnes'
        if prod_col in group.columns:
            total_prod = group[prod_col].sum()
        else:
            total_prod = 0
        overview_text = f"Agricultural production data for {state} in {year}: "
        overview_text += f"{len(group)} crop records, "
        overview_text += f"total production: {total_prod:,.0f} tonnes"

        chunks.append({
            "text": overview_text,
            "metadata": {
                "state": str(state),
                "year": str(year),
                "type": "agricultural_overview",
                "source": file_path,
                "record_count": len(group)
            }
        })

        # Individual crop records
        for _, row in group.iterrows():
            crop_context = f"In {state} during {year}, {row.get('Crop', 'Unknown')} "
            crop_context += f"was cultivated on {row.get('Area_hectares', 'N/A')} hectares "
            crop_context += f"with yield of {row.get('Yield_tonnes_per_ha', 'N/A')} tonnes/ha "
            crop_context += f"producing {row.get('Production_tonnes', 'N/A')} tonnes total"

            chunks.append({
                "text": crop_context,
                "metadata": {
                    "state": str(state),
                    "year": str(year),
                    "crop": str(row.get('Crop', 'Unknown')),
                    "district": str(row.get('District', 'Unknown')),
                    "type": "crop_production",
                    "source": file_path
                }
            })

    return chunks

def _create_climate_chunks(df: pd.DataFrame, file_path: str) -> List[Dict]:
    """Create contextual chunks for climate data."""
    chunks = []

    # Check if required columns exist
    required_cols = ['State', 'Year']
    if not all(col in df.columns for col in required_cols):
        logger.warning(f"Missing required columns {required_cols} in {file_path}, skipping climate chunking")
        return chunks

    # Group by state and year
    for (state, year), group in df.groupby(['State', 'Year']):
        if pd.isna(state) or pd.isna(year):
            continue

        # Climate overview - use safe column access
        temp_col = 'Avg_Temperature_C' if 'Avg_Temperature_C' in group.columns else None
        rainfall_col = 'Total_Rainfall_mm' if 'Total_Rainfall_mm' in group.columns else None
        humidity_col = 'Humidity_percent' if 'Humidity_percent' in group.columns else None

        overview_text = f"Climate data for {state} in {year}: "
        if temp_col:
            avg_temp = group[temp_col].mean()
            overview_text += f"average temperature {avg_temp:.1f}°C, "
        if rainfall_col:
            total_rainfall = group[rainfall_col].sum()
            overview_text += f"total rainfall {total_rainfall:.0f}mm, "
        if humidity_col:
            avg_humidity = group[humidity_col].mean()
            overview_text += f"average humidity {avg_humidity:.1f}%"

        chunks.append({
            "text": overview_text,
            "metadata": {
                "state": str(state),
                "year": str(year),
                "type": "climate_overview",
                "source": file_path
            }
        })

        # Seasonal data if available
        if 'Season' in group.columns:
            for season in group['Season'].unique():
                season_data = group[group['Season'] == season]
                if not season_data.empty:
                    season_text = f"{state} {season} {year}: "
                    if temp_col and temp_col in season_data.columns:
                        season_text += f"temperature {season_data[temp_col].mean():.1f}°C, "
                    if rainfall_col and rainfall_col in season_data.columns:
                        season_text += f"rainfall {season_data[rainfall_col].sum():.0f}mm"

                    chunks.append({
                        "text": season_text,
                        "metadata": {
                            "state": str(state),
                            "year": str(year),
                            "season": str(season),
                            "type": "seasonal_climate",
                            "source": file_path
                        }
                    })

    return chunks

def _create_generic_chunks(df: pd.DataFrame, file_path: str) -> List[Dict]:
    """Create generic chunks for other data types."""
    chunks = []

    for _, row in df.iterrows():
        # Create meaningful text representation
        text_parts = []
        for col, value in row.items():
            if pd.notna(value) and str(value).lower() not in ['n/a', 'nan', 'null']:
                text_parts.append(f"{col}: {value}")

        text = ", ".join(text_parts)

        if len(text) > settings.max_chunk_size:
            text = text[:settings.max_chunk_size] + "..."

        chunks.append({
            "text": text,
            "metadata": {
                "source": file_path,
                "type": "generic_data"
            }
        })

    return chunks

def get_combined_analysis_data(states: List[str] = None, years: List[int] = None) -> pd.DataFrame:
    """Get combined agricultural and climate data for analysis."""
    client = DataGovClient()
    return client.get_combined_data(states=states, years=years)

def get_crop_trends(crop: str, state: str, years: List[int] = None) -> pd.DataFrame:
    """Get production trends for a specific crop in a state."""
    client = DataGovClient()
    agri_data = client.get_agricultural_data(state=state, crop=crop)
    climate_data = client.get_climate_data(state=state)

    if years:
        agri_data = agri_data[agri_data['Year'].isin(years)]
        climate_data = climate_data[climate_data['Year'].isin(years)]

    # Merge datasets
    merged = pd.merge(agri_data, climate_data, on=['State', 'District', 'Year'], how='inner')

    return merged