# src/core/data_gov_client.py
"""Data.gov.in API client for accessing government datasets."""
import requests
import pandas as pd
import json
from typing import List, Dict, Optional
import os
from datetime import datetime
from src.utils.logger import logger

class DataGovClient:
    """Client for accessing data.gov.in API endpoints."""

    BASE_URL = "https://api.data.gov.in"
    AGRICULTURE_API = "/resource/agricultural-production"
    CLIMATE_API = "/resource/climate-data"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Samarth-RAG/1.0',
            'Accept': 'application/json'
        })

    def get_agricultural_data(self, state: str = None, crop: str = None, year: int = None) -> pd.DataFrame:
        """
        Fetch agricultural production data from Ministry of Agriculture & Farmers Welfare.

        In a real implementation, this would call:
        https://api.data.gov.in/resource/{resource-id}?api-key={api-key}&format=json
        """
        try:
            # For prototype, return sample data
            # In production, this would make actual API calls
            sample_data = self._get_sample_agricultural_data()
            df = pd.DataFrame(sample_data)

            # Apply filters if specified
            if state:
                df = df[df['State'].str.lower() == state.lower()]
            if crop:
                df = df[df['Crop'].str.lower() == crop.lower()]
            if year:
                df = df[df['Year'] == year]

            logger.info(f"Retrieved agricultural data: {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Error fetching agricultural data: {e}")
            return pd.DataFrame()

    def get_climate_data(self, state: str = None, district: str = None, year: int = None) -> pd.DataFrame:
        """
        Fetch climate data from India Meteorological Department.

        In a real implementation, this would call IMD APIs or data.gov.in climate datasets.
        """
        try:
            # For prototype, return sample climate data
            sample_data = self._get_sample_climate_data()
            df = pd.DataFrame(sample_data)

            # Apply filters if specified
            if state:
                df = df[df['State'].str.lower() == state.lower()]
            if district:
                df = df[df['District'].str.lower() == district.lower()]
            if year:
                df = df[df['Year'] == year]

            logger.info(f"Retrieved climate data: {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Error fetching climate data: {e}")
            return pd.DataFrame()

    def _get_sample_agricultural_data(self) -> List[Dict]:
        """Sample agricultural production data for testing."""
        return [
            {
                "State": "Maharashtra", "District": "Pune", "Crop": "Rice", "Season": "Kharif",
                "Year": 2022, "Area_hectares": 1500, "Yield_tonnes_per_ha": 3.2, "Production_tonnes": 4800,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            },
            {
                "State": "Maharashtra", "District": "Pune", "Crop": "Wheat", "Season": "Rabi",
                "Year": 2022, "Area_hectares": 800, "Yield_tonnes_per_ha": 2.8, "Production_tonnes": 2240,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            },
            {
                "State": "Karnataka", "District": "Bangalore", "Crop": "Maize", "Season": "Kharif",
                "Year": 2022, "Area_hectares": 600, "Yield_tonnes_per_ha": 4.1, "Production_tonnes": 2460,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            },
            {
                "State": "Karnataka", "District": "Bangalore", "Crop": "Cotton", "Season": "Kharif",
                "Year": 2022, "Area_hectares": 900, "Yield_tonnes_per_ha": 2.5, "Production_tonnes": 2250,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            },
            {
                "State": "Tamil Nadu", "District": "Coimbatore", "Crop": "Sugarcane", "Season": "Annual",
                "Year": 2022, "Area_hectares": 1200, "Yield_tonnes_per_ha": 85, "Production_tonnes": 102000,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            },
            {
                "State": "Punjab", "District": "Ludhiana", "Crop": "Wheat", "Season": "Rabi",
                "Year": 2022, "Area_hectares": 5000, "Yield_tonnes_per_ha": 4.5, "Production_tonnes": 22500,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            },
            {
                "State": "Punjab", "District": "Ludhiana", "Crop": "Rice", "Season": "Kharif",
                "Year": 2022, "Area_hectares": 3000, "Yield_tonnes_per_ha": 3.8, "Production_tonnes": 11400,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            },
            {
                "State": "Gujarat", "District": "Ahmedabad", "Crop": "Cotton", "Season": "Kharif",
                "Year": 2022, "Area_hectares": 1500, "Yield_tonnes_per_ha": 2.2, "Production_tonnes": 3300,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            },
            # Historical data for trend analysis
            {
                "State": "Maharashtra", "District": "Pune", "Crop": "Rice", "Season": "Kharif",
                "Year": 2021, "Area_hectares": 1450, "Yield_tonnes_per_ha": 3.1, "Production_tonnes": 4495,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            },
            {
                "State": "Maharashtra", "District": "Pune", "Crop": "Rice", "Season": "Kharif",
                "Year": 2020, "Area_hectares": 1400, "Yield_tonnes_per_ha": 3.3, "Production_tonnes": 4620,
                "Source": "Ministry of Agriculture & Farmers Welfare", "Dataset": "Agricultural Production Statistics"
            }
        ]

    def _get_sample_climate_data(self) -> List[Dict]:
        """Sample climate data for testing."""
        return [
            {
                "State": "Maharashtra", "District": "Pune", "Year": 2022,
                "Avg_Temperature_C": 28, "Total_Rainfall_mm": 650, "Humidity_percent": 65,
                "Source": "India Meteorological Department", "Dataset": "District-wise Climate Statistics"
            },
            {
                "State": "Maharashtra", "District": "Pune", "Year": 2021,
                "Avg_Temperature_C": 27, "Total_Rainfall_mm": 580, "Humidity_percent": 62,
                "Source": "India Meteorological Department", "Dataset": "District-wise Climate Statistics"
            },
            {
                "State": "Maharashtra", "District": "Pune", "Year": 2020,
                "Avg_Temperature_C": 29, "Total_Rainfall_mm": 720, "Humidity_percent": 68,
                "Source": "India Meteorological Department", "Dataset": "District-wise Climate Statistics"
            },
            {
                "State": "Karnataka", "District": "Bangalore", "Year": 2022,
                "Avg_Temperature_C": 26, "Total_Rainfall_mm": 720, "Humidity_percent": 70,
                "Source": "India Meteorological Department", "Dataset": "District-wise Climate Statistics"
            },
            {
                "State": "Karnataka", "District": "Bangalore", "Year": 2021,
                "Avg_Temperature_C": 25, "Total_Rainfall_mm": 680, "Humidity_percent": 68,
                "Source": "India Meteorological Department", "Dataset": "District-wise Climate Statistics"
            },
            {
                "State": "Tamil Nadu", "District": "Coimbatore", "Year": 2022,
                "Avg_Temperature_C": 29, "Total_Rainfall_mm": 800, "Humidity_percent": 75,
                "Source": "India Meteorological Department", "Dataset": "District-wise Climate Statistics"
            },
            {
                "State": "Punjab", "District": "Ludhiana", "Year": 2022,
                "Avg_Temperature_C": 18, "Total_Rainfall_mm": 400, "Humidity_percent": 60,
                "Source": "India Meteorological Department", "Dataset": "District-wise Climate Statistics"
            },
            {
                "State": "Punjab", "District": "Ludhiana", "Year": 2021,
                "Avg_Temperature_C": 19, "Total_Rainfall_mm": 450, "Humidity_percent": 58,
                "Source": "India Meteorological Department", "Dataset": "District-wise Climate Statistics"
            },
            {
                "State": "Gujarat", "District": "Ahmedabad", "Year": 2022,
                "Avg_Temperature_C": 31, "Total_Rainfall_mm": 550, "Humidity_percent": 55,
                "Source": "India Meteorological Department", "Dataset": "District-wise Climate Statistics"
            }
        ]

    def get_combined_data(self, states: List[str] = None, years: List[int] = None) -> pd.DataFrame:
        """Get combined agricultural and climate data for analysis."""
        agri_df = self.get_agricultural_data()
        climate_df = self.get_climate_data()

        # Merge datasets on State, District, and Year
        combined_df = pd.merge(
            agri_df,
            climate_df,
            on=['State', 'District', 'Year'],
            how='inner',
            suffixes=('_agri', '_climate')
        )

        # Apply filters if specified
        if states:
            combined_df = combined_df[combined_df['State'].isin(states)]
        if years:
            combined_df = combined_df[combined_df['Year'].isin(years)]

        logger.info(f"Combined dataset: {len(combined_df)} records")
        return combined_df