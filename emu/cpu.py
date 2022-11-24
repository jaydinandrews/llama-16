import ctypes, sys

IP_START = 0x4000
SP_START = 0xDFC0
BP_START = 0xDFC0
RIP_REG = 4
RSP_REG = 5
RBP_REG = 6
RFLAG_REG = 7

def ushort(value):
    return ctypes.c_ushort(value).value


class CpuHalted(Exception):
    pass


class LLAMACpu(object):

    def __init__(self, memory):
        self.memory = memory
        self.registers = [0, 0, 0, 0, IP_START, SP_START, BP_START, 0]

    def exec_next_instruction(self):
        ip = self._get_ip()
        self._increment_rip()
        instruction = self._mem_read(ip)
        self._decode_instruction(instruction)

    def dump_state(self):
        print("======== LLAMA-16 CPU State ========")
        print(f"REG A: {hex(self.registers[0])}")
        print(f"REG B: {hex(self.registers[1])}")
        print(f"REG C: {hex(self.registers[2])}")
        print(f"REG D: {hex(self.registers[3])}")
        print(f"IP   : {hex(self.registers[RIP_REG])}")
        print(f"SP   : {hex(self.registers[RSP_REG])}")
        print(f"BP   : {hex(self.registers[RBP_REG])}")
        print(f"FLAGS: {self._get_flags()}\n")
        
    def _get_flags(self):
        # 0000 000H 0GEL 0NZP
        set_flags = []
        flags_code = self.registers[RFLAG_REG]
        flags = flags_code & 0x0007
        if(flags == 4):
            set_flags.append('negative')
        elif(flags == 2):
            set_flags.append('zero')
        elif(flags == 1):
            set_flags.append('positive')

        cmp_flags = flags_code & 0x0070
        if(cmp_flags == 4):
            set_flags.append('greater')
        elif(cmp_flags == 2):
            set_flags.append('equal')
        elif(cmp_flags == 1):
            set_flags.append('less')

        halt_flag = flags_code & 0x0100
        if(halt_flag == 1):
            set_flags.append('halt')

        return set_flags

    def _increment_rip(self):
        self.registers[RIP_REG] = ushort(self.registers[RIP_REG] + 1)

    def _mem_read(self, address):
        # Will need to be refactored for memory mapped I/O
        return self.memory.mem_read(address)

    def _mem_write(self, address, value):
        self.memory.mem_write(address, value)

    def _get_ip(self):
        return self.registers[RIP_REG]

    def _update_flags(self, reg_index):
        # 0000 0000 0HGE LNZP
        value = self.registers[reg_index]
        if(value == 0):
            self.registers[RFLAG_REG]

    def _decode_instruction(self, instruction):
        opcode = (instruction >> 12)
        if opcode == 0x0:
            self._mv()
        elif opcode == 0x1:
            self._lea()
        elif opcode == 0x2:
            self._push()
        elif opcode == 0x3:
            self._pop()
        elif opcode == 0x4:
            self._add()
        elif opcode == 0x5:
            self._sub()
        elif opcode == 0x6:
            self._inc()
        elif opcode == 0x7:
            self._dec()
        elif opcode == 0x8:
            self._and()
        elif opcode == 0x9:
            self._or()
        elif opcode == 0xA:
            self._not()
        elif opcode == 0xB:
            self._cmp()
        elif opcode == 0xC:
            self._call()
        elif opcode == 0xD:
            self._jnz()
        elif opcode == 0xE:
            self._ret()
        elif opcode == 0xF:
            self._hlt()
        else:
            #ERROR
            pass
