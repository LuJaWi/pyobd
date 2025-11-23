

def is_hex(s):
    """ returns True if s is a valid hex string """
    try:
        int(s, 16)
        return True
    except ValueError:
        return False
    

def bytes_to_int(bs):
    """ converts a big-endian byte array into a single integer """
    v = 0
    p = 0
    for b in reversed(bs):
        v += b * (2 ** p)
        p += 8
    return v


def bytes_to_hex(bs):
    h = ""
    for b in bs:
        bh = hex(b)[2:]
        h += ("0" * (2 - len(bh))) + bh
    return h


def twos_comp(val, num_bits):
    """compute the 2's compliment of int value val"""
    if ((val & (1 << (num_bits - 1))) != 0):
        val = val - (1 << num_bits)
    return val

