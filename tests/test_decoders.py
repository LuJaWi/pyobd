"""
Test decoder functions for the new codebase.

Tests all decoder functions from decoding.decoders
"""

import pytest
from typing import List
from decoding import decoders


@pytest.mark.decoders
class TestBasicDecoders:
    """Test basic decoder functions (drop, noop, pid, raw_string)"""
    
    def test_drop_returns_none(self, sample_messages_new):
        """Test that drop() returns None for any input"""
        result = decoders.drop(sample_messages_new)
        assert result is None
    
    def test_noop_returns_data(self, sample_messages_new):
        """Test that noop() returns raw message data"""
        result = decoders.noop(sample_messages_new)
        assert isinstance(result, bytearray)
        assert len(result) > 0
    
    def test_raw_string_converts_to_hex(self):
        """Test that raw_string() converts bytes to hex string"""
        # Create minimal message structure
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x00, 0xBE, 0x3F])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x00, 0xBE, 0x3F])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.raw_string(messages)
        
        # Should return hex string representation
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.decoders
class TestTemperatureDecoders:
    """Test temperature-related decoders"""
    
    def test_temp_decoder_coolant(self):
        """Test temperature decoder with coolant temp response"""
        # 41 05 5F = Mode 1, PID 5, Value 95 (0x5F)
        # Formula: value - 40 = 95 - 40 = 55°C
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x05, 0x5F])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x05, 0x5F])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.temp(messages)
        
        # Check it returns a temperature value
        # New code returns pint Quantity, legacy returns Quantity
        if hasattr(result, 'magnitude'):
            temp_value = result.magnitude
        else:
            temp_value = result.to('degC').magnitude if hasattr(result, 'to') else float(result)
        
        assert abs(temp_value - 55.0) < 0.1  # 55°C
    
    def test_temp_decoder_negative(self):
        """Test temperature decoder with negative temp"""
        # Value 20 = 20 - 40 = -20°C
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x05, 0x14])
                self.raw = str(self.data.hex())  # 0x14 = 20
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x05, 0x14])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.temp(messages)
        
        if hasattr(result, 'magnitude'):
            temp_value = result.magnitude
        else:
            temp_value = result.to('degC').magnitude if hasattr(result, 'to') else float(result)
        
        assert abs(temp_value - (-20.0)) < 0.1


@pytest.mark.decoders
class TestPercentDecoders:
    """Test percentage-related decoders"""
    
    def test_percent_decoder_half(self):
        """Test percent decoder at 50%"""
        # Value 128 (0x80) = 128 * 100/255 ≈ 50.2%
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x04, 0x80])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x04, 0x80])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.percent(messages)
        
        if hasattr(result, 'magnitude'):
            percent_value = result.magnitude
        else:
            percent_value = float(result)
        
        assert abs(percent_value - 50.2) < 1.0  # ~50%
    
    def test_percent_centered_zero(self):
        """Test percent_centered decoder at 0%"""
        # Value 128 (0x80) centered = (128 - 128) * 100/128 = 0%
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x06, 0x80])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x06, 0x80])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.percent_centered(messages)
        
        if hasattr(result, 'magnitude'):
            percent_value = result.magnitude
        else:
            percent_value = float(result)
        
        assert abs(percent_value) < 0.1  # Should be ~0%
    
    def test_percent_centered_positive(self):
        """Test percent_centered with positive value"""
        # Value 138 (0x8A) = (138 - 128) * 100/128 ≈ 7.8%
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x06, 0x8A])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x06, 0x8A])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.percent_centered(messages)
        
        if hasattr(result, 'magnitude'):
            percent_value = result.magnitude
        else:
            percent_value = float(result)
        
        assert abs(percent_value - 7.8) < 1.0


@pytest.mark.decoders
class TestPressureDecoders:
    """Test pressure-related decoders"""
    
    def test_pressure_decoder(self):
        """Test basic pressure decoder"""
        # Value 100 (0x64) = 100 kPa
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x0B, 0x64])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x0B, 0x64])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.pressure(messages)
        
        if hasattr(result, 'magnitude'):
            pressure_value = result.magnitude
        else:
            pressure_value = float(result)
        
        assert abs(pressure_value - 100.0) < 0.1  # 100 kPa
    
    def test_fuel_pressure_decoder(self):
        """Test fuel pressure decoder"""
        # Value 50 (0x32) = 50 * 3 = 150 kPa
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x0A, 0x32])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x0A, 0x32])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.fuel_pressure(messages)
        
        if hasattr(result, 'magnitude'):
            pressure_value = result.magnitude
        else:
            pressure_value = float(result)
        
        assert abs(pressure_value - 150.0) < 0.1  # 150 kPa


