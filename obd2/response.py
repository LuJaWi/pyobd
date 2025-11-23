""" Module for OBD response objects """

from time import time


class OBDResponse:
    """ Standard response object for any OBDCommand """

    def __init__(self, command=None, messages=None):
        self.command = command
        self.messages = messages if messages else []
        self.value = None
        self.time = time()

    @property
    def unit(self):
        # for backwards compatibility
        from obd import Unit  # local import to avoid cyclic-dependency
        if isinstance(self.value, Unit.Quantity):
            return str(self.value.u)
        elif self.value is None:
            return None
        else:
            return str(type(self.value))

    def is_null(self):
        return (not self.messages) or (self.value == None)

    def __str__(self):
        return str(self.value)

