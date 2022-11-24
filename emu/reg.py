from ctypes import c_uint16
from array import array

class Registers():
    def __init__(self):
        # 0-3 : A-D, 4: IP, 5: SP, 6: BP, 7: F
        self.gprs = array('H', [0]*8)
        # Set IP, SP, BP, and F
        self.gprs[4] = 0x4000
        self.gprs[5] = 0xFFBF
        self.gprs[6] = 0xFFBF

        self.registers = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'ip': 4, 'sp': 5, 'bp': 6, 'f': 7}
        self.flags = {'halt': 6, 'greater': 5, 'equal': 4, 'less': 3, 'negative': 2, 'zero': 1, 'positive': 0}

    def reg_write(self, register, value):
        self.gprs[self.registers[register]] = value

    def reg_read(self, register):
        return self.gprs[self.registers[register]]

    def update_flags(self, register, set_negative=False):
        # Clear bits 0-2
        self.reg_write('f', self.reg_read('f') & 0xFFF8)
        if set_negative == True:
            self.reg_write('f', 1 << 2)
            return

        if self.reg_read(register) == 0:
            self.reg_write('f', 1 << 1)
        elif self.reg_read(register) > 0:
            self.reg_write('f', 1 << 0)

    def update_cmp_flags(self, a, b):
        # Clear bits 3-5
        self.reg_write('f', self.reg_read('f') & 0xFFC7)
        if a > b:
            self.reg_write('f', 1 << 5)
        elif b < a:
            self.reg_write('f', 1 < 3)
        elif a == b:
            self.reg_write('f', 1 << 4)

    def clear_flags(self):
        self.reg_write('f', 0x0)

    def get_flags(self):
        # 0000 0000 0HGE LNZP
        set_flags = []
        cmp_flags = self.reg_read('f') & 0x0038
        if cmp_flags == 32:
            set_flags.append('greater')
        elif cmp_flags == 16:
            set_flags.append('equal')
        elif cmp_flags == 8:
            set_flags.append('less')

        flags = self.reg_read('f') & 0x0007 
        if flags == 4:
            set_flags.append('negative')
        elif flags == 2:
            set_flags.append('zero')
        elif flags == 1:
            set_flags.append('positive')

        return set_flags

    def set_halt(self):
        self.reg_write('f', 1 << 6)
