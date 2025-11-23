
from enum import Enum

class OBDStatus(Enum):
    """ Values for the connection status flags """

    NOT_CONNECTED = "Not Connected"
    ELM_CONNECTED = "ELM Connected"
    OBD_CONNECTED = "OBD Connected"
    CAR_CONNECTED = "Car Connected"