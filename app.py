"""
app.py
-------
Flask backend for the Vehicle Emergency Accident Alert System.

Runs a background thread that continuously reads simulated sensor
data, feeds it through the AlertSystem's threshold detection, and
exposes everything to the frontend dashboard through a small JSON API.

Run with:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import threading
import time

from flask import Flask, jsonify, render_template, request

from sensor_simulator import SensorSimulator
from alert_system import AlertSystem

app = Flask(__name__)

simulator = SensorSimulator()
alert_system = AlertSystem()

# shared state, guarded by a lock since it's written from the background thread
state_lock = threading.Lock()
latest_reading = simulator.read()
monitoring_active = True


def sensor_loop():
    """Background thread: takes a new reading once per second and
    runs it through the accident-detection logic."""
    global latest_reading
    while True:
        if monitoring_active:
            with state_lock:
                latest_reading = simulator.read()
                alert_system.evaluate(latest_reading)
        time.sleep(1)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    with state_lock:
        return jsonify({
            "reading": latest_reading,
            "monitoring_active": monitoring_active,
            "threshold_g": alert_system.threshold_g,
            "alert_count": len(alert_system.alerts),
        })


@app.route("/api/alerts")
def api_alerts():
    return jsonify(alert_system.get_alerts())


@app.route("/api/simulate-crash", methods=["POST"])
def api_simulate_crash():
    """Manually trigger a simulated high-impact reading, useful for
    demoing the system without needing real crash hardware."""
    with state_lock:
        reading = simulator.simulate_impact()
        global latest_reading
        latest_reading = reading
        alert = alert_system.evaluate(reading)
    return jsonify({"reading": reading, "alert": alert})


@app.route("/api/toggle-monitoring", methods=["POST"])
def api_toggle_monitoring():
    global monitoring_active
    monitoring_active = not monitoring_active
    return jsonify({"monitoring_active": monitoring_active})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    alert_system.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    thread = threading.Thread(target=sensor_loop, daemon=True)
    thread.start()
    app.run(debug=True, port=5000)
