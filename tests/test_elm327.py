"""
Tests for ELM327 class - focuses on improving coverage for elm327.py

This test suite directly tests the ELM327 class to achieve better code coverage,
particularly for initialization, protocol detection, baudrate detection, and
communication methods.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import serial

from elm327.elm327 import ELM327, detect_elm327_baudrate
from obd2.utils.obd_status import OBDStatus
from elm327.protocols.protocol_unknown import UnknownProtocol


class TestELM327Initialization:
    """Test ELM327 __init__ and initialization sequence"""
    
    def test_init_successful_connection(self, mock_serial_class):
        """Test successful initialization with all steps passing"""
        mock_port = mock_serial_class.return_value
        mock_port.portstr = '/dev/ttyUSB0'
        mock_port.baudrate = 38400
        
        # Configure responses for initialization sequence
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',  # ATZ response
            b'ATE0\rOK>',     # ATE0 response (with echo)
            b'OK>',           # ATH1 response
            b'OK>',           # ATL0 response
            b'OK>',           # ATSP0 response
            b'41 00 BE 3E B8 13>',  # 0100 response
            b'A6>',           # ATDPN response (protocol 6)
        ]
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        
        assert elm.status() == OBDStatus.CAR_CONNECTED
        assert mock_port.write.call_count >= 4  # At least ATZ, ATE0, ATH1, ATL0
        
    def test_init_baudrate_failure(self, mock_serial_class):
        """Test initialization fails when baudrate cannot be set"""
        mock_port = mock_serial_class.return_value
        mock_port.baudrate = None
        
        # Make set_baudrate fail
        with patch.object(ELM327, 'set_baudrate', return_value=False):
            elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
            assert elm.status() == OBDStatus.NOT_CONNECTED
    
    def test_init_atz_no_elm_response(self, mock_serial_class):
        """Test initialization fails when ATZ doesn't get ELM response"""
        mock_port = mock_serial_class.return_value
        mock_port.read.return_value = b'JUNK DATA>'
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        assert elm.status() == OBDStatus.NOT_CONNECTED
    
    def test_init_atz_serial_exception(self, mock_serial_class):
        """Test initialization handles SerialException during ATZ"""
        mock_port = mock_serial_class.return_value
        mock_port.write.side_effect = serial.SerialException("Port error")
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        assert elm.status() == OBDStatus.NOT_CONNECTED
    
    def test_init_ate0_failure(self, mock_serial_class):
        """Test initialization fails when ATE0 doesn't return OK"""
        mock_port = mock_serial_class.return_value
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',  # ATZ response
            b'ERROR>',        # ATE0 fails
        ]
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        assert elm.status() == OBDStatus.NOT_CONNECTED
    
    def test_init_ath1_failure(self, mock_serial_class):
        """Test initialization fails when ATH1 doesn't return OK"""
        mock_port = mock_serial_class.return_value
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',  # ATZ response
            b'ATE0\rOK>',     # ATE0 success
            b'ERROR>',        # ATH1 fails
        ]
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        assert elm.status() == OBDStatus.NOT_CONNECTED
    
    def test_init_atl0_failure(self, mock_serial_class):
        """Test initialization fails when ATL0 doesn't return OK"""
        mock_port = mock_serial_class.return_value
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',  # ATZ response
            b'ATE0\rOK>',     # ATE0 success
            b'OK>',           # ATH1 success
            b'ERROR>',        # ATL0 fails
        ]
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        assert elm.status() == OBDStatus.NOT_CONNECTED
    
    def test_init_with_voltage_check_success(self, mock_serial_class):
        """Test initialization with voltage check passes"""
        mock_port = mock_serial_class.return_value
        mock_port.portstr = '/dev/ttyUSB0'
        mock_port.baudrate = 38400
        
        # Note: voltage check was refactored - need to patch the method directly
        with patch.object(ELM327, '_ELM327__is_vehicle_voltage_correct', return_value=True):
            mock_port.read.side_effect = [
                b'ELM327 v1.5>',  # ATZ response
                b'ATE0\rOK>',     # ATE0 response
                b'OK>',           # ATH1 response
                b'OK>',           # ATL0 response
                b'OK>',           # ATSP0 response
                b'41 00 BE 3E B8 13>',  # 0100 response
                b'A6>',           # ATDPN response
            ]
            
            elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, 
                         timeout=10, check_voltage=True)
            
            assert elm.status() == OBDStatus.CAR_CONNECTED
    
    def test_init_with_voltage_check_low_voltage(self, mock_serial_class):
        """Test initialization fails when voltage is too low"""
        mock_port = mock_serial_class.return_value
        
        with patch.object(ELM327, '_ELM327__is_vehicle_voltage_correct', return_value=False):
            mock_port.read.side_effect = [
                b'ELM327 v1.5>',  # ATZ response
                b'ATE0\rOK>',     # ATE0 response
                b'OK>',           # ATH1 response
                b'OK>',           # ATL0 response
            ]
            
            elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, 
                         timeout=10, check_voltage=True)
            
            assert elm.status() == OBDStatus.ELM_CONNECTED
    
    def test_init_with_voltage_check_no_response(self, mock_serial_class):
        """Test initialization fails when voltage check returns no data"""
        mock_port = mock_serial_class.return_value
        
        with patch.object(ELM327, '_ELM327__is_vehicle_voltage_correct', return_value=False):
            mock_port.read.side_effect = [
                b'ELM327 v1.5>',  # ATZ response
                b'ATE0\rOK>',     # ATE0 response
                b'OK>',           # ATH1 response
                b'OK>',           # ATL0 response
            ]
            
            elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, 
                         timeout=10, check_voltage=True)
            
            assert elm.status() == OBDStatus.ELM_CONNECTED
    
    def test_init_with_start_low_power(self, mock_serial_class):
        """Test initialization with start_low_power flag"""
        mock_port = mock_serial_class.return_value
        mock_port.portstr = '/dev/ttyUSB0'
        mock_port.baudrate = 38400
        
        mock_port.read.side_effect = [
            b'ELM327 v1.5>',  # ATZ response
            b'ATE0\rOK>',     # ATE0 response
            b'OK>',           # ATH1 response
            b'OK>',           # ATL0 response
            b'OK>',           # ATSP0 response
            b'41 00 BE 3E B8 13>',  # 0100 response
            b'A6>',           # ATDPN response
        ]
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, 
                     timeout=10, start_low_power=True)
        
        # Should send space character to wake up
        assert any(b' ' in call[0][0] for call in mock_port.write.call_args_list)
    
    def test_init_protocol_set_failure(self, mock_serial_class):
        """Test initialization when protocol cannot be set"""
        mock_port = mock_serial_class.return_value
        
        # Provide enough responses for all protocol attempts to fail
        responses = [
            b'ELM327 v1.5>',  # ATZ response
            b'ATE0\rOK>',     # ATE0 response
            b'OK>',           # ATH1 response
            b'OK>',           # ATL0 response
            b'OK>',           # ATSP0 response
            b'UNABLE TO CONNECT>',  # 0100 fails
            b'0>',            # ATDPN returns 0 (unknown)
        ]
        # Add failures for all protocol attempts (need 2 per protocol: ATTP + 0100)
        for _ in range(len(ELM327._TRY_PROTOCOL_ORDER) * 2):
            responses.append(b'UNABLE TO CONNECT>')
        
        mock_port.read.side_effect = responses
        
        elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
        
        # Should stay at ELM_CONNECTED since protocol failed
        assert elm.status() == OBDStatus.ELM_CONNECTED


