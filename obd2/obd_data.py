"""
Class for storing and retrieving OBD data from an established connection.
"""

from obd2.obd_connection import OBDConnection
from obd2.command_functions import OBDCommand, commands
from obd2.response import OBDResponse
from typing import Any

import logging

from obd2.sensors.sensor_value import SensorValue
from obd2.sensors.sensor_data import OBDSensorData

logger = logging.getLogger(__name__)

class OBDData:
    """
    High-level interface for querying and storing OBD sensor data.
    Manages connection, queries, and historical data storage.
    """

    def __init__(self, obd_connection: OBDConnection):
        self.__connection: OBDConnection = obd_connection
        self.supported_command_names: frozenset[str] = frozenset(
            self.__connection.supported_commands.keys()
        )
        # Storage for historical sensor data
        self._sensor_history: dict[str, OBDSensorData] = {}

    @property
    def is_connected(self) -> bool:
        """Check if the OBD connection is established."""
        return self.__connection.is_connected()
    
    @property
    def connection(self) -> OBDConnection:
        """Access the underlying OBD connection (read-only)."""
        return self.__connection

    def query(self, command_name: str, store: bool = False) -> SensorValue | None:
        """
        Query a sensor by command name and optionally store the result.
        
        Args:
            command_name: Name of the OBD command (e.g., "RPM", "SPEED")
            store: If True, store the reading in historical data
            
        Returns:
            SensorValue with the reading, or None if query failed
            
        Raises:
            ValueError: If command_name is not supported
        """

        if command_name not in self.supported_command_names:
            raise ValueError(
                f"Command '{command_name}' not supported. "
                f"Use get_supported_commands() to see available commands."
            )
        
        command: OBDCommand = commands[command_name]
        response: OBDResponse = self.__connection.query(command)
        
        if response.is_null():
            logger.debug(f"Query '{command_name}' returned no data")
            return None

        sensor_value = SensorValue(
            name=command.name,
            value=response.magnitude,
            unit=str(response.unit),
            timestamp=response.time
        )
        
        if store:
            self._store_reading(sensor_value)
        
        return sensor_value

    def query_multiple(self, command_names: list[str], store: bool = False) -> dict[str, SensorValue | None]:
        """
        Query multiple sensors at once.
        
        Args:
            command_names: List of command names to query
            store: If True, store all successful readings
            
        Returns:
            Dictionary mapping command names to their SensorValue results
        """
        results = {}
        for cmd_name in command_names:
            try:
                results[cmd_name] = self.query(cmd_name, store=store)
            except ValueError as e:
                logger.warning(f"Skipping command '{cmd_name}': {e}")
                results[cmd_name] = None
        return results

    def start_monitoring(self, command_names: list[str]) -> None:
        """
        Start monitoring specific sensors (initializes storage for them).
        
        Args:
            command_names: List of command names to monitor
        """
        for cmd_name in command_names:
            if cmd_name in self.supported_command_names and cmd_name not in self._sensor_history:
                self._sensor_history[cmd_name] = OBDSensorData(cmd_name)
                logger.info(f"Started monitoring '{cmd_name}'")

    def update_monitored_sensors(self) -> dict[str, SensorValue | None]:
        """
        Query all monitored sensors and store their readings.
        
        Returns:
            Dictionary of command names to their latest readings
        """
        if not self._sensor_history:
            logger.warning("No sensors are being monitored. Use start_monitoring() first.")
            return {}
        
        return self.query_multiple(list(self._sensor_history.keys()), store=True)

    def get_sensor_history(self, command_name: str) -> OBDSensorData | None:
        """
        Get the historical data for a specific sensor.
        
        Args:
            command_name: Name of the sensor/command
            
        Returns:
            OBDSensorData object containing all readings, or None if not monitored
        """
        return self._sensor_history.get(command_name)

    def get_latest_value(self, command_name: str) -> SensorValue | None:
        """
        Get the latest stored reading for a sensor (from history).
        Does not perform a new query.
        
        Args:
            command_name: Name of the sensor/command
            
        Returns:
            Most recent SensorValue, or None if no history exists
        """
        history = self.get_sensor_history(command_name)
        return history.latest if history else None

    def get_monitored_sensors(self) -> list[str]:
        """Get list of sensors currently being monitored."""
        return list(self._sensor_history.keys())

    def clear_history(self, command_name: str | None = None) -> None:
        """
        Clear historical data.
        
        Args:
            command_name: Specific sensor to clear. If None, clears all history.
        """
        if command_name:
            if command_name in self._sensor_history:
                self._sensor_history[command_name].clear()
                logger.info(f"Cleared history for '{command_name}'")
        else:
            for sensor_data in self._sensor_history.values():
                sensor_data.clear()
            logger.info("Cleared all sensor history")

    def stop_monitoring(self, command_name: str | None = None) -> None:
        """
        Stop monitoring sensor(s) and clear their history.
        
        Args:
            command_name: Specific sensor to stop. If None, stops all monitoring.
        """
        if command_name:
            if command_name in self._sensor_history:
                del self._sensor_history[command_name]
                logger.info(f"Stopped monitoring '{command_name}'")
        else:
            self._sensor_history.clear()
            logger.info("Stopped monitoring all sensors")

    def get_supported_commands(self) -> list[str]:
        """Get list of all supported command names for this vehicle."""
        return sorted(self.supported_command_names)

    def _store_reading(self, sensor_value: SensorValue) -> None:
        """Internal method to store a sensor reading in history."""
        cmd_name = sensor_value.name
        
        # Initialize storage if this sensor isn't being monitored yet
        if cmd_name not in self._sensor_history:
            self._sensor_history[cmd_name] = OBDSensorData(cmd_name)
        
        self._sensor_history[cmd_name].add_reading(sensor_value)
        logger.debug(f"Stored reading for '{cmd_name}': {sensor_value.value} {sensor_value.unit}")

    def format_response(self, response: OBDResponse) -> str:
        """
        Format an OBDResponse for display.
        
        Args:
            response: OBDResponse object to format
            
        Returns:
            Human-readable string representation
        """
        if not response or response.is_null():
            return "No data"
        return f"{response.value} {response.unit}"
    
    def format_sensor_value(self, sensor_value: SensorValue | None) -> str:
        """
        Format a SensorValue for display.
        
        Args:
            sensor_value: SensorValue object to format
            
        Returns:
            Human-readable string representation
        """
        if not sensor_value:
            return "No data"
        return f"{sensor_value.value} {sensor_value.unit}"

    def get_monitoring_summary(self) -> dict[str, dict[str, Any]]:
        """
        Get a summary of all monitored sensors.
        
        Returns:
            Dictionary with sensor names as keys and summary info as values
        """
        summary = {}
        for cmd_name, sensor_data in self._sensor_history.items():
            latest = sensor_data.latest
            summary[cmd_name] = {
                'reading_count': sensor_data.count,
                'latest_value': latest.value if latest else None,
                'latest_unit': latest.unit if latest else None,
                'latest_time': latest.timestamp if latest else None
            }
        return summary

    def __str__(self) -> str:
        conn_status = "connected" if self.is_connected else "disconnected"
        monitored = len(self._sensor_history)
        return f"OBDData({conn_status}, {monitored} sensors monitored, {len(self.supported_command_names)} commands supported)"
