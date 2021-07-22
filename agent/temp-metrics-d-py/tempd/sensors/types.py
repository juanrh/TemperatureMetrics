"""
Type declarations for the sensors module
"""
from typing import Callable, Tuple

TempMeasurement = Tuple[float, float]
TempSensor = Callable[[int, int], TempMeasurement]
