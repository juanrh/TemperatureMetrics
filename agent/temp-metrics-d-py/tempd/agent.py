"""
Temperature metrics agent
"""

import time
import math
import signal
import logging
import os
import json
import threading
from dataclasses import dataclass
from typing import Callable, Optional
from typing_extensions import Protocol
import boto3

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

    Only valid measurements should be returned, e.g. discard NaN returned by the
    driver and retry until a valid measurement is obtained"""
    def measure(self) -> "TempMeasurement":
        """Get a new measurement from the sensor"""
        ...


class MeasurementRecorder(Protocol): # pylint: disable=too-few-public-methods
    """A measurement recorder is able to record measurements in some
    permanent storage"""
    def record(self, measurement: "TempMeasurement"):
        """Records a measurement in some permanent storage"""
        ...

class Timer(Protocol):
    """A timer.
    This makes the code more testeable, because even if
    we patch the time module, we don't know how other third modules
    might be using the time module"""
    def sleep(self, sleep_time:float):
        """Block this thread for a number of milliseconds"""
        ...

    def time(self) -> float:
        """Give the current epoch time in milliseconds"""
        ...

class TimeTimer(Timer):
    """Timer based on time module"""
    def sleep(self, sleep_time):
        time.sleep(sleep_time)

    def time(self):
        return time.time()

class ThreadDaemon:
    """
    A deamon that runs an action on a scheduled periodicity,
    running on its own thread
    """
    def __init__(self, seconds: float,
                       action: Callable[[], None],
                       timer: Timer = TimeTimer()):
        """Schedule the process to run each `seconds` seconds"""
        self.__seconds = seconds
        self.__action = action
        self.__timer = timer
        self.__running = False
        self.__thread: Optional[threading.Thread] = None

    @property
    def running(self) -> bool:
        """Whether this deamon is running or not"""
        return self.__thread.is_alive() if self.__thread is not None\
               else False


    __polling_interval = 0.1
    def start(self, blocking:bool=False):
        """Launch the daemon

        If blocking is true the current thread blocks
        to join this deamon's thread
        """
        signal.signal(signal.SIGINT, lambda _signal, _stack: self.stop())
        self.__running = True
        def thread_function():
            logging.info("Starting deamon")
            latest_exec_time = 0
            while self.__running:
                current_time = self.__timer.time()
                if current_time - latest_exec_time > self.__seconds:
                    self.__action()
                    latest_exec_time = current_time
                self.__timer.sleep(ThreadDaemon.__polling_interval)
        self.__thread = threading.Thread(target=thread_function, daemon=True)
        self.__thread.start()
        if blocking:
            self.__thread.join()


    def stop(self):
        """Stop the deamon"""
        logging.info("Stopping deamon")
        self.__running = False

    def wait_for_completion(self, timeout: float):
        """Block waiting for the daemon to stop"""
        if self.__thread is not None:
            self.__thread.join(timeout)


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


class CloudwatchMeasurementRecorder(MeasurementRecorder): # pylint: disable=too-few-public-methods
    """A MeasurementRecorder that stores the measurements
    as AWS Cloudwatch metrics. 2 metrics are emitted per
    measurement, one for temperature and one for humidity

    Attributes:

    - source_dimension: name of the cloudwatch dimension used to
      specify the metrics source
    - temperature_metric_name: name of the cloudwatch metrics used to
      for temperature metrics
    - humidity_metric_name: name of the cloudwatch metrics used to
      for humidity metrics
    """
    source_dimension = 'source'
    temperature_metric_name = 'temperature'
    humidity_metric_name = 'humidity'

    def __init__(self, session: "boto3.session.Session",
                 namespace:str='temp_agent',
                 # Union[Literal[1], Literal[60]] would be better,
                 # but it's only available in Python 3.8+
                 storage_resolution:int=60):
        """
        These arguments match with parameters used put a
        metric into CloudWatch metrics, see https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/publishingMetrics.html#high-resolution-metrics # pylint: disable=line-too-long
        for more details.
        """
        self.__metrics_namespace = namespace
        self.__storage_resolution = storage_resolution
        self.__cloudwatch = session.client('cloudwatch')

    def record(self, measurement: "TempMeasurement"):
        def create_metric(metric_name, value):
            return {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name': self.__class__.source_dimension,
                        'Value': measurement.source
                    },
                ],
                'Timestamp': measurement.timestamp,
                'Value': value,
                'StorageResolution': self.__storage_resolution
            }

        temp_metric = create_metric(self.__class__.temperature_metric_name,
                                    measurement.temperature)
        humidity_metric = create_metric(self.__class__.humidity_metric_name,
                                        measurement.humidity)
        put_metric_data_params = {
            'Namespace': self.__metrics_namespace,
            'MetricData': [temp_metric, humidity_metric]
        }
        self.__cloudwatch.put_metric_data(**put_metric_data_params)
        logging.info('Measurement recorded in cloudwatch %s',
            json.dumps(put_metric_data_params))


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

    @staticmethod
    def __create_boto_session() -> "boto3.session.Session":
        if len(os.environ.get('AWS_ACCESS_KEY_ID', '')) > 0 \
            and len(os.environ.get('AWS_SECRET_ACCESS_KEY', '')) > 0:
            return boto3.session.Session()

        # Useful for local devel, without polluting prod data
        logging.warning('Missing AWS credentials, using mock AWS clients for devel')
        from unittest.mock import Mock # pylint: disable=import-outside-toplevel
        session_mock = Mock()
        cloudwatch_mock = Mock()
        def put_metric_data(**args):
            logging.warning('Mock cloudwatch client: put_metric_data called with args %s', args)
        cloudwatch_mock.put_metric_data.side_effect = put_metric_data
        session_mock.client.return_value = cloudwatch_mock
        return session_mock

    def create_deamon(self) -> ThreadDaemon:
        """Factory for the daemon object"""
        measurement_conf = self.__config['measurement']
        meter: TempMeter = Dht11TempMeter(measurement_conf['source_name'])
        boto_session = Main.__create_boto_session()
        measurement_recorder: MeasurementRecorder = \
            CloudwatchMeasurementRecorder(boto_session)

        def action():
            measurement_recorder.record(meter.measure())

        deamon = ThreadDaemon(
            float(measurement_conf['frequency_in_seconds']),
            action
        )
        return deamon
