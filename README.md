# 🦙 LLAMA-16 🦙

Have you ever cried while trying to implement a recursive fibonacci calculator in x86_64 assembly? Have you tried to take your exploration of computer science closer to the metal only to learn that abstraction is actually a protector of your mental well being? Have you ever tried programming in LC-3 assembly and begrudgingly learned how to manually implement a stack with arithmetic operators?

If you answered yes to any of the previous questions, you might be entitled to compensation from Kernighan and Ritchie. While I am not sure how to get that, I can at least offer you a potentially more enjoyable manner of exploring system level architectures with the LLAMA-16.

LLAMA-16 is a 16 bit micro-architecture designed with simplicity in mind. The project consists primarily of an assembler and an emulator. First, you can use the assembler to convert your artisan hand crafted code into a binary format that the machine can read. Then, you can feed your state of the art bug-free programs to the emulator which will execute the program in a virtual environment.

## Design Specifications ([spec](./SPEC.txt))
#### Features
* 8 16-bit registers (4 normal, 3 address, 1 flags)
* 16-bit address bus (65536 16-bit words = a massive 64 KiB of memory)
* 16 instruction RISC architecture
* "Memory mapped" I/O for user interaction*

\*Since the machine is emulated entirely virtually, the `io` instruction reads and writes data to the memory mapped location and then promptly manipulates it. While the design is to be memory mapped, in the virtual space it's difficult not to shortcut.

#### Instruction Set:

```
0: MV   [imm16/reg/mem], [reg/mem]       -> [reg/mem] = [imm16/reg/mem]
1: IO   [imm16/reg/mem], [IN/OUT]        -> [reg/mem] = IN ; OUT = [imm16/reg/mem]
2: PUSH [imm16/reg/mem]                  -> [SP++] = [imm16/reg/mem]
3: POP  [reg/mem]                        -> reg = [SP--]
4: ADD^ [imm16/reg/mem], [reg/mem]       -> [reg/mem] = [rem/mem] + [imm16/reg/mem]
5: SUB^ [imm16/reg/mem], [reg/mem]       -> [reg/mem] = [reg/mem] - [imm16/reg/mem]
6: INC^ [reg/mem]                        -> [reg/mem] = [reg/mem]++
7: DEC^ [reg/mem]                        -> [reg/mem] = [reg/mem]--
8: AND^ [imm16/reg/mem], [reg/mem]       -> [reg/mem] = [reg/mem] & [imm16/reg/mem]
9: OR^  [imm16/reg/mem], [reg/mem]       -> [reg/mem] = [reg/mem] | [imm16/reg/mem]
A: NOT^ [imm16/reg/mem], [reg/mem]       -> [reg/mem] = ~([imm16/reg/mem])
B: CMP* [imm16/reg/mem], [reg/mem]       -> f = compare reg, [imm16/reg/mem]
C: CALL [LABEL]                          -> [SP++] = IP; IP = [mem of LABEL]
D: JNZ  [LABEL]                          -> IP = [mem of LABEL/reg/mem] if f != zero
E: RET                                   -> IP = [SP--]
F: HLT                                   -> f_halt = true

^These instructions read and load the flags register.
*cmp has its own set of flags: greater, equal, and less. In the current state of the project,
 no other instruction can check these flags so the positive, zero, and negative flags are used
 instead.
```
#### Registers:
```
0: A  General Purpose Register
1: B  General Purpose Register
2: C  General Purpose Register
3: D  General Purpose Register
4: IP Instruction Pointer Register
5: SP Stack Pointer Register
6: BP Base Pointer Register
7: F  Flags Register:
        15-7: Unused
        8: HALT
        7: Unused
        6: GREATER
        5: EQUAL
        4: LESS
        3: Unused
        2: NEGATIVE
        1: ZERO
        0: POSITIVE
```

## Installing
#### Requirements
LLAMA-16 is written in standard library Python version >=3.6. No additional modules or packages are required.
## The Tool Suite
#### Assembler ([asm](./docs/asm.md))
`./asm/core.py [-h] [-o OUTFILE] [-s] [-d] filename`

#### Emulator ([emu](./docs/emu.md))
`./emu/core.py [-h] [-d] program`
