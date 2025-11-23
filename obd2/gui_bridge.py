#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUI Bridge for OBD Connection

Provides wxPython-compatible wrapper around OBDConnection.
Handles GUI event posting and legacy interface compatibility.
"""

import time
import string
import logging
from typing import Optional, Tuple

from obd2.connection import OBDConnection

logger = logging.getLogger(__name__)


class OBDConnectionGUI:
    """
    GUI-aware wrapper for OBDConnection.
    
    This class wraps OBDConnection and adds wxPython event posting
    for status updates. Maintains backward compatibility with the
    original GUI interface.
    """
    
    def __init__(
        self,
        portnum: str,
        notify_window,
        baud: str,
        SERTIMEOUT: float,
        RECONNATTEMPTS: int,
        FAST: str
    ):
        """
        Initialize OBD connection with GUI notifications.
        
        Args:
            portnum: Serial port or 'AUTO'
            notify_window: wxPython window for event posting
            baud: Baud rate or 'AUTO'
            SERTIMEOUT: Timeout in seconds
            RECONNATTEMPTS: Number of reconnection attempts
            FAST: 'FAST' to enable fast mode, anything else for normal mode
        """
        self._notify_window = notify_window
        
        # Import wx here to keep it isolated
        try:
            import wx
            from debugEvent import DebugEvent
            self.wx = wx
            self.DebugEvent = DebugEvent
        except ImportError:
            logger.warning("wxPython not available - GUI notifications disabled")
            self.wx = None
            self.DebugEvent = None
        
        # Normalize FAST parameter
        fast_mode = (FAST == 'FAST')
        
        # Create status callback for GUI events
        def status_callback(message: str):
            self._post_debug_event([2, message])
        
        # Create the underlying connection
        try:
            self.connection = OBDConnection(
                portnum=portnum,
                baud=baud,
                timeout=SERTIMEOUT,
                reconnect_attempts=RECONNATTEMPTS,
                fast=fast_mode,
                status_callback=status_callback
            )
        except ConnectionError as e:
            self._post_debug_event([2, f"Connection failed: {e}"])
            raise
    
    def _post_debug_event(self, data):
        """Post a debug event to the GUI window if available."""
        if self.wx and self.DebugEvent and self._notify_window:
            try:
                self.wx.PostEvent(
                    self._notify_window,
                    self.DebugEvent(data)
                )
            except Exception as e:
                logger.warning(f"Failed to post GUI event: {e}")
    
    def close(self):
        """Close the OBD connection."""
        if hasattr(self, 'connection'):
            self.connection.close()
    
    def clear_dtc(self):
        """Clear all DTCs and freeze frame data."""
        return self.connection.clear_dtc()
    
    def sensor(self, sensor_index: int) -> Tuple[str, str, str]:
        """
        Get sensor reading by index.
        
        Args:
            sensor_index: Index into SENSORS list
            
        Returns:
            Tuple of (name, value, unit)
            
        Note:
            This is a legacy method that needs implementation.
            Consider using the newer command-based interface instead.
        """
        # TODO: Implement sensor reading
        # This requires integration with obd2.sensors.sensors
        logger.warning("sensor() method not yet implemented")
        return ("Unknown", "N/A", "")
    
    def log(self, sensor_index: int, filename: str) -> None:
        """
        Log sensor data to a file continuously.
        
        Args:
            sensor_index: Index of sensor to log
            filename: Output file path
            
        Warning:
            This method runs an infinite loop! Use with caution.
            Consider implementing stop conditions or using a separate thread.
        """
        try:
            with open(filename, "w") as file:
                start_time = time.time()
                
                # Write header
                data = self.sensor(sensor_index)
                file.write(f"Time\t{data[0].strip()}({data[2]})\n")
                
                # Continuous logging loop
                while True:
                    now = time.time()
                    data = self.sensor(sensor_index)
                    line = f"{now - start_time:.6f},\t{data[1]}\n"
                    file.write(line)
                    file.flush()
                    
        except KeyboardInterrupt:
            logger.info("Logging stopped by user")
        except Exception as e:
            logger.error(f"Logging error: {e}")
            raise
    
    @property
    def ELMver(self) -> str:
        """Get ELM327 version string."""
        if hasattr(self, 'connection'):
            return self.connection.ELMver
        return "Unknown"
    
    @ELMver.setter
    def ELMver(self, value: str):
        """Set ELM327 version string."""
        if hasattr(self, 'connection'):
            self.connection.ELMver = value
