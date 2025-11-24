"""Module for storing historical OBD-II sensor data readings."""

from collections import OrderedDict
from datetime import datetime
from typing import Any

from obd2.sensors.sensor_value import SensorValue

class OBDSensorData:
    """
    Stores historical sensor readings for a specific sensor/command.
    Maintains time-series data in chronological order.
    """
    
    def __init__(self, sensor_name: str):
        self.sensor_name = sensor_name
        self._readings: OrderedDict[datetime, SensorValue] = OrderedDict()
        self._latest: SensorValue | None = None

    def add_reading(self, sensor_value: SensorValue) -> None:
        """Add a new sensor reading to the history."""
        if sensor_value.name != self.sensor_name:
            raise ValueError(f"Sensor name mismatch: expected {self.sensor_name}, got {sensor_value.name}")
        
        self._readings[sensor_value.timestamp] = sensor_value
        self._latest = sensor_value
    
    @property
    def latest(self) -> SensorValue | None:
        """Get the most recent reading."""
        return self._latest
    
    @property
    def count(self) -> int:
        """Number of readings stored."""
        return len(self._readings)
    
    def get_readings(self, limit: int | None = None) -> list[SensorValue]:
        """
        Get historical readings in chronological order.
        
        Args:
            limit: Maximum number of readings to return (most recent). None = all.
        """
        readings = list(self._readings.values())
        if limit is not None and limit > 0:
            return readings[-limit:]
        return readings
    
    def get_values(self, limit: int | None = None) -> list[Any]:
        """Get just the values (without metadata) from recent readings."""
        readings = self.get_readings(limit)
        return [r.value for r in readings]
    
    def clear(self) -> None:
        """Clear all historical readings."""
        self._readings.clear()
        self._latest = None
    
    def __len__(self) -> int:
        return self.count
    
    def __str__(self) -> str:
        if self._latest:
            return f"OBDSensorData({self.sensor_name}): {self.count} readings, latest={self._latest}"
        return f"OBDSensorData({self.sensor_name}): No readings"
