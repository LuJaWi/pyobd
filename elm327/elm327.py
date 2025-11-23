"""
Module for communicating with ELM327 OBD-II adapters.

This module provides the ELM327 class, which handles communication
with ELM327-compatible OBD-II adapters over serial connections.

It supports automatic baud rate detection, protocol selection,
and sending/receiving OBD-II commands.

"""


import re
import serial
import time
import logging
from elm327.protocols.protocol_can import (
    ISO_15765_4_11bit_500k,
    ISO_15765_4_29bit_500k,
    ISO_15765_4_11bit_250k,
    ISO_15765_4_29bit_250k,
    SAE_J1939,
)
from elm327.protocols.protocol_legacy import (
    SAE_J1850_PWM,
    SAE_J1850_VPW,
    ISO_9141_2,
    ISO_14230_4_5baud,
    ISO_14230_4_fast,
)
from elm327.protocols.protocol_unknown import UnknownProtocol

from obd2.utils.obd_status import OBDStatus


logger = logging.getLogger(__name__)


class ELM327:
    """
        Handles communication with the ELM327 adapter.

        After instantiation with a portname (/dev/ttyUSB0, etc...),
        the following functions become available:

            send_and_parse()
            close()
            status()
            port_name()
            protocol_name()
            ecus()
    """

    # chevron (ELM prompt character)
    ELM_PROMPT = b'>'
    # an 'OK' which indicates we are entering low power state
    ELM_LP_ACTIVE = b'OK'

    _SUPPORTED_PROTOCOLS = {
        # "0" : None,
        # Automatic Mode. This isn't an actual protocol. If the
        # ELM reports this, then we don't have enough
        # information. see auto_protocol()
        "1": SAE_J1850_PWM,
        "2": SAE_J1850_VPW,
        "3": ISO_9141_2,
        "4": ISO_14230_4_5baud,
        "5": ISO_14230_4_fast,
        "6": ISO_15765_4_11bit_500k,
        "7": ISO_15765_4_29bit_500k,
        "8": ISO_15765_4_11bit_250k,
        "9": ISO_15765_4_29bit_250k,
        "A": SAE_J1939,
        # "B" : None, # user defined 1
        # "C" : None, # user defined 2
    }

    # used as a fallback, when ATSP0 doesn't cut it
    _TRY_PROTOCOL_ORDER = [
        "6",  # ISO_15765_4_11bit_500k
        "8",  # ISO_15765_4_11bit_250k
        "1",  # SAE_J1850_PWM
        "7",  # ISO_15765_4_29bit_500k
        "9",  # ISO_15765_4_29bit_250k
        "2",  # SAE_J1850_VPW
        "3",  # ISO_9141_2
        "4",  # ISO_14230_4_5baud
        "5",  # ISO_14230_4_fast
        "A",  # SAE_J1939
    ]

    # 38400, 9600 are the possible boot bauds (unless reprogrammed via
    # PP 0C).  19200, 38400, 57600, 115200, 230400, 500000 are listed on
    # p.46 of the ELM327 datasheet.
    #
    # Once pyserial supports non-standard baud rates on platforms other
    # than Linux, we'll add 500K to this list.
    #
    # We check the two default baud rates first, then go fastest to
    # slowest, on the theory that anyone who's using a slow baud rate is
    # going to be less picky about the time required to detect it.
    _TRY_BAUDS = [38400, 9600,  115200, 57600, 19200, 14400, 3000000, 2000000, 1000000, 250000, 230400, 128000, 500000, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000]

    def __init__(self, 
                 portname: str, 
                 baudrate: int, 
                 protocol: str, 
                 timeout: float,
                 check_voltage: bool = False, 
                 start_low_power: bool = False
                 ) -> None:
        """Initializes port by resetting device and getting supported PIDs."""
        log_msg = f"Initializing ELM327: PORT={portname} BAUD={baudrate} PROTOCOL={protocol}"
        logger.info(log_msg)
        print(log_msg)
        
        # Save connection parameters for reconnection
        self.__portname = portname
        self.__baudrate = baudrate
        self.__protocol_id = protocol
        self.__check_voltage = check_voltage
        self.__start_low_power = start_low_power
        
        # Initialize instance variables
        self.__status = OBDStatus.NOT_CONNECTED
        self.__protocol = UnknownProtocol([])
        self.__low_power_mode = False
        self.__timeout = timeout
        self.__port = None
        
        # Perform initial connection
        self._connect(portname, baudrate, protocol, check_voltage, start_low_power)

    def _connect(self, portname: str, baudrate: int, protocol: str, 
                 check_voltage: bool = False, start_low_power: bool = False) -> bool:
        """
        Internal method to establish connection to ELM327 device.
        
        This performs the full connection sequence:
        1. Open serial port
        2. Wake from low power (if needed)
        3. Set baudrate
        4. Reset device (ATZ)
        5. Configure settings (ATE0, ATH1, ATL0)
        6. Check voltage (optional)
        7. Set protocol
        
        Args:
            portname: Serial port path
            baudrate: Communication baudrate
            protocol: OBD protocol to use (None for auto-detect)
            check_voltage: Whether to verify vehicle voltage
            start_low_power: Whether device starts in low power mode
            
        Returns:
            True if connection successful, False otherwise
        """
        # Reset status
        self.__status = OBDStatus.NOT_CONNECTED
        
        # Open serial port
        self.__port = self.__open_serial_port(portname, timeout=self.__timeout)
        if self.__port is None:
            self.__status = OBDStatus.NOT_CONNECTED
            return False

        # Wake from low power if needed
        if start_low_power:
            self.__wake_from_low_power()

        # Set baudrate
        if not self.set_baudrate(baudrate):
            logger.error("Failed to set baudrate")
            print("Failed to set baudrate")
            self.__cleanup_failed_connection()
            return False
        print(f"Baudrate set to {baudrate}")

        # Reset device (ATZ)
        if not self.__reset_device():
            self.__cleanup_failed_connection()
            return False

        # Configure ELM327 settings
        if not self.__disable_echo():  # ATE0 (echo OFF)
            self.__cleanup_failed_connection()
            return False

        if not self.__enable_headers():  # ATH1 (headers ON)
            self.__cleanup_failed_connection()
            return False

        if not self.__disable_linefeeds():  # ATL0 (linefeeds OFF)
            self.__cleanup_failed_connection()
            return False

        # Successfully communicated with ELM
        self.__status = OBDStatus.ELM_CONNECTED
        print('Connected to the ELM327')
        
        # Check voltage if requested
        if check_voltage:
            if not self.__is_vehicle_voltage_correct():
                # Keep ELM_CONNECTED status - we can talk to adapter
                logger.warning("Voltage check failed, but ELM is connected")
                return False
            self.__status = OBDStatus.OBD_CONNECTED
            print('OBD Connected')
        
        # Try to communicate with the car
        if not self.set_protocol(protocol):
            err_msg = "Failed to set protocol. "
            err_msg += "Adapter is connected, but failed to connect to the vehicle, ignition may be off."
            logger.error(err_msg)
            print(err_msg)
            # Keep ELM_CONNECTED status - adapter works, just can't reach vehicle
            return False
        
        # Success!
        self.__status = OBDStatus.CAR_CONNECTED
        log_msg = f"Connected Successfully: PORT={portname} BAUD={self.__port.baudrate} PROTOCOL={self.__protocol.ELM_ID}"
        logger.info(log_msg)
        print(log_msg)
        return True

    def is_connected(self) -> bool:
        """ Check if the port is still valid and open """
        if self.__port is None or self.__status == OBDStatus.NOT_CONNECTED:
            return False
        try:
            return self.__port.is_open
        except serial.SerialException:
            logging.error("Serial exception when checking port status")
            return False

    def set_protocol(self, protocol_) -> bool:
        if not self.is_connected():
            err_msg = "Cannot set_protocol() when unconnected"
            logger.error(err_msg)
            print(err_msg)
            return False
        if protocol_ is not None:
            # an explicit protocol was specified
            if protocol_ not in self._SUPPORTED_PROTOCOLS:
                err_msg = f"{protocol_} is not a valid protocol. Please use \"1\" through \"A\""
                logger.error(err_msg)
                print(err_msg)
                return False
            return self.manual_protocol(protocol_)
        else:
            # auto detect the protocol
            return self.auto_protocol()

    def manual_protocol(self, protocol_):
        r = self.__send(b"ATTP" + protocol_.encode())
        r0100 = self.__send(b"0100")

        if not self.__has_message(r0100, "UNABLE TO CONNECT"):
            # success, found the protocol
            self.__protocol = self._SUPPORTED_PROTOCOLS[protocol_](r0100)
            print('Protocol set.')
            return True
        else:
            print('Failed to set protocol.')
        return False

    def auto_protocol(self):
        """
            Attempts communication with the car.

            If no protocol is specified, then protocols at tried with `ATTP`

            Upon success, the appropriate protocol parser is loaded,
            and this function returns True
        """

        # -------------- try the ELM's auto protocol mode --------------
        r = self.__send(b"ATSP0", delay=1)
        print('Trying to set auto protocol.')
        # -------------- 0100 (first command, SEARCH protocols) --------------
        r0100 = self.__send(b"0100", delay=1)
        if self.__has_message(r0100, "UNABLE TO CONNECT"):
            logger.error("Failed to query protocol 0100: unable to connect")
            print("Failed to query protocol 0100: unable to connect")
            # return False  -- Try one by one !!

        # ------------------- ATDPN (list protocol number) -------------------
        r = self.__send(b"ATDPN")
        if len(r) != 1:
            logger.error("Failed to retrieve current protocol")
            print("Failed to retrieve current protocol")
            # return False  -- Try one by one !!

        p = r[0]  # grab the first (and only) line returned
        # suppress any "automatic" prefix
        p = p[1:] if (len(p) > 1 and p.startswith("A")) else p

        # check if the protocol is something we know
        if p in self._SUPPORTED_PROTOCOLS:
            # jackpot, instantiate the corresponding protocol handler
            self.__protocol = self._SUPPORTED_PROTOCOLS[p](r0100)
            return True
        else:
            # an unknown protocol
            # this is likely because not all adapter/car combinations work
            # in "auto" mode. Some respond to ATDPN responded with "0"
            logger.debug("ELM responded with unknown protocol. Trying them one-by-one")
            print("ELM responded with unknown protocol. Trying them one-by-one")
            for p in self._TRY_PROTOCOL_ORDER:
                r = self.__send(b"ATTP" + p.encode())
                r0100 = self.__send(b"0100")
                if not self.__has_message(r0100, "UNABLE TO CONNECT") and \
                    not self.__has_message(r0100, "NO DATA") and \
                    not self.__has_message(r0100, "BUS INIT: ...ERROR") and \
                    not self.__has_message(r0100, "CAN ERROR"):
                    # success, found the protocol
                    print('success, found the protocol')
                    self.__protocol = self._SUPPORTED_PROTOCOLS[p](r0100)
                    return True

        # if we've come this far, then we have failed...
        logger.error("Failed to determine protocol")
        print("Failed to determine protocol")
        return False

    def set_baudrate(self, baud_rate: int = None, psuedo_baud_rate: int = 38400) -> int | None:
        """
        Set the baud rate of the ELM327 interface.

        If baud is None, attempts to auto-detect the baud rate.

        Returns the set baud rate on success, or None on failure.
        
        """

        if baud_rate is None:
            # when connecting to pseudo terminal, don't bother with auto baud
            if self.port_name.startswith("/dev/pts"):
                logger.debug("Detected pseudo terminal, skipping baudrate setup")
                print("Detected pseudo terminal, skipping baudrate setup")
                self.__port.baudrate = psuedo_baud_rate
                return psuedo_baud_rate
            else:
                return self.auto_detect_baudrate()
        else:
            try:
                self.__port.baudrate = baud_rate
                print(f"Baud rate set to {baud_rate}")
                return baud_rate
            except serial.SerialException:
                print("Baud rate not supported!")
                return None

    def auto_detect_baudrate(self) -> int | None:
        """
        Detect the baud rate at which a connected ELM32x interface is operating.
        
        Returns the detected baud rate on success, or None on failure.
        """
        return detect_elm327_baudrate(self.__port)
 
    def __reset_device(self) -> bool:
        try:
            response = self.__send(b"ATZ", delay=1)  # wait 1 second for ELM to initialize
            if "ELM" in str(response).upper():
                print(str(response))
                print("ATZ successful")
                return True
            else:
                print('ELM not found on this port.')
                return False
            # return data can be junk, so don't bother checking
        except serial.SerialException as e:
            self.__error(e)
            print(e)
            return False

    def __disable_linefeeds(self) -> bool:    
        """ Disable linefeeds"""    
        r = self.__send(b"ATL0")
        if not self.__isok(r):
            self.__error("ATL0 did not return 'OK'")
            return False
        else:
            print('ATL0 OK')
            return True
        
    def __disable_echo(self) -> bool:
        response = self.__send(b"ATE0", delay=1)
        if not self.__isok(response, expectEcho=True):
            self.__error("ATE0 did not return 'OK'")
            return False
        else:
            logger.debug("ATE0 OK")
            return True

    def __enable_headers(self) -> bool:
        response = self.__send(b"ATH1", delay=1)
        if not self.__isok(response):
            self.__error("ATH1 did not return 'OK', or echoing is still ON")
            return False
        else:
            logger.debug("ATH1 OK")
            return True

    def check_voltage(self) -> float | None:
        """ 
        Check the vehicle voltage
        returns the voltage as a float on success, or None on failure
        """
        response = self.__send(b"AT RV")
        if not response or len(response) != 1 or response[0] == '':
            logger.error("No response from 'AT RV'")
            return None
        try:
            response_volts = float(response[0].lower().replace('v', ''))
            return response_volts
        except ValueError as e:
            self.__error(f"Incorrect response from 'AT RV' {response_volts}")
            return None
    
    def __is_vehicle_voltage_correct(self, voltage: float) -> bool:
        """ Check if the vehicle voltage is within acceptable range """
        try:
            voltage = float(self.check_voltage())
        except (TypeError, ValueError):
            voltage = None
        if voltage is None:
            logger.error("Failed to read vehicle voltage")
            print("Failed to read vehicle voltage")
            return False
        elif voltage < 6.0:
            logger.error("Vehicle voltage too low: %.2f V" % voltage)
            print("Vehicle voltage too low: %.2f V" % voltage)
            return False
        elif voltage > 16.0:
            logger.error("Vehicle voltage too high: %.2f V" % voltage)
            print("Vehicle voltage too high: %.2f V" % voltage)
            return False
        return True

    def __isok(self, lines, expectEcho=False):
        if not lines:
            return False
        if expectEcho:
            # don't test for the echo itself
            # allow the adapter to already have echo disabled
            return self.__has_message(lines, 'OK')
        else:
            return len(lines) == 1 and lines[0] == 'OK'

    def __has_message(self, lines, text):
        for line in lines:
            if text in line:
                return True
        return False

    def __cleanup_failed_connection(self):
        """
        Clean up after a failed connection attempt.
        Sets status to NOT_CONNECTED and closes the port.
        """
        self.__status = OBDStatus.NOT_CONNECTED
        if self.__port is not None:
            try:
                self.__port.close()
            except Exception as e:
                logger.debug(f"Exception while closing port during cleanup: {e}")
            self.__port = None

    def __error(self, msg):
        """ handles fatal failures, logs error info and closes serial """
        logger.error(str(msg))
        print(str(msg))
        self.__cleanup_failed_connection()
    
    @property
    def timeout(self):
        """Get the current timeout value."""
        return self.__timeout
    
    @timeout.setter
    def timeout(self, value):
        """Set the timeout value. Also updates the port timeout if connected."""
        if value <= 0:
            raise ValueError("Timeout must be positive")
        self.__timeout = value
        if self.__port is not None:
            self.__port.timeout = value
            self.__port.write_timeout = value
    
    @property
    def port_name(self):
        """Get the name/path of the serial port."""
        if self.__port is not None:
            return self.__port.portstr
        else:
            return ""

    @property
    def status(self):
        """Get the current connection status."""
        return self.__status

    @property
    def baudrate(self):
        """Get the current baudrate."""
        if self.__port is not None:
            return self.__port.baudrate
        return None

    @property
    def ecus(self):
        """Get the list of ECUs detected."""
        return self.__protocol.ecu_map.values()

    @property
    def protocol_name(self):
        """Get the name of the current protocol."""
        return self.__protocol.ELM_NAME

    @property
    def protocol_id(self):
        """Get the ID of the current protocol."""
        return self.__protocol.ELM_ID
    
    @property
    def is_low_power_mode(self):
        """Check if the device is in low power mode."""
        return self.__low_power_mode

    def low_power(self):
        """
            Enter Low Power mode

            This command causes the ELM327 to shut off all but essential
            services.

            The ELM327 can be woken up by a message to the RS232 bus as
            well as a few other ways. See the Power Control section in
            the ELM327 datasheet for details on other ways to wake up
            the chip.

            Returns the status from the ELM327, 'OK' means low power mode
            is going to become active.
        """
        
        if not self.is_connected():
            err_msg = "Cannot enter low power when unconnected"
            logger.info(err_msg)
            print(err_msg)
            return None

        lines = self.__send(b"ATLP", delay=1, end_marker=self.ELM_LP_ACTIVE)

        if 'OK' in lines:
            logger.debug("Successfully entered low power mode")
            print("Successfully entered low power mode")
            self.__low_power_mode = True
        else:
            logger.debug("Failed to enter low power mode")
            print("Failed to enter low power mode")

        return lines

    def normal_power(self):
        """
            Exit Low Power mode

            Send a space to trigger the RS232 to wakeup.

            This will send a space even if we aren't in low power mode as
            we want to ensure that we will be able to leave low power mode.

            See the Power Control section in the ELM327 datasheet for details
            on other ways to wake up the chip.

            Returns the status from the ELM327.
        """
        
        if not self.is_connected():
            err_msg = "Cannot exit low power when unconnected"
            logger.info(err_msg)
            print(err_msg)
            return None

        lines = self.__send(b" ")

        # Assume we woke up
        logger.debug("Successfully exited low power mode")
        print("Successfully exited low power mode")
        self.__low_power_mode = False

        return lines

    def close(self):
        """
            Resets the device, and sets all
            attributes to unconnected states.
        """
        if self.__port is not None:
            logger.info("closing port")
            print("closing port")
            try:
                self.__port.write_timeout = 0.1
                self.__write(b"ATZ")
            except:
                pass
            try:
                self.__port.close()
            except:
                logger.debug("Exception while closing port")
            finally:
                self.__port = None
        
        self.__status = OBDStatus.NOT_CONNECTED
        self.__protocol = None

    def reconnect(self, max_attempts: int = 3, retry_delay: float = 1.0) -> bool:
        """
        Attempt to reconnect to the ELM327 device.
        
        This method tries to re-establish connection after a disconnect by:
        1. Closing any existing connection
        2. Reopening the serial port
        3. Re-running the initialization sequence
        
        Args:
            max_attempts: Maximum number of reconnection attempts (default: 3)
            retry_delay: Delay in seconds between attempts (default: 1.0)
            
        Returns:
            True if reconnection successful, False otherwise
        """
        logger.info(f"Attempting to reconnect (max {max_attempts} attempts)...")
        print(f"Attempting to reconnect (max {max_attempts} attempts)...")
        
        # Use saved connection parameters
        portname = self.__portname
        baudrate = self.__baudrate
        protocol = self.__protocol_id
        check_voltage = self.__check_voltage
        start_low_power = self.__start_low_power
        
        # If we don't have the original parameters, can't reconnect
        if not portname:
            logger.error("Cannot reconnect: original port name not available")
            print("Cannot reconnect: original port name not available")
            return False
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Reconnection attempt {attempt}/{max_attempts}")
            print(f"Reconnection attempt {attempt}/{max_attempts}")
            
            try:
                # Close existing connection cleanly
                self.close()
                
                # Wait before retry (except first attempt)
                if attempt > 1:
                    time.sleep(retry_delay)
                
                # Use the _connect() method to re-establish connection
                if self._connect(portname, baudrate, protocol, check_voltage, start_low_power):
                    logger.info(f"Reconnection successful on attempt {attempt}")
                    print(f"Reconnection successful on attempt {attempt}")
                    return True
                else:
                    logger.warning(f"Attempt {attempt}: Connection failed")
                    print(f"Attempt {attempt}: Connection failed")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt}: Exception during reconnect: {e}")
                print(f"Attempt {attempt}: Exception during reconnect: {e}")
                continue
        
        # All attempts failed
        logger.error(f"Reconnection failed after {max_attempts} attempts")
        print(f"Reconnection failed after {max_attempts} attempts")
        self.__cleanup_failed_connection()
        return False

    # def send_and_parse_with_reconnect(self, cmd, auto_reconnect: bool = True, max_reconnect_attempts: int = 1):
    #     """
    #     Send command with automatic reconnection on failure.
        
    #     This is a wrapper around send_and_parse() that will automatically
    #     attempt to reconnect if the connection is lost.
        
    #     Args:
    #         cmd: Command to send
    #         auto_reconnect: Whether to attempt reconnection on failure (default: True)
    #         max_reconnect_attempts: Number of reconnection attempts (default: 1)
            
    #     Returns:
    #         List of Message objects on success, None on failure
    #     """
    #     # Try normal send first
    #     result = self.send_and_parse(cmd)
        
    #     # If it worked, return the result
    #     if result is not None:
    #         return result
        
    #     # If auto-reconnect is disabled, give up
    #     if not auto_reconnect:
    #         return None
        
    #     # Connection lost - try to reconnect
    #     logger.info("Connection lost during send, attempting reconnect...")
    #     print("Connection lost during send, attempting reconnect...")
        
    #     if self.reconnect(max_attempts=max_reconnect_attempts):
    #         # Reconnection successful, retry the command
    #         logger.info("Reconnected successfully, retrying command...")
    #         print("Reconnected successfully, retrying command...")
    #         return self.send_and_parse(cmd)
    #     else:
    #         # Reconnection failed
    #         logger.error("Reconnection failed, cannot send command")
    #         print("Reconnection failed, cannot send command")
    #         return None

    def send_and_parse(self, cmd):
        """
            send() function used to service all OBDCommands

            Sends the given command string, and parses the
            response lines with the protocol object.

            An empty command string will re-trigger the previous command

            Returns a list of Message objects
        """
        if not self.is_connected():
            err_msg = "Cannot send_and_parse() when unconnected"
            logger.error(err_msg)
            print(err_msg)
            return None

        # Check if we are in low power
        if self.__low_power_mode == True:
            self.normal_power()

        lines = self.__send(cmd)
        messages = self.__protocol(lines)
        return messages

    def __send(self, cmd, delay=None, end_marker=ELM_PROMPT):
        """
            unprotected send() function

            will __write() the given string, no questions asked.
            returns result of __read() (a list of line strings)
            after an optional delay, until the end marker (by
            default, the prompt) is seen
        """
        self.__write(cmd)

        delayed = 0.0
        if delay is not None:
            logger.debug("wait: %d seconds" % delay)
            print("wait: %d seconds" % delay)
            time.sleep(delay)
            delayed += delay

        r = self.__read(end_marker=end_marker)
        while delayed < 1.0 and len(r) <= 0:
            d = 0.1
            logger.debug("no response; wait: %f seconds" % d)
            print("no response; wait: %f seconds" % d)
            time.sleep(d)
            delayed += d
            r = self.__read(end_marker=end_marker)
        return r

    def __write(self, cmd):
        """
            "low-level" function to write a string to the port
        """

        if self.__port:
            cmd += b"\r"  # terminate with carriage return in accordance with ELM327 and STN11XX specifications
            logger.debug("write: " + repr(cmd))
            print("write: " + repr(cmd))
            try:
                self.__port.flushInput()  # dump everything in the input buffer
                self.__port.write(cmd)  # turn the string into bytes and write
                self.__port.flush()  # wait for the output buffer to finish transmitting
            except Exception as e:
                logger.critical(f"Device disconnected while writing: {e}")
                print(f"Device disconnected while writing: {e}")
                self.__cleanup_failed_connection()
                return
        else:
            logger.info("cannot perform __write() when unconnected")
            print("cannot perform __write() when unconnected")

    def __read(self, end_marker=ELM_PROMPT):
        """
            "low-level" read function

            accumulates characters until the end marker (by
            default, the prompt character) is seen
            returns a list of [/r/n] delimited strings
        """
        if not self.__port:
            logger.info("cannot perform __read() when unconnected")
            print("cannot perform __read() when unconnected")
            return []

        buffer = bytearray()

        while True:
            # retrieve as much data as possible
            try:
                data = self.__port.read(self.__port.in_waiting or 1)
            except Exception as e:
                logger.critical(f"Device disconnected while reading: {e}")
                print(f"Device disconnected while reading: {e}")
                self.__cleanup_failed_connection()
                return []

            # if nothing was received
            if not data:
                logger.warning("Failed to read port")
                print("Failed to read port")
                self.__cleanup_failed_connection()
                break

            buffer.extend(data)

            # end on specified end-marker sequence
            if end_marker in buffer:
                break

        # log, and remove the "bytearray(   ...   )" part
        logger.debug("read: " + repr(buffer)[10:-1])

        # clean out any null characters
        buffer = re.sub(b"\x00", b"", buffer)

        # remove the prompt character
        if buffer.endswith(self.ELM_PROMPT):
            buffer = buffer[:-1]

        # convert bytes into a standard string
        string = buffer.decode("utf-8", "ignore")

        # splits into lines while removing empty lines and trailing spaces
        lines = [s.strip() for s in re.split("[\r\n]", string) if bool(s)]

        return lines
    
    def __open_serial_port(self, portname: str, timeout: float) -> serial.Serial:
        """
        Opens the serial port with the given port name.

        timeout parameter is not used for opening the port, but is set
        for read and write operations.
        
        Returns the opened serial port object, or None on failure.
        """
        
        try:
            port = serial.serial_for_url(url=portname,
                                                parity=serial.PARITY_NONE,
                                                stopbits=1,
                                                bytesize=8,
                                                timeout=10)  # Use a long timeout for opening the port, but use the set timeout for reads
            print(f"Port {portname} created")
            port.write_timeout = timeout
            return port
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port: {e}")
            print(f"Failed to open serial port: {e}")
            return None
        except OSError as e:
            logger.error(f"OS error opening serial port: {e}")
            print(f"OS error opening serial port: {e}")
            return None
        
    def __wake_from_low_power(self):
        """
        Wakes the ELM327 from Low Power mode

        Send a space to trigger the RS232 to wakeup.
        """
        if self.__port:
            self.__write(b" ")
            time.sleep(1)
            print("Start low power")
        else:
            log_msg = "Cannot wake from low power when unconnected"
            logger.info(log_msg)
            print(log_msg)


