"""
Tests for ELM327 reconnection functionality

Tests the reconnect() and send_and_parse_with_reconnect() methods
to ensure the device can recover from disconnections.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import serial

from elm327.elm327 import ELM327
from obd2.utils.obd_status import OBDStatus


class TestELM327Reconnect:
    """Test ELM327 reconnection capabilities"""
    
    def test_reconnect_success_first_attempt(self, mock_serial_class):
        """Test successful reconnection on first attempt"""
        mock_port = mock_serial_class.return_value
        mock_port.portstr = '/dev/ttyUSB0'
        mock_port.baudrate = 38400
        
        # Initial connection
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',  # ATZ
            b'ATE0\rOK>',     # ATE0
            b'OK>',           # ATH1
            b'OK>',           # ATL0
            b'OK>',           # ATSP0
            b'41 00 BE 3E B8 13>',  # 0100
            b'A6>',           # ATDPN
        ]
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        assert elm.status == OBDStatus.CAR_CONNECTED
        
        # Simulate disconnection
        elm._ELM327__status = OBDStatus.NOT_CONNECTED
        elm._ELM327__port = None
        
        # Setup responses for reconnection - need full sequence including protocol detection
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',  # ATZ
            b'ATE0\rOK>',     # ATE0
            b'OK>',           # ATH1
            b'OK>',           # ATL0
            b'OK>',           # ATSP0
            b'41 00 BE 3E B8 13>',  # 0100
            b'A6>',           # ATDPN (protocol 6)
        ]
        
        # Attempt reconnection
        result = elm.reconnect()
        
        assert result == True
        assert elm.status in [OBDStatus.CAR_CONNECTED, OBDStatus.ELM_CONNECTED]
    
    def test_reconnect_fails_port_open(self, mock_serial_class):
        """Test reconnection fails when port cannot be opened"""
        mock_port = mock_serial_class.return_value
        mock_port.portstr = '/dev/ttyUSB0'
        mock_port.baudrate = 38400
        
        # Initial connection
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',
            b'ATE0\rOK>',
            b'OK>',
            b'OK>',
            b'OK>',
            b'41 00 BE 3E B8 13>',
            b'A6>',
        ]
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        
        # Make port opening fail
        with patch('serial.serial_for_url', side_effect=serial.SerialException("Port not found")):
            result = elm.reconnect(max_attempts=2)
            
            assert result == False
            assert elm.status == OBDStatus.NOT_CONNECTED
    
    def test_reconnect_succeeds_second_attempt(self, mock_serial_class):
        """Test reconnection succeeds on second attempt after first fails"""
        mock_port = mock_serial_class.return_value
        mock_port.portstr = '/dev/ttyUSB0'
        mock_port.baudrate = 38400
        
        # Initial connection
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',
            b'ATE0\rOK>',
            b'OK>',
            b'OK>',
            b'OK>',
            b'41 00 BE 3E B8 13>',
            b'A6>',
        ]
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        
        # Setup reconnection: first attempt fails ATZ, second succeeds
        mock_port.read.side_effect = [
            b'JUNK>',          # First ATZ fails (no ELM in response)
            b'ELM327 v1.5>',   # Second ATZ succeeds
            b'ATE0\rOK>',
            b'OK>',
            b'OK>',
            b'OK>',           # ATSP0
            b'41 00 BE 3E B8 13>',  # 0100
            b'A6>',           # ATDPN
        ]
        
        result = elm.reconnect(max_attempts=2, retry_delay=0.1)
        
        assert result == True
    
    def test_reconnect_no_portname_available(self, mock_serial_class):
        """Test reconnection fails gracefully when port name not available"""
        mock_port = mock_serial_class.return_value
        mock_port.portstr = '/dev/ttyUSB0'
        
        # Initial connection
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',
            b'ATE0\rOK>',
            b'OK>',
            b'OK>',
            b'OK>',
            b'41 00 BE 3E B8 13>',
            b'A6>',
        ]
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        
        # Simulate complete loss of port info
        elm._ELM327__port = None
        
        result = elm.reconnect()
        
        assert result == False


# class TestELM327SendWithReconnect:
#     """Test send_and_parse_with_reconnect method"""
    
#     def test_send_with_reconnect_no_reconnect_needed(self, initialized_elm):
#         """Test normal send when connection is good"""
#         elm = initialized_elm
#         elm._ELM327__status = OBDStatus.CAR_CONNECTED
#         elm._ELM327__port.read.return_value = b'41 0C 1A F8>'
        
#         result = elm.send_and_parse_with_reconnect(b"010C")
        
#         assert result is not None
    
#     def test_send_with_reconnect_auto_reconnect_disabled(self, initialized_elm):
#         """Test send fails when auto_reconnect disabled"""
#         elm = initialized_elm
#         elm._ELM327__status = OBDStatus.NOT_CONNECTED
        
#         result = elm.send_and_parse_with_reconnect(b"010C", auto_reconnect=False)
        
#         assert result is None
    
#     def test_send_with_reconnect_succeeds_after_reconnect(self, mock_serial_class, initialized_elm):
#         """Test send succeeds after automatic reconnection"""
#         elm = initialized_elm
#         mock_port = mock_serial_class.return_value
        
#         # First send fails (disconnected)
#         elm._ELM327__status = OBDStatus.NOT_CONNECTED
        
#         # Setup reconnection responses
#         mock_port.read.side_effect = [
#             b'ELM327 v1.5>',  # ATZ
#             b'ATE0\rOK>',     # ATE0
#             b'OK>',           # ATH1
#             b'OK>',           # ATL0
#             b'OK>',           # ATSP6
#             b'41 00 BE 3E B8 13>',  # 0100
#             b'41 0C 1A F8>',  # Actual command response
#         ]
        
#         with patch.object(elm, 'reconnect', return_value=True):
#             with patch.object(elm, 'send_and_parse', side_effect=[None, ['message']]):
#                 result = elm.send_and_parse_with_reconnect(b"010C")
                
#                 # Should attempt reconnect and retry
#                 assert elm.reconnect.called
    
#     def test_send_with_reconnect_fails_after_reconnect_fails(self, initialized_elm):
#         """Test send returns None when reconnection fails"""
#         elm = initialized_elm
#         elm._ELM327__status = OBDStatus.NOT_CONNECTED
        
#         with patch.object(elm, 'reconnect', return_value=False):
#             result = elm.send_and_parse_with_reconnect(b"010C")
            
#             assert result is None
#             assert elm.reconnect.called


# Fixtures

@pytest.fixture
def mock_serial_class():
    """Mock serial.Serial class"""
    with patch('serial.serial_for_url') as mock:
        mock_port = MagicMock(spec=serial.Serial)
        mock_port.portstr = '/dev/ttyUSB0'
        mock_port.baudrate = 38400
        mock_port.timeout = 10
        mock_port.write_timeout = 10
        mock_port.in_waiting = 0
        mock_port.is_open = True
        mock.return_value = mock_port
        yield mock


@pytest.fixture(autouse=True)
def mock_time_sleep():
    """Mock time.sleep to speed up tests"""
    with patch('time.sleep', return_value=None):
        yield


@pytest.fixture
def initialized_elm(mock_serial_class):
    """Create a minimally initialized ELM327 instance for testing"""
    mock_port = mock_serial_class.return_value
    
    # Minimal responses to get through initialization
    mock_port.read.side_effect = [
        b'ELM327 v1.5>',
        b'ATE0\rOK>',
        b'OK>',
        b'OK>',
        b'OK>',
        b'41 00 BE 3E B8 13>',
        b'A6>',
    ]
    
    elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
    
    # Reset mock for actual test usage
    mock_port.reset_mock()
    mock_port.read.side_effect = None
    
    return elm