class TestELM327ProtocolMethods:
    """Test protocol detection and configuration"""
    
    def test_set_protocol_with_explicit_protocol(self, mock_serial_class, initialized_elm):
        """Test set_protocol with explicit protocol number"""
        elm = initialized_elm
        elm._ELM327__port.read.side_effect = [
            b'OK>',                  # ATTP6 response
            b'41 00 BE 3E B8 13>',   # 0100 response
        ]
        
        result = elm.set_protocol("6")
        assert result == True
    
    def test_set_protocol_invalid_protocol(self, initialized_elm):
        """Test set_protocol with invalid protocol number"""
        elm = initialized_elm
        result = elm.set_protocol("Z")
        assert result == False
    
    def test_manual_protocol_success(self, mock_serial_class, initialized_elm):
        """Test manual_protocol with successful connection"""
        elm = initialized_elm
        elm._ELM327__port.read.side_effect = [
            b'OK>',                  # ATTP6 response
            b'41 00 BE 3E B8 13>',   # 0100 response (success!)
        ]
        
        result = elm.manual_protocol("6")
        assert result == True
    
    def test_manual_protocol_unable_to_connect(self, mock_serial_class, initialized_elm):
        """Test manual_protocol when unable to connect"""
        elm = initialized_elm
        elm._ELM327__port.read.side_effect = [
            b'OK>',                    # ATTP6 response
            b'UNABLE TO CONNECT>',     # 0100 fails
        ]
        
        result = elm.manual_protocol("6")
        assert result == False
    
    def test_auto_protocol_success(self, mock_serial_class, initialized_elm):
        """Test auto_protocol successfully detects protocol"""
        elm = initialized_elm
        elm._ELM327__port.read.side_effect = [
            b'OK>',                  # ATSP0 response
            b'41 00 BE 3E B8 13>',   # 0100 response
            b'A6>',                  # ATDPN returns protocol 6
        ]
        
        result = elm.auto_protocol()
        assert result == True
    
    def test_auto_protocol_fallback_to_manual(self, mock_serial_class, initialized_elm):
        """Test auto_protocol falls back to trying protocols manually"""
        elm = initialized_elm
        elm._ELM327__port.read.side_effect = [
            b'OK>',                    # ATSP0 response
            b'UNABLE TO CONNECT>',     # 0100 fails
            b'0>',                     # ATDPN returns 0 (unknown)
            b'OK>',                    # ATTP6 (first in order)
            b'41 00 BE 3E B8 13>',     # 0100 success!
        ]
        
        result = elm.auto_protocol()
        assert result == True
    
    def test_auto_protocol_all_fail(self, mock_serial_class, initialized_elm):
        """Test auto_protocol when all protocols fail"""
        elm = initialized_elm
        
        # Generate enough UNABLE TO CONNECT responses for all protocol attempts
        responses = [
            b'OK>',                    # ATSP0 response
            b'UNABLE TO CONNECT>',     # 0100 fails
            b'0>',                     # ATDPN returns 0
        ]
        # Add failures for all protocols in _TRY_PROTOCOL_ORDER
        for _ in range(len(ELM327._TRY_PROTOCOL_ORDER) * 2):
            responses.append(b'UNABLE TO CONNECT>')
        
        elm._ELM327__port.read.side_effect = responses
        
        result = elm.auto_protocol()
        assert result == False


