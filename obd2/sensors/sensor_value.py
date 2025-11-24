"""Module defining an immutable snapshot of a sensor reading."""

from datetime import datetime
from typing import Any

class SensorValue:
    """Immutable snapshot of a sensor reading at a point in time."""
    
    def __init__(self, name: str, value: Any, unit: str, timestamp: datetime | None = None):
        self._name = name
        self._value = value
        self._unit = unit
        self._timestamp = timestamp or datetime.now()

    @property
    def name(self) -> str:
        """Sensor/command name."""
        return self._name
    
    @property
    def value(self) -> Any:
        """Decoded sensor value (type depends on sensor)."""
        return self._value
    
    @property
    def unit(self) -> str:
        """Unit of measurement."""
        return self._unit

    @property
    def timestamp(self) -> datetime:
        """When this reading was taken."""
        return self._timestamp

    def __str__(self) -> str:
        return f"{self.name}: {self.value} {self.unit} at {self.timestamp.strftime('%H:%M:%S.%f')[:-3]}"
    
    def __repr__(self) -> str:
        return f"SensorValue(name='{self.name}', value={self.value}, unit='{self.unit}', timestamp={self.timestamp})"

