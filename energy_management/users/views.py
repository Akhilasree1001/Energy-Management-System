from django.shortcuts import render, HttpResponse
from .forms import UserRegistrationForm
from django.contrib import messages
from .models import UserRegistrationModel
from django.conf import settings
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from imblearn.under_sampling import RandomUnderSampler
from .ml_models import (
    AnomalyDetector, AutoencoderAnomalyDetector,
    DeviceScheduler, EnergyPredictor, LSTMEnergyPredictor
)
from .energy_utils import (
    generate_sample_energy_data, detect_energy_theft,
    calculate_energy_cost, get_energy_saving_tips,
    prepare_weather_forecast
)
from datetime import datetime
import json

# Global variables
global_model = None
features = None
label_encoder = None
scaler = None  # Add global scaler
anomaly_detector = None
device_scheduler = DeviceScheduler()
energy_predictor = None

# Utility function to load and preprocess dataset
def load_and_preprocess_dataset():
    path = os.path.join(settings.MEDIA_ROOT, 'smart_building_energy_dataset.csv')
    df = pd.read_csv(path)
    # Ensure numerical columns are properly typed
    numerical_cols = ['Temperature', 'Humidity', 'Wind_Speed', 'Time_of_Day', 'Day_of_Week']
    for col in numerical_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # Drop rows with missing values
    df = df.dropna()
    return df

# User Registration View
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have been successfully registered')
            return render(request, 'UserRegistrations.html', {'form': UserRegistrationForm()})
        else:
            messages.error(request, 'Email or Mobile already existed.')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})

# User Login Check View
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if check.status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                return render(request, 'users/UserHome.html')
            else:
                messages.warning(request, 'Your account is not activated.')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid Login ID or Password.')
    return render(request, 'UserLogin.html')

# User Home View
def UserHome(request):
    return render(request, 'users/UserHome.html')

# Dataset View
def DatasetView(request):
    try:
        df = load_and_preprocess_dataset()
        # Limit to first 100 rows for display
        df_html = df.head(100).to_html(classes='table table-striped')
        return render(request, 'users/viewdataset.html', {'data': df_html})
    except Exception as e:
        return HttpResponse(f"Error loading dataset: {str(e)}")

# Training View
def training(request):
    global global_model, features, label_encoder, scaler
    try:
        df = load_and_preprocess_dataset()

        # Define target and features
        target_column = 'Device_Selected'
        features = ['Temperature', 'Humidity', 'Wind_Speed', 'Time_of_Day', 'Day_of_Week']

        # Encode target variable
        label_encoder = LabelEncoder()
        df[target_column] = label_encoder.fit_transform(df[target_column])

        # Separate features and target
        X = df[features]
        y = df[target_column]

        # Normalize numerical features BEFORE balancing
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Balance dataset using undersampling
        rus = RandomUnderSampler(random_state=42)
        X_balanced, y_balanced = rus.fit_resample(X_scaled, y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42)

        # Train RandomForest with tuned parameters
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42
        )
        model.fit(X_train, y_train)
        global_model = model

        # Predictions and accuracy
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        report = classification_report(y_test, preds, target_names=label_encoder.classes_, output_dict=True)
        df_report = pd.DataFrame(report).transpose()

        # Cross-validation score
        cv_scores = cross_val_score(model, X_balanced, y_balanced, cv=5)
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()

        return render(request, 'users/training.html', {
            'nb': df_report.to_html(classes='table table-bordered'),
            'acc': acc,
            'cv_mean': cv_mean,
            'cv_std': cv_std,
            'selected_features': features
        })

    except Exception as e:
        return HttpResponse(f"Error during training: {str(e)}")
