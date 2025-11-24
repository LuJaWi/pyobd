from obd2.response import OBDResponse
from obd2.command import OBDCommand
from obd2.command_functions import commands as commands_singleton
from elm327.elm327 import ELM327
from ecu.ecu_header import ECU_HEADERS
from obd2.utils.obd_status import OBDStatus
from serial_utils.scan_serial import *
from general_utils.version import get_version

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

version = get_version()

class OBDConnection(object):
    commands = commands_singleton
    """
    Class representing an OBD-II connection
    with its assorted commands/sensors.
    """

    def __init__(self, 
                 portstr: str, 
                 baudrate: int = None, 
                 protocol = None, 
                 fast = True,
                 timeout = 0.1, 
                 check_voltage = True, 
                 start_low_power = False
                 ) -> None:
        
        self.__interface: ELM327 = None
        self.__supported_commands = set(OBDConnection.commands.base_commands())
        self.__fast = fast  # global switch for disabling optimizations
        self.__timeout: float = timeout
        self.__last_command: bytes = b""  # used for running the previous command with a CR
        self.__last_header = ECU_HEADERS.ENGINE  # for comparing with the previously used header
        self.__frame_counts: dict = {}  # keeps track of the number of return frames for each command

        logger.info(f"======================= python-OBD {'(v' + version + ')' if version else ''} =======================")
        self.__connect(portstr, baudrate, protocol,
                       check_voltage, start_low_power)  # initialize by connecting and loading sensors
        self.__load_commands()  # try to load the car's supported commands
        logger.info("===================================================================")

    def __connect(self, 
                  portstr: str, 
                  baudrate: int, 
                  protocol, 
                  check_voltage: bool,
                  start_low_power: bool
                  ) -> None:
        """
            Attempts to instantiate an ELM327 connection object.
        """

        if portstr is None:
            logger.info("Using scan_serial to select port")
            port_names = scan_serial()
            logger.info("Available ports: " + str(port_names))

            if not port_names:
                logger.warning("No OBD-II adapters found")
                return

            for port in port_names:
                logger.info("Attempting to use port: " + str(port))
                print("Attempting to use port: " + str(port))
                self.__interface = ELM327(port, baudrate, protocol,
                                        self.__timeout, check_voltage,
                                        start_low_power)

                print(self.__interface.status)
                if self.__interface.status == OBDStatus.CAR_CONNECTED:
                    break # success! stop searching for serial
                else:
                    continue # try other ports
        else:
            logger.info("Explicit port defined")
            self.__interface = ELM327(portstr, baudrate, protocol,
                                    self.__timeout, check_voltage,
                                    start_low_power)

        # if the connection failed, close it
        if self.__interface.status != OBDStatus.CAR_CONNECTED:
            # the ELM327 class will report its own errors
            self.close()

    def __load_commands(self):
        """
            Queries for available PIDs, sets their support status,
            and compiles a list of command objects.
        """

        if self.status() != OBDStatus.CAR_CONNECTED:
            logger.warning("Cannot load commands: No connection to car")
            return

        logger.info("querying for supported commands")
        pid_getters = OBDConnection.commands.pid_getters()
        for get in pid_getters:
            # PID listing commands should sequentially become supported
            # Mode 1 PID 0 is assumed to always be supported
            if not self.test_cmd(get, warn=False):
                continue

            # when querying, only use the blocking OBDConnection.query()
            # prevents problems when query is redefined in a subclass (like Async)
            response = OBDConnection.query(self, get)

            if response.is_null():
                logger.info("No valid data for PID listing command: %s" % get)
                continue

            # loop through PIDs bit-array
            for i, bit in enumerate(response.value):
                if bit:

                    mode = get.mode
                    pid = get.pid + i + 1

                    if OBDConnection.commands.has_pid(mode, pid):
                        self.__supported_commands.add(OBDConnection.commands[mode][pid])

                    # set support for mode 2 commands
                    if mode == 1 and OBDConnection.commands.has_pid(2, pid):
                        self.__supported_commands.add(OBDConnection.commands[2][pid])

        logger.info("finished querying with %d commands supported" % len(self.__supported_commands))

    def __set_header(self, header):
        if header == self.__last_header:
            return
        r = self.__interface.send_and_parse(b'AT SH ' + header + b' ')
        if not r:
            logger.info("Set Header ('AT SH %s') did not return data", header)
            return OBDResponse()
        if "\n".join([m.raw() for m in r]) != "OK":
            logger.info("Set Header ('AT SH %s') did not return 'OK'", header)
            return OBDResponse()
        self.__last_header = header

    def close(self):
        """
            Closes the connection, and clears supported_commands
        """

        self.__supported_commands = set()

        if self.__interface is not None:
            logger.info("Closing connection")
            self.__set_header(ECU_HEADERS.ENGINE)
            self.__interface.close()
            self.__interface = None

    @property
    def interface(self):
        """Get the ELM327 interface (read-only)."""
        return self.__interface
    
    @property
    def supported_commands(self):
        """Get a copy of supported commands (read-only)."""
        return frozenset(self.__supported_commands)
    
    @property
    def supported_command_names(self):
        """Get a list of supported command names (read-only)."""
        return [cmd.name for cmd in self.__supported_commands]

    @property
    def fast(self):
        """Get the fast mode setting."""
        return self.__fast
    
    @fast.setter
    def fast(self, value: bool):
        """Set the fast mode (query optimization) setting."""
        if not isinstance(value, bool):
            raise TypeError("fast must be a boolean")
        self.__fast = value
    
    @property
    def timeout(self):
        """Get the current timeout value."""
        return self.__timeout
    
    @timeout.setter
    def timeout(self, value: float):
        """Set the timeout value. Also updates the interface timeout if connected."""
        if value <= 0:
            raise ValueError("Timeout must be positive")
        self.__timeout = value
        if self.__interface is not None:
            self.__interface.timeout = value

    def status(self):
        """ returns the OBD connection status """
        if self.__interface is None:
            return OBDStatus.NOT_CONNECTED
        else:
            return self.__interface.status

    def low_power(self):
        """ Enter low power mode """
        if self.__interface is None:
            return OBDStatus.NOT_CONNECTED
        else:
            return self.__interface.low_power()

    def normal_power(self):
        """ Exit low power mode """
        if self.__interface is None:
            return OBDStatus.NOT_CONNECTED
        else:
            return self.__interface.normal_power()

    # not sure how useful this would be

    # def ecus(self):
    #     """ returns a list of ECUs in the vehicle """
    #     if self.__interface is None:
    #         return []
    #     else:
    #         return self.__interface.ecus()

    def protocol_name(self):
        """ returns the name of the protocol being used by the ELM327 """
        if self.__interface is None:
            return ""
        else:
            return self.__interface.protocol_name

    def protocol_id(self):
        """ returns the ID of the protocol being used by the ELM327 """
        if self.__interface is None:
            return ""
        else:
            return self.__interface.protocol_id

    def port_name(self):
        """ Returns the name of the currently connected port """
        if self.__interface is not None:
            return self.__interface.port_name
        else:
            return ""

    def is_connected(self):
        """
            Returns a boolean for whether a connection with the car was made.

            Note: this function returns False when:
            obd.status = OBDStatus.ELM_CONNECTED
        """
        if self.status() == OBDStatus.ELM_CONNECTED:
            logger.warning("ELM connected but no car connection")
            return False
        return self.status() == OBDStatus.CAR_CONNECTED

    def print_commands(self):
        """
            Utility function meant for working in interactive mode.
            Prints all commands supported by the car.
        """
        for c in self.__supported_commands:
            print(str(c))

    def supports(self, cmd):
        """
            Returns a boolean for whether the given command
            is supported by the car
        """
        return cmd in self.__supported_commands

    def test_cmd(self, cmd, warn=True):
        """
            Returns a boolean for whether a command will
            be sent without using force=True.
        """
        # test if the command is supported
        if not self.supports(cmd):
            if warn:
                logger.warning("'%s' is not supported" % str(cmd))
            return False

        # mode 06 is only implemented for the CAN protocols
        if cmd.mode == 6 and self.__interface.protocol_id not in ["6", "7", "8", "9"]:
            if warn:
                logger.warning("Mode 06 commands are only supported over CAN protocols")
            return False

        return True

    def query(self, cmd: OBDCommand, force: bool=False) -> OBDResponse:
        """
            primary API function. Sends commands to the car, and
            protects against sending unsupported commands.
        """

        if self.status() == OBDStatus.NOT_CONNECTED:
            logger.warning("Query failed, no connection available")
            return OBDResponse()

        # if the user forces, skip all checks
        if not force and not self.test_cmd(cmd):
            return OBDResponse()

        self.__set_header(cmd.header)

        logger.info(f"Sending command: {str(cmd)}")
        cmd_string = self.__build_command_string(cmd)
        messages = self.__interface.send_and_parse(cmd_string)

        if cmd_string:
            self.__last_command = cmd_string

        # if we don't already know how many frames this command returns,
        # log it, so we can specify it next time
        if cmd not in self.__frame_counts:
            self.__frame_counts[cmd] = sum([len(m.frames) for m in messages])

        if not messages:
            logger.info("No valid OBD Messages returned")
            return OBDResponse()

        return cmd(messages)  # compute a response object

    def __build_command_string(self, cmd):
        """ assembles the appropriate command string """
        cmd_string = cmd.command

        # if we know the number of frames that this command returns,
        # only wait for exactly that number. This avoids some harsh
        # timeouts from the ELM, thus speeding up queries.
        if self.__fast and cmd.fast and (cmd in self.__frame_counts):
            cmd_string += str(self.__frame_counts[cmd]).encode()

        # if we sent this last time, just send a CR
        # (CR is added by the ELM327 class)
        if self.__fast and (cmd_string == self.__last_command):
            cmd_string = b""

        return cmd_string
