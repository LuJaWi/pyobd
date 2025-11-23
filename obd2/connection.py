#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OBD-II Connection Management

Pure OBD communication logic without GUI dependencies.
Handles connection initialization, retry logic, and basic OBD operations.
"""

import time
import logging
from typing import Optional, Tuple, Callable, Any
from obd2.obd_connection import OBDConnection

logger = logging.getLogger(__name__)


# OBD-II Mode Commands
GET_DTC_COMMAND = "03"
CLEAR_DTC_COMMAND = "04"
GET_FREEZE_DTC_COMMAND = "07"


class OBDConnection:
    """
    Manages OBD-II connection without GUI dependencies.
    
    This class handles the low-level OBD communication including
    connection establishment, retry logic, and basic operations.
    """
    
    def __init__(
        self,
        portnum: Optional[str] = None,
        baud: Optional[int] = None,
        timeout: float = 0.1,
        reconnect_attempts: int = 5,
        fast: bool = False,
        status_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize OBD connection.
        
        Args:
            portnum: Serial port (e.g., '/dev/ttyUSB0', 'COM3'). 
                    None or 'AUTO' for auto-detection.
            baud: Baud rate. None or 'AUTO' for auto-detection.
            timeout: Command timeout in seconds
            reconnect_attempts: Number of connection attempts before giving up
            fast: Enable fast mode (skip some initialization)
            status_callback: Optional[Callable[[str], None]] = None for status updates
        """
        self.connection: OBDConnection = None
        self.ELMver = "Unknown"
        self._status_callback = status_callback
        
        # Normalize parameters
        if portnum == 'AUTO':
            portnum = None
        if baud == 'AUTO' or isinstance(baud, str):
            baud = None
        
        counter = 0
        last_error = None
        
        while counter < reconnect_attempts:
            counter += 1
            self._notify_status(f"Connection attempt: {counter}/{reconnect_attempts}")
            
            # Close any existing connection
            if self.connection:
                try:
                    self.connection.close()
                except Exception as e:
                    logger.debug(f"Error closing connection: {e}")
            
            # Attempt new connection
            try:
                self.connection = OBDConnection(
                    portstr=portnum,
                    baudrate=baud,
                    protocol=None,
                    fast=fast,
                    timeout=_truncate(float(timeout), 1),
                    check_voltage=False,
                    start_low_power=False
                )
                
                if self.connection.status() == "Car Connected":
                    port_name = self.connection.port_name()
                    self._notify_status(f"Connected to: {port_name}")
                    logger.info(f"OBD connection established on {port_name}")
                    return  # Success!
                else:
                    self.connection.close()
                    last_error = f"Status: {self.connection.status()}"
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Connection attempt {counter} failed: {e}")
            
            # Wait before retry (except on last attempt)
            if counter < reconnect_attempts:
                time.sleep(1)
        
        # All attempts failed
        error_msg = f"Failed to connect after {reconnect_attempts} attempts"
        if last_error:
            error_msg += f": {last_error}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)
    
    def _notify_status(self, message: str) -> None:
        """Send status update via callback if available."""
        if self._status_callback:
            try:
                self._status_callback(message)
            except Exception as e:
                logger.warning(f"Status callback error: {e}")
    
    def close(self) -> None:
        """Close the OBD connection and reset state."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("OBD connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        self.ELMver = "Unknown"
    
    def is_connected(self) -> bool:
        """Check if currently connected to vehicle."""
        if not self.connection:
            return False
        return self.connection.status() == "Car Connected"
    
    def get_port_name(self) -> Optional[str]:
        """Get the name of the connected port."""
        if self.connection:
            try:
                return self.connection.port_name()
            except:
                pass
        return None
    
    def clear_dtc(self) -> Any:
        """
        Clear all Diagnostic Trouble Codes and freeze frame data.
        
        Returns:
            OBD response object
            
        Raises:
            ConnectionError: If not connected to vehicle
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to vehicle")
        
        try:
            response = self.connection.query(OBDConnection.commands["CLEAR_DTC"])
            logger.info("DTC codes cleared")
            return response
        except Exception as e:
            logger.error(f"Failed to clear DTC: {e}")
            raise
    
    def query_command(self, command: str) -> Any:
        """
        Send a raw OBD command and get response.
        
        Args:
            command: OBD command to send
            
        Returns:
            OBD response object
            
        Raises:
            ConnectionError: If not connected to vehicle
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to vehicle")
        
        try:
            return self.connection.query(OBDConnection.commands[command])
        except KeyError:
            raise ValueError(f"Unknown OBD command: {command}")
        except Exception as e:
            logger.error(f"Query failed for command {command}: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed."""
        self.close()
        return False


def _truncate(num: float, n: int) -> float:
    """
    Truncate a float to n decimal places without rounding.
    
    Args:
        num: Number to truncate
        n: Number of decimal places
        
    Returns:
        Truncated float
        
    Example:
        >>> _truncate(3.14159, 2)
        3.14
    """
    integer = int(num * (10 ** n)) / (10 ** n)
    return float(integer)
