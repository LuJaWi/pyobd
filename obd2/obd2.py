from obd2.response import OBDResponse
from obd2.command import OBDCommand
from obd2.command_functions import Commands
from elm327.elm327 import ELM327
from ecu.ecu_header import ECU_HEADERS
from obd2.utils.obd_status import OBDStatus
from serial_utils.scan_serial import *
from general_utils.version import get_version

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

version = get_version()

class OBD(object):
    commands = Commands()
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
        self.interface = None
        self.supported_commands = set(OBD.commands.base_commands())
        self.fast = fast  # global switch for disabling optimizations
        self.timeout: float = timeout
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
                self.interface = ELM327(port, baudrate, protocol,
                                        self.timeout, check_voltage,
                                        start_low_power)

                print(self.interface.status())
                if self.interface.status() == OBDStatus.CAR_CONNECTED:
                    break # success! stop searching for serial
                else:
                    continue # try other ports
        else:
            logger.info("Explicit port defined")
            self.interface = ELM327(portstr, baudrate, protocol,
                                    self.timeout, check_voltage,
                                    start_low_power)

        # if the connection failed, close it
        if self.interface.status() != OBDStatus.CAR_CONNECTED:
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
        pid_getters = OBD.commands.pid_getters()
        for get in pid_getters:
            # PID listing commands should sequentially become supported
            # Mode 1 PID 0 is assumed to always be supported
            if not self.test_cmd(get, warn=False):
                continue

            # when querying, only use the blocking OBD.query()
            # prevents problems when query is redefined in a subclass (like Async)
            response = OBD.query(self, get)

            if response.is_null():
                logger.info("No valid data for PID listing command: %s" % get)
                continue

            # loop through PIDs bit-array
            for i, bit in enumerate(response.value):
                if bit:

                    mode = get.mode
                    pid = get.pid + i + 1

                    if OBD.commands.has_pid(mode, pid):
                        self.supported_commands.add(OBD.commands[mode][pid])

                    # set support for mode 2 commands
                    if mode == 1 and OBD.commands.has_pid(2, pid):
                        self.supported_commands.add(OBD.commands[2][pid])

        logger.info("finished querying with %d commands supported" % len(self.supported_commands))

    def __set_header(self, header):
        if header == self.__last_header:
            return
        r = self.interface.send_and_parse(b'AT SH ' + header + b' ')
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

        self.supported_commands = set()

        if self.interface is not None:
            logger.info("Closing connection")
            self.__set_header(ECU_HEADERS.ENGINE)
            self.interface.close()
            self.interface = None

    def status(self):
        """ returns the OBD connection status """
        if self.interface is None:
            return OBDStatus.NOT_CONNECTED
        else:
            return self.interface.status()

    def low_power(self):
        """ Enter low power mode """
        if self.interface is None:
            return OBDStatus.NOT_CONNECTED
        else:
            return self.interface.low_power()

    def normal_power(self):
        """ Exit low power mode """
        if self.interface is None:
            return OBDStatus.NOT_CONNECTED
        else:
            return self.interface.normal_power()

    # not sure how useful this would be

    # def ecus(self):
    #     """ returns a list of ECUs in the vehicle """
    #     if self.interface is None:
    #         return []
    #     else:
    #         return self.interface.ecus()

    def protocol_name(self):
        """ returns the name of the protocol being used by the ELM327 """
        if self.interface is None:
            return ""
        else:
            return self.interface.protocol_name()

    def protocol_id(self):
        """ returns the ID of the protocol being used by the ELM327 """
        if self.interface is None:
            return ""
        else:
            return self.interface.protocol_id()

    def port_name(self):
        """ Returns the name of the currently connected port """
        if self.interface is not None:
            return self.interface.port_name()
        else:
            return ""

    def is_connected(self):
        """
            Returns a boolean for whether a connection with the car was made.

            Note: this function returns False when:
            obd.status = OBDStatus.ELM_CONNECTED
        """
        return self.status() == OBDStatus.CAR_CONNECTED

    def print_commands(self):
        """
            Utility function meant for working in interactive mode.
            Prints all commands supported by the car.
        """
        for c in self.supported_commands:
            print(str(c))

    def supports(self, cmd):
        """
            Returns a boolean for whether the given command
            is supported by the car
        """
        return cmd in self.supported_commands

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
        if cmd.mode == 6 and self.interface.protocol_id() not in ["6", "7", "8", "9"]:
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

        logger.info("Sending command: %s" % str(cmd))
        cmd_string = self.__build_command_string(cmd)
        messages = self.interface.send_and_parse(cmd_string)

        # if we're sending a new command, note it
        # first check that the current command WASN'T sent as an empty CR
        # (CR is added by the ELM327 class)
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
        if self.fast and cmd.fast and (cmd in self.__frame_counts):
            cmd_string += str(self.__frame_counts[cmd]).encode()

        # if we sent this last time, just send a CR
        # (CR is added by the ELM327 class)
        if self.fast and (cmd_string == self.__last_command):
            cmd_string = b""

        return cmd_string
