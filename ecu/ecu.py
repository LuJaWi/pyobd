"""ECU constants for marking and filtering messages."""

from enum import Enum

class ECU(Enum):
    """ constant flags used for marking and filtering messages """

    ALL = 0b11111111  # used by OBDCommands to accept messages from any ECU
    ALL_KNOWN = 0b11111110  # used to ignore unknown ECUs, since this lib probably can't handle them

    # each ECU gets its own bit for ease of making OR filters
    UNKNOWN = 0b00000001  # unknowns get their own bit, since they need to be accepted by the ALL filter
    ENGINE = 0b00000010
    TRANSMISSION = 0b00000100