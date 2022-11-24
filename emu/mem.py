import array


class LLAMAMemory(object):

    def __init__(self):
        self.mem_size = 2**16
        self.memory = array.array('H', [0 for i in range(self.mem_size)])

    def load_program(self, filename):
        self._wipe_memory()
        prog_bytes = self._read_program(filename)

        for i in range(0, len(prog_bytes)):
            self.memory[0x4000+i] = prog_bytes[i]

    def mem_write(self, address, value):
        self.memory[address] = value

    def mem_read(self, address):
        return self.memory[address]

    def dump_mem_map(self):
        print("========== LLAMA-16 Memory Map ==========")
        for i in range(2**16):
            if self.memory[i] != 0:
                print(f"{hex(i)}: {hex(self.memory[i])}")
        print("=========== END OF Memory Map ===========")

    def _read_program(self, filename):
        prog_bytes = array.array('H', range(0))
        with open(filename, 'rb') as f:
            prog_bytes.frombytes(f.read())
        return prog_bytes

    def _wipe_memory(self):
        for i in range(self.mem_size):
            self.memory[i] = 0