def prediction(request):
    global global_model, features, label_encoder, scaler

    hours = list(range(24))

    if request.method == 'POST':
        try:
            if not features:
                return render(request, 'users/predictForm1.html', {
                    'output': "Error: No features found. Please train the model first!",
                    'features': [],
                    'hours': hours,
                })

            if global_model is None:
                return render(request, 'users/predictForm1.html', {
                    'output': "Error: Model not trained yet. Please train the model first!",
                    'features': features,
                    'hours': hours,
                })

            if scaler is None:
                return render(request, 'users/predictForm1.html', {
                    'output': "Error: Scaler not initialized. Please train the model first!",
                    'features': features,
                    'hours': hours,
                })

            input_data = {}
            for feature in features:
                value = request.POST.get(feature)
                if value is None:
                    raise ValueError(f"Missing value for {feature}")
                try:
                    input_data[feature] = float(value)
                except ValueError:
                    raise ValueError(f"Invalid numerical value for {feature}: {value}")

            input_df = pd.DataFrame([input_data])

            # Use the global scaler fitted during training
            input_scaled = scaler.transform(input_df)

            # Predict
            prediction = global_model.predict(input_scaled)[0]
            prediction_proba = global_model.predict_proba(input_scaled)[0]
            prediction_label = label_encoder.inverse_transform([prediction])[0]

            # Get all class probabilities
            all_classes = label_encoder.classes_
            class_probabilities = {all_classes[i]: round(prediction_proba[i] * 100, 2) for i in range(len(all_classes))}

            return render(request, 'users/predictForm1.html', {
                'output': f'Predicted Device: {prediction_label}',
                'probabilities': class_probabilities,
                'features': features,
                'hours': hours,
            })
        except Exception as e:
            return render(request, 'users/predictForm1.html', {
                'output': f"Error: {str(e)}",
                'features': features if features else [],
                'hours': hours,
            })

    # If method == GET
    return render(request, 'users/predictForm1.html', {
        'features': features if features else [],
        'hours': hours,
    })


# ==================== NEW FEATURES ====================

# Feature 1: Anomaly Detection
def anomaly_detection_view(request):
    """Anomaly Detection for Energy Theft or Faults"""
    global anomaly_detector

    if request.method == 'POST':
        try:
            # Get input data
            consumption = float(request.POST.get('consumption', 0))
            temperature = float(request.POST.get('temperature', 25))
            humidity = float(request.POST.get('humidity', 60))
            occupancy = int(request.POST.get('occupancy', 1))

            # Create input dataframe with correct column names
            input_data = pd.DataFrame([[consumption, temperature, humidity, occupancy]],
                                     columns=['energy_consumption', 'temperature', 'humidity', 'occupancy'])

            # Initialize and train detector if not already trained
            if anomaly_detector is None:
                # Generate training data
                training_data = generate_sample_energy_data(days=30)
                train_features = training_data[['energy_consumption', 'temperature', 'humidity', 'occupancy']]

                anomaly_detector = AnomalyDetector(contamination=0.1)
                anomaly_detector.train(train_features)

            # Detect anomaly
            result = anomaly_detector.detect(input_data)[0]

            if result == -1:
                alert_type = "danger"
                message = "⚠️ ANOMALY DETECTED! Abnormal energy usage pattern."
                recommendation = "Possible causes: Energy theft, faulty equipment, or unusual consumption."
            else:
                alert_type = "success"
                message = "✓ Normal energy consumption pattern."
                recommendation = "Energy usage is within expected range."

            # Calculate historical average
            historical_avg = 50  # Default average
            is_theft, theft_msg = detect_energy_theft(consumption, historical_avg)

            return render(request, 'users/anomaly_detection.html', {
                'result': message,
                'alert_type': alert_type,
                'recommendation': recommendation,
                'theft_alert': theft_msg,
                'consumption': consumption,
                'temperature': temperature,
                'humidity': humidity,
                'occupancy': occupancy
            })

        except Exception as e:
            return render(request, 'users/anomaly_detection.html', {
                'error': f"Error: {str(e)}"
            })

    return render(request, 'users/anomaly_detection.html')


