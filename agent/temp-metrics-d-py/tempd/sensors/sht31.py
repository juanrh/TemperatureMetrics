"""SHT31 sensor
Temperature and humidity sensor with 2 decimal precission for
temperature

References:

- https://wiki.seeedstudio.com/Grove-TempAndHumi_Sensor-SHT31/#play-with-raspberry-pi
"""
import os
import time
from retrying import retry
from .types import TempMeasurement, TempSensor
from . import fake

def is_rpi():
    """Detect whether or not this code is running on a Raspberry Pi"""
    model_filename = '/sys/firmware/devicetree/base/model'
    if os.path.isfile(model_filename):
        with open(model_filename, 'r', encoding='utf-8') as in_f:
            line = in_f.readline()
        return line.startswith('Raspberry Pi')
    return False

class Sensor(TempSensor): # pylint: disable=too-few-public-methods
    """A temperature meter based on the DHT11 sensor. This sensor has
    2 decimal precision for temperature, but it's not very stable:

    - Sometimes it fails to measure with "OSError: [Errno 121] Remote I/O error",
    this is an error documented in several internet forums. Mitigated by
    retrying the measure after a small wait
    - There are occasional spikes in the measurements, specially for the humidity.

    Adapted from https://github.com/ControlEverythingCommunity/SHT31/blob/master/Python/SHT31.py
    and https://wiki.seeedstudio.com/Grove-TempAndHumi_Sensor-SHT31/#software_1
    """
    __is_rpi = is_rpi()
    __SENSOR_ADDRESS = 0x44 # SHT31 address
    __SEND_MEASUREMENT_CMD = 0x2C # Send measurement command
    __SEND_MEASUREMENT_CMD_ARGS = [0x06] # High repeatability measurement
    # Time recommended in https://wiki.seeedstudio.com/Grove-TempAndHumi_Sensor-SHT31/#software_1
    __CMD_EXEC_TIME = 0.032
    __READ_MEASUREMENT_CMD = 0x00
    __MEASUREMENT_MSG_BYTE_SIZE = 6

    def __init__(self):
        if Sensor.__is_rpi:
            from smbus import SMBus # pylint: disable=no-name-in-module,import-outside-toplevel
            # I2C bus
            self.__bus = SMBus(1)
        else:
            print("WARNING: Running on a platform different than RPI, fake measures will be returned for SHT31 sensor") # pylint: disable=line-too-long
            self.__sensor: TempSensor = fake.Sensor()

    @retry(wait_fixed=10, stop_max_attempt_number=2000, wrap_exception=True,
           retry_on_exception=lambda ex: isinstance(ex, OSError))
    def measure(self) -> TempMeasurement:
        """Get a temperature (in Celsius) and humidity measurement
        from the SHT31 sensor through the I2C bus"""
        if Sensor.__is_rpi:
            self.__bus.write_i2c_block_data(Sensor.__SENSOR_ADDRESS,
                Sensor.__SEND_MEASUREMENT_CMD, Sensor.__SEND_MEASUREMENT_CMD_ARGS)
            time.sleep(Sensor.__CMD_EXEC_TIME)
            # Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
            data = self.__bus.read_i2c_block_data(Sensor.__SENSOR_ADDRESS,
                Sensor.__READ_MEASUREMENT_CMD, Sensor.__MEASUREMENT_MSG_BYTE_SIZE)
            # Convert the data
            temp = data[0] * 256 + data[1]
            celsius_temp = -45 + (175 * temp / 65535.0)
            humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
            return (celsius_temp, humidity)
        # Stub reading for SHT31 sensor
        return self.__sensor.measure()
