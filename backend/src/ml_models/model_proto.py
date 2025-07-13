
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AirPollutionPredictor:
    def __init__(self, model_save_path: str = "data/models/"):
        self.model_save_path = model_save_path
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.target_columns = ['pm2_5', 'pm10', 'no2', 'o3', 'aqi']
        
        # Create directory if it doesn't exist
        os.makedirs(model_save_path, exist_ok=True)
    
    def prepare_features(self, data: List[Dict]) -> pd.DataFrame:
        """
        Prepare features from collected data for ML model
        """
        features_list = []
        
        for item in data:
            feature_dict = {}
            
            # Weather features
            if 'current_weather' in item:
                weather = item['current_weather']
                feature_dict.update({
                    'temperature': weather.get('temperature', 0),
                    'humidity': weather.get('humidity', 0),
                    'pressure': weather.get('pressure', 0),
                    'wind_speed': weather.get('wind_speed', 0),
                    'wind_direction': weather.get('wind_direction', 0),
                    'visibility': weather.get('visibility', 10000),
                })
                
                # Encode weather condition
                weather_condition = weather.get('weather_condition', 'Clear')
                feature_dict['weather_condition'] = weather_condition
            
            # Air pollution features (current)
            if 'current_pollution' in item:
                pollution = item['current_pollution']
                feature_dict.update({
                    'pm2_5': pollution.get('pm2_5', 0),
                    'pm10': pollution.get('pm10', 0),
                    'no2': pollution.get('no2', 0),
                    'o3': pollution.get('o3', 0),
                    'co': pollution.get('co', 0),
                    'so2': pollution.get('so2', 0),
                    'aqi': pollution.get('aqi', 0)
                })
            
            # Satellite features
            if 'atmospheric' in item and item['atmospheric']:
                sat_data = item['atmospheric']['satellite_data']
                feature_dict.update({
                    'sat_no2': sat_data.get('no2', 0) or 0,
                    'sat_o3': sat_data.get('o3', 0) or 0,
                    'sat_so2': sat_data.get('so2', 0) or 0,
                    'sat_co': sat_data.get('co', 0) or 0,
                    'sat_aerosol': sat_data.get('aerosol', 0) or 0
                })
            
            # Surface features
            if 'surface' in item and item['surface']:
                surface = item['surface']
                feature_dict.update({
                    'ndvi': surface.get('ndvi', 0) or 0,
                    'surface_temp': surface.get('surface_temperature', 0) or 0,
                    'vegetation_health': surface.get('vegetation_health', 0) or 0
                })
            
            # Location features
            if 'location' in item:
                location = item['location']
                feature_dict.update({
                    'latitude': location.get('lat', 0),
                    'longitude': location.get('lon', 0)
                })
            
            # Time features
            if 'collected_at' in item:
                timestamp = pd.to_datetime(item['collected_at'])
                feature_dict.update({
                    'hour': timestamp.hour,
                    'day_of_week': timestamp.dayofweek,
                    'month': timestamp.month,
                    'is_weekend': 1 if timestamp.dayofweek >= 5 else 0
                })
            
            # Historical pollution trends (simple moving averages)
            if 'historical_pollution' in item and item['historical_pollution']:
                hist_data = item['historical_pollution']
                hist_df = pd.DataFrame(hist_data)
                
                if not hist_df.empty:
                    feature_dict.update({
                        'hist_pm2_5_avg': hist_df['pm2_5'].mean(),
                        'hist_pm10_avg': hist_df['pm10'].mean(),
                        'hist_no2_avg': hist_df['no2'].mean(),
                        'hist_o3_avg': hist_df['o3'].mean(),
                        'hist_aqi_avg': hist_df['aqi'].mean()
                    })
            
            features_list.append(feature_dict)
        
        df = pd.DataFrame(features_list)
        
        # Handle categorical variables
        if 'weather_condition' in df.columns:
            le = LabelEncoder()
            df['weather_condition_encoded'] = le.fit_transform(df['weather_condition'].fillna('Clear'))
            df.drop('weather_condition', axis=1, inplace=True)
        
        # Fill missing values
        df = df.fillna(0)
        
        return df
    
    def train_models(self, training_data: List[Dict]) -> Dict:
        """
        Train multiple models for different pollutants
        """
        print("Preparing features...")
        df = self.prepare_features(training_data)
        
        if df.empty:
            print("No data to train on!")
            return {}
        
        print(f"Training on {len(df)} samples with {len(df.columns)} features")
        
        # Store feature columns
        self.feature_columns = [col for col in df.columns if col not in self.target_columns]
        
        X = df[self.feature_columns]
        
        results = {}
        
        for target in self.target_columns:
            if target not in df.columns:
                print(f"Target {target} not found in data, skipping...")
                continue
                
            y = df[target]
            
            # Remove samples where target is 0 (likely missing data)
            valid_indices = y > 0
            X_valid = X[valid_indices]
            y_valid = y[valid_indices]
            
            if len(X_valid) < 10:
                print(f"Not enough valid data for {target}, skipping...")
                continue
            
            print(f"Training model for {target}...")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_valid, y_valid, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train ensemble of models
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
            }
            
            best_model = None
            best_score = float('-inf')
            
            for model_name, model in models.items():
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test_scaled)
                score = r2_score(y_test, y_pred)
                
                print(f"  {model_name} R² score: {score:.4f}")
                
                if score > best_score:
                    best_score = score
                    best_model = model
            
            # Store best model and scaler
            self.models[target] = best_model
            self.scalers[target] = scaler
            
            # Calculate additional metrics
            y_pred_final = best_model.predict(X_test_scaled)
            results[target] = {
                'r2_score': best_score,
                'mse': mean_squared_error(y_test, y_pred_final),
                'mae': mean_absolute_error(y_test, y_pred_final),
                'samples_used': len(X_valid)
            }
            
            print(f"  Final R² score: {best_score:.4f}")
            print(f"  MSE: {results[target]['mse']:.4f}")
            print(f"  MAE: {results[target]['mae']:.4f}")
        
        # Save models
        self.save_models()
        
        return results
    
    def predict(self, data: Dict) -> Dict:
        """
        Make predictions for new data
        """
        # Prepare features
        df = self.prepare_features([data])
        
        if df.empty:
            return {}
        
        X = df[self.feature_columns]
        
        predictions = {}
        
        for target in self.target_columns:
            if target in self.models and target in self.scalers:
                # Scale features
                X_scaled = self.scalers[target].transform(X)
                
                # Make prediction
                pred = self.models[target].predict(X_scaled)[0]
                predictions[target] = max(0, pred)  # Ensure non-negative
        
        return predictions
    
    def save_models(self):
        """Save trained models and scalers"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for target in self.models:
            # Save model
            model_path = os.path.join(self.model_save_path, f"{target}_model_{timestamp}.pkl")
            joblib.dump(self.models[target], model_path)
            
            # Save scaler
            scaler_path = os.path.join(self.model_save_path, f"{target}_scaler_{timestamp}.pkl")
            joblib.dump(self.scalers[target], scaler_path)
            
            print(f"Saved {target} model and scaler")
        
        # Save feature columns
        feature_path = os.path.join(self.model_save_path, f"feature_columns_{timestamp}.pkl")
        joblib.dump(self.feature_columns, feature_path)
    
    def load_models(self, timestamp: str = None):
        """Load previously trained models"""
        if timestamp is None:
            # Find the most recent model
            model_files = [f for f in os.listdir(self.model_save_path) if f.endswith('.pkl')]
            if not model_files:
                print("No saved models found!")
                return False
            
            # Get the most recent timestamp
            timestamps = set()
            for f in model_files:
                if '_model_' in f:
                    ts = f.split('_model_')[1].replace('.pkl', '')
                    timestamps.add(ts)
            
            if not timestamps:
                print("No valid model files found!")
                return False
            
            timestamp = max(timestamps)
        
        print(f"Loading models from {timestamp}...")
        
        # Load feature columns
        feature_path = os.path.join(self.model_save_path, f"feature_columns_{timestamp}.pkl")
        if os.path.exists(feature_path):
            self.feature_columns = joblib.load(feature_path)
        
        # Load models and scalers
        for target in self.target_columns:
            model_path = os.path.join(self.model_save_path, f"{target}_model_{timestamp}.pkl")
            scaler_path = os.path.join(self.model_save_path, f"{target}_scaler_{timestamp}.pkl")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.models[target] = joblib.load(model_path)
                self.scalers[target] = joblib.load(scaler_path)
                print(f"Loaded {target} model and scaler")
        
        return True
    
    def retrain_with_new_data(self, new_data: List[Dict], existing_data: List[Dict] = None):
        """
        Retrain models with new data (incremental learning simulation)
        """
        print("Retraining models with new data...")
        
        # Combine new data with existing data
        if existing_data:
            combined_data = existing_data + new_data
        else:
            combined_data = new_data
        
        # Retrain models
        results = self.train_models(combined_data)
        
        print("Retraining completed!")
        return results
    
    def get_feature_importance(self, target: str) -> Dict:
        """Get feature importance for a specific target"""
        if target not in self.models:
            return {}
        
        model = self.models[target]
        if hasattr(model, 'feature_importances_'):
            importance_dict = {}
            for i, feature in enumerate(self.feature_columns):
                importance_dict[feature] = model.feature_importances_[i]
            
            # Sort by importance
            sorted_importance = dict(sorted(importance_dict.items(), 
                                          key=lambda x: x[1], reverse=True))
            
            return sorted_importance
        
        return {}

# Example usage and testing
if __name__ == "__main__":
    # Create dummy data for testing
    def create_dummy_data(n_samples: int = 100):
        """Create dummy data for testing"""
        import random
        
        dummy_data = []
        for i in range(n_samples):
            # Create realistic dummy data
            temp = random.uniform(10, 40)  # Temperature 10-40°C
            humidity = random.uniform(30, 90)  # Humidity 30-90%
            
            # Simulate pollution based on weather (simplified)
            base_pollution = 50 + (temp - 25) * 2 + (humidity - 50) * 0.5
            
            data_point = {
                'current_weather': {
                    'temperature': temp,
                    'humidity': humidity,
                    'pressure': random.uniform(980, 1020),
                    'wind_speed': random.uniform(0, 15),
                    'wind_direction': random.uniform(0, 360),
                    'visibility': random.uniform(1000, 10000),
                    'weather_condition': random.choice(['Clear', 'Clouds', 'Rain', 'Mist'])
                },
                'current_pollution': {
                    'pm2_5': max(0, base_pollution + random.uniform(-20, 20)),
                    'pm10': max(0, base_pollution * 1.5 + random.uniform(-30, 30)),
                    'no2': max(0, base_pollution * 0.8 + random.uniform(-15, 15)),
                    'o3': max(0, base_pollution * 0.6 + random.uniform(-10, 10)),
                    'aqi': max(1, int(base_pollution + random.uniform(-20, 20)))
                },
                'location': {
                    'lat': 28.6139 + random.uniform(-0.1, 0.1),
                    'lon': 77.2090 + random.uniform(-0.1, 0.1)
                },
                'collected_at': datetime.now() - timedelta(days=random.randint(0, 30)),
                'historical_pollution': [
                    {
                        'pm2_5': max(0, base_pollution + random.uniform(-10, 10)),
                        'pm10': max(0, base_pollution * 1.5 + random.uniform(-15, 15)),
                        'no2': max(0, base_pollution * 0.8 + random.uniform(-8, 8)),
                        'o3': max(0, base_pollution * 0.6 + random.uniform(-5, 5)),
                        'aqi': max(1, int(base_pollution + random.uniform(-10, 10)))
                    } for _ in range(5)
                ]
            }
            
            dummy_data.append(data_point)
        
        return dummy_data
    
    # Test the model
    print("Creating dummy data...")
    training_data = create_dummy_data(200)
    
    print("Initializing model...")
    predictor = AirPollutionPredictor()
    
    print("Training models...")
    results = predictor.train_models(training_data)
    
    print("\nTraining results:")
    for target, metrics in results.items():
        print(f"{target}: R² = {metrics['r2_score']:.4f}, MAE = {metrics['mae']:.4f}")
    
    # Test prediction
    print("\nTesting prediction...")
    test_data = create_dummy_data(1)[0]
    predictions = predictor.predict(test_data)
    
    print("Predictions:")
    for target, value in predictions.items():
        print(f"{target}: {value:.2f}")
    
    # Test feature importance
    print("\nFeature importance for PM2.5:")
    importance = predictor.get_feature_importance('pm2_5')
    for feature, imp in list(importance.items())[:5]:
        print(f"{feature}: {imp:.4f}")
    
    print("\nModel training and testing completed!")
