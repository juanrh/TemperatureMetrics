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
from .types import TempMeasurement, TempSensor
from . import fake

class Sensor(TempSensor): # pylint: disable=too-few-public-methods
    """A temperature meter based on the DHT11 sensor

        Limitations:

        - It is not able to reliably read at a frequency faster than 5 seconds
        - Temperature read precision of +/- 2 degree, fraction temperature is always 0

        https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/"""
    def __init__(self, sensor_port: int, sensor_type: int):
        """
        Args:
            sensor_port: grovepi port the sensor is connected to
            sensor_type: use 0 for the blue-colored sensor and 1
                for the white one__dht_sensor_type
        """
        try:
            from grovepi import dht # type: ignore # pylint: disable=import-error,import-outside-toplevel

            self.__measure = lambda: cast(TempMeasurement, dht(sensor_port, sensor_type))
        except ModuleNotFoundError as mnfe:
            print(f"WARNING: No driver for DHT11 sensor found, fake measures will be returned for this sensor: {mnfe}") # pylint: disable=line-too-long
            sensor = fake.Sensor()
            self.__measure = sensor.measure

    def measure(self) -> TempMeasurement:
        """Get a measurement fom the DHT11 sensor"""
        return self.__measure()
