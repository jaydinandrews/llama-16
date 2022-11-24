import argparse
from ctypes import c_uint16
from reg import Registers, Flags
from array import array
from pathlib import Path
from struct import unpack


class Emulator(object):
    def __init__(self):
        description = "LLAMA-16 Emulator"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("program",
                            default="",
                            help="input program to be ran")
        args = parser.parse_args()

        self.memory = array('H', [0]*65536)
        self.registers = Registers()
        self.registers.pc.value = 0x4000
        self.load_program(args.program)

    def load_program(self, filename):
        with open(filename, 'rb') as f:
            c = f.read()
        for count in range(0, len(c), 2):
            self.memory[int(0x4000+count/2)] = unpack('>H', c[count:count+2])[0]
            

if __name__ == "__main__":
    emulator = Emulator()
