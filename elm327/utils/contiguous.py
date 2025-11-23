def is_contiguous(l: list[int], start: int, end: int) -> bool:
    """ Specialized function to determine if a list of integers is contiguous """
    if not l:
        return False
    if l[0] != start:
        return False
    if l[-1] != end:
        return False

    # for consequtiveness, look at the integers in pairs
    pairs = zip(l, l[1:])
    if not all([p[0] + 1 == p[1] for p in pairs]):
        return False

    return True