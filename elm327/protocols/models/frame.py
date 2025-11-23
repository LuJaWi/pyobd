
from dataclasses import dataclass

@dataclass
class Frame:
    """ Represents a single OBD-II frame/message line. """

    raw: str
    data: bytearray = bytearray()
    priority: int = None
    addr_mode: int = None
    rx_id: int = None
    tx_id: int = None
    type: int = None
    seq_index: int = 0  # only used when type = CF
    data_len: int = None