class TestELM327BaudrateMethods:
    """Test baudrate detection and configuration"""
    
    def test_set_baudrate_with_specific_rate(self, mock_serial_class, initialized_elm):
        """Test set_baudrate with specific baudrate"""
        elm = initialized_elm
        result = elm.set_baudrate(115200)
        assert result == 115200
        assert elm._ELM327__port.baudrate == 115200
    
    def test_set_baudrate_auto_detect_pseudo_terminal(self, mock_serial_class, initialized_elm):
        """Test set_baudrate auto-detection skips pseudo terminals"""
        elm = initialized_elm
        elm._ELM327__port.portstr = '/dev/pts/0'
        
        result = elm.set_baudrate(None)
        assert result == 38400  # Default for pseudo terminals
    
    def test_auto_detect_baudrate_success(self, mock_serial_class, initialized_elm):
        """Test auto_detect_baudrate finds correct baudrate"""
        elm = initialized_elm
        elm._ELM327__port.read.side_effect = [
            b'',                      # First baudrate fails
            b'ELM327 v1.5>',          # Second baudrate succeeds
        ]
        
        result = elm.auto_detect_baudrate()
        # auto_detect_baudrate returns the baudrate on success
        assert result is not None
        assert isinstance(result, int)
    
    def test_auto_detect_baudrate_all_fail(self, mock_serial_class, initialized_elm):
        """Test auto_detect_baudrate when all baudrates fail"""
        elm = initialized_elm
        elm._ELM327__port.read.return_value = b''  # Always empty
        
        result = elm.auto_detect_baudrate()
        # Returns None on failure
        assert result is None
    
    def test_detect_elm327_baudrate_standalone_success(self, mock_serial_class):
        """Test standalone detect_elm327_baudrate function"""
        mock_port = mock_serial_class.return_value
        mock_port.timeout = 10
        mock_port.read.side_effect = [
            b'',                      # First baudrate fails
            b'ELM327 v1.5>',          # Second baudrate succeeds
        ]
        
        result = detect_elm327_baudrate(mock_port)
        assert result == ELM327._TRY_BAUDS[1]  # Second in list
    
    def test_detect_elm327_baudrate_with_prompt_only(self, mock_serial_class):
        """Test detect_elm327_baudrate recognizes prompt character"""
        mock_port = mock_serial_class.return_value
        mock_port.timeout = 10
        mock_port.read.return_value = b'\x7f\x7f\r>'  # Just echo and prompt
        
        result = detect_elm327_baudrate(mock_port)
        assert result == ELM327._TRY_BAUDS[0]  # First baudrate
    
    def test_detect_elm327_baudrate_all_fail(self, mock_serial_class):
        """Test detect_elm327_baudrate when no baudrate works"""
        mock_port = mock_serial_class.return_value
        mock_port.timeout = 10
        mock_port.read.return_value = b''  # Always empty
        
        result = detect_elm327_baudrate(mock_port)
        assert result is None


