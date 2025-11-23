
from dataclasses import dataclass, field

@dataclass
class Frame:
    """ Represents a single OBD-II frame/message line. """

    raw: str
    data: bytearray = field(default_factory=bytearray)
    priority: int = None
    addr_mode: int = None
    rx_id: int = None
    tx_id: int = None
    type: int = None
    seq_index: int = 0  # only used when type = CF
    data_len: int = None
