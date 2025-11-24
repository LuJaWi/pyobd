""" Module for OBD response objects """

from time import time
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from pint import Quantity
    from obd2.command import OBDCommand
    from elm327.protocols.models.message import Message


class OBDResponse:
    """ Standard response object for any OBDCommand """

    def __init__(self, 
                 command: 'OBDCommand' = None, 
                 messages: 'list[Message]' = None
                 ) -> None:
        self.command = command
        self.messages = messages if messages else []
        self.value = None
        self.time = time()
        
        # Decode the value if we have messages and a decoder
        if self.messages and command and hasattr(command, 'decode'):
            self._decode_value(command.decode)
    
    def _decode_value(self, decoder: Callable[['list[Message]'], Any]) -> None:
        """
        Internal method to decode messages into a value.
        
        Args:
            decoder: Function that takes messages and returns decoded value
        """
        try:
            self.value = decoder(self.messages)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Decoding failed: {e}")
            self.value = None

    @property
    def magnitude(self):
        """
        Extract numeric magnitude from the response value.
        
        Returns:
            - Numeric value for Pint Quantity objects (e.g., 1500 from "1500 rpm")
            - The raw value itself for non-Quantity types
            - None if value is None
        """
        if self.value is None:
            return None
        
        # Check if it's a Pint Quantity (has magnitude attribute)
        if hasattr(self.value, 'magnitude'):
            return self.value.magnitude
        
        # Return raw value for non-Quantity types (int, str, Status objects, etc.)
        return self.value
    
    @property
    def unit(self) -> str | None:
        """
        Extract unit string from the response value.
        
        Returns:
            - Unit string for Pint Quantity objects (e.g., "revolutions_per_minute")
            - None if value is None
            - Type name as fallback (e.g., "<class 'str'>")
        """
        if self.value is None:
            return None
        
        # Check if it's a Pint Quantity (has magnitude and units attributes)
        if hasattr(self.value, 'magnitude') and hasattr(self.value, 'units'):
            return str(self.value.units)
        
        # Fallback for non-Quantity values (Status objects, strings, etc.)
        return str(type(self.value))

    def is_null(self) -> bool:
        """Check if response has no data or null value."""
        return (not self.messages) or (self.value is None)

    def __str__(self) -> str:
        return str(self.value)

