"""
Type declarations for the sensors module
"""
from typing import Callable, Tuple

Dht11Measurement = Tuple[float, float]
Dht11Sensor = Callable[[int, int], Dht11Measurement]