# Feature 2: Smart Device Scheduling
def device_scheduling_view(request):
    """Smart Device Scheduling"""
    global device_scheduler

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_device':
            device_name = request.POST.get('device_name')
            preferred_time = int(request.POST.get('preferred_time', 18))
            duration = int(request.POST.get('duration', 1))

            device_scheduler.add_device(device_name, preferred_time, duration)

            return render(request, 'users/device_scheduling.html', {
                'message': f"Device '{device_name}' added successfully!",
                'schedules': device_scheduler.schedules
            })

        elif action == 'optimize':
            # Generate sample energy prices (lower at night)
            energy_prices = [0.08 if h < 6 or h > 22 else 0.12 if 10 <= h <= 16 else 0.10 for h in range(24)]

            # Generate sample occupancy data
            occupancy_data = [0 if h < 6 or h > 23 else 1 if 18 <= h <= 22 else 0.5 for h in range(24)]

            optimized = device_scheduler.optimize_schedule(energy_prices, occupancy_data)

            return render(request, 'users/device_scheduling.html', {
                'schedules': device_scheduler.schedules,
                'optimized': optimized,
                'energy_prices': energy_prices,
                'message': "Schedule optimized successfully!"
            })

    current_hour = datetime.now().hour
    active_devices = device_scheduler.get_current_schedule(current_hour)

    return render(request, 'users/device_scheduling.html', {
        'schedules': device_scheduler.schedules,
        'active_devices': active_devices,
        'current_hour': current_hour
    })


# Feature 3: Energy Consumption Prediction
def energy_prediction_view(request):
    """Energy Consumption Prediction"""
    global energy_predictor

    if request.method == 'POST':
        try:
            action = request.POST.get('action')

            if action == 'train':
                # Generate training data
                training_data = generate_sample_energy_data(days=60)

                # Prepare features - create 'hour' column first
                training_data['hour'] = pd.to_datetime(training_data['timestamp']).dt.hour
                X = training_data[['hour', 'temperature', 'humidity', 'occupancy']].values
                y = training_data['energy_consumption'].values

                # Initialize and train predictor
                energy_predictor = EnergyPredictor()
                energy_predictor.train(X, y)

                return render(request, 'users/energy_prediction.html', {
                    'message': "Model trained successfully!",
                    'trained': True
                })

            elif action == 'predict':
                if energy_predictor is None or not energy_predictor.is_trained:
                    return render(request, 'users/energy_prediction.html', {
                        'error': "Please train the model first!"
                    })

                # Get weather forecast
                weather_forecast = prepare_weather_forecast()

                # Predict next 24 hours
                predictions = []
                for hour in range(24):
                    features = pd.DataFrame([[
                        hour,
                        weather_forecast['temperature'][hour],
                        weather_forecast['humidity'][hour],
                        1  # Assume occupied
                    ]], columns=['hour', 'temperature', 'humidity', 'occupancy'])

                    pred = energy_predictor.predict(features, model_type='ensemble')[0]
                    predictions.append({
                        'hour': hour,
                        'predicted_consumption': round(pred, 2),
                        'temperature': round(weather_forecast['temperature'][hour], 1),
                        'estimated_cost': round(calculate_energy_cost(pred), 2)
                    })

                total_predicted = sum([p['predicted_consumption'] for p in predictions])
                total_cost = sum([p['estimated_cost'] for p in predictions])

                # Get energy saving tips
                tips = get_energy_saving_tips(total_predicted)

                return render(request, 'users/energy_prediction.html', {
                    'predictions': predictions,
                    'total_predicted': round(total_predicted, 2),
                    'total_cost': round(total_cost, 2),
                    'tips': tips,
                    'trained': True
                })

        except Exception as e:
            return render(request, 'users/energy_prediction.html', {
                'error': f"Error: {str(e)}"
            })

    return render(request, 'users/energy_prediction.html')
