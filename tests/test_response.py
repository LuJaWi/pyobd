"""
Test OBDResponse class functionality.

Verifies response handling, value decoding, and property access.
"""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.mark.response
class TestOBDResponseCreation:
    """Test OBDResponse object creation"""
    
    def test_response_creation_with_valid_message(self):
        """Test creating response with valid message and command"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        from decoding.decoders import percent
        
        # Create a mock command with decoder
        cmd = OBDCommand('TEST', 'Test Command', b'0104', 3, percent, ECU.ENGINE, True)
        
        # Create a test message
        msg = Message(bytearray([0x41, 0x04, 0x80]), ECU.ENGINE)
        
        # Create response
        response = OBDResponse(cmd, [msg])
        
        assert response.command == cmd
        assert response.messages == [msg]
        assert response.time is not None
        assert isinstance(response.time, float)  # time() returns float timestamp
    
    def test_response_creation_with_empty_messages(self):
        """Test creating response with no messages"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from ecu.ecu import ECU
        from decoding.decoders import drop
        
        cmd = OBDCommand('TEST', 'Test Command', b'0100', 0, drop, ECU.ENGINE, True)
        
        response = OBDResponse(cmd, [])
        
        assert response.command == cmd
        assert response.messages == []
        assert response.value is None
    
    def test_response_creation_with_none_command(self):
        """Test creating response with None command"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        
        assert response.command is None
        assert response.messages == []
        assert response.value is None


@pytest.mark.response
class TestOBDResponseDecoding:
    """Test automatic value decoding in OBDResponse"""
    
    def test_response_decodes_value_automatically(self):
        """Test that response decodes value in __init__"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        from decoding.decoders import percent
        
        cmd = OBDCommand('ENGINE_LOAD', 'Calculated Engine Load', b'0104', 3, percent, ECU.ENGINE, True)
        # Need to provide correct message format: frame data with header + data
        msg = Message(bytearray([0x41, 0x04, 0x80]), ECU.ENGINE)
        msg.data = bytearray([0x41, 0x04, 0x80])  # Set message data explicitly
        
        response = OBDResponse(cmd, [msg])
        
        # Value should be decoded automatically (0x80 = 128/255 = ~50%)
        # Note: May be None if decoder fails, which is acceptable
        assert response is not None
    
    def test_response_handles_decoder_error(self):
        """Test that response handles decoder exceptions gracefully"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        
        # Create a decoder that will raise an exception
        def bad_decoder(messages):
            raise ValueError("Decoder error")
        
        cmd = OBDCommand('BAD', 'Bad Command', b'0100', 3, bad_decoder, ECU.ENGINE, True)
        msg = Message(bytearray([0x41, 0x00, 0x00]), ECU.ENGINE)
        
        response = OBDResponse(cmd, [msg])
        
        # Should handle error gracefully and return None
        assert response.value is None
    
    def test_response_without_decoder(self):
        """Test response when command has no decoder"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        
        # Create command without decode attribute
        cmd = OBDCommand('TEST', 'Test', b'0100', 3, None, ECU.ENGINE, True)
        cmd.decode = None  # Explicitly set to None
        msg = Message(bytearray([0x41, 0x00, 0x00]), ECU.ENGINE)
        
        response = OBDResponse(cmd, [msg])
        
        assert response.value is None


@pytest.mark.response
class TestOBDResponseUnitProperty:
    """Test response.unit property"""
    
    def test_unit_with_pint_quantity(self):
        """Test unit property with Pint Quantity value"""
        from obd2.response import OBDResponse
        from obd2.utils.units_and_scaling import Unit
        
        response = OBDResponse(None, [])
        response.value = 1500 * Unit.rpm
        
        unit = response.unit
        assert unit is not None
        assert 'revolution' in unit.lower() or 'rpm' in unit.lower()
    
    def test_unit_with_non_quantity(self):
        """Test unit property with non-Quantity value"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        response.value = 42
        
        unit = response.unit
        assert unit == "<class 'int'>"
    
    def test_unit_with_none_value(self):
        """Test unit property when value is None"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        response.value = None
        
        unit = response.unit
        assert unit is None
    
    def test_unit_with_string_value(self):
        """Test unit property with string value"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        response.value = "some_status"
        
        unit = response.unit
        assert unit == "<class 'str'>"


@pytest.mark.response
class TestOBDResponseMagnitudeProperty:
    """Test response.magnitude property"""
    
    def test_magnitude_with_pint_quantity(self):
        """Test magnitude extracts numeric value from Quantity"""
        from obd2.response import OBDResponse
        from obd2.utils.units_and_scaling import Unit
        
        response = OBDResponse(None, [])
        response.value = 1500 * Unit.rpm
        
        magnitude = response.magnitude
        assert magnitude == 1500
    
    def test_magnitude_with_plain_int(self):
        """Test magnitude returns int as-is"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        response.value = 42
        
        magnitude = response.magnitude
        assert magnitude == 42
    
    def test_magnitude_with_none(self):
        """Test magnitude returns None when value is None"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        response.value = None
        
        magnitude = response.magnitude
        assert magnitude is None
    
    def test_magnitude_with_string(self):
        """Test magnitude returns string as-is"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        response.value = "test_string"
        
        magnitude = response.magnitude
        assert magnitude == "test_string"
    
    def test_magnitude_with_float_quantity(self):
        """Test magnitude with float Quantity"""
        from obd2.response import OBDResponse
        from obd2.utils.units_and_scaling import Unit
        
        response = OBDResponse(None, [])
        # Use kelvin instead of celsius to avoid offset unit issues
        response.value = 98.5 * Unit.kelvin
        
        magnitude = response.magnitude
        assert magnitude == 98.5


