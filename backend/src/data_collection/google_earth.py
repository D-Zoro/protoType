
import ee
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

class GoogleEarthClient:
    def __init__(self, service_account_path: str = None):
        """
        Initialize Google Earth Engine client
        
        Args:
            service_account_path: Path to service account JSON file
        """
        self.service_account_path = service_account_path or os.getenv('GEE_SERVICE_ACCOUNT_PATH')
        print(self.service_account_path)
        print("test")
        self.initialize_ee()
    
    def initialize_ee(self):
        """Initialize Earth Engine with authentication"""
        try:
            if self.service_account_path and os.path.exists(self.service_account_path):
                # Use service account authentication
                credentials = ee.ServiceAccountCredentials(
                    email=None,
                    key_file=self.service_account_path
                )
                ee.Initialize(credentials)
            else:
                # Use default authentication (requires ee.Authenticate() to be run once)
                ee.Initialize()
            print("Earth Engine initialized successfully")
        except Exception as e:
            print(f"Error initializing Earth Engine: {e}")
            print("You may need to run: earthengine authenticate")
    
    def get_sentinel5p_data(self, lat: float, lon: float, days: int = 30) -> Dict:
        """
        Get Sentinel-5P atmospheric data (air quality from satellite)
        
        Args:
            lat: Latitude
            lon: Longitude  
            days: Number of days to look back
        """
        try:
            # Define the area of interest (a small region around the point)
            point = ee.Geometry.Point([lon, lat])
            region = point.buffer(5000)  # 5km buffer
            
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get different atmospheric measurements
            datasets = {
                'no2': 'COPERNICUS/S5P/NRTI/L3_NO2',
                'o3': 'COPERNICUS/S5P/NRTI/L3_O3', 
                'so2': 'COPERNICUS/S5P/NRTI/L3_SO2',
                'co': 'COPERNICUS/S5P/NRTI/L3_CO',
                'aerosol': 'COPERNICUS/S5P/NRTI/L3_AER_AI'
            }
            
            results = {}
            
            for pollutant, dataset_id in datasets.items():
                try:
                    # Get the dataset
                    dataset = ee.ImageCollection(dataset_id)
                    
                    # Filter by date and location
                    filtered = dataset.filterDate(
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d')
                    ).filterBounds(region)
                    
                    # Get the mean value over the time period
                    mean_image = filtered.mean()
                    
                    # Sample the data at our point
                    sample = mean_image.sample(
                        region=region,
                        scale=1000,  # 1km resolution
                        numPixels=100
                    ).getInfo()
                    
                    if sample['features']:
                        # Extract the relevant band value
                        properties = sample['features'][0]['properties']
                        results[pollutant] = self._extract_main_value(properties, pollutant)
                    else:
                        results[pollutant] = None
                        
                except Exception as e:
                    print(f"Error getting {pollutant} data: {e}")
                    results[pollutant] = None
            
            return {
                'satellite_data': results,
                'location': {'lat': lat, 'lon': lon},
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'collected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting satellite data: {e}")
            return None
    
    def _extract_main_value(self, properties: Dict, pollutant: str) -> Optional[float]:
        """Extract the main measurement value for each pollutant type"""
        value_mappings = {
            'no2': 'NO2_column_number_density',
            'o3': 'O3_column_number_density', 
            'so2': 'SO2_column_number_density',
            'co': 'CO_column_number_density',
            'aerosol': 'absorbing_aerosol_index'
        }
        
        band_name = value_mappings.get(pollutant)
        if band_name and band_name in properties:
            return properties[band_name]
        
        # If specific band not found, try to get any numeric value
        for key, value in properties.items():
            if isinstance(value, (int, float)) and not key.startswith('system:'):
                return value
        
        return None
    
    def get_landsat_data(self, lat: float, lon: float, days: int = 30) -> Dict:
        """
        Get Landsat imagery data (for environmental context)
        """
        try:
            point = ee.Geometry.Point([lon, lat])
            region = point.buffer(5000)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get Landsat 8 data
            landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
            
            # Filter and get cloud-free images
            filtered = landsat.filterDate(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            ).filterBounds(region).filter(
                ee.Filter.lt('CLOUD_COVER', 20)
            )
            
            if filtered.size().getInfo() > 0:
                # Get the median image
                median_image = filtered.median()
                
                # Sample the data
                sample = median_image.sample(
                    region=region,
                    scale=30,  # 30m resolution for Landsat
                    numPixels=50
                ).getInfo()
                
                if sample['features']:
                    properties = sample['features'][0]['properties']
                    return {
                        'ndvi': self._calculate_ndvi(properties),
                        'surface_temperature': properties.get('ST_B10'),
                        'vegetation_health': properties.get('SR_B4'),  # Red band
                        'collected_at': datetime.now().isoformat()
                    }
            
            return None
            
        except Exception as e:
            print(f"Error getting Landsat data: {e}")
            return None
    
    def _calculate_ndvi(self, properties: Dict) -> Optional[float]:
        """Calculate NDVI from Landsat bands"""
        try:
            nir = properties.get('SR_B5')  # Near-infrared
            red = properties.get('SR_B4')  # Red
            
            if nir and red and red != 0:
                return (nir - red) / (nir + red)
            return None
        except:
            return None
    
    def get_comprehensive_satellite_data(self, lat: float, lon: float) -> Dict:
        """Get all available satellite data for a location"""
        try:
            # Get atmospheric data
            atmospheric_data = self.get_sentinel5p_data(lat, lon, days=7)
            
            # Get land surface data
            landsat_data = self.get_landsat_data(lat, lon, days=30)
            
            return {
                'atmospheric': atmospheric_data,
                'surface': landsat_data,
                'location': {'lat': lat, 'lon': lon},
                'collected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error collecting comprehensive satellite data: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Test the client
    client = GoogleEarthClient()
    
    # Delhi coordinates
    lat, lon = 28.6139, 77.2090
    
    print("Collecting satellite data...")
    data = client.get_comprehensive_satellite_data(lat, lon)
    
    if data:
        print("Satellite data collected successfully!")
        if data['atmospheric']:
            print(f"NO2 levels: {data['atmospheric']['satellite_data'].get('no2', 'N/A')}")
            print(f"O3 levels: {data['atmospheric']['satellite_data'].get('o3', 'N/A')}")
        if data['surface']:
            print(f"NDVI: {data['surface'].get('ndvi', 'N/A')}")
    else:
        print("Failed to collect satellite data")
