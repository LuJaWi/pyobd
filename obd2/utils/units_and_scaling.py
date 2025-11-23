# -*- coding: utf-8 -*-

########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2009 Peter J. Creath                                       #
# Copyright 2016 Brendan Whitfield (brendan-w.com)                     #
#                                                                      #
########################################################################
#                                                                      #
# UnitsAndScaling.py                                                   #
#                                                                      #
# This file is part of python-OBD (a derivative of pyOBD)              #
#                                                                      #
# python-OBD is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 2 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# python-OBD is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with python-OBD.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                      #
########################################################################

import pint
from dataclasses import dataclass

from typing import Any

@dataclass
class UAS:
    """
    Class for representing a Unit and Scale conversion
    Used in the decoding of Mode 06 monitor responses
    """

    signed: bool
    scale: float
    unit: Any
    offset: float = 0.0
    description: str = ""

    def __call__(self, _bytes):
        """ Convert raw bytes to a scaled, unit-bearing quantity """

        value = int.from_bytes(_bytes, "big", signed=self.signed)

        value *= self.scale
        value += self.offset
        return Unit.Quantity(value, self.unit)

# export the unit registry
Unit = pint.UnitRegistry()
Unit.define("ratio = []")
Unit.define("percent = 1e-2 ratio = %")
Unit.define("gps = gram / second = GPS = grams_per_second")
Unit.define("lph = liter / hour = LPH = liters_per_hour")
Unit.define("ppm = count / 1000000 = PPM = parts_per_million")

