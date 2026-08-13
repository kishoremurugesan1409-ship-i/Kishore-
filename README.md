# 🚨 Vehicle Emergency Accident Alert System

An academic project that detects vehicle accidents automatically using
accelerometer (impact) data and reports real-time GPS location to
emergency contacts — with a live web dashboard for monitoring.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

Road accidents often go unreported for critical minutes because no one
nearby is able to call for help. This project simulates an in-vehicle
safety unit that:

1. Continuously reads accelerometer data to detect sudden, high-G impacts
   characteristic of a collision
2. Reads GPS location in real time
3. When an impact crosses the danger threshold, automatically triggers
   an alert containing the location, speed, and impact force, and
   notifies emergency contacts
4. Displays everything on a live dashboard, so the system's state is
   always visible

This repo uses **simulated sensor data** (no physical hardware
required) so the full detection → alert pipeline can be demonstrated
and evaluated end-to-end. The `sensor_simulator.py` module is written
so it can be swapped for real accelerometer/GPS hardware drivers
(e.g. MPU6050 + NEO-6M) with no changes to the detection or alert logic.

## ✨ Features

- **Real-time telemetry** — live accelerometer (X/Y/Z + magnitude) and
  GPS readings, updated every second
- **Automatic accident detection** — configurable G-force threshold
  triggers alerts without any manual step
- **Manual crash simulation** — a "Simulate Impact" control to demo the
  full pipeline instantly
- **Emergency notification pipeline** — pluggable alert dispatch
  (stubbed for SMS/email/API integration — see `alert_system.py`)
- **Live dashboard** — G-force gauge, live map, telemetry sparkline,
  and a running alert log, built with Flask + vanilla JS + Leaflet

## 🛠️ Tech Stack

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Backend      | Python, Flask                       |
| Frontend     | HTML, CSS, JavaScript                |
| Mapping      | Leaflet.js + OpenStreetMap           |
| Location     | GPS module (simulated in this build) |
| Detection    | Accelerometer threshold algorithm    |

## 📂 Project Structure

```
vehicle-emergency-alert-system/
├── app.py                  # Flask app & API routes
├── sensor_simulator.py     # Simulated accelerometer + GPS data source
├── alert_system.py         # Threshold detection + alert dispatch logic
├── requirements.txt
├── templates/
│   └── index.html          # Dashboard UI
└── static/
    ├── css/style.css
    └── js/script.js
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/vehicle-emergency-alert-system.git
cd vehicle-emergency-alert-system
pip install -r requirements.txt
```

### Run

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser. The dashboard starts
streaming simulated telemetry immediately. Click **Simulate Impact**
to trigger a mock collision and watch the detection → alert pipeline
fire in real time.

## ⚙️ How Detection Works

Each telemetry sample includes an accelerometer magnitude, computed as:

```
magnitude = sqrt(x² + y² + z²)
```

Normal driving stays close to 1g (gravity at rest, with small noise
from road vibration). When `magnitude` meets or exceeds the configured
`IMPACT_THRESHOLD_G` (default: **4.0g**) in `alert_system.py`, the
reading is classified as a collision and an alert is generated
immediately, capturing:

- Timestamp
- Impact force (g)
- GPS coordinates at the moment of impact
- Vehicle speed at impact
- List of notified emergency contacts

## 🔌 Extending to Real Hardware

This project is structured so the simulation layer is the only part
that needs replacing for a real deployment:

- Swap `SensorSimulator` for real driver code reading an **MPU6050**
  (accelerometer) over I2C and a **NEO-6M** GPS module over UART
- Replace the `_notify_emergency_contacts` stub in `alert_system.py`
  with a real integration (e.g. Twilio for SMS, SMTP for email, or a
  push notification API)
- Everything downstream — detection logic, the API, and the dashboard
  — works unchanged

## 🎓 Project Background

Built as an academic project (BCA) exploring how low-cost sensors and
simple threshold-based logic can create a functioning emergency
response aid. Roadmap ideas for future iterations: false-positive
filtering (e.g. requiring sustained speed drop + impact together),
configurable per-contact notification channels, and a mobile companion
app.

## 📄 License

MIT — free to use and adapt for learning or further development.