class TestELM327Communication:
    """Test communication methods"""
    
    def test_send_and_parse_when_connected(self, initialized_elm):
        """Test send_and_parse returns parsed messages"""
        elm = initialized_elm
        elm._ELM327__status = OBDStatus.CAR_CONNECTED
        elm._ELM327__port.read.return_value = b'41 0C 1A F8>'
        
        messages = elm.send_and_parse(b"010C")
        assert messages is not None
    
    def test_send_and_parse_when_not_connected(self, initialized_elm):
        """Test send_and_parse returns None when not connected"""
        elm = initialized_elm
        elm._ELM327__status = OBDStatus.NOT_CONNECTED
        
        messages = elm.send_and_parse(b"010C")
        assert messages is None
    
    def test_send_and_parse_wakes_from_low_power(self, initialized_elm):
        """Test send_and_parse wakes device from low power"""
        elm = initialized_elm
        elm._ELM327__status = OBDStatus.CAR_CONNECTED
        elm._ELM327__low_power = True
        elm._ELM327__port.read.return_value = b'41 0C 1A F8>'
        
        messages = elm.send_and_parse(b"010C")
        
        # Should have sent space to wake up
        assert any(b' ' in call[0][0] for call in elm._ELM327__port.write.call_args_list)


class TestELM327PowerManagement:
    """Test power management methods"""
    
    def test_low_power_success(self, initialized_elm):
        """Test entering low power mode"""
        elm = initialized_elm
        elm._ELM327__status = OBDStatus.CAR_CONNECTED
        elm._ELM327__port.read.return_value = b'OK>'
        
        result = elm.low_power()
        assert 'OK' in result
    
    def test_low_power_when_not_connected(self, initialized_elm):
        """Test low_power returns None when not connected"""
        elm = initialized_elm
        elm._ELM327__status = OBDStatus.NOT_CONNECTED
        
        result = elm.low_power()
        assert result is None
    
    def test_normal_power(self, initialized_elm):
        """Test exiting low power mode"""
        elm = initialized_elm
        elm._ELM327__status = OBDStatus.CAR_CONNECTED
        elm._ELM327__low_power = True
        elm._ELM327__port.read.return_value = b'>'
        
        result = elm.normal_power()
        assert result is not None
    
    def test_normal_power_when_not_connected(self, initialized_elm):
        """Test normal_power returns None when not connected"""
        elm = initialized_elm
        elm._ELM327__status = OBDStatus.NOT_CONNECTED
        
        result = elm.normal_power()
        assert result is None


