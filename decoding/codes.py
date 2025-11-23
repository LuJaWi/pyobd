
from enum import Enum
from typing import NamedTuple, Optional


class TestInfo(NamedTuple):
    """Information about an OBD-II Monitor Test ID."""
    name: str
    description: str


TEST_IDS = {
    # <TID>: TestInfo(name, description)
    # 0x0 is reserved
    0x01: TestInfo("RTL_THRESHOLD_VOLTAGE", "Rich to lean sensor threshold voltage"),
    0x02: TestInfo("LTR_THRESHOLD_VOLTAGE", "Lean to rich sensor threshold voltage"),
    0x03: TestInfo("LOW_VOLTAGE_SWITCH_TIME", "Low sensor voltage for switch time calculation"),
    0x04: TestInfo("HIGH_VOLTAGE_SWITCH_TIME", "High sensor voltage for switch time calculation"),
    0x05: TestInfo("RTL_SWITCH_TIME", "Rich to lean sensor switch time"),
    0x06: TestInfo("LTR_SWITCH_TIME", "Lean to rich sensor switch time"),
    0x07: TestInfo("MIN_VOLTAGE", "Minimum sensor voltage for test cycle"),
    0x08: TestInfo("MAX_VOLTAGE", "Maximum sensor voltage for test cycle"),
    0x09: TestInfo("TRANSITION_TIME", "Time between sensor transitions"),
    0x0A: TestInfo("SENSOR_PERIOD", "Sensor period"),
    0x0B: TestInfo("MISFIRE_AVERAGE", "Average misfire counts for last ten driving cycles"),
    0x0C: TestInfo("MISFIRE_COUNT", "Misfire counts for last/current driving cycles"),
}


# Base tests (always present for all vehicle types)
BASE_TESTS = [
    "MISFIRE_MONITORING",
    "FUEL_SYSTEM_MONITORING",
    "COMPONENT_MONITORING",
]

# Spark ignition engine tests (bit position indexed, None = reserved/unused)
SPARK_TESTS = [
    "CATALYST_MONITORING",
    "HEATED_CATALYST_MONITORING",
    "EVAPORATIVE_SYSTEM_MONITORING",
    "SECONDARY_AIR_SYSTEM_MONITORING",
    None,  # Reserved
    "OXYGEN_SENSOR_MONITORING",
    "OXYGEN_SENSOR_HEATER_MONITORING",
    "EGR_VVT_SYSTEM_MONITORING"
]

# Compression ignition (diesel) engine tests (bit position indexed, None = reserved/unused)
COMPRESSION_TESTS = [
    "NMHC_CATALYST_MONITORING",
    "NOX_SCR_AFTERTREATMENT_MONITORING",
    None,  # Reserved
    "BOOST_PRESSURE_MONITORING",
    None,  # Reserved
    "EXHAUST_GAS_SENSOR_MONITORING",
    "PM_FILTER_MONITORING",
    "EGR_VVT_SYSTEM_MONITORING",
]

FUEL_STATUS = [
    "Open loop due to insufficient engine temperature",
    "Closed loop, using oxygen sensor feedback to determine fuel mix",
    "Open loop due to engine load OR fuel cut due to deceleration",
    "Open loop due to system failure",
    "Closed loop, using at least one oxygen sensor but there is a fault in the feedback system",
]

AIR_STATUS = [
    "Upstream",
    "Downstream of catalytic converter",
    "From the outside atmosphere or off",
    "Pump commanded on for diagnostics",
]

OBD_COMPLIANCE = [
    "Undefined",
    "OBD-II as defined by the CARB",
    "OBD as defined by the EPA",
    "OBD and OBD-II",
    "OBD-I",
    "Not OBD compliant",
    "EOBD (Europe)",
    "EOBD and OBD-II",
    "EOBD and OBD",
    "EOBD, OBD and OBD II",
    "JOBD (Japan)",
    "JOBD and OBD II",
    "JOBD and EOBD",
    "JOBD, EOBD, and OBD II",
    "Reserved",
    "Reserved",
    "Reserved",
    "Engine Manufacturer Diagnostics (EMD)",
    "Engine Manufacturer Diagnostics Enhanced (EMD+)",
    "Heavy Duty On-Board Diagnostics (Child/Partial) (HD OBD-C)",
    "Heavy Duty On-Board Diagnostics (HD OBD)",
    "World Wide Harmonized OBD (WWH OBD)",
    "Reserved",
    "Heavy Duty Euro OBD Stage I without NOx control (HD EOBD-I)",
    "Heavy Duty Euro OBD Stage I with NOx control (HD EOBD-I N)",
    "Heavy Duty Euro OBD Stage II without NOx control (HD EOBD-II)",
    "Heavy Duty Euro OBD Stage II with NOx control (HD EOBD-II N)",
    "Reserved",
    "Brazil OBD Phase 1 (OBDBr-1)",
    "Brazil OBD Phase 2 (OBDBr-2)",
    "Korean OBD (KOBD)",
    "India OBD I (IOBD I)",
    "India OBD II (IOBD II)",
    "Heavy Duty Euro OBD Stage VI (HD EOBD-IV)",
]

IGNITION_TYPE = [
    "spark",       # Gas
    "compression", # Diesel
]

FUEL_TYPES = [
    "Not available",
    "Gasoline",
    "Methanol",
    "Ethanol",
    "Diesel",
    "LPG",
    "CNG",
    "Propane",
    "Electric",
    "Bifuel running Gasoline",
    "Bifuel running Methanol",
    "Bifuel running Ethanol",
    "Bifuel running LPG",
    "Bifuel running CNG",
    "Bifuel running Propane",
    "Bifuel running Electricity",
    "Bifuel running electric and combustion engine",
    "Hybrid gasoline",
    "Hybrid Ethanol",
    "Hybrid Diesel",
    "Hybrid Electric",
    "Hybrid running electric and combustion engine",
    "Hybrid Regenerative",
    "Bifuel running diesel",
]