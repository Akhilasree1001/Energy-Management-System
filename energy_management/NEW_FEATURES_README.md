# Energy Management System - New Features

## Overview
This document describes the three new machine learning features added to the Energy Management System for Smart Buildings.

---

## 🚀 New Features

### 1. Anomaly Detection for Energy Theft or Faults

**Purpose:** Detect abnormal energy usage patterns that may indicate energy theft, equipment faults, or unusual consumption.

**Algorithms Used:**
- **Isolation Forest:** Unsupervised learning algorithm that isolates anomalies
- **Autoencoders:** Neural network-based approach for detecting outliers

**How it Works:**
- Analyzes energy consumption, temperature, humidity, and occupancy data
- Compares current usage against historical patterns
- Triggers alerts when consumption exceeds normal thresholds
- Identifies potential energy theft or faulty equipment

**Access:** Navigate to `Anomaly Detection` in the user menu

**Example Use Case:**
- If power consumption suddenly increases by 50% → System alerts user
- Detects unusual patterns during unoccupied hours
- Identifies malfunctioning appliances consuming excess energy

---

### 2. Smart Device Scheduling

**Purpose:** Automatically schedule appliances to optimize energy costs and efficiency.

**Technologies:**
- **Time-series Analysis:** Analyzes energy price patterns
- **Reinforcement Learning:** Learns optimal scheduling strategies
- **Occupancy-based Optimization:** Schedules based on user presence

**How it Works:**
- Users add devices (AC, Heater, Water Heater, etc.) with preferred times
- System analyzes energy prices (off-peak, mid-peak, peak hours)
- Optimizes schedule to minimize costs while maintaining comfort
- Automatically adjusts based on occupancy patterns

**Access:** Navigate to `Device Scheduling` in the user menu

**Example Use Case:**
- AC scheduled to turn ON at 6 PM before user arrives home
- Water heater runs during off-peak hours (lower electricity rates)
- High-power devices scheduled during cheapest time slots

**Energy Price Periods:**
- **Off-Peak:** 12 AM - 6 AM, 10 PM - 12 AM (Lowest rates: $0.08/kWh)
- **Mid-Peak:** 6 AM - 10 AM, 4 PM - 10 PM (Medium rates: $0.10/kWh)
- **Peak:** 10 AM - 4 PM (Highest rates: $0.12/kWh)

---

### 3. Energy Consumption Prediction

**Purpose:** Predict future energy consumption to help users plan and optimize usage.

**Algorithms Used:**
- **LSTM (Long Short-Term Memory):** Deep learning for time-series patterns
- **Random Forest:** Ensemble learning for robust predictions
- **XGBoost:** Gradient boosting for high accuracy

**How it Works:**
- Trains on historical consumption data
- Considers weather conditions (temperature, humidity, wind speed)
- Analyzes occupancy patterns and time-based features
- Predicts next 24 hours of energy consumption
- Provides cost estimates and energy-saving recommendations

**Access:** Navigate to `Energy Forecast` in the user menu

**Prediction Factors:**
- Weather forecast (temperature, humidity)
- Time of day and day of week
- Historical consumption patterns
- Occupancy status
- Seasonal variations

**Example Use Case:**
- Predict tomorrow's energy usage: 1,200 kWh
- Estimated cost: $144.00
- Recommendations: Use high-power devices during off-peak hours

---

## 📁 File Structure

```
energy_management/
├── users/
│   ├── ml_models.py              # ML models (Anomaly Detection, Scheduling, Prediction)
│   ├── energy_utils.py           # Utility functions
│   ├── views.py                  # Updated with new feature views
│   └── templates/
│       └── users/
│           ├── anomaly_detection.html
│           ├── device_scheduling.html
│           └── energy_prediction.html
├── energy_management/
│   └── urls.py                   # Updated with new routes
└── requirements.txt              # Updated dependencies
```

---

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
cd "C:\Users\pranaya\Downloads\88.Machine Learning based Energy Management System for Smart Buildings\energy_management_for_smart_buildings\code\energy_management"

pip install -r requirements.txt
```

### 2. Run Migrations (if needed)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Start the Server

```bash
python manage.py runserver
```

### 4. Access the Application

Open your browser and navigate to: `http://127.0.0.1:8000/`

---

## 📊 Usage Guide

### Anomaly Detection

1. Login to the user portal
2. Click on **Anomaly Detection** in the navigation menu
3. Enter current energy data:
   - Energy Consumption (kWh)
   - Temperature (°C)
   - Humidity (%)
   - Occupancy Status
4. Click **Detect Anomaly**
5. View results and recommendations

### Device Scheduling

1. Click on **Device Scheduling** in the navigation menu
2. Add devices:
   - Select device type (AC, Heater, etc.)
   - Set preferred start time
   - Set duration
3. Click **Add Device**
4. Click **Optimize Now** to get optimized schedule
5. View cost savings and optimal time slots

### Energy Prediction

1. Click on **Energy Forecast** in the navigation menu
2. Click **Train Model** (first time only)
3. Click **Predict Next 24 Hours**
4. View:
   - Hourly predictions
   - Total consumption and cost
   - Energy-saving tips

---

## 🔧 Technical Details

### ML Models

**Anomaly Detection:**
- `AnomalyDetector` class using Isolation Forest
- `AutoencoderAnomalyDetector` class using PyTorch neural networks
- Contamination rate: 10% (adjustable)

**Device Scheduling:**
- `DeviceScheduler` class with time-series optimization
- Considers energy prices and occupancy patterns
- Supports multiple devices with different schedules

**Energy Prediction:**
- `EnergyPredictor` class with ensemble approach
- `LSTMEnergyPredictor` class for deep learning predictions
- Combines Random Forest, XGBoost, and LSTM for accuracy

### Data Requirements

- Historical energy consumption data
- Weather data (temperature, humidity, wind speed)
- Occupancy patterns
- Time-based features (hour, day of week, month)

---

## 🎯 Benefits

1. **Cost Savings:** Optimize device schedules to reduce electricity bills by 15-30%
2. **Theft Detection:** Identify energy theft and equipment faults early
3. **Predictive Planning:** Plan energy usage based on accurate forecasts
4. **Sustainability:** Reduce carbon footprint through efficient energy management
5. **User Comfort:** Maintain comfort while optimizing costs

---

## 🔮 Future Enhancements

- Real-time monitoring dashboard
- Mobile app integration
- Integration with smart home devices (IoT)
- Advanced reinforcement learning for scheduling
- Weather API integration for real-time forecasts
- Multi-building energy management
- Solar panel integration and optimization

---

## 📝 Notes

- All models are trained on sample data initially
- For production use, replace sample data with actual building data
- Models improve accuracy over time with more data
- Ensure proper data collection infrastructure for best results

---

## 🐛 Troubleshooting

**Issue:** Model not trained error
- **Solution:** Click "Train Model" button first before making predictions

**Issue:** Import errors
- **Solution:** Run `pip install -r requirements.txt` to install all dependencies

**Issue:** Template not found
- **Solution:** Ensure all HTML templates are in `assets/templates/users/` directory

---

## 📧 Support

For issues or questions, please refer to the project documentation or contact the development team.

---

**Version:** 2.0
**Last Updated:** March 2026
**Author:** Energy Management System Team