class TestELM327CloseAndCleanup:
    """Test close and cleanup methods"""
    
    def test_close_sends_atz(self, initialized_elm, mock_serial_class):
        """Test close sends ATZ to reset device"""
        elm = initialized_elm
        mock_port = mock_serial_class.return_value
        
        # Reset mock to clear initialization calls
        mock_port.reset_mock()
        
        elm.close()
        
        # Should send ATZ
        write_calls = [call[0][0] for call in mock_port.write.call_args_list]
        assert any(b'ATZ' in call for call in write_calls)
    
    def test_close_closes_port(self, initialized_elm, mock_serial_class):
        """Test close closes the serial port"""
        elm = initialized_elm
        mock_port = mock_serial_class.return_value
        
        elm.close()
        
        assert mock_port.close.called
        assert elm.status() == OBDStatus.NOT_CONNECTED
    
    def test_close_handles_exceptions(self, initialized_elm):
        """Test close handles exceptions gracefully"""
        elm = initialized_elm
        elm._ELM327__port.write.side_effect = Exception("Port error")
        
        # Should not raise
        elm.close()
        assert elm.status() == OBDStatus.NOT_CONNECTED


class TestELM327Properties:
    """Test property methods"""
    
    def test_port_name(self, initialized_elm):
        """Test port_name returns port string"""
        elm = initialized_elm
        elm._ELM327__port.portstr = '/dev/ttyUSB0'
        
        assert elm.port_name() == '/dev/ttyUSB0'
    
    def test_port_name_when_none(self, initialized_elm):
        """Test port_name when port is None"""
        elm = initialized_elm
        elm._ELM327__port = None
        
        assert elm.port_name() == ""
    
    def test_status(self, initialized_elm):
        """Test status method"""
        elm = initialized_elm
        elm._ELM327__status = OBDStatus.CAR_CONNECTED
        
        assert elm.status() == OBDStatus.CAR_CONNECTED
    
    def test_baudrate(self, initialized_elm):
        """Test baudrate method"""
        elm = initialized_elm
        elm._ELM327__port.baudrate = 115200
        
        assert elm.baudrate() == 115200
    
    def test_protocol_name(self, initialized_elm):
        """Test protocol_name method"""
        elm = initialized_elm
        assert hasattr(elm.protocol_name(), '__len__')  # Returns a string
    
    def test_protocol_id(self, initialized_elm):
        """Test protocol_id method"""
        elm = initialized_elm
        assert hasattr(elm.protocol_id(), '__len__')  # Returns a string
    
    def test_ecus(self, initialized_elm):
        """Test ecus method"""
        elm = initialized_elm
        ecus = elm.ecus()
        assert hasattr(ecus, '__iter__')  # Returns iterable


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
    """Mock time.sleep to speed up tests - applies to all tests automatically"""
    with patch('time.sleep', return_value=None):
        yield


@pytest.fixture
def initialized_elm(mock_serial_class):
    """Create a minimally initialized ELM327 instance for testing"""
    mock_port = mock_serial_class.return_value
    
    # Minimal responses to get through initialization
    mock_port.read.side_effect = [
        b'ELM327 v1.5>',  # ATZ response
        b'ATE0\rOK>',     # ATE0 response
        b'OK>',           # ATH1 response
        b'OK>',           # ATL0 response
        b'OK>',           # ATSP0 response
        b'41 00 BE 3E B8 13>',  # 0100 response
        b'A6>',           # ATDPN response
    ]
    
    elm = ELM327(portname='/dev/ttyUSB0', baudrate=38400, protocol=None, timeout=10)
    
    # Reset mock for actual test usage
    mock_port.reset_mock()
    mock_port.read.side_effect = None
    
    return elm