def detect_elm327_baudrate(port: serial.Serial) -> int | None:
    """
    Detect the baud rate at which a connected ELM32x interface is operating.

    Args:
        port: An opened serial port object.
    Returns:
        The detected baud rate on success, or None on failure.
    """

    timeout = port.timeout
    port.timeout = 0.1  # we're only talking with the ELM, so things should go quickly
    port.write_timeout = 0.1

    found_baud = False
    for baud in ELM327._TRY_BAUDS:
        print(f"Trying baudrate {baud}...")
        if _test_baudrate(port, baud):
            found_baud = True
            break

    if not found_baud:
        log_msg = "Failed to find baud rate"
        logger.debug(log_msg)
        print(log_msg)
    else:
        log_msg = f"Detected baud rate: {baud}"
        logger.debug(log_msg)
        print(log_msg)

    log_msg = "Reinstating original timeout"
    logger.debug(log_msg)
    print(log_msg)
    try:
        port.timeout = timeout  # reinstate our original timeout
        port.write_timeout = timeout
    except serial.SerialException:
        log_msg = "Failed to reinstate original timeout"
        logger.debug(log_msg)
        print(log_msg)
        return None
    if found_baud:
        return baud
    else:
        log_msg = "Failed to find baud"
        logger.debug(log_msg)
        print(log_msg)
        return None