# Standardized UAS IDs from SAE J1979 (Mode 06 test results)
# Used to convert raw bytes from monitor tests into properly scaled values
UAS_IDS = {
    # ===== UNSIGNED CONVERSIONS (0x01-0x41) =====
    
    # Count/Generic measurements
    0x01: UAS(False, 1, Unit.count),                    # Raw count (no scaling)
    0x02: UAS(False, 0.1, Unit.count),                  # Count × 0.1
    0x03: UAS(False, 0.01, Unit.count),                 # Count × 0.01
    0x04: UAS(False, 0.001, Unit.count),                # Count × 0.001
    0x05: UAS(False, 0.0000305, Unit.count),            # Count × 0.0000305
    0x06: UAS(False, 0.000305, Unit.count),             # Count × 0.000305
    0x24: UAS(False, 1, Unit.count),                    # Raw count (duplicate)
    0x2B: UAS(False, 1, Unit.count),                    # Raw count (duplicate)
    
    # Rotational speed
    0x07: UAS(False, 0.25, Unit.rpm),                   # Engine/component RPM
    
    # Vehicle speed
    0x08: UAS(False, 0.01, Unit.kph),                   # Speed (0.01 km/h resolution)
    0x09: UAS(False, 1, Unit.kph),                      # Speed (1 km/h resolution)
    
    # Voltage measurements
    0x0A: UAS(False, 0.122, Unit.millivolt),            # Sensor voltage (122 µV resolution)
    0x0B: UAS(False, 0.001, Unit.volt),                 # Voltage (1 mV resolution)
    0x0C: UAS(False, 0.01, Unit.volt),                  # Voltage (10 mV resolution)
    
    # Current measurements
    0x0D: UAS(False, 0.00390625, Unit.milliampere),     # Current (1/256 mA resolution)
    0x0E: UAS(False, 0.001, Unit.ampere),               # Current (1 mA resolution)
    0x0F: UAS(False, 0.01, Unit.ampere),                # Current (10 mA resolution)
    0x3D: UAS(False, 0.01, Unit.milliampere),           # Current (0.01 mA resolution)
    0x41: UAS(False, 0.01, Unit.microampere),           # Current (0.01 µA resolution)
    
    # Time measurements
    0x10: UAS(False, 1, Unit.millisecond),              # Time (1 ms resolution)
    0x11: UAS(False, 100, Unit.millisecond),            # Time (100 ms resolution)
    0x12: UAS(False, 1, Unit.second),                   # Time (1 s resolution)
    0x34: UAS(False, 1, Unit.minute),                   # Time (1 min resolution)
    0x35: UAS(False, 10, Unit.millisecond),             # Time (10 ms resolution)
    0x3C: UAS(False, 0.1, Unit.microsecond),            # Time (0.1 µs resolution)
    
    # Resistance measurements
    0x13: UAS(False, 1, Unit.milliohm),                 # Resistance (1 mΩ resolution)
    0x14: UAS(False, 1, Unit.ohm),                      # Resistance (1 Ω resolution)
    0x15: UAS(False, 1, Unit.kiloohm),                  # Resistance (1 kΩ resolution)
    
    # Temperature measurements
    0x16: UAS(False, 0.1, Unit.celsius, offset=-40.0),  # Temperature (-40 to 215°C)
    
    # Pressure measurements
    0x17: UAS(False, 0.01, Unit.kilopascal),            # Pressure (0.01 kPa resolution)
    0x18: UAS(False, 0.0117, Unit.kilopascal),          # Pressure (0.0117 kPa resolution)
    0x19: UAS(False, 0.079, Unit.kilopascal),           # Pressure (0.079 kPa resolution)
    0x1A: UAS(False, 1, Unit.kilopascal),               # Pressure (1 kPa resolution)
    0x1B: UAS(False, 10, Unit.kilopascal),              # Pressure (10 kPa resolution)
    
    # Angle measurements
    0x1C: UAS(False, 0.01, Unit.degree),                # Angle (0.01° resolution)
    0x1D: UAS(False, 0.5, Unit.degree),                 # Angle (0.5° resolution)
    
    # Ratio/efficiency measurements
    0x1E: UAS(False, 0.0000305, Unit.ratio),            # Ratio (very fine resolution)
    0x1F: UAS(False, 0.05, Unit.ratio),                 # Ratio (0.05 resolution)
    0x20: UAS(False, 0.00390625, Unit.ratio),           # Ratio (1/256 resolution)
    0x33: UAS(False, 0.00024414, Unit.ratio),           # Ratio (1/4096 resolution)
    
    # Frequency measurements
    0x21: UAS(False, 1, Unit.millihertz),               # Frequency (1 mHz resolution)
    0x22: UAS(False, 1, Unit.hertz),                    # Frequency (1 Hz resolution)
    0x23: UAS(False, 1, Unit.kilohertz),                # Frequency (1 kHz resolution)
    
    # Distance measurements
    0x25: UAS(False, 1, Unit.kilometer),                # Distance (1 km resolution)
    0x32: UAS(False, 0.0000305, Unit.inch),             # Distance (very fine resolution)
    
    # Rate of change (voltage over time)
    0x26: UAS(False, 0.1, Unit.millivolt / Unit.millisecond),  # Voltage slew rate
    
    # Mass flow measurements
    0x27: UAS(False, 0.01, Unit.grams_per_second),      # Mass flow (0.01 g/s)
    0x28: UAS(False, 1, Unit.grams_per_second),         # Mass flow (1 g/s)
    0x2A: UAS(False, 0.001, Unit.kilogram / Unit.hour), # Mass flow (kg/h)
    
    # Pressure rate of change
    0x29: UAS(False, 0.25, Unit.pascal / Unit.second),  # Pressure change rate
    
    # Fuel mass measurements
    0x2C: UAS(False, 0.01, Unit.gram),                  # Fuel mass per cylinder
    0x2D: UAS(False, 0.01, Unit.milligram),             # Fuel mass per stroke
    0x36: UAS(False, 0.01, Unit.gram),                  # Mass (0.01 g resolution)
    0x37: UAS(False, 0.1, Unit.gram),                   # Mass (0.1 g resolution)
    0x38: UAS(False, 1, Unit.gram),                     # Mass (1 g resolution)
    0x3A: UAS(False, 0.001, Unit.gram),                 # Mass (0.001 g resolution)
    0x3B: UAS(False, 0.0001, Unit.gram),                # Mass (0.0001 g resolution)
    
    # Boolean/status indicator
    0x2E: lambda _bytes: any([bool(x) for x in _bytes]),  # Any byte non-zero = True
    
    # Percentage measurements
    0x2F: UAS(False, 0.01, Unit.percent),               # Percentage (0.01% resolution)
    0x30: UAS(False, 0.001526, Unit.percent),           # Percentage (0.001526% resolution)
    0x39: UAS(False, 0.01, Unit.percent, offset=-327.68),  # Percentage with offset
    
    # Volume measurements
    0x31: UAS(False, 0.001, Unit.liter),                # Volume (0.001 L resolution)
    0x3F: UAS(False, 0.01, Unit.liter),                 # Volume (0.01 L resolution)
    
    # Area measurement
    0x3E: UAS(False, 0.00006103516, Unit.millimeter ** 2),  # Area (mm²)
    
    # Concentration measurement
    0x40: UAS(False, 1, Unit.ppm),                      # Parts per million
    
    
    # ===== SIGNED CONVERSIONS (0x81-0xFE) =====
    # For measurements that can be negative (e.g., below zero temperature)
    
    # Count/Generic measurements (signed)
    0x81: UAS(True, 1, Unit.count),                     # Signed raw count
    0x82: UAS(True, 0.1, Unit.count),                   # Signed count × 0.1
    0x83: UAS(True, 0.01, Unit.count),                  # Signed count × 0.01
    0x84: UAS(True, 0.001, Unit.count),                 # Signed count × 0.001
    0x85: UAS(True, 0.0000305, Unit.count),             # Signed count × 0.0000305
    0x86: UAS(True, 0.000305, Unit.count),              # Signed count × 0.000305
    
    # Concentration measurement (signed)
    0x87: UAS(True, 1, Unit.ppm),                       # Signed PPM
    
    # Voltage measurements (signed)
    0x8A: UAS(True, 0.122, Unit.millivolt),             # Signed sensor voltage
    0x8B: UAS(True, 0.001, Unit.volt),                  # Signed voltage (1 mV)
    0x8C: UAS(True, 0.01, Unit.volt),                   # Signed voltage (10 mV)
    
    # Current measurements (signed)
    0x8D: UAS(True, 0.00390625, Unit.milliampere),      # Signed current (1/256 mA)
    0x8E: UAS(True, 0.001, Unit.ampere),                # Signed current (1 mA)
    
    # Time measurement (signed)
    0x90: UAS(True, 1, Unit.millisecond),               # Signed time
    
    # Temperature measurement (signed)
    0x96: UAS(True, 0.1, Unit.celsius),                 # Signed temperature (no offset)
    
    # Pressure measurement (signed)
    0x99: UAS(True, 0.1, Unit.kilopascal),              # Signed pressure
    0xFC: UAS(True, 0.01, Unit.kilopascal),             # Signed pressure (0.01 kPa)
    0xFD: UAS(True, 0.001, Unit.kilopascal),            # Signed pressure (0.001 kPa)
    0xFE: UAS(True, 0.25, Unit.pascal),                 # Signed pressure (0.25 Pa)
    
    # Angle measurements (signed)
    0x9C: UAS(True, 0.01, Unit.degree),                 # Signed angle (0.01°)
    0x9D: UAS(True, 0.5, Unit.degree),                  # Signed angle (0.5°)
    
    # Mass flow measurements (signed)
    0xA8: UAS(True, 1, Unit.grams_per_second),          # Signed mass flow
    
    # Pressure rate of change (signed)
    0xA9: UAS(True, 0.25, Unit.pascal / Unit.second),   # Signed pressure change
    
    # Fuel mass measurements (signed)
    0xAD: UAS(True, 0.01, Unit.milligram),              # Signed fuel mass per stroke
    0xAE: UAS(True, 0.1, Unit.milligram),               # Signed fuel mass per stroke
    
    # Percentage measurements (signed)
    0xAF: UAS(True, 0.01, Unit.percent),                # Signed percentage
    0xB0: UAS(True, 0.003052, Unit.percent),            # Signed percentage (fine)
    
    # Voltage slew rate (signed)
    0xB1: UAS(True, 2, Unit.millivolt / Unit.second),   # Signed voltage rate
}
