"""
Type declarations for the sensors module
"""
from typing import Tuple
from typing_extensions import Protocol

TempMeasurement = Tuple[float, float]
class TempSensor(Protocol): # pylint: disable=too-few-public-methods
    """A sensor able to read temperature and humidty"""
    def measure(self) -> TempMeasurement:
        """Get a new measurement from the sensor"""
