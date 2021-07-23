"""DHT11 sensor
Precision is +/- 2 degree temp measurement, it always returns floats
with decimal part equal to 0.
The module is only available for supported platforms like Raspberry Pi,
so a stub `measure()` function is defined for other platforms

References:

- https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/
- https://raspberrypi.stackexchange.com/questions/47230/how-to-get-the-accurate-temperature-readings-from-dht11-sensor-on-grovepi # pylint: disable=line-too-long
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