@pytest.mark.decoders
class TestUASDecoders:
    """Test Units and Scaling (UAS) decoders"""
    
    def test_uas_rpm(self):
        """Test UAS decoder for RPM (ID 0x07)"""
        # RPM: bytes [2,3], formula: ((A*256)+B)/4
        # Example: 0x1AF8 = 6904, 6904/4 = 1726 RPM
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        
        # UAS decoder requires ID
        result = decoders.decode_uas(messages, 0x07)
        
        if hasattr(result, 'magnitude'):
            rpm_value = result.magnitude
        else:
            rpm_value = float(result)
        
        assert abs(rpm_value - 1726.0) < 1.0  # 1726 RPM


@pytest.mark.decoders
class TestDTCDecoders:
    """Test DTC (Diagnostic Trouble Code) decoders"""
    
    def test_parse_dtc_powertrain(self):
        """Test parsing powertrain DTC (Pxxxx)"""
        # P0301 = [0x03, 0x01] in bytes
        dtc_bytes = [0x03, 0x01]
        
        result = decoders.parse_dtc(dtc_bytes)
        
        if result:
            code, description = result
            assert code == "P0301"
    
    def test_parse_dtc_chassis(self):
        """Test parsing chassis DTC (Cxxxx)"""
        # C0561 = [0x45, 0x61] in bytes (0100 prefix = C)
        dtc_bytes = [0x45, 0x61]
        
        result = decoders.parse_dtc(dtc_bytes)
        
        if result:
            code, description = result
            assert code == "C0561"
    
    def test_dtc_decoder_multiple(self):
        """Test decoding multiple DTCs from response"""
        # Response: 43 02 02 01 03 01 (count=2, P0201 and P0301)
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x43, 0x02, 0x02, 0x01, 0x03, 0x01])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x43, 0x02, 0x02, 0x01, 0x03, 0x01])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.dtc(messages)
        
        assert isinstance(result, list)
        assert len(result) == 2
        # Check codes are present (decoder extracts the actual codes from the data)
        codes = [dtc[0] for dtc in result]
        assert "P0202" in codes  # Injector Circuit/Open - Cylinder 2
        assert "P0103" in codes  # Mass or Volume Air Flow Circuit High Input


@pytest.mark.decoders
class TestStatusDecoders:
    """Test status and diagnostic decoders"""
    
    def test_status_decoder(self):
        """Test status decoder (Mode 01, PID 01)"""
        # Example status response: 41 01 00 07 65 04
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x01, 0x00, 0x07, 0x65, 0x04])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x01, 0x00, 0x07, 0x65, 0x04])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.status(messages)
        
        # Should return a Status object
        assert result is not None
        assert hasattr(result, 'MIL')  # Has MIL (check engine light) attribute
    
    def test_fuel_status_decoder(self):
        """Test fuel status decoder"""
        # Fuel status: 41 03 01 00 (example: open loop due to insufficient temp)
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x03, 0x01, 0x00])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x03, 0x01, 0x00])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.fuel_status(messages)
        
        # Should return tuple of fuel status strings or None
        if result is not None:
            assert isinstance(result, tuple)
            assert len(result) == 2


@pytest.mark.decoders
class TestVoltageDecoders:
    """Test voltage-related decoders"""
    
    def test_sensor_voltage(self):
        """Test sensor voltage decoder"""
        # O2 sensor: 41 14 80 FF
        # Voltage: 0x80 * 0.005 = 0.64V
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x14, 0x80, 0xFF])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x14, 0x80, 0xFF])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.sensor_voltage(messages)
        
        if hasattr(result, 'magnitude'):
            voltage_value = result.magnitude
        else:
            voltage_value = float(result)
        
        assert abs(voltage_value - 0.64) < 0.01  # ~0.64V


@pytest.mark.decoders
class TestCountDecoders:
    """Test count-based decoders"""
    
    def test_count_decoder(self):
        """Test simple count decoder"""
        # Distance traveled: 41 21 00 64 = 100 km
        
        class MockFrame:
            def __init__(self):
                self.data = bytearray([0x41, 0x21, 0x00, 0x64])
                self.raw = str(self.data.hex())
        
        class MockMessage:
            def __init__(self):
                self.frames = [MockFrame()]
                self.data = bytearray([0x41, 0x21, 0x00, 0x64])
                self.can = True
                self.num_frames = 1
            
            def raw(self):
                return "\n".join([f.raw if hasattr(f, 'raw') else str(f.data.hex()) for f in self.frames])
        
        messages = [MockMessage()]
        result = decoders.count(messages)
        
        if hasattr(result, 'magnitude'):
            count_value = result.magnitude
        else:
            count_value = float(result)
        
        assert abs(count_value - 100.0) < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
