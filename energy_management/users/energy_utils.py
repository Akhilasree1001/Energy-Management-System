"""
Utility functions for energy management features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_energy_data(days=30):
    """Generate sample energy consumption data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=days*24, freq='h')

    data = {
        'timestamp': dates,
        'energy_consumption': np.random.normal(50, 10, len(dates)) +
                             np.sin(np.arange(len(dates)) * 2 * np.pi / 24) * 20,
        'temperature': np.random.normal(25, 5, len(dates)),
        'humidity': np.random.normal(60, 10, len(dates)),
        'occupancy': np.random.choice([0, 1], len(dates), p=[0.3, 0.7])
    }

    return pd.DataFrame(data)


def detect_energy_theft(current_consumption, historical_avg, threshold=1.5):
    """Simple rule-based energy theft detection"""
    if current_consumption > historical_avg * threshold:
        return True, f"Alert: Consumption {current_consumption:.2f} kWh exceeds normal by {((current_consumption/historical_avg - 1) * 100):.1f}%"
    return False, "Normal consumption"


def calculate_energy_cost(consumption, price_per_kwh=0.12):
    """Calculate energy cost"""
    return consumption * price_per_kwh


def get_energy_saving_tips(consumption_level):
    """Provide energy saving recommendations"""
    tips = []

    if consumption_level > 100:
        tips.append("High consumption detected. Consider using energy-efficient appliances.")
        tips.append("Schedule high-power devices during off-peak hours.")

    if consumption_level > 150:
        tips.append("Critical: Check for faulty devices or energy theft.")
        tips.append("Consider installing solar panels to offset costs.")

    return tips


def create_time_slots():
    """Create time slots for device scheduling"""
    return {
        'off_peak': list(range(0, 6)) + list(range(22, 24)),
        'mid_peak': list(range(6, 10)) + list(range(16, 22)),
        'peak': list(range(10, 16))
    }


def get_optimal_schedule_time(device_type, current_hour):
    """Get optimal time to schedule a device"""
    time_slots = create_time_slots()

    # Prefer off-peak hours for high-power devices
    if device_type in ['AC', 'Heater', 'Water_Heater']:
        if current_hour in time_slots['peak']:
            return time_slots['off_peak'][0]  # Suggest first off-peak hour

    return current_hour


def prepare_weather_forecast():
    """Generate sample weather forecast for next 24 hours"""
    hours = 24
    base_temp = 25

    forecast = {
        'temperature': [base_temp + np.sin(i * np.pi / 12) * 5 for i in range(hours)],
        'humidity': [60 + np.random.randint(-10, 10) for _ in range(hours)],
        'wind_speed': [np.random.uniform(5, 15) for _ in range(hours)]
    }

    return forecast
