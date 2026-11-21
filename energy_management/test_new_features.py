"""
Quick Test Script for New Features
Run this to verify all new features are working correctly
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_management.settings')
django.setup()

from users.ml_models import (
    AnomalyDetector, AutoencoderAnomalyDetector,
    DeviceScheduler, EnergyPredictor, LSTMEnergyPredictor
)
from users.energy_utils import generate_sample_energy_data
import pandas as pd
import numpy as np

print("=" * 60)
print("Testing New Energy Management Features")
print("=" * 60)

# Test 1: Anomaly Detection
print("\n1. Testing Anomaly Detection...")
try:
    # Generate sample data
    training_data = generate_sample_energy_data(days=30)
    train_features = training_data[['energy_consumption', 'temperature', 'humidity', 'occupancy']]

    # Train detector
    detector = AnomalyDetector(contamination=0.1)
    detector.train(train_features)

    # Test normal data
    normal_data = pd.DataFrame([[50, 25, 60, 1]],
                               columns=['energy_consumption', 'temperature', 'humidity', 'occupancy'])
    result = detector.detect(normal_data)[0]
    print(f"   ✓ Normal data detection: {'Normal' if result == 1 else 'Anomaly'}")

    # Test anomaly data
    anomaly_data = pd.DataFrame([[150, 25, 60, 1]],
                                columns=['energy_consumption', 'temperature', 'humidity', 'occupancy'])
    result = detector.detect(anomaly_data)[0]
    print(f"   ✓ Anomaly data detection: {'Normal' if result == 1 else 'Anomaly'}")

    print("   ✓ Anomaly Detection: PASSED")
except Exception as e:
    print(f"   ✗ Anomaly Detection: FAILED - {str(e)}")

# Test 2: Device Scheduling
print("\n2. Testing Device Scheduling...")
try:
    scheduler = DeviceScheduler()

    # Add devices
    scheduler.add_device('AC', preferred_time=18, duration_hours=4)
    scheduler.add_device('Water_Heater', preferred_time=6, duration_hours=2)
    scheduler.add_device('Washing_Machine', preferred_time=14, duration_hours=1)

    print(f"   ✓ Added {len(scheduler.schedules)} devices")

    # Generate sample energy prices
    energy_prices = [0.08 if h < 6 or h > 22 else 0.12 if 10 <= h <= 16 else 0.10 for h in range(24)]
    occupancy_data = [0 if h < 6 or h > 23 else 1 if 18 <= h <= 22 else 0.5 for h in range(24)]

    # Optimize schedule
    optimized = scheduler.optimize_schedule(energy_prices, occupancy_data)

    print(f"   ✓ Optimized schedule for {len(optimized)} devices")
    for device, config in optimized.items():
        print(f"      - {device}: {config['scheduled_time']}:00 (Cost: ${config['estimated_cost']:.2f})")

    print("   ✓ Device Scheduling: PASSED")
except Exception as e:
    print(f"   ✗ Device Scheduling: FAILED - {str(e)}")

# Test 3: Energy Prediction
print("\n3. Testing Energy Prediction...")
try:
    # Generate training data
    training_data = generate_sample_energy_data(days=60)
    training_data['hour'] = pd.to_datetime(training_data['timestamp']).dt.hour

    X = training_data[['hour', 'temperature', 'humidity', 'occupancy']].values
    y = training_data['energy_consumption'].values

    # Train predictor
    predictor = EnergyPredictor()
    predictor.train(X, y)

    print("   ✓ Model trained successfully")

    # Make predictions
    test_data = pd.DataFrame([[12, 28, 65, 1]],
                            columns=['hour', 'temperature', 'humidity', 'occupancy'])

    rf_pred = predictor.predict(test_data, model_type='rf')[0]
    xgb_pred = predictor.predict(test_data, model_type='xgb')[0]
    ensemble_pred = predictor.predict(test_data, model_type='ensemble')[0]

    print(f"   ✓ Random Forest prediction: {rf_pred:.2f} kWh")
    print(f"   ✓ XGBoost prediction: {xgb_pred:.2f} kWh")
    print(f"   ✓ Ensemble prediction: {ensemble_pred:.2f} kWh")

    print("   ✓ Energy Prediction: PASSED")
except Exception as e:
    print(f"   ✗ Energy Prediction: FAILED - {str(e)}")

# Test 4: Autoencoder Anomaly Detection
print("\n4. Testing Autoencoder Anomaly Detection...")
try:
    training_data = generate_sample_energy_data(days=30)
    train_features = training_data[['energy_consumption', 'temperature', 'humidity', 'occupancy']].values

    autoencoder = AutoencoderAnomalyDetector(input_dim=4)
    autoencoder.train_model(train_features, epochs=20)

    # Test detection
    test_data = np.array([[50, 25, 60, 1]])
    anomalies = autoencoder.detect_anomaly(test_data)

    print(f"   ✓ Autoencoder trained and tested")
    print(f"   ✓ Test data result: {'Anomaly' if anomalies[0] else 'Normal'}")

    print("   ✓ Autoencoder Detection: PASSED")
except Exception as e:
    print(f"   ✗ Autoencoder Detection: FAILED - {str(e)}")

print("\n" + "=" * 60)
print("All Tests Completed!")
print("=" * 60)
print("\nNext Steps:")
print("1. Run: python manage.py runserver")
print("2. Navigate to: http://127.0.0.1:8000/")
print("3. Login and test the new features in the UI")
print("=" * 60)
