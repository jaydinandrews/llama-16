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
    debug_mode = False

    def __init__(self, memory, debug_mode=False):
        if debug_mode:
            self.debug_mode = True
        self.memory = memory
        self.registers = [0, 0, 0, 0, IP_START, SP_START, BP_START, 0]

    def exec_next_instruction(self):
        if self.debug_mode:
            self.dump_state()
        ip = self._get_ip()
        self._increment_rip()
        instruction = self._mem_read(ip)
        self._decode_instruction(instruction)
        if self.registers[RFLAG_REG] & 0x0100:
            raise CpuHalted

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

        cmp_flags = (flags_code & 0x0070) >> 4
        if(cmp_flags == 4):
            set_flags.append('greater')
        elif(cmp_flags == 2):
            set_flags.append('equal')
        elif(cmp_flags == 1):
            set_flags.append('less')

        halt_flag = (flags_code & 0x0100) >> 8
        if(halt_flag == 1):
            set_flags.append('halt')

        return set_flags

    def _increment_rip(self):
        self.registers[RIP_REG] = ushort(self.registers[RIP_REG] + 0x1)

    def _mem_read(self, address):
        # Will need to be refactored for memory mapped I/O
        return self.memory.mem_read(address)

    def _mem_write(self, address, value):
        self.memory.mem_write(address, value)

    def _reg_read(self, register):
        if register == 'a':
            return self.registers[0]
        elif register == 'b':
            return self.registers[1]
        elif register == 'c':
            return self.registers[2]
        elif register == 'd':
            return self.registers[3]

    def _reg_write(self, register, value):
        if register == 'a':
            self.registers[0] = ushort(value)
        elif register == 'b':
            self.registers[1] = ushort(value)
        elif register == 'c':
            self.registers[2] = ushort(value)
        elif register == 'd':
            self.registers[3] = ushort(value)

    def _get_ip(self):
        return self.registers[RIP_REG]

    def _update_flags(self, register, compare_flags=0x0):
        # 0000 000H 0GEL 0NZP
        self.registers[RFLAG_REG] = self.registers[RFLAG_REG] & 0xFFF0

        value = self._reg_read(register)
        if value == 0:
            self.registers[RFLAG_REG] = self.registers[RFLAG_REG] + 0x2
        elif value > 0x7FFF:
            self.registers[RFLAG_REG] = self.registers[RFLAG_REG] + 0x4
        else:
            self.registers[RFLAG_REG] = self.registers[RFLAG_REG] + 0x1
        
        if compare_flags != 0x0:
            self.registers[RFLAG_REG] = self.registers[RFLAG_REG] & 0xFF0F
            self.registers[RFLAG_REG] = self.registers[RFLAG_REG] + compare_flags

    def _decode_instruction(self, instruction):
        opcode = (instruction & 0xF000) >> 12
            
        if opcode == 0x0:
            self._mv(instruction)
        elif opcode == 0x1:
            self._lea(instruction)
        elif opcode == 0x2:
            self._push(instruction)
        elif opcode == 0x3:
            self._pop(instruction)
        elif opcode == 0x4:
            self._add(instruction)
        elif opcode == 0x5:
            self._sub(instruction)
        elif opcode == 0x6:
            self._inc(instruction)
        elif opcode == 0x7:
            self._dec(instruction)
        elif opcode == 0x8:
            self._and(instruction)
        elif opcode == 0x9:
            self._or(instruction)
        elif opcode == 0xA:
            self._not(instruction)
        elif opcode == 0xB:
            self._cmp(instruction)
        elif opcode == 0xC:
            self._call(instruction)
        elif opcode == 0xD:
            self._jnz(instruction)
        elif opcode == 0xE:
            self._ret()
        elif opcode == 0xF:
            self._hlt()

    def _get_op_types(self, instruction):
        src_encode = (instruction & 0x00F0) >> 4
        dst_encode = instruction & 0x000F
        if src_encode < 0x4:
            src_type = 'reg'
        elif src_encode == 0xE:
            src_type = 'imm'
        elif src_encode == 0xF:
            src_type = 'mem_adr'

        if dst_encode < 0x4:
            dst_type = 'reg'
        elif dst_encode == 0xF:
            dst_type = 'mem_adr'

        return (src_type, dst_type)

    def _get_register(self, encode):
        if encode == 0:
            return 'a'
        elif encode == 1:
            return 'b'
        elif encode == 2:
            return 'c'
        elif encode == 3:
            return 'd'
    
    def _get_next_word(self):
        word = self._mem_read(self.registers[RIP_REG])
        self._increment_rip()
        return word

    def _mv(self, instruction):
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'imm':
            src = self._get_next_word()
        elif src_type == 'mem_adr':
            address = self._get_next_word()
            src = self._mem_read(address)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            src = self._reg_read(register)

        if dst_type == 'mem_adr':
            address = self._get_next_word()
            self._mem_write(address, src)
        elif dst_type == 'reg':
            register = self._get_register((instruction & 0x000F))
            self._reg_write(register, src)

    def _push(self, instruction):
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'imm':
            value = self._get_next_word()
        elif src_type == 'mem_adr':
            address = self._get_next_word()
            value = self._mem_read(address)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            value = self._reg_read(register)

        self._mem_write(self.registers[RSP_REG], value)
        self.registers[RSP_REG] += 0x1

    def _pop(self, instruction):
        self.registers[RSP_REG] -= 0x1
        value = self._mem_read(self.registers[RSP_REG])

        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'mem_adr':
            address = self._get_next_word()
            self._mem_write(address, value)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            self._reg_write(register, value)

    def _add(self, instruction):
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'imm':
            src = self._get_next_word()
        elif src_type == 'mem_adr':
            address = self._get_next_word()
            src = self._mem_read(address)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            src = self._reg_read(register)

        if dst_type == 'mem_adr':
            address = self._get_next_word()
            dst = self._mem_read(address)
            dst = dst + src
            self._mem_write(address, dst)
        elif dst_type == 'reg':
            register = self._get_register((instruction & 0x000F))
            dst = self._reg_read(register)
            dst = dst + src
            self._reg_write(register, dst)
            self._update_flags(register)

    def _sub(self, instruction):
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'imm':
            src = self._get_next_word()
        elif src_type == 'mem_adr':
            address = self._get_next_word()
            src = self._mem_read(address)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            src = self._reg_read(register)

        if dst_type == 'mem_adr':
            address = self._get_next_word()
            dst = self._mem_read(address)
            dst = dst - src
            self._mem_write(address, dst)
        elif dst_type == 'reg':
            register = self._get_register((instruction & 0x000F))
            dst = self._reg_read(register)
            dst = dst - src
            self._reg_write(register, dst)
            self._update_flags(register)

    def _inc(self, instruction):
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'mem_adr':
            address = self._get_next_word()
            value = self.mem_read(address)
            self.mem_write(address, value + 1)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            value = self._reg_read(register)
            self._reg_write(register, value + 1)
            self._update_flags(register)

    def _dec(self, instruction):
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'mem_adr':
            address = self._get_next_word()
            value = self.mem_read(address)
            self.mem_write(address, value - 1)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            value = self._reg_read(register)
            self._reg_write(register, value - 1)
            self._update_flags(register)

    def _and(self, instruction):
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'imm':
            src = self._get_next_word()
        elif src_type == 'mem_adr':
            address = self._get_next_word()
            src = self._mem_read(address)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            src = self._reg_read(register)

        if dst_type == 'mem_adr':
            address = self._get_next_word()
            dst = self._mem_read(address)
            dst =  dst & src
            self._mem_write(address, dst)
        elif dst_type == 'reg':
            register = self._get_register((instruction & 0x000F))
            dst = self._reg_read(register)
            dst = dst & src
            self._reg_write(register, dst)
            self._update_flags(register)

    def _or(self, instruction):
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'imm':
            src = self._get_next_word()
        elif src_type == 'mem_adr':
            address = self._get_next_word()
            src = self._mem_read(address)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            src = self._reg_read(register)

        if dst_type == 'mem_adr':
            address = self._get_next_word()
            dst = self._mem_read(address)
            dst = dst | src
            self._mem_write(address, dst)
        elif dst_type == 'reg':
            register = self._get_register((instruction & 0x00F))
            dst = self._reg_read(register)
            dst = dst | src
            self._reg_write(register, dst)
            self._update_flags(register)

    def _not(self, instruction):
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'imm':
            src = self._get_next_word()
        elif src_type == 'mem_adr':
            address = self._get_next_word()
            src = self.mem_read(address)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            src = self._reg_read(register)

        if dst_type == 'mem_adr':
            address = self._get_next_word()
            dst = self._mem_read(address)
            self._mem_write(address, ~dst)
        elif dst_type == 'reg':
            register = self._get_register((instruction & 0x000F))
            dst = self._reg_read(register)
            self._reg_write(register, ~dst)
            self._update_flags(register)

    def _cmp(self, instruction):
        # 0000 000H 0GEL 0NZP
        src_type, dst_type = self._get_op_types(instruction)
        if src_type == 'imm':
            src = self._get_next_word()
        elif src_type == 'mem_adr':
            address = self._get_next_word()
            src = self._mem_read(address)
        elif src_type == 'reg':
            register = self._get_register((instruction & 0x00F0) >> 4)
            src = self._reg_read(register)

        if dst_type == 'mem_adr':
            address = self._get_next_word()
            dst = self._mem_read(address)
        elif dst_type == 'reg':
            register = self._get_register((instruction & 0x000F))
            dst = self._reg_read(register)

            if src < dst:
                self._update_flags(register, 0x0010)
            elif src == dst:
                self._update_flags(register, 0x0020)
            elif src > dst:
                self._update_flags(register, 0x0040)

    def _call(self, instruction):
        sub_routine = self._get_next_word()
        self._mem_write(self.registers[RSP_REG], self.registers[RIP_REG])
        self.registers[RSP_REG] += 0x1
        self.registers[RIP_REG] = sub_routine

    def _ret(self):
        self.registers[RSP_REG] -= 0x1
        self.registers[RIP_REG] = self._mem_read(self.registers[RSP_REG])

    def _jnz(self, instruction):
        flags = self.registers[RFLAG_REG]
        address = self._get_next_word()
        if (flags & 0x0002) != 0x2:
            self.registers[RIP_REG] = ushort(address)

    def _hlt(self):
        self.registers[RFLAG_REG] = self.registers[RFLAG_REG] + 0x100
