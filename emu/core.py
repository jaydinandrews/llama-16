import argparse, array
from reg import Registers
from pathlib import Path
from struct import unpack


class Emulator(object):
    debug_mode = False

    def __init__(self):
        description = "LLAMA-16 Emulator"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("program",
                            default="",
                            help="input program to be ran")
        parser.add_argument("-d",
                            "--debug",
                            action="store_true",
                            help="print extra debugging infomation")
        args = parser.parse_args()
        if args.debug:
            self.debug_mode = True

        self.memory = array.array('H', [0]*65536)
        self.registers = Registers()
        self.load_program(args.program)

        self.dump_state()

    def dump_state(self):
        print("======== LLAMA-16 Emulator State ========")
        print(f"IP: {hex(self.registers.reg_read('ip'))}")
        print(f"SP: {hex(self.registers.reg_read('sp'))}")
        print(f"BP: {hex(self.registers.reg_read('bp'))}")
        print(f"F:  {self.registers.get_flags()}")

    def mem_read(address):
        return self.memory[address]

    def mem_write(address, value):
        self.memory[address] = value
   
    def load_program(self, filename):
        with open(filename, 'rb') as f:
            c = f.read()
            if debug_mode:
                print(f"loading {filename} of size {len(c)} bytes")
        for count in range(0, len(c), 2):
            self.memory[int(0x4000+count/2)] = unpack('<H', c[count:count+2])[0]

   
if __name__ == "__main__":
    emulator = Emulator()