def _test_baudrate(port: serial.Serial, baud_rate: int) -> bool:
    """
    Test if the given baud rate is supported by the ELM327 interface.

    Args:
        port: An opened serial port object.
        baud_rate: The baud rate to test.
    Returns:
        True if the baud rate is supported, False otherwise.
    """

    try:
        port.baudrate = baud_rate
    except serial.SerialException:
        log_msg = f"Baudrate {baud_rate} not supported by serial port."
        logger.debug(log_msg)
        print(log_msg)
        return False

    port.flush()

    try:
        port.write(b"\x7F\x7F\r")
    except serial.SerialTimeoutException:
        log_msg = "Port write timeout"
        logger.debug(log_msg)
        print(log_msg)
        return False

    port.flush()
    try:
        response = port.read(1024)
    except serial.SerialTimeoutException:
        log_msg = "Port read timeout"
        logger.debug(log_msg)
        print(log_msg)
        return False

    log_msg = f"Response from baud {baud_rate}: {repr(response)}"
    logger.debug(log_msg)
    print(log_msg)

    if "ELM" in str(response).upper() or ((b'\x7f\x7f\r' in response) and (response.endswith(b">"))):
        log_msg = f"Baudrate {baud_rate} returned valid response"
        logger.debug(log_msg)
        print(log_msg)
        return True
    else:
        log_msg = f"Baudrate {baud_rate} did not return valid response"
        logger.debug(log_msg)
        print(log_msg)
        return False
