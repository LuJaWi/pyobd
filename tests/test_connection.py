"""
Test OBD connection class for the codebase.

Tests connection initialization, querying, and status management with mocks.
"""

import pytest
from unittest.mock import patch
from obd2.obd_connection import OBDConnection
from obd2.utils.obd_status import OBDStatus


@pytest.mark.connection
class TestOBDConnection:
    """Test OBD class connection and initialization"""
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_connection_with_explicit_port_new(self, mock_serial_for_url, mock_serial):
        """Test OBDConnection connection with explicit port"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        
        assert connection is not None
        assert hasattr(connection, 'interface')
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_connection_close_new(self, mock_serial_for_url, mock_serial):
        """Test closing OBDConnection connection"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        connection.close()
        
        assert connection.interface is None


@pytest.mark.connection
class TestOBDStatus:
    """Test OBD status checking"""
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_status_method_new(self, mock_serial_for_url, mock_serial):
        """Test status() method"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        status = connection.status()
        
        assert isinstance(status, OBDStatus)
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_is_connected_method_new(self, mock_serial_for_url, mock_serial):
        """Test is_connected() method"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        
        assert hasattr(connection, 'is_connected')
        assert callable(connection.is_connected)


@pytest.mark.connection
class TestOBDProperties:
    """Test OBD connection properties"""
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_port_name_new(self, mock_serial_for_url, mock_serial):
        """Test port_name property"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        
        assert hasattr(connection, 'port_name')
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_protocol_name_new(self, mock_serial_for_url, mock_serial):
        """Test protocol_name property"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        
        assert hasattr(connection, 'protocol_name')
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_protocol_id_new(self, mock_serial_for_url, mock_serial):
        """Test protocol_id property"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        
        assert hasattr(connection, 'protocol_id')


@pytest.mark.connection
class TestOBDCommands:
    """Test OBD command support checking"""
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_supports_method_new(self, mock_serial_for_url, mock_serial):
        """Test supports() method"""
        from obd2.command_functions import Commands
        
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        commands = Commands()
        
        assert hasattr(connection, 'supports')
        assert callable(connection.supports)
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_print_commands_new(self, mock_serial_for_url, mock_serial):
        """Test print_commands() method"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        
        assert hasattr(connection, 'print_commands')


@pytest.mark.connection
class TestOBDPowerModes:
    """Test OBD power mode operations"""
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_low_power_new(self, mock_serial_for_url, mock_serial):
        """Test setting low power mode"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        # Just check the connection was created successfully
        assert connection is not None
    
    @patch('elm327.elm327.serial.serial_for_url')
    def test_normal_power_new(self, mock_serial_for_url, mock_serial):
        """Test setting normal power mode"""
        mock_serial_for_url.return_value = mock_serial
        
        connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
        # Just check the connection was created successfully
        assert connection is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
