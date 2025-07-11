# src/data_collection/weather_api.py
import requests
import os
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional

class WeatherAPIClient:
    def __init__(self, api_key: str = None):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.air_pollution_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        
    def get_current_weather(self, lat: float, lon: float) -> Dict:
        """Get current weather data for given coordinates"""
        url = f"{self.base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_air_pollution_current(self, lat: float, lon: float) -> Dict:
        """Get current air pollution data"""
        url = f"{self.air_pollution_url}/current"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_air_pollution_history(self, lat: float, lon: float, days: int = 30) -> Dict:
        """Get historical air pollution data"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        url = f"{self.air_pollution_url}/history"
        params = {
            'lat': lat,
            'lon': lon,
            'start': int(start_time.timestamp()),
            'end': int(end_time.timestamp()),
            'appid': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_forecast(self, lat: float, lon: float) -> Dict:
        """Get 5-day weather forecast"""
        url = f"{self.base_url}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def process_weather_data(self, weather_data: Dict) -> Dict:
        """Process raw weather data into features for ML model"""
        return {
            'temperature': weather_data['main']['temp'],
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'wind_speed': weather_data['wind']['speed'],
            'wind_direction': weather_data['wind'].get('deg', 0),
            'visibility': weather_data.get('visibility', 10000),
            'weather_condition': weather_data['weather'][0]['main'],
            'timestamp': datetime.fromtimestamp(weather_data['dt'])
        }
    
    def process_air_pollution_data(self, pollution_data: Dict) -> List[Dict]:
        """Process air pollution data"""
        processed_data = []
        
        for item in pollution_data['list']:
            processed_item = {
                'timestamp': datetime.fromtimestamp(item['dt']),
                'aqi': item['main']['aqi'],  # Air Quality Index
                'co': item['components']['co'],  # Carbon monoxide
                'no': item['components']['no'],  # Nitric oxide
                'no2': item['components']['no2'],  # Nitrogen dioxide
                'o3': item['components']['o3'],  # Ozone
                'so2': item['components']['so2'],  # Sulphur dioxide
                'pm2_5': item['components']['pm2_5'],  # PM2.5
                'pm10': item['components']['pm10'],  # PM10
                'nh3': item['components']['nh3']  # Ammonia
            }
            processed_data.append(processed_item)
        
        return processed_data
    
    def collect_comprehensive_data(self, lat: float, lon: float) -> Dict:
        """Collect all available data for a location"""
        try:
            # Get current weather
            current_weather = self.get_current_weather(lat, lon)
            weather_features = self.process_weather_data(current_weather)
            
            # Get current air pollution
            current_pollution = self.get_air_pollution_current(lat, lon)
            pollution_features = self.process_air_pollution_data(current_pollution)
            
            # Get historical pollution data
            historical_pollution = self.get_air_pollution_history(lat, lon, days=7)
            historical_features = self.process_air_pollution_data(historical_pollution)
            
            return {
                'current_weather': weather_features,
                'current_pollution': pollution_features[0] if pollution_features else {},
                'historical_pollution': historical_features,
                'location': {'lat': lat, 'lon': lon},
                'collected_at': datetime.now()
            }
            
        except Exception as e:
            print(f"Error collecting data: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Test with coordinates (example: Delhi, India)
    client = WeatherAPIClient()
    
    # Delhi coordinates
    lat, lon = 28.6139, 77.2090
    
    data = client.collect_comprehensive_data(lat, lon)
    if data:
        print("Data collected successfully!")
        print(f"Current AQI: {data['current_pollution'].get('aqi', 'N/A')}")
        print(f"PM2.5: {data['current_pollution'].get('pm2_5', 'N/A')}")
        print(f"Temperature: {data['current_weather']['temperature']}°C")
    else:
        print("Failed to collect data")
