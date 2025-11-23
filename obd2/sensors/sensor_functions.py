"""
Sensor decoder functions for OBD-II diagnostic data.

These functions convert hex string responses from OBD-II sensors
into human-readable values with appropriate units. Used by the
obd2.sensors.sensors module to define sensor configurations.

NOTE: This module works with hex string inputs (e.g., "FF"). 
The obd/ directory contains an alternative implementation that works
with byte arrays and includes unit handling via Pint.
"""

from typing import List


def hex_to_int(hex_str: str) -> int:
    """
    Convert a hex string to an integer.
    
    Args:
        hex_str: Hexadecimal string (without '0x' prefix)
        
    Returns:
        Integer value of the hex string
        
    Example:
        >>> hex_to_int("FF")
        255
    """
    return int(hex_str, 16)


def maf(code: str) -> float:
    """
    Mass Air Flow sensor reading.
    
    Converts hex code to grams/second using MAF sensor formula.
    
    Args:
        code: Hex string from MAF sensor
        
    Returns:
        Mass air flow in grams/second
        
    Range:
        0 to ~337 g/s
    """
    value = hex_to_int(code)
    return value * 0.00132276


def throttle_pos(code: str) -> float:
    """
    Throttle position as percentage.
    
    Args:
        code: Hex string from throttle position sensor
        
    Returns:
        Throttle position as percentage (0-100%)
    """
    value = hex_to_int(code)
    return value * 100.0 / 255.0


def intake_m_pres(code: str) -> float:
    """
    Intake manifold absolute pressure in kPa.
    
    Args:
        code: Hex string from MAP sensor
        
    Returns:
        Pressure in kilopascals (kPa)
        
    Range:
        0 to 255 kPa
    """
    value = hex_to_int(code)
    return value / 0.14504


def rpm(code: str) -> float:
    """
    Engine RPM (revolutions per minute).
    
    Args:
        code: Hex string from RPM sensor
        
    Returns:
        Engine speed in RPM
        
    Range:
        0 to 16,383.75 RPM
    """
    value = hex_to_int(code)
    return value / 4


def speed(code: str) -> float:
    """
    Vehicle speed in miles per hour.
    
    Converts km/h reading to mph.
    
    Args:
        code: Hex string from speed sensor
        
    Returns:
        Vehicle speed in mph
        
    Range:
        0 to 255 mph
    """
    value = hex_to_int(code)
    return value / 1.609


def percent_scale(code: str) -> float:
    """
    Generic percentage scale (0-100%).
    
    Scales a 0-255 value to 0-100%.
    
    Args:
        code: Hex string value (0-FF)
        
    Returns:
        Percentage (0-100%)
    """
    value = hex_to_int(code)
    return value * 100.0 / 255.0


def timing_advance(code: str) -> float:
    """
    Ignition timing advance in degrees before TDC.
    
    Args:
        code: Hex string from timing sensor
        
    Returns:
        Timing advance in degrees
        
    Range:
        -64 to 63.5 degrees
    """
    value = hex_to_int(code)
    return (value - 128) / 2.0


def sec_to_min(code: str) -> float:
    """
    Convert seconds to minutes.
    
    Args:
        code: Hex string representing seconds
        
    Returns:
        Time in minutes
    """
    value = hex_to_int(code)
    return value / 60


def temp(code: str) -> int:
    """
    Temperature in Celsius.
    
    Converts OBD-II temperature encoding to Celsius.
    
    Args:
        code: Hex string from temperature sensor
        
    Returns:
        Temperature in °C
        
    Range:
        -40 to 215 °C
    """
    value = hex_to_int(code)
    return value - 40


def cpass(code: str) -> str:
    """
    Pass-through function (no conversion).
    
    FIXME: This function needs proper implementation.
    
    Args:
        code: Raw hex string
        
    Returns:
        Unmodified code
    """
    # TODO: Implement proper conversion
    return code


def fuel_trim_percent(code: str) -> float:
    """
    Fuel trim percentage.
    
    Converts fuel trim value to percentage adjustment.
    
    Args:
        code: Hex string from fuel trim sensor
        
    Returns:
        Fuel trim as percentage
        
    Range:
        -100 to 99.22% (negative = lean, positive = rich)
    """
    value = hex_to_int(code)
    return (value - 128.0) * 100.0 / 128


def dtc_decrypt(code: str) -> List[int]:
    """
    Decrypt diagnostic trouble code status byte.
    
    Decodes the OBD-II PID 01 response which contains:
    - MIL (Check Engine Light) status
    - Number of DTCs stored
    - Readiness test status bits
    
    Args:
        code: 8-character hex string (4 bytes) from PID 01
        
    Returns:
        List containing:
        [0]: Number of DTCs (0-127)
        [1]: MIL status (0=off, 1=on)
        [2-4]: Readiness test status (bytes B bits 0-2)
        [5-11]: Readiness test status (bytes C&D bits 0-6)
        [12]: EGR system status (byte D bit 7)
        
    Note:
        This is a legacy implementation. See obd/decoders.py status()
        for the modern implementation with better structure.
    """
    # First byte (A): MIL and DTC count
    num = hex_to_int(code[:2])
    res = []

    # Bit 7: MIL (Malfunction Indicator Lamp) status
    mil = 1 if num & 0x80 else 0
    
    # Bits 0-6: Number of DTCs stored
    num = num & 0x7f
    
    res.append(num)  # DTC count
    res.append(mil)  # MIL status
    
    # Second byte (B): Readiness test status
    numB = hex_to_int(code[2:4])
    
    # Extract 3 test status values from byte B
    for i in range(0, 3):
        # Combine bit i and bit (3+i) to form 2-bit status
        status = ((numB >> i) & 0x01) + ((numB >> (3 + i)) & 0x02)
        res.append(status)
    
    # Third and fourth bytes (C&D): More readiness test status
    numC = hex_to_int(code[4:6])
    numD = hex_to_int(code[6:8])
    
    # Extract 7 test status values from bytes C and D
    for i in range(0, 7):
        # Combine bit i from C and bit i from D to form 2-bit status
        status = ((numC >> i) & 0x01) + (((numD >> i) & 0x01) << 1)
        res.append(status)
    
    # Bit 7 of byte D: EGR system status (handled separately)
    res.append((numD >> 7) & 0x01)
    
    return res


def hex_to_bitstring(hex_str: str) -> str:
    """
    Convert hex string to binary string representation.
    
    Each hex character is converted to its 4-bit binary representation.
    
    Args:
        hex_str: String of hex characters
        
    Returns:
        Binary string (e.g., "1010" for "A")
        
    Example:
        >>> hex_to_bitstring("A3")
        "10100011"
        
    Note:
        This is a legacy implementation. Consider using Python's
        built-in bin() or format() functions instead:
        format(int(hex_str, 16), f'0{len(hex_str)*4}b')
    """
    bitstring = ""
    for char in hex_str:
        # Only process string characters (type safety)
        if isinstance(char, str):
            value = int(char, 16)
            # Convert to 4-bit binary (MSB to LSB)
            bitstring += '1' if value & 8 else '0'
            bitstring += '1' if value & 4 else '0'
            bitstring += '1' if value & 2 else '0'
            bitstring += '1' if value & 1 else '0'
    return bitstring