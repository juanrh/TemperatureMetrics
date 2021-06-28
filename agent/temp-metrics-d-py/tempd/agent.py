"""
Temperature metrics agent
"""

import time
import math
import signal
import logging
from dataclasses import dataclass
from typing import Callable
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

class BlockingDaemon:
    """
    A deamon that runs an action on a scheduled periodicity,
    blocking the main thread
    """
    def __init__(self, seconds: float, action: Callable[[], None]):
        """Schedule the process to run each `seconds` seconds"""
        self.__seconds = seconds
        self.__action = action
        self.__running = False

    def start(self):
        """Launch the daemon"""
        signal.signal(signal.SIGINT, lambda _signal, _stack: self.stop())
        latest_exec_time = 0
        self.__running = True
        while self.__running:
            current_time = time.time()
            if current_time - latest_exec_time > self.__seconds:
                self.__action()
                latest_exec_time = current_time
            time.sleep(0.1)

    def stop(self):
        """Stop the deamon"""
        print("INFO: stopping the deamon")
        self.__running = False

class Dht11TempMeter(TempMeter): # pylint: disable=too-few-public-methods
    """A temperature meter based on the DHT11 sensor

    Limitations:

    - It is not able to reliably read at a frequency faster than 5 seconds
    - Temperature read precision of +/- 2 degree, fraction temperature is always 0

    https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/"""
    __dht_sensor_port = 7 # connect the DHt sensor to port 7
    __dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white one

    def __init__(self, source_name: str,
                       retry_sleep_time: float = 0.05,
                       sensor_port: int = __dht_sensor_port,
                       sensor_type: int = __dht_sensor_type,
                       sensor: Dht11Sensor=dht11.measure):
        self.__source_name = source_name
        self.__retry_sleep_time = retry_sleep_time
        self.__sensor = lambda: sensor(sensor_port, sensor_type)

    @staticmethod
    def __get_current_timestamp():
        return math.floor(time.time())

    def measure(self) -> "TempMeasurement":
        (temperature, humidity) = self.__sensor()
        while math.isnan(temperature) or math.isnan(humidity):
            logging.debug("Retrying measurement")
            time.sleep(self.__retry_sleep_time)
            (temperature, humidity) = self.__sensor()
        measurement = TempMeasurement(self.__source_name,
                               Dht11TempMeter.__get_current_timestamp(),
                               temperature, humidity)
        logging.info('Measured %s', measurement)
        return measurement

class Main: # pylint: disable=too-few-public-methods
    """Analogous to a Guice module, this just builds
    a deamon that performs the measurement
    """
    def __init__(self, config: dict):
        """
        Params:: dict[str, str]
        - config: a dictionary of keys corresponding to
          the JSON configuration documented in the readme
        """
        self.__config = config

    def create_deamon(self) -> BlockingDaemon:
        """Factory for the daemon object"""
        measurement_conf = self.__config['measurement']
        meter = Dht11TempMeter(measurement_conf['source_name'])
        def action():
            meter.measure()
        deamon = BlockingDaemon(
            float(measurement_conf['frequency_in_seconds']),
            action
        )
        return deamon