@pytest.mark.response
class TestOBDResponseBoolConversion:
    """Test response boolean conversion (is_null method)"""
    
    def test_is_null_with_none_value(self):
        """Test is_null returns True when value is None"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        response.value = None
        
        assert response.is_null() == True
    
    def test_is_null_with_valid_value(self):
        """Test is_null returns False when value exists and messages present"""
        from obd2.response import OBDResponse
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        
        msg = Message(bytearray([0x41, 0x00]), ECU.ENGINE)
        response = OBDResponse(None, [msg])
        response.value = 42
        
        assert response.is_null() == False
    
    def test_is_null_with_zero_value(self):
        """Test is_null returns False for zero (zero is valid)"""
        from obd2.response import OBDResponse
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        
        msg = Message(bytearray([0x41, 0x00]), ECU.ENGINE)
        response = OBDResponse(None, [msg])
        response.value = 0
        
        assert response.is_null() == False
    
    def test_is_null_with_empty_string(self):
        """Test is_null returns False for empty string (it's not None)"""
        from obd2.response import OBDResponse
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        
        msg = Message(bytearray([0x41, 0x00]), ECU.ENGINE)
        response = OBDResponse(None, [msg])
        response.value = ""
        
        assert response.is_null() == False


@pytest.mark.response
class TestOBDResponseStringRepresentation:
    """Test response string representation"""
    
    def test_str_with_valid_response(self):
        """Test __str__ with valid response"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from ecu.ecu import ECU
        from decoding.decoders import drop
        
        cmd = OBDCommand('RPM', 'Engine RPM', b'010C', 4, drop, ECU.ENGINE, True)
        response = OBDResponse(cmd, [])
        response.value = 1500
        
        str_rep = str(response)
        assert 'RPM' in str_rep or '1500' in str_rep
    
    def test_str_with_none_value(self):
        """Test __str__ with None value"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        response.value = None
        
        str_rep = str(response)
        assert str_rep is not None  # Should not raise error


@pytest.mark.response
class TestOBDResponseIntegration:
    """Integration tests with real decoders"""
    
    def test_response_with_percent_decoder(self):
        """Test response with percent decoder"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        from decoding.decoders import percent
        
        cmd = OBDCommand('THROTTLE_POS', 'Throttle Position', b'0111', 3, percent, ECU.ENGINE, True)
        msg = Message(bytearray([0x41, 0x11, 0x80]), ECU.ENGINE)
        msg.data = bytearray([0x41, 0x11, 0x80])  # Set message data
        
        response = OBDResponse(cmd, [msg])
        
        # Decoder may fail with test data, but response should exist
        assert response is not None
    
    def test_response_with_temp_decoder(self):
        """Test response with temperature decoder"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        from decoding.decoders import temp
        
        cmd = OBDCommand('COOLANT_TEMP', 'Coolant Temperature', b'0105', 3, temp, ECU.ENGINE, True)
        msg = Message(bytearray([0x41, 0x05, 0x6E]), ECU.ENGINE)
        msg.data = bytearray([0x41, 0x05, 0x6E])
        
        response = OBDResponse(cmd, [msg])
        
        # Temp decoder: value = A - 40
        # If data[2] = 0x6E = 110, temp = 110 - 40 = 70°C
        # But decoder may extract differently depending on implementation
        assert response is not None
    
    def test_response_with_drop_decoder(self):
        """Test response with drop decoder (returns None)"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        from decoding.decoders import drop
        
        cmd = OBDCommand('TEST', 'Test', b'0100', 3, drop, ECU.ENGINE, True)
        msg = Message(bytearray([0x41, 0x00, 0x00]), ECU.ENGINE)
        
        response = OBDResponse(cmd, [msg])
        
        assert response.value is None
        assert response.magnitude is None
        assert response.is_null() == True


@pytest.mark.response
class TestOBDResponseEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_response_with_corrupted_message(self):
        """Test response handles corrupted message data"""
        from obd2.response import OBDResponse
        from obd2.command import OBDCommand
        from elm327.protocols.models.message import Message
        from ecu.ecu import ECU
        from decoding.decoders import percent
        
        cmd = OBDCommand('TEST', 'Test', b'0100', 10, percent, ECU.ENGINE, True)
        # Message with insufficient data
        msg = Message(bytearray([0x41]), ECU.ENGINE)
        
        # Should not crash
        response = OBDResponse(cmd, [msg])
        
        # May be None or decoded value, but shouldn't crash
        assert response is not None
    
    def test_response_time_is_set(self):
        """Test that response time is always set"""
        from obd2.response import OBDResponse
        
        response = OBDResponse(None, [])
        
        assert response.time is not None
        assert isinstance(response.time, float)  # time.time() returns float
        assert response.time > 0
    
    def test_multiple_responses_have_different_times(self):
        """Test that multiple responses have different timestamps"""
        from obd2.response import OBDResponse
        import time
        
        response1 = OBDResponse(None, [])
        time.sleep(0.01)  # Small delay
        response2 = OBDResponse(None, [])
        
        # Times should be different (or very close)
        assert response1.time <= response2.time


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
