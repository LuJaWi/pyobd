
from binascii import hexlify
from dataclasses import dataclass, field

from ecu.ecu import ECU

from elm327.protocols.models.frame import Frame

@dataclass
class Message(object):
    """ represents a fully parsed OBD message of one or more Frames (lines) """

    frames: list[Frame]
    ecu = ECU.UNKNOWN
    num_frames: int = 0
    data: bytearray = field(default_factory=bytearray)
    can: bool = False

    @property
    def tx_id(self):
        if len(self.frames) == 0:
            return None
        else:
            return self.frames[0].tx_id

    def hex(self):
        return hexlify(self.data)

    def raw(self):
        """ returns the original raw input string from the adapter """
        return "\n".join([f.raw for f in self.frames])

    def parsed(self):
        """ boolean for whether this message was successfully parsed """
        return bool(self.data)

    def __eq__(self, other):
        if isinstance(other, Message):
            for attr in ["frames", "ecu", "data"]:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            return True
        else:
            return False
