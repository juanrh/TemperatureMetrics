"""
Temperature metrics agent
"""

import time
import math
from dataclasses import dataclass
from typing_extensions import Protocol

from .sensors.types import Dht11Sensor
from .sensors import dht11

@dataclass
class TempMeasurement:
    """A temperature measurement

    Args:
        timestamp (int): timestamp as a unix epoch time
    """
    source: str
    timestamp: int
    temperature: float
    humidity: float


class TempMeter(Protocol): # pylint: disable=too-few-public-methods
    """A temperature meter is able to get temperature measurements

    TODO: Only valid measurements should be returned, e.g. discard NaN returned by the
    driver and retry until a valid measurement is obtained"""
    def measure(self) -> "TempMeasurement":
        """Get a new measurement from the sensor"""
        ...


class Dht11TempMeter(TempMeter): # pylint: disable=too-few-public-methods
    """A temperature meter based on the DHT11 sensor
    https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/"""
    __dht_sensor_port = 7 # connect the DHt sensor to port 7
    __dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white one

    def __init__(self, source_name: str,
                       sensor_port: int = __dht_sensor_port,
                       sensor_type: int = __dht_sensor_type,
                       sensor: Dht11Sensor=dht11.measure):
        self.__source_name = source_name
        self.__sensor = lambda: sensor(sensor_port, sensor_type)

    @staticmethod
    def __get_current_timestamp():
        return math.floor(time.time())

    def measure(self) -> "TempMeasurement":
        (temperature, humidity) = self.__sensor()
        return TempMeasurement(self.__source_name,
                               Dht11TempMeter.__get_current_timestamp(),
                               temperature, humidity)
