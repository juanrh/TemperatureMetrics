"""SHT31 sensor
Temperature and humidity sensor with 2 decimal precission for
temperature

References:

- https://wiki.seeedstudio.com/Grove-TempAndHumi_Sensor-SHT31/#play-with-raspberry-pi
"""
import os
import time
from .types import TempMeasurement
from . import fake

def is_rpi():
    """Detect whether or not this code is running on a Raspberry Pi"""
    model_filename = '/sys/firmware/devicetree/base/model'
    if os.path.isfile(model_filename):
        with open(model_filename, 'r') as in_f:
            line = in_f.readline()
        return line.startswith('Raspberry Pi')
    return False

_is_rpi = is_rpi()

if _is_rpi:
    from smbus import SMBus # pylint: disable=no-name-in-module

    # Adapted from https://github.com/ControlEverythingCommunity/SHT31/blob/master/Python/SHT31.py
    # I2C bus
    _bus = SMBus(1)
    _SENSOR_ADDRESS = 0x44 # SHT31 address
    _SEND_MEASUREMENT_CMD = 0x2C # Send measurement command
    _SEND_MEASUREMENT_CMD_ARGS = [0x06] # High repeatability measurement
    # Time recommended in https://wiki.seeedstudio.com/Grove-TempAndHumi_Sensor-SHT31/#software_1
    _CMD_EXEC_TIME = 0.016
    _READ_MEASUREMENT_CMD = 0x00
    _MEASUREMENT_MSG_BYTE_SIZE = 6
    def measure(sensor_port: int, sensor_type: int) -> TempMeasurement: # pylint: disable=unused-argument
        """Get a temperature (in Celsius) and humidity measurement
        from the SHT31 sensor through the I2C bus"""
        _bus.write_i2c_block_data(_SENSOR_ADDRESS,
            _SEND_MEASUREMENT_CMD, _SEND_MEASUREMENT_CMD_ARGS)
        time.sleep(_CMD_EXEC_TIME)
        # Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
        data = _bus.read_i2c_block_data(_SENSOR_ADDRESS,
            _READ_MEASUREMENT_CMD, _MEASUREMENT_MSG_BYTE_SIZE)
        # Convert the data
        temp = data[0] * 256 + data[1]
        celsius_temp = -45 + (175 * temp / 65535.0)
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
        return (celsius_temp, humidity)
else:
    print("WARNING: Running on a platform different than RPI, fake measures will be returned for SHT31 sensor") # pylint: disable=line-too-long
    def measure(sensor_port: int, sensor_type: int) -> TempMeasurement: # pylint: disable=unused-argument
        """Stub reading for SHT31 sensor"""
        return fake.measure(sensor_port, sensor_type)
