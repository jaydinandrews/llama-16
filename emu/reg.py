from ctypes import c_uint16
from array import array
from enum import IntEnum

class Registers():
    def __init__(self):
        self.gprs = array('H', [0]*4)
        self.pc = (c_uint16)()
        self.sp = (c_uint16)()
        self.bp = (c_uint16)()
        self.flags = (c_uint16)()

class Flags(IntEnum):
    positive = 0
    zero = 1
    negative = 2
    less = 3
    equal = 4
    great = 5
