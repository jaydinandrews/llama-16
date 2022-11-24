import sys
import argparse
from mem import LLAMAMemory
from cpu import LLAMACpu, CpuHalted


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

        self.memory = LLAMAMemory()
        self.memory.load_program(args.program)
        self.cpu = LLAMACpu(self.memory, self.debug_mode)

        try:
            while True:
                self.cpu.exec_next_instruction()
        except CpuHalted:
            print("CPU halted. Closing emulator...")
            if self.debug_mode:
                self.dump_state()
            sys.exit(0)
        except (Exception, KeyboardInterrupt) as e:
            self.dump_state()
            raise e

    def dump_state(self):
        self.cpu.dump_state()
        self.memory.dump_mem_map()


if __name__ == "__main__":
    emulator = Emulator()
