
from fastapi import FastAPI, Query 
from src.data_collection.weather_api import WeatherAPIClient
from src.data_collection.google_earth import GoogleEarthClient

app = FastAPI()
client = WeatherAPIClient()

@app.get("/")
def read_root():
            return {"message": "Backend is alvie"}

@app.get("/weather")
def get_weather_data( 
    lat: float = Query(...,description="Latitude"),
    lon: float = Query(...,description="Longitude")
):
    data = client.collect_comprehensive_data(lat, lon)
    if not data:
        return{
            "status":"error",
            "message":"Failed to collectdata"
        }
    return {
        "status" : "success",
        "location": data['location'],
        "weather": data['current_weather'],
        "pollution": data['current_pollution']
    }

@app.get("/google-earth")
def test_earth_engine(lat:float=28.6139, lon: float = 77.2090):
    """
    Test route to check if Earth Engine and satellite data collection work
    Default coordinates: New Delhi (28.6139, 77.2090)
    """
    try:
        client = GoogleEarthClient()
        data = client.get_comprehensive_satellite_data(lat, lon)
        
        if not data:
            return {"status": "error", "message": "Failed to collect satellite data"}

        return {
            "status": "success",
            "location": data["location"],
            "atmospheric": data["atmospheric"]["satellite_data"],
            "surface": data["surface"]
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

