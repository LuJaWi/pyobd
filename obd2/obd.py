"""
Wrapper class for OBD-II data access and storage.

This is the main interface for querying OBD-II commands and storing
historical sensor data.

When using is library, this class is the safest entry point, and should be sufficient
for gathering most OBD-II data.
"""

from datetime import datetime

from obd2.obd_connection import OBDConnection
from obd2.sensors.sensor_value import SensorValue
from obd2.command_functions import OBDCommand, commands
from obd2.response import OBDResponse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from obd2.sensors.sensor_data import OBDSensorData

import logging

logger = logging.getLogger(__name__)

class OBD:
    """
    High-level interface for querying and storing OBD sensor data.
    Manages connection, queries, and historical data storage.
    """

    def __init__(self, obd_connection: OBDConnection):
        self.__connection: OBDConnection = obd_connection
        self.all_supported_commands: frozenset[OBDCommand] = frozenset(
            self.__connection.supported_commands
        )
        # Storage for historical sensor data
        self._sensor_history: dict[str, 'OBDSensorData'] = {}


    @property
    def connection(self) -> OBDConnection:
        """Access the underlying OBD connection (read-only)."""
        return self.__connection

    @property
    def is_connected(self) -> bool:
        """Check if the OBD connection is established."""
        return self.__connection.is_connected()
    
    @property
    def connection(self) -> OBDConnection:
        """Access the underlying OBD connection (read-only)."""
        return self.__connection


    # def supported_pids(self) -> frozenset[str]:
    #     pass # Not implemented
    
    # def status(self) -> SensorValue | None:
    #     """Get the current OBD-II status."""
    #     response: OBDResponse = self.connection.query("STATUS", store=True)
    #     return self.__as_sensor_value(response)

    # def freeze_dtc(self) -> list[str]:
    #     """Get the current freeze frame DTCs."""
    #     response: OBDResponse = self.connection.query("FREEZE_DTC", store=False)
    #     if response.is_null():
    #         return []
    
    # def fuel_system_status(self) -> SensorValue | None:
    #     """Get the current fuel system status."""
    #     response: OBDResponse = self.connection.query("FUEL_STATUS", store=True)
    #     return self.__as_sensor_value(response)

    # def engine_load(self) -> SensorValue | None:
    #     """Get the current engine load percentage."""
    #     response = self.connection.query("ENGINE_LOAD", store=True)
    #     return self.__as_sensor_value(response)
    
    # def coolant_temp(self) -> SensorValue | None:
    #     """Get the current engine coolant temperature."""
    #     response = self.connection.query("COOLANT_TEMP", store=True)
    #     return self.__as_sensor_value(response)
    
    # def short_term_fuel_trim(self, bank: int = 1) -> SensorValue | None:
    #     """Get the short term fuel trim for the specified bank."""
    #     command_name = f"SHORT_FUEL_TRIM_{bank}"
    #     response = self.connection.query(command_name, store=True)
    #     return self.__as_sensor_value(response)
    
    # def long_term_fuel_trim(self, bank: int = 1) -> SensorValue | None:
    #     """Get the long term fuel trim for the specified bank."""
    #     command_name = f"LONG_FUEL_TRIM_{bank}"
    #     response = self.connection.query(command_name, store=True)
    #     return self.__as_sensor_value(response)
    
    # def fuel_pressure(self) -> SensorValue | None:
    #     """Get the current fuel pressure."""
    #     response = self.connection.query("FUEL_PRESSURE", store=True)
    #     return self.__as_sensor_value(response)
    
    # def intake_pressure(self) -> SensorValue | None:
    #     """Get the current intake manifold absolute pressure."""
    #     response = self.connection.query("INTAKE_PRESSURE", store=True)
    #     return self.__as_sensor_value(response)

    # def rpm(self) -> SensorValue | None:
    #     """
    #     Get the current engine RPM.
        
    #     Returns:
    #         SensorValue with the RPM reading, or None if query failed"""
        
    #     response: OBDResponse = self.connection.query("RPM", store=True)
    #     return self.__as_sensor_value(response)
    
    # def speed(self, metric: bool = True) -> SensorValue | None:
    #     """Get the current vehicle speed."""
    #     reponse: OBDResponse = self.connection.query("SPEED", store=True)
    #     if reponse.value and metric and reponse.unit == "mph":
    #         return SensorValue(
    #             name="SPEED",
    #             value=reponse.value * 1.60934,
    #             unit="kmh",
    #             timestamp=datetime.now()
    #         )
    #     else:
    #         return self.__as_sensor_value(reponse)
        
    # def timing_advance(self) -> SensorValue | None:
    #     """Get the current ignition timing advance."""
    #     response = self.connection.query("TIMING_ADVANCE", store=True)
    #     return self.__as_sensor_value(response)
    
    # def o2_voltage(self, bank: int = 1, sensor: int = 1) -> SensorValue | None:
    #     """Get the O2 sensor voltage for the specified bank and sensor number."""
    #     command_name = f"O2_B{bank}_S{sensor}"
    #     response = self.connection.query(command_name, store=True)
    #     return self.__as_sensor_value(response)
    
    # def __as_sensor_value(self, response: OBDResponse) -> SensorValue:
    #     """Helper to format a response as SensorValue."""
    #     try:
    #         return SensorValue(
    #             name=response.command,
    #             value=response.value,
    #             unit=str(response.unit),
    #             timestamp=response.time
    #         )
    #     except Exception as e:
    #         logger.error(f"Error formatting sensor value for {response.command}: {e}")
    #         return None
        