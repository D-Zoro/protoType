# src/api/main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import os
import sys
from datetime import datetime
import asyncio
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_collection.weather_api import WeatherAPIClient
from data_collection.google_earth import GoogleEarthClient
from ml_models.model_proto import AirPollutionPredictor

app = FastAPI(title="Air Pollution Prediction API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
weather_client = WeatherAPIClient()
earth_client = GoogleEarthClient()
predictor = AirPollutionPredictor()

# In-memory storage for collected data (in production, use a proper database)
collected_data = []

# Pydantic models for request/response
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

class PredictionResponse(BaseModel):
    predictions: Dict[str, float]
    location: Dict[str, float]
    timestamp: str
    data_sources: List[str]

class TrainingRequest(BaseModel):
    locations: List[Dict[str, float]]
    days_back: int = 7

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    models_loaded: bool
    data_points: int

class RootRespose(BaseModel):
    message: str
    version: str 
    endpoints: List[str]

@app.get("/", response_model=RootRespose)
async def root():
    """Root endpoint"""
    return {
        "message": "Air Pollution Prediction API",
        "version": "1.0.0",
        "endpoints": [
            "/predict",
            "/train",
            "/health",
            "/data-collection"
        ]
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        models_loaded=len(predictor.models) > 0,
        data_points=len(collected_data)
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_pollution(request: LocationRequest):
    """
    Predict air pollution for a given location
    """
    try:
        lat, lon = request.latitude, request.longitude
        
        # Collect real-time data
        print(f"Collecting data for location: {lat}, {lon}")
        
        # Get weather data
        weather_data = weather_client.collect_comprehensive_data(lat, lon)
        if not weather_data:
            raise HTTPException(status_code=500, detail="Failed to collect weather data")
        
        data_sources = ["weather_api"]
        
        # Try to get satellite data (this might fail if not properly authenticated)
        try:
            satellite_data = earth_client.get_comprehensive_satellite_data(lat, lon)
            if satellite_data:
                weather_data.update(satellite_data)
                data_sources.append("satellite_data")
        except Exception as e:
            print(f"Satellite data collection failed: {e}")
            # Continue without satellite data
        
        # Make prediction
        if len(predictor.models) == 0:
            # Try to load existing models
            if not predictor.load_models():
                raise HTTPException(
                    status_code=500, 
                    detail="No trained models available. Please train models first."
                )
        
        predictions = predictor.predict(weather_data)
        
        if not predictions:
            raise HTTPException(
                status_code=500, 
                detail="Failed to make predictions. Check if models are properly trained."
            )
        
        # Store the data for future retraining
        collected_data.append(weather_data)
        
        return PredictionResponse(
            predictions=predictions,
            location={"latitude": lat, "longitude": lon},
            timestamp=datetime.now().isoformat(),
            data_sources=data_sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/train")
async def train_models(background_tasks: BackgroundTasks, request: TrainingRequest):
    """
    Train or retrain models with new data
    """
    try:
        # Start training in background
        background_tasks.add_task(
            train_models_background, 
            request.locations, 
            request.days_back
        )
        
        return {
            "message": "Model training started in background",
            "locations": len(request.locations),
            "status": "training_started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

async def train_models_background(locations: List[Dict[str, float]], days_back: int):
    """
    Background task for training models
    """
    print(f"Starting background training for {len(locations)} locations")
    
    training_data = []
    
    for location in locations:
        try:
            lat, lon = location["latitude"], location["longitude"]
            
            # Collect comprehensive data
            weather_data = weather_client.collect_comprehensive_data(lat, lon)
            if weather_data:
                # Try to add satellite data
                try:
                    satellite_data = earth_client.get_comprehensive_satellite_data(lat, lon)
                    if satellite_data:
                        weather_data.update(satellite_data)
                except:
                    pass
                
                training_data.append(weather_data)
                
            # Add small delay to avoid hitting API limits
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Error collecting data for {location}: {e}")
            continue
    
    # Add existing collected data
    if collected_data:
        training_data.extend(collected_data)
    
    if training_data:
        print(f"Training with {len(training_data)} data points")
        results = predictor.train_models(training_data)
        print(f"Training completed: {results}")
    else:
        print("No training data collected")

@app.get("/data-collection")
async def get_collected_data():
    """
    Get information about collected data
    """
    return {
        "total_data_points": len(collected_data),
        "latest_collection": collected_data[-1]["collected_at"] if collected_data else None,
        "models_available": list(predictor.models.keys()),
        "feature_columns": len(predictor.feature_columns) if predictor.feature_columns else 0
    }

@app.post("/retrain")
async def retrain_models(background_tasks: BackgroundTasks):
    """
    Retrain models with existing collected data
    """
    if not collected_data:
        raise HTTPException(status_code=400, detail="No data available for retraining")
    
    background_tasks.add_task(retrain_models_background)
    
    return {
        "message": "Model retraining started",
        "data_points": len(collected_data),
        "status": "retraining_started"
    }

async def retrain_models_background():
    """
    Background task for retraining models
    """
    print(f"Retraining models with {len(collected_data)} data points")
    
    try:
        results = predictor.train_models(collected_data)
        print(f"Retraining completed: {results}")
    except Exception as e:
        print(f"Retraining failed: {e}")

@app.get("/predictions/batch")
async def batch_predictions(locations: str):
    """
    Get predictions for multiple locations
    locations should be a JSON string of [{"latitude": lat, "longitude": lon}, ...]
    """
    try:
        locations_list = json.loads(locations)
        
        if len(predictor.models) == 0:
            predictor.load_models()
        
        results = []
        
        for location in locations_list:
            try:
                lat, lon = location["latitude"], location["longitude"]
                
                # Collect data
                weather_data = weather_client.collect_comprehensive_data(lat, lon)
                if weather_data:
                    predictions = predictor.predict(weather_data)
                    results.append({
                        "location": location,
                        "predictions": predictions,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Small delay to avoid API limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                results.append({
                    "location": location,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@app.get("/model-info")
async def get_model_info():
    """
    Get information about the trained models
    """
    info = {
        "available_models": list(predictor.models.keys()),
        "feature_columns": predictor.feature_columns,
        "model_save_path": predictor.model_save_path
    }
    
    # Get feature importance for each model
    for target in predictor.models.keys():
        importance = predictor.get_feature_importance(target)
        info[f"{target}_feature_importance"] = dict(list(importance.items())[:10])
    
    return info

# Auto-load models on startup
@app.on_event("startup")
async def startup_event():
    """
    Load models on startup if available
    """
    print("Starting Air Pollution Prediction API...")
    
    # Try to load existing models
    try:
        if predictor.load_models():
            print("Models loaded successfully")
        else:
            print("No existing models found")
    except Exception as e:
        print(f"Error loading models: {e}")

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
