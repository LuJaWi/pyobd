"""
pytest configuration and shared fixtures for PyOBD tests.

This file provides:
- Mock ELM327 adapter responses
- Mock serial port connections
- Parametrization for testing both legacy and new code
- Common test data and expected results
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import List, Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Mock Data - Common OBD responses
# ============================================================================

class MockOBDResponses:
    """Collection of realistic OBD-II responses for testing"""
    
    # Mode 01 Responses (Live Data)
    ENGINE_RPM = ["41 0C 1A F8"]  # ~1726 RPM
    VEHICLE_SPEED = ["41 0D 3C"]  # 60 km/h
    COOLANT_TEMP = ["41 05 5F"]  # 55°C
    THROTTLE_POS = ["41 11 80"]  # ~50%
    ENGINE_LOAD = ["41 04 7F"]  # ~50%
    MAF = ["41 10 1E 14"]  # ~76.84 g/s
    INTAKE_PRESSURE = ["41 0B 64"]  # 100 kPa
    INTAKE_TEMP = ["41 0F 3C"]  # 20°C
    TIMING_ADVANCE = ["41 0E 88"]  # 8° before TDC
    FUEL_PRESSURE = ["41 0A 32"]  # 156 kPa
    
    # Status response (Mode 01, PID 01)
    STATUS = ["41 01 00 07 65 04"]
    
    # Fuel trim
    SHORT_FUEL_TRIM_1 = ["41 06 80"]  # 0%
    LONG_FUEL_TRIM_1 = ["41 07 85"]  # ~2.34%
    
    # O2 Sensors
    O2_B1S1 = ["41 14 80 FF"]  # 0V, 100%
    
    # Supported PIDs
    PIDS_A = ["41 00 BE 3F B8 13"]  # Bitmap of supported PIDs 01-20
    PIDS_B = ["41 20 80 00 00 01"]  # Bitmap of supported PIDs 21-40
    
    # Mode 03 Responses (DTCs)
    DTC_COUNT = ["43 02"]  # 2 DTCs
    DTCS = ["43 01 03 01 04"]  # P0103, P0104
    NO_DTCS = ["43 00"]  # No DTCs
    
    # Mode 04 Response (Clear DTCs)
    CLEAR_OK = ["44"]
    
    # Mode 09 Responses (Vehicle Info)
    VIN = ["49 02 01 31 47 34 47 43", "49 02 02 35 34 38 34 37", "49 02 03 34 35 36 37 38"]  # Multi-frame
    
    # ELM327 responses
    ELM_VERSION = ["ELM327 v1.5"]
    ELM_OK = ["OK"]
    ELM_VOLTAGE = ["12.6V"]
    ELM_PROMPT = [">"]
    
    # Error responses
    NO_DATA = ["NO DATA"]
    CAN_ERROR = ["CAN ERROR"]
    UNABLE_TO_CONNECT = ["UNABLE TO CONNECT"]
    STOPPED = ["STOPPED"]
    
    # Protocol detection
    PROTOCOL_AUTO = ["ATSP0"]
    PROTOCOL_6 = ["6"]  # ISO 15765-4 CAN (11 bit ID, 500 kbaud)


# ============================================================================
# Mock Serial Port
# ============================================================================

class MockSerial:
    """
    Mock pyserial.Serial class for testing without hardware.
    Simulates an ELM327 adapter over serial connection.
    """
    
    def __init__(self, port=None, baudrate=38400, timeout=0.1):
        self.port = port
        self.portstr = port  # pyserial uses portstr attribute
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = True
        self._read_buffer = []
        self._command_responses = self._default_responses()
        
    def _default_responses(self) -> Dict[bytes, List[str]]:
        """Default ELM327 command/response pairs"""
        return {
            b"ATZ\r": MockOBDResponses.ELM_VERSION,
            b"ATE0\r": MockOBDResponses.ELM_OK,
            b"ATL0\r": MockOBDResponses.ELM_OK,
            b"ATS0\r": MockOBDResponses.ELM_OK,
            b"ATH1\r": MockOBDResponses.ELM_OK,
            b"ATSP0\r": MockOBDResponses.ELM_OK,
            b"0100\r": MockOBDResponses.PIDS_A,
            b"0120\r": MockOBDResponses.PIDS_B,
            b"0101\r": MockOBDResponses.STATUS,
            b"010C\r": MockOBDResponses.ENGINE_RPM,
            b"010D\r": MockOBDResponses.VEHICLE_SPEED,
            b"0105\r": MockOBDResponses.COOLANT_TEMP,
            b"ATRV\r": MockOBDResponses.ELM_VOLTAGE,
            b"0300\r": MockOBDResponses.DTC_COUNT,
            b"03\r": MockOBDResponses.DTCS,
            b"04\r": MockOBDResponses.CLEAR_OK,
        }
    
    def write(self, data: bytes) -> int:
        """Simulate writing command to adapter"""
        # Look up response for this command
        response = self._command_responses.get(data, MockOBDResponses.NO_DATA)
        
        # Add response to read buffer
        for line in response:
            self._read_buffer.extend((line + "\r\r>").encode('utf-8'))
        
        return len(data)
    
    def read(self, size: int = 1) -> bytes:
        """Simulate reading response from adapter"""
        if not self._read_buffer:
            return b''
        
        result = bytes(self._read_buffer[:size])
        self._read_buffer = self._read_buffer[size:]
        return result
    
    def readline(self) -> bytes:
        """Read a line from the buffer"""
        line = b''
        while self._read_buffer:
            byte = self._read_buffer.pop(0)
            line += bytes([byte])
            if byte == ord('\r'):
                break
        return line
    
    def close(self):
        """Close the mock serial port"""
        self.is_open = False
    
    def open(self):
        """Open the mock serial port"""
        self.is_open = True
    
    def flushInput(self):
        """Clear input buffer"""
        self._read_buffer = []
    
    def flushOutput(self):
        """Clear output buffer (no-op for mock)"""
        pass
    
    def flush(self):
        """Flush write buffer (no-op for mock)"""
        pass
    
    def set_response(self, command: bytes, response: List[str]):
        """Set custom response for specific command"""
        self._command_responses[command] = response


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_serial():
    """Provide a mock serial port"""
    return MockSerial(port='/dev/ttyUSB0')


@pytest.fixture
def mock_serial_factory():
    """Factory for creating mock serial ports with custom responses"""
    def _factory(**response_overrides):
        serial = MockSerial()
        for cmd, resp in response_overrides.items():
            serial.set_response(cmd, resp)
        return serial
    return _factory


@pytest.fixture
def obd_responses():
    """Provide collection of mock OBD responses"""
    return MockOBDResponses()


@pytest.fixture
def patch_serial(mock_serial):
    """Patch serial.Serial with mock"""
    with patch('serial.Serial', return_value=mock_serial):
        yield mock_serial


@pytest.fixture(params=['legacy', 'new'])
def codebase(request):
    """
    Parametrized fixture that runs tests against both legacy and new code.
    
    Usage:
        def test_something(codebase):
            OBD = codebase.OBD
            connection = OBD()
            assert connection.status() == OBDStatus.CAR_CONNECTED
    """
    if request.param == 'legacy':
        # Import legacy modules
        from legacy.obd import obd as legacy_obd
        from legacy.obd import commands as legacy_commands
        from legacy.obd import decoders as legacy_decoders
        from legacy.obd import utils as legacy_utils
        from legacy.obd import asynchronous as legacy_async
        from legacy.obd.OBDCommand import OBDCommand as LegacyOBDCommand
        from legacy.obd.OBDResponse import OBDResponse as LegacyOBDResponse
        from legacy.obd.protocols import protocol as legacy_protocol
        
        class LegacyCodebase:
            OBD = legacy_obd.OBD
            Async = legacy_async.Async
            commands = legacy_commands.commands
            decoders = legacy_decoders
            utils = legacy_utils
            OBDCommand = LegacyOBDCommand
            OBDResponse = LegacyOBDResponse
            OBDStatus = legacy_utils.OBDStatus
            ECU = legacy_protocol.ECU
            Message = legacy_protocol.Message
            Frame = legacy_protocol.Frame
            
        return LegacyCodebase()
    
    else:  # 'new'
        # Import new modules
        from obd2.obd2 import OBD as NewOBD
        from obd2.asynchronous import Async as NewAsync
        from obd2.command_functions import Commands
        from decoding import decoders as new_decoders
        from obd2.utils import hex_tools as new_hex_tools
        from obd2.utils.obd_status import OBDStatus as NewOBDStatus
        from obd2.command import OBDCommand as NewOBDCommand
        from obd2.response import OBDResponse as NewOBDResponse
        from ecu.ecu import ECU as NewECU
        from elm327.protocols.models.message import Message as NewMessage
        from elm327.protocols.models.frame import Frame as NewFrame
        from serial_utils.scan_serial import scan_serial as new_scan_serial
        
        class NewCodebase:
            OBD = NewOBD
            Async = NewAsync
            commands = Commands()
            decoders = new_decoders
            hex_tools = new_hex_tools
            OBDCommand = NewOBDCommand
            OBDResponse = NewOBDResponse
            OBDStatus = NewOBDStatus
            ECU = NewECU
            Message = NewMessage
            Frame = NewFrame
            scan_serial = new_scan_serial
            
        return NewCodebase()


@pytest.fixture
def sample_messages_legacy():
    """Create sample Message objects for legacy code"""
    from legacy.obd.protocols.protocol import Message, Frame
    
    # Create a simple message with one frame
    frame = Frame("41 0C 1A F8")
    frame.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
    
    message = Message([frame])
    message.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
    
    return [message]


@pytest.fixture
def sample_messages_new():
    """Create sample Message objects for new code"""
    from elm327.protocols.models.message import Message
    from elm327.protocols.models.frame import Frame
    
    # Create a simple message with one frame
    frame = Frame("41 0C 1A F8")
    frame.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
    
    message = Message([frame])
    message.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
    
    return [message]


# ============================================================================
# Marks for organizing tests
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "decoders: tests for decoder functions"
    )
    config.addinivalue_line(
        "markers", "protocols: tests for protocol parsing"
    )
    config.addinivalue_line(
        "markers", "connection: tests for OBD connection"
    )
    config.addinivalue_line(
        "markers", "commands: tests for command definitions"
    )
    config.addinivalue_line(
        "markers", "utils: tests for utility functions"
    )
    config.addinivalue_line(
        "markers", "integration: integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )
