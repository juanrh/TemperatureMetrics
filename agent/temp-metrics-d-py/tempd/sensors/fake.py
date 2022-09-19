"""Fake sensor
Fake sensor to use for development outside of the target platform.
"""

import time
import math
from datetime import datetime
from .types import TempMeasurement, TempSensor

class Sensor(TempSensor): # pylint: disable=too-few-public-methods
    """Fake sensor for stubbing when actual sensors are not available"""
    def measure(self) -> TempMeasurement:
        """The expected sensor is not available for this platform, so just
        return a stub reading"""
        timestamp = math.floor(time.time())
        date = datetime.fromtimestamp(timestamp)
        return (date.second, date.minute)
