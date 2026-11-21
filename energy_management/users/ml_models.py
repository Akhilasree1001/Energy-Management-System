"""
Machine Learning Models for Energy Management System
Features:
1. Anomaly Detection (Isolation Forest & Autoencoder)
2. Smart Device Scheduling (Reinforcement Learning)
3. Energy Consumption Prediction (LSTM, Random Forest, XGBoost)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import torch
import torch.nn as nn
from datetime import datetime, timedelta
import pickle
import os

# ==================== ANOMALY DETECTION ====================

class AnomalyDetector:
    """Detects abnormal energy usage using Isolation Forest"""

    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def train(self, data):
        """Train anomaly detection model"""
        scaled_data = self.scaler.fit_transform(data)
        self.model.fit(scaled_data)
        self.is_trained = True

    def detect(self, data):
        """Detect anomalies. Returns -1 for anomaly, 1 for normal"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        scaled_data = self.scaler.transform(data)
        predictions = self.model.predict(scaled_data)
        return predictions

    def save_model(self, path):
        """Save trained model"""
        with open(path, 'wb') as f:
            pickle.dump({'model': self.model, 'scaler': self.scaler}, f)

    def load_model(self, path):
        """Load trained model"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = True


class AutoencoderAnomalyDetector(nn.Module):
    """Autoencoder-based anomaly detection"""

    def __init__(self, input_dim):
        super(AutoencoderAnomalyDetector, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 4)
        )
        self.decoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim)
        )
        self.threshold = None
        self.scaler = StandardScaler()

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

    def train_model(self, data, epochs=50, lr=0.001):
        """Train autoencoder"""
        scaled_data = self.scaler.fit_transform(data)
        tensor_data = torch.FloatTensor(scaled_data)

        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)

        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self(tensor_data)
            loss = criterion(outputs, tensor_data)
            loss.backward()
            optimizer.step()

        # Calculate threshold
        with torch.no_grad():
            reconstructed = self(tensor_data)
            mse = torch.mean((tensor_data - reconstructed) ** 2, dim=1)
            self.threshold = torch.mean(mse) + 2 * torch.std(mse)

    def detect_anomaly(self, data):
        """Detect anomalies based on reconstruction error"""
        scaled_data = self.scaler.transform(data)
        tensor_data = torch.FloatTensor(scaled_data)

        with torch.no_grad():
            reconstructed = self(tensor_data)
            mse = torch.mean((tensor_data - reconstructed) ** 2, dim=1)
            anomalies = (mse > self.threshold).numpy()

        return anomalies


# ==================== SMART DEVICE SCHEDULING ====================

class DeviceScheduler:
    """Smart device scheduling using time-series analysis"""

    def __init__(self):
        self.schedules = {}
        self.user_preferences = {}

    def add_device(self, device_name, preferred_time, duration_hours=1):
        """Add device to scheduling system"""
        self.schedules[device_name] = {
            'preferred_time': preferred_time,
            'duration': duration_hours,
            'active': False
        }

    def optimize_schedule(self, energy_prices, occupancy_data):
        """Optimize device schedule based on energy prices and occupancy"""
        optimized = {}

        for device, config in self.schedules.items():
            # Find optimal time slot (lowest price + occupancy match)
            preferred_hour = config['preferred_time']
            duration = config['duration']

            # Search window around preferred time
            search_window = range(max(0, preferred_hour - 2), min(24, preferred_hour + 3))

            best_time = preferred_hour
            best_score = float('inf')

            for hour in search_window:
                if hour < len(energy_prices):
                    score = energy_prices[hour]
                    if hour < len(occupancy_data):
                        score -= occupancy_data[hour] * 0.5  # Prefer when occupied

                    if score < best_score:
                        best_score = score
                        best_time = hour

            optimized[device] = {
                'scheduled_time': best_time,
                'duration': duration,
                'estimated_cost': best_score * duration
            }

        return optimized

    def get_current_schedule(self, current_hour):
        """Get devices that should be active at current hour"""
        active_devices = []

        for device, config in self.schedules.items():
            start = config['preferred_time']
            end = start + config['duration']

            if start <= current_hour < end:
                active_devices.append(device)

        return active_devices


# ==================== ENERGY CONSUMPTION PREDICTION ====================

class EnergyPredictor:
    """Predict future energy consumption using multiple ML models"""

    def __init__(self):
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self, df, weather_data=None, occupancy_data=None):
        """Prepare features for prediction"""
        features = df.copy()

        # Add time-based features
        if 'timestamp' in features.columns:
            features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
            features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
            features['month'] = pd.to_datetime(features['timestamp']).dt.month

        # Add weather features if available
        if weather_data is not None:
            features = features.merge(weather_data, on='timestamp', how='left')

        # Add occupancy features if available
        if occupancy_data is not None:
            features = features.merge(occupancy_data, on='timestamp', how='left')

        return features

    def train(self, X, y):
        """Train prediction models"""
        X_scaled = self.scaler.fit_transform(X)

        # Train Random Forest
        self.rf_model.fit(X_scaled, y)

        # Train XGBoost
        self.xgb_model.fit(X_scaled, y)

        self.is_trained = True

    def predict(self, X, model_type='ensemble'):
        """Predict energy consumption"""
        if not self.is_trained:
            raise ValueError("Models not trained yet")

        X_scaled = self.scaler.transform(X)

        if model_type == 'rf':
            return self.rf_model.predict(X_scaled)
        elif model_type == 'xgb':
            return self.xgb_model.predict(X_scaled)
        else:  # ensemble
            rf_pred = self.rf_model.predict(X_scaled)
            xgb_pred = self.xgb_model.predict(X_scaled)
            return (rf_pred + xgb_pred) / 2

    def predict_next_day(self, current_data, weather_forecast):
        """Predict next 24 hours of energy consumption"""
        predictions = []

        for hour in range(24):
            features = {
                'hour': hour,
                'day_of_week': (datetime.now().weekday() + 1) % 7,
                'month': datetime.now().month,
                'temperature': weather_forecast.get('temperature', [25] * 24)[hour],
                'humidity': weather_forecast.get('humidity', [60] * 24)[hour],
            }

            # Add previous consumption as feature
            if current_data is not None and len(current_data) > 0:
                features['prev_consumption'] = current_data[-1]

            X = pd.DataFrame([features])
            pred = self.predict(X, model_type='ensemble')
            predictions.append(pred[0])

        return predictions


class LSTMEnergyPredictor(nn.Module):
    """LSTM-based energy consumption predictor"""

    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super(LSTMEnergyPredictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.scaler = StandardScaler()

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)

        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

    def train_model(self, X, y, epochs=50, lr=0.001):
        """Train LSTM model"""
        X_scaled = self.scaler.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)

        X_tensor = torch.FloatTensor(X_scaled)
        y_tensor = torch.FloatTensor(y).reshape(-1, 1)

        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)

        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()

            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

    def predict(self, X):
        """Predict energy consumption"""
        X_scaled = self.scaler.transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
        X_tensor = torch.FloatTensor(X_scaled)

        with torch.no_grad():
            predictions = self(X_tensor)

        return predictions.numpy()
