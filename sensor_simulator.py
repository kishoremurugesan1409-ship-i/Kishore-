"""
sensor_simulator.py
--------------------
Simulates the data a real vehicle would produce from an accelerometer
(impact / sudden-deceleration detection) and a GPS module (live location).

In a production system this module would be replaced by real hardware
drivers (e.g. MPU6050 accelerometer over I2C, NEO-6M GPS over UART).
Here it generates realistic values so the rest of the system -
detection, alerting, and the dashboard - can be demonstrated end to end.
"""

import random
import time
import math


class SensorSimulator:
    def __init__(self, base_lat=11.0168, base_lon=76.9558):
        """
        base_lat/base_lon default to Coimbatore, Tamil Nadu.
        The simulated vehicle wanders around this point.
        """
        self.base_lat = base_lat
        self.base_lon = base_lon
        self.lat = base_lat
        self.lon = base_lon
        self.speed_kmph = round(random.uniform(20, 45), 1)
        self.heading = random.uniform(0, 360)
        self._t = 0

    def _normal_driving_step(self):
        """Small, smooth changes that look like normal driving."""
        self._t += 1
        # gentle speed drift
        self.speed_kmph += random.uniform(-2, 2)
        self.speed_kmph = max(0, min(80, self.speed_kmph))

        # move position slightly based on heading + speed
        self.heading += random.uniform(-5, 5)
        distance_deg = (self.speed_kmph / 3600) * 0.00001 * 5
        self.lat += distance_deg * math.cos(math.radians(self.heading))
        self.lon += distance_deg * math.sin(math.radians(self.heading))

        # baseline accelerometer noise (in g's), resting around 1g (gravity)
        accel_x = round(random.uniform(-0.15, 0.15), 3)
        accel_y = round(random.uniform(-0.15, 0.15), 3)
        accel_z = round(1.0 + random.uniform(-0.05, 0.05), 3)
        return accel_x, accel_y, accel_z

    def read(self):
        """Return one telemetry sample: accel (g), gps, speed, timestamp."""
        ax, ay, az = self._normal_driving_step()
        magnitude = round(math.sqrt(ax ** 2 + ay ** 2 + az ** 2), 3)

        return {
            "timestamp": time.time(),
            "accel": {"x": ax, "y": ay, "z": az, "magnitude": magnitude},
            "gps": {"lat": round(self.lat, 6), "lon": round(self.lon, 6)},
            "speed_kmph": round(self.speed_kmph, 1),
        }

    def simulate_impact(self):
        """
        Force a single high-G impact reading, as if a collision just
        happened. Real accelerometers report impact spikes of 4g-20g+
        depending on crash severity - we use a value well above the
        detection threshold.
        """
        impact_g = round(random.uniform(6.5, 14.0), 2)
        ax = round(random.uniform(-impact_g, impact_g), 2)
        ay = round(random.uniform(-impact_g, impact_g), 2)
        az = round(random.uniform(0.5, 2.5), 2)
        magnitude = round(math.sqrt(ax ** 2 + ay ** 2 + az ** 2), 3)

        # a crash usually coincides with a sudden drop in speed
        self.speed_kmph = round(max(0, self.speed_kmph * random.uniform(0, 0.2)), 1)

        return {
            "timestamp": time.time(),
            "accel": {"x": ax, "y": ay, "z": az, "magnitude": magnitude},
            "gps": {"lat": round(self.lat, 6), "lon": round(self.lon, 6)},
            "speed_kmph": self.speed_kmph,
        }
