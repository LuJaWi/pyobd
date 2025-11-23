

from dataclasses import dataclass
from typing import Callable, Any

class Sensor:
    name:str
    cmd: str
    value: Callable
    unit: Any