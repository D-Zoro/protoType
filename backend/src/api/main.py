from fastapi import FastAPI, Query 
from src.data_collection.weather_api import WeatherAPIClient

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
