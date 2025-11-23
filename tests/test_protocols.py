"""
Test protocol parsing for both legacy and new codebase.

Tests CAN, legacy, and unknown protocol message parsing.
"""

import pytest


@pytest.mark.protocols
class TestProtocolClasses:
    """Test protocol class structure"""
    

    def test_frame_class_exists_new(self):
        """Test Frame class exists (new)"""
        from elm327.protocols.models.frame import Frame
        
        frame = Frame("41 0C 1A F8")
        assert frame is not None
        assert hasattr(frame, 'raw')
        assert hasattr(frame, 'data')
    

    def test_message_class_exists_new(self):
        """Test Message class exists (new)"""
        from elm327.protocols.models.message import Message
        from elm327.protocols.models.frame import Frame
        
        frame = Frame("41 0C 1A F8")
        message = Message([frame])
        assert message is not None
        assert hasattr(message, 'frames')
        assert hasattr(message, 'data')


@pytest.mark.protocols
class TestECUConstants:
    """Test ECU constant definitions"""
    

    def test_ecu_constants_new(self):
        """Test ECU constants exist (new)"""
        from ecu.ecu import ECU
        
        assert hasattr(ECU, 'ENGINE')
        assert hasattr(ECU, 'TRANSMISSION')
        assert hasattr(ECU, 'UNKNOWN')


@pytest.mark.protocols
class TestProtocolDetection:
    """Test protocol auto-detection"""
    

    def test_protocol_classes_exist_new(self):
        """Test all protocol classes exist (new)"""
        from elm327.protocols import protocol_can
        from elm327.protocols import protocol_legacy
        from elm327.protocols import protocol_unknown
        
        assert hasattr(protocol_can, 'CANProtocol')
        assert hasattr(protocol_legacy, 'LegacyProtocol')
        assert hasattr(protocol_unknown, 'UnknownProtocol')


@pytest.mark.protocols
class TestCANProtocol:
    """Test CAN protocol implementations"""
    

    def test_can_protocol_variants_new(self):
        """Test CAN protocol variants exist (new)"""
        from elm327.protocols import protocol_can
        
        assert hasattr(protocol_can, 'ISO_15765_4_11bit_500k')
        assert hasattr(protocol_can, 'ISO_15765_4_29bit_500k')
        assert hasattr(protocol_can, 'ISO_15765_4_11bit_250k')
        assert hasattr(protocol_can, 'ISO_15765_4_29bit_250k')
        assert hasattr(protocol_can, 'SAE_J1939')


@pytest.mark.protocols
class TestLegacyProtocol:
    """Test legacy protocol implementations"""
    

    def test_legacy_protocol_variants_new(self):
        """Test legacy protocol variants exist (new)"""
        from elm327.protocols import protocol_legacy
        
        assert hasattr(protocol_legacy, 'SAE_J1850_PWM')
        assert hasattr(protocol_legacy, 'SAE_J1850_VPW')
        assert hasattr(protocol_legacy, 'ISO_9141_2')
        assert hasattr(protocol_legacy, 'ISO_14230_4_5baud')
        assert hasattr(protocol_legacy, 'ISO_14230_4_fast')


@pytest.mark.protocols
class TestMessageParsing:
    """Test message parsing functionality"""
    

    def test_message_hex_method_new(self):
        """Test Message.hex() method (new)"""
        from elm327.protocols.models.message import Message
        from elm327.protocols.models.frame import Frame
        
        frame = Frame("41 0C 1A F8")
        frame.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
        
        message = Message([frame])
        message.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
        
        hex_str = message.hex()
        assert isinstance(hex_str, bytes)
        assert b'410c1af8' in hex_str.lower()
    

    def test_message_raw_method_new(self):
        """Test Message.raw() method (new)"""
        from elm327.protocols.models.message import Message
        from elm327.protocols.models.frame import Frame
        
        frame = Frame("41 0C 1A F8")
        frame.raw = "41 0C 1A F8"
        
        message = Message([frame])
        raw_str = message.raw()
        
        assert isinstance(raw_str, str)
        assert "41" in raw_str


@pytest.mark.protocols
class TestFrameData:
    """Test frame data handling"""
    

    def test_frame_data_assignment_new(self):
        """Test Frame data assignment (new)"""
        from elm327.protocols.models.frame import Frame
        
        frame = Frame("41 0C 1A F8")
        frame.data = bytearray([0x41, 0x0C])
        
        assert len(frame.data) == 2
        assert frame.data[0] == 0x41
        assert frame.data[1] == 0x0C


@pytest.mark.protocols  
class TestMultiFrameMessages:
    """Test multi-frame message handling"""
    

    def test_multi_frame_message_new(self):
        """Test Message with multiple frames (new)"""
        from elm327.protocols.models.message import Message
        from elm327.protocols.models.frame import Frame
        
        frame1 = Frame("10 14 49 02 01 31 47 34")
        frame1.data = bytearray([0x10, 0x14, 0x49, 0x02, 0x01, 0x31, 0x47, 0x34])
        
        frame2 = Frame("21 47 43 35 34 38 34 37")
        frame2.data = bytearray([0x21, 0x47, 0x43, 0x35, 0x34, 0x38, 0x34, 0x37])
        
        message = Message([frame1, frame2])
        
        assert len(message.frames) == 2
        assert message.frames[0] == frame1
        assert message.frames[1] == frame2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
