"""
Test utility functions for both legacy and new codebase.

Tests hex tools, bit arrays, serial scanning, status enums, etc.
"""

import pytest


@pytest.mark.utils
class TestHexTools:
    """Test hex conversion utilities"""
    
    def test_bytes_to_int_new(self):
        """Test converting byte array to integer (new code)"""
        from obd2.utils.hex_tools import bytes_to_int
        assert bytes_to_int([0x1A, 0xF8]) == 6904
        assert bytes_to_int([0x00, 0x64]) == 100
        assert bytes_to_int([0xFF, 0xFF]) == 65535
        assert bytes_to_int([0x01]) == 1
        assert bytes_to_int([0x00, 0x00]) == 0
    
    def test_bytes_to_hex_new(self):
        """Test converting bytes to hex string (new code)"""
        from obd2.utils.hex_tools import bytes_to_hex
        assert bytes_to_hex([0x41, 0x0C]) == "410c"
        assert bytes_to_hex([0xFF, 0x00]) == "ff00"
        assert bytes_to_hex([0x00]) == "00"
    
    def test_twos_comp_positive_new(self):
        """Test two's complement for positive values (new code)"""
        from obd2.utils.hex_tools import twos_comp
        assert twos_comp(10, 8) == 10
        assert twos_comp(127, 8) == 127
    
    def test_twos_comp_negative_new(self):
        """Test two's complement for negative values (new code)"""
        from obd2.utils.hex_tools import twos_comp
        # 0xFF in 8 bits = -1
        assert twos_comp(0xFF, 8) == -1
        # 0x80 in 8 bits = -128
        assert twos_comp(0x80, 8) == -128
    
    def test_is_hex_valid_new(self):
        """Test hex string validation (new code)"""
        from obd2.utils.hex_tools import is_hex
        assert is_hex("410C") == True
        assert is_hex("ABCDEF") == True
        assert is_hex("123456") == True
        assert is_hex("0") == True
    
    def test_is_hex_invalid_new(self):
        """Test hex string validation with invalid strings (new code)"""
        from obd2.utils.hex_tools import is_hex
        assert is_hex("GHIJ") == False
        assert is_hex("NO DATA") == False


@pytest.mark.utils
class TestBitArray:
    """Test BitArray class functionality"""
    
    def test_bitarray_creation_new(self):
        """Test BitArray creation with new code"""
        from obd2.utils.bit_array import BitArray
        
        ba = BitArray(bytearray([0xBE, 0x3F]))
        assert len(ba) == 16
    
    def test_bitarray_getitem_new(self):
        """Test BitArray indexing with new code"""
        from obd2.utils.bit_array import BitArray
        
        # 0xBE = 10111110
        ba = BitArray(bytearray([0xBE]))
        
        assert ba[0] == True   # MSB
        assert ba[1] == False
        assert ba[2] == True
        assert ba[7] == False  # LSB
    
    def test_bitarray_slice_new(self):
        """Test BitArray slicing with new code"""
        from obd2.utils.bit_array import BitArray
        
        ba = BitArray(bytearray([0xFF, 0x00]))
        
        slice_result = ba[0:8]
        assert len(slice_result) == 8
        assert all(slice_result)  # All True for 0xFF
    
    def test_bitarray_value_new(self):
        """Test BitArray.value() method with new code"""
        from obd2.utils.bit_array import BitArray
        
        # 0b11110000 = 240
        ba = BitArray(bytearray([0xF0]))
        
        value = ba.value(0, 4)  # First 4 bits = 0b1111 = 15
        assert value == 15


@pytest.mark.utils
class TestOBDStatus:
    """Test OBDStatus enum/class"""
    
    def test_status_values_new(self):
        """Test OBDStatus enum in new code"""
        from obd2.utils.obd_status import OBDStatus
        
        assert OBDStatus.NOT_CONNECTED.value == "Not Connected"
        assert OBDStatus.ELM_CONNECTED.value == "ELM Connected"
        assert OBDStatus.OBD_CONNECTED.value == "OBD Connected"
        assert OBDStatus.CAR_CONNECTED.value == "Car Connected"


@pytest.mark.utils
class TestContiguous:
    """Test contiguous list checking"""
    
    def test_contiguous_valid_new(self):
        """Test contiguous check with valid list (new)"""
        from elm327.utils.contiguous import is_contiguous
        
        assert is_contiguous([1, 2, 3, 4], 1, 4) == True
        assert is_contiguous([5, 6, 7], 5, 7) == True
    
    def test_contiguous_invalid_new(self):
        """Test contiguous check with invalid list (new)"""
        from elm327.utils.contiguous import is_contiguous
        
        assert is_contiguous([1, 3, 4], 1, 4) == False  # Gap at 2
        assert is_contiguous([2, 3, 4], 1, 4) == False  # Wrong start
        assert is_contiguous([1, 2, 3], 1, 4) == False  # Wrong end
    
    def test_contiguous_empty_new(self):
        """Test contiguous check with empty list (new)"""
        from elm327.utils.contiguous import is_contiguous
        
        assert is_contiguous([], 1, 4) == False


@pytest.mark.utils
class TestSerialScanning:
    """Test serial port scanning (with mocks)"""
    
    def test_scan_serial_with_mock(self, monkeypatch):
        """Test scan_serial with mocked serial ports"""
        import glob
        from unittest.mock import Mock
        
        # Mock glob to return fake ports
        def mock_glob(pattern):
            if '/dev/tty' in pattern:
                return ['/dev/tty.usbserial-123', '/dev/tty.usbmodem-456']
            return []
        
        monkeypatch.setattr(glob, 'glob', mock_glob)
        
        # Mock serial.Serial to succeed
        mock_serial = Mock()
        mock_serial.close = Mock()
        
        def mock_serial_constructor(port):
            return mock_serial
        
        import serial
        monkeypatch.setattr(serial, 'Serial', mock_serial_constructor)
        
        # Test new scan_serial
        from serial_utils.scan_serial import scan_serial as new_scan_serial
        result_new = new_scan_serial()
        assert isinstance(result_new, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
