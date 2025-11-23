"""
Class for storing and retrieving OBD data from an established connection.
"""

from obd2.obd_connection import OBDConnection
from obd2.command_functions import OBDCommand
from obd2.response import OBDResponse
import logging
from datetime import datetime

from typing_extensions import OrderedDict

logger = logging.getLogger(__name__)

class OBDData:
    """ Class for storing and retrieving OBD data from an established connection. """

    def __init__(
            self,
            obd_connection: OBDConnection
            ):
        self.__connection: OBDConnection = obd_connection
        
        self.supported_command_names: frozenset[str] = frozenset(self.__connection.supported_commands.keys())

    @property
    def is_connected(self) -> bool:
        """ Check if the OBD connection is established. """
        return self.__connection.is_connected()
    
    def get_sensor_value(self, command_name: str) -> 'SensorValue' | None:
        """Query sensor and return formatted result."""
        if command_name not in self.__connection.supported_command_names:
            raise ValueError(f"Invalid command name: {command_name}")
        command: OBDCommand = self.__connection.commands[command_name]
        if type(command) is not OBDCommand:
            logger.error(f"Command {command_name} is not a valid OBDCommand.")
            return None
        response = self.__connection.query(command)
        logger.debug(f"Query: {command_name}\nResponse: {response}")
        
        if response.value is None:
            return None
            
        return SensorValue(command.name, response.value, response.unit)
    
    def format_response(self, response: OBDResponse) -> str:
        """Format the OBDResponse for display."""
        if not response or response.is_null():
            return "No data"
        return f"{response.value} {response.unit}"

class SensorValue:
    def __init__(self, name: str, value, unit: str):
        self._name = name
        self._value = value
        self._unit = unit
        self._last_updated = datetime.now()

    # Ensure properties are read-only
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def value(self):
        return self._value
    
    @property
    def unit(self) -> str:
        return self._unit

    @property
    def last_updated(self) -> datetime:
        return self._last_updated

    def __str__(self):
        return f"{self.name}: {self.value} {self.unit} at {self.last_updated}"
    

class OBDSensorData:
    """
    Class for storing data from OBD sensors over time.
    """
    
    def __init__(self):
        self.data: OrderedDict[datetime, SensorValue] = OrderedDict()  # key: sensor name, value: list of (timestamp, value) tuples
        self.latest: SensorValue = None

    def add_reading(self, sensor_value: SensorValue):
        """Add a new sensor reading."""
        self.data.update({sensor_value.last_updated: sensor_value})
        self.latest = sensor_value
