import time, math
from datetime import datetime
from .types import Dht11Measurement
from typing import cast

"""DHT11 sensor

. Precision is +/- 2 degree temp measurement, always 
returns float with decimal part equal to 0

https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/
https://raspberrypi.stackexchange.com/questions/47230/how-to-get-the-accurate-temperature-readings-from-dht11-sensor-on-grovepi
"""

try:
    from grovepi import dht # type: ignore
    def measure(sensor_port: int, sensor_type: int) -> Dht11Measurement:
        # https://mypy.readthedocs.io/en/stable/casts.html#casts
        return cast(Dht11Measurement, dht(sensor_port, sensor_type))
except ModuleNotFoundError: 
    # If not available just return a stub readings
    def measure(sensor_port: int, sensor_type: int) -> Dht11Measurement:
        timestamp = math.floor(time.time())
        date = datetime.fromtimestamp(timestamp)
        return (date.second, date.minute)

