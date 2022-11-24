import argparse, array, sys
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
        self.run()
        self.dump_state()

    def run(self):
        halted = False
        while not halted:
            # get current instruction pointer
            ip = self.registers.reg_read('ip')
            if self.debug_mode:
                print(f"IP: {hex(ip)}")
            # get instruction at the ip
            instruction = self.mem_read(ip)
            if self.debug_mode:
                print(f"Opcode at IP: {hex(instruction)}")

            # executed instruction will return the next ip
            ip = self.execute(instruction)

            # set new ip
            self.registers.reg_write('ip', ip)
            if self.debug_mode:
                print(f"New IP: {hex(ip)}")
                print(f"Next Opcode: {(hex(self.mem_read(self.registers.reg_read('ip'))))}")
            halted = True


    def execute(self, instruction):
       op, src, dst = self.decode_operand_types(instruction) 
       print(f"SRCCCC is {src}")
       return self.registers.reg_read('ip') + 0x1

    def decode_operand_types(self, instruction):
        op_code = (instruction & 0xF000) >> 12
        src_code = (instruction & 0x00F0) >> 4
        dst_code = instruction & 0x000F

        if self.debug_mode:
            print(f"OPERATION is {hex(op_code)}")
            print(f"SOURCE is {hex(src_code)}")
            print(f"DEST is {hex(dst_code)}")

        if src_code == 0xE:
            #immediate
            print("src is imm")
            src = self.mem_read(self.registers.reg_read('ip') + 0x1)
        elif src_code == 0xF:
            #mem
            print("src is mem adr")
            adr = self.mem_read(self.registers.reg_read('ip') + 0x1)
            src = self.mem_read(adr)
        elif src_code < 8:
            #reg
            print("src is reg")
            src = self.reg_read('src_code')
        else:
            self.write_error("Invalid source encoding: {hex(src_code)}")

        if dst_code == 15:
            print("dst is mem")
            # mem
        elif dst_code < 8:
            print("dst is reg")
            # reg
        else:
            self.write_error("Invalid destination encoding: {hex(dst_code)}")

        return op_code, src, dst_code


    def write_error(self, message):
        print(f"Emulator error: {message}")
        if self.debug_mode:
            print("Dumping state at error...")
            self.dump_state()
            sys.exit(1)


    def dump_state(self):
        print("======== LLAMA-16 Emulator State ========")
        print(f"IP: {hex(self.registers.reg_read('ip'))}")
        print(f"SP: {hex(self.registers.reg_read('sp'))}")
        print(f"BP: {hex(self.registers.reg_read('bp'))}")
        print(f"F:  {self.registers.get_flags()}")

    def mem_read(self, address):
        return self.memory[address]

    def mem_write(self, address, value):
        self.memory[address] = value
   
    def load_program(self, filename):
        with open(filename, 'rb') as f:
            c = f.read()
            if self.debug_mode:
                print(f"loading {filename} of size {len(c)} bytes")
        for count in range(0, len(c), 2):
            self.memory[int(0x4000+count/2)] = unpack('<H', c[count:count+2])[0]

   
if __name__ == "__main__":
    emulator = Emulator()
