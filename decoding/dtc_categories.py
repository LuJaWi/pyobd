"""General DTC code categories for classification."""

from enum import Enum

class DTCCategory(Enum):
    """DTC code categories for classification."""
    
    P00XX = "Fuel and Air Metering and Auxiliary Emission Controls"
    P01XX = "Fuel and Air Metering"
    P02XX = "Fuel and Air Metering"
    P03XX = "Ignition System or Misfire"
    P04XX = "Auxiliary Emission Controls"
    P05XX = "Vehicle Speed, Idle Control, and Auxiliary Inputs"
    P06XX = "Computer and Auxiliary Outputs"
    P07XX = "Transmission"
    P08XX = "Transmission"
    P09XX = "Transmission"
    P0AXX = "Hybrid Propulsion"
    P10XX = "Manufacturer Controlled Fuel and Air Metering and Auxiliary Emission Controls"
    P11XX = "Manufacturer Controlled Fuel and Air Metering"
    P12XX = "Fuel and Air Metering"
    P13XX = "Ignition System or Misfire"
    P14XX = "Auxiliary Emission Controls"
    P15XX = "Vehicle Speed, Idle Control, and Auxiliary Inputs"
    P16XX = "Computer and Auxiliary Outputs"
    P17XX = "Transmission"
    P18XX = "Transmission"
    P19XX = "Transmission"