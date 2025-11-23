from bitarray import bitarray


class BitArray:
    """
    Class for representing bitarrays (inefficiently)

    There's a nice C-optimized lib for this: https://github.com/ilanschnell/bitarray
    but python-OBD doesn't use it enough to be worth adding the dependency.
    But, if this class starts getting used too much, we should switch to that lib.
    """

    def __init__(self, _bytearray):
        self.bits = bitarray()
        self.bits.frombytes(_bytearray)

    def num_set(self):
        return self.bits.count(True)

    def num_cleared(self):
        return self.bits.count(False)

    def value(self, start, stop):
        bits_slice = self.bits[start:stop]
        if len(bits_slice) == 0:
            return 0
        return int(bits_slice.to01(), 2)

    def __getitem__(self, key):
        result = self.bits[key]
        if isinstance(result, slice):
            return list(result)
        else:
            return result

    def __len__(self):
        return len(self.bits)

    def __str__(self):
        return self.bits

    def __iter__(self):
        return [b == "1" for b in self.bits].__iter__()

