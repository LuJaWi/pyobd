"""
Class for storing and retrieving OBD data from an established connection.
"""

from obd2.obd_connection import OBDConnection
from obd2.command_functions import OBDCommand
from obd2.response import OBDResponse
import logging

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
    
    def get_sensor_value(self, command_name: str):
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
            
        # Value is already decoded by python-obd
        return {
            'name': command.name,
            'value': response.value,
            'unit': str(response.unit),
            'time': response.time
        }
    
    def format_response(self, response: OBDResponse) -> str:
        """Format the OBDResponse for display."""
        if not response or response.is_null():
            return "No data"
        return f"{response.value} {response.unit}"
    