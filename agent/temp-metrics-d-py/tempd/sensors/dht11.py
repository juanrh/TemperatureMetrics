"""DHT11 sensor
Precision is +/- 2 degree temp measurement, it always returns floats
with decimal part equal to 0.
The module is only available for supported platforms like Raspberry Pi,
so a stub `measure()` function is defined for other platforms

References:

- https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/
- https://raspberrypi.stackexchange.com/questions/47230/how-to-get-the-accurate-temperature-readings-from-dht11-sensor-on-grovepi # pylint: disable=line-too-long
"""

from typing import cast
from .types import TempMeasurement
from . import fake

try:
    from grovepi import dht # type: ignore # pylint: disable=import-error
    def measure(sensor_port: int, sensor_type: int) -> TempMeasurement:
        """Get a measurement fom the DHT11 sensor"""
        # https://mypy.readthedocs.io/en/stable/casts.html#casts
        return cast(TempMeasurement, dht(sensor_port, sensor_type))
except ModuleNotFoundError as mnfe:
    print(f"WARNING: No driver for DHT11 sensor found, fake measures will be returned for this sensor: {mnfe}") # pylint: disable=line-too-long
    def measure(sensor_port: int, sensor_type: int) -> TempMeasurement: # pylint: disable=unused-argument
        """Stub reading for DHT11 sensor"""
        return fake.measure(sensor_port, sensor_type)
