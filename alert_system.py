"""
alert_system.py
-----------------
Detects accidents from accelerometer readings and manages the alert
lifecycle: logging the event, "notifying" emergency contacts, and
keeping a history that the dashboard can display.

The notification step (send_sms / send_email) is stubbed out with
clear extension points - swap in Twilio, an SMTP client, or any
messaging API to make this production-ready.
"""

import time
import uuid

# g-force magnitude above which a reading is classified as a collision
IMPACT_THRESHOLD_G = 4.0

EMERGENCY_CONTACTS = [
    {"name": "Primary Contact", "phone": "+91XXXXXXXXXX"},
    {"name": "Local Emergency Services", "phone": "108"},  # India emergency number
]


class AlertSystem:
    def __init__(self, threshold_g=IMPACT_THRESHOLD_G):
        self.threshold_g = threshold_g
        self.alerts = []  # history of triggered alerts, most recent first

    def evaluate(self, reading):
        """
        Check a telemetry reading against the impact threshold.
        Returns the created alert dict if an accident was detected,
        otherwise None.
        """
        magnitude = reading["accel"]["magnitude"]
        if magnitude >= self.threshold_g:
            return self.trigger_alert(reading)
        return None

    def trigger_alert(self, reading):
        alert = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": reading["timestamp"],
            "time_readable": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(reading["timestamp"])
            ),
            "impact_g": reading["accel"]["magnitude"],
            "location": reading["gps"],
            "speed_at_impact_kmph": reading["speed_kmph"],
            "status": "ALERT SENT",
            "notified": [c["name"] for c in EMERGENCY_CONTACTS],
        }
        self.alerts.insert(0, alert)
        self._notify_emergency_contacts(alert)
        return alert

    def _notify_emergency_contacts(self, alert):
        """
        Stub for real-world notification dispatch.
        Replace this with actual SMS/email/API calls, e.g.:

            from twilio.rest import Client
            client.messages.create(to=contact["phone"], body=message, from_=TWILIO_NUMBER)
        """
        message = (
            f"EMERGENCY ALERT: Possible accident detected. "
            f"Impact: {alert['impact_g']}g at "
            f"({alert['location']['lat']}, {alert['location']['lon']}). "
            f"Speed at impact: {alert['speed_at_impact_kmph']} km/h."
        )
        for contact in EMERGENCY_CONTACTS:
            print(f"[ALERT DISPATCH] -> {contact['name']} ({contact['phone']}): {message}")

    def get_alerts(self, limit=20):
        return self.alerts[:limit]

    def clear(self):
        self.alerts = []
