# 🦙⌨️ LLAMA-16 ISA ⌨️🦙

## The Language
### Syntax
LLAMA-16 Assembly mimics the Intel style of instruction syntax. An instruction is made of four distinct parts: `<LABEL>: <MNEMONIC> <OPERAND> <COMMENT>`.

##### Label Field
The label field is an optional field for most instructions. It is a name used to reference the instruction's address. The label can consist of any number of ASCII characters except for a colon ( : ). A colon must follow the last character. By convention, a space should follow the colon character of the label before the mnemonic field.
Examples of valid labels include: `LABEL:`, `23F:`, `@HERE:`, `?IFZERO:`.

##### Mnemonic Field
The mnemonic field contains of a single mnemonic that represents a specific machine instruction. The instructions described later in this document are identified by a mnemonic label which must appear in this field. If the instruction uses operand(s), at least one space must follow the mnemonic before the first operand. 

##### Operand(s) Field
The operand field contains information that the defines precisely the operation to be performed by the instruction. Depending on the instruction in the mnemonic field, the operand field may consist of none, one, or two operands separated by a comma.

There are four types of information that may be required as operands: a register, immediate data, a label, or a 16-bit memory address.
* A register will be specified by specific sequence of one or two characters. There are seven user accessible registers: four general purpose and three address registers.
  * General purpose registers are referenced by: `a`, `b`, `c`, and `d`
  * The stack pointer register, referenced by `sp`, and base pointer register, referenced by `bp`, are memory registers used to access and manipulate the stack data structure.
  * Finally, the instruction pointer register is referenced by `ip`. As a general guideline, user programs will not directly modify the address in this register.
* An immediate value is a decimal value specified by a leading number sign ( # ). The number must be representable as a 16-bit signed number (values between -32768 and +32767).
* A label is a name used as a reference to an instructions address in the program. If a label is used as an operand, it must be defined exactly once somewhere else in the program.
* A 16-bit memory address has to be referenced by a 4 character hexadecimal value (addresses between 0x0000 and 0xFFFF) and should be surrounded by brackets [ ].

Each instruction has a specific set of valid operands it can use. All instructions and their variants are specified further in this document. Each instruction variant can also be found in its specified source file in the [test/asm](../test/asm) directory of the project.

##### Comment Field
The comment field is used for the programmer to document their programs or keep notes. They will be ignored by the assembler. The only rule governing this field is that it must begin with a semicolon ( ; ) and cannot consist of another semicolon.

## The Instruction Set
### Data Transfer Instruction
#### Move - `mv`
`mv [imm16/reg/mem], [reg/mem]`

The move instruction is used to transfer data between various locations where data can be stored and retrieved. Those locations include registers and memory addresses. The move instruction is also used to load immediate values into registers or memory.

### Input/Output Instruction
#### I/O - `io`
`io [reg/mem], IN` or `io [imm16/reg/mem], OUT`

LLAMA-16 uses the same instruction for both reading in input data and writing out output data.

When reading in data from standard in, data can be stored in either a register or in memory. When storing data in a register, only the first 16 bits of input will be stored while the rest will be discarded.

When writing data to standard out, data can be read from an immediate, a register, or memory. When reading data from memory to be printed out, all words will be printed until a null character is found.

***PLEASE READ THE [Quirks of LLAMA-16](./quirks.md) REGARDING HOW THE I/O INSTRUCTION TREATS DATA STORED IN REGISTERS VS MEMORY.***

### Stack Operators
A stack is First-In-Last-Out data structure used for storing temporary data accessible by the machine and the programmer. The LLAMA-16 stack starts are the address 0xDFC0 and grows upwards to address 0xFFBF.

#### Push - `push`
`push [imm16/reg/memory]`

The push instruction is used to stored data in the built in stack. When the operand is a memory address, only the data stored at this one memory address is pushed.

#### Pop - `pop`
`pop [reg/mem]`

The pop instruction is used to retrieve the top most data in the stack. That data can be stored in a register or another memory location specified by the operand.

### Arithmetic Instructions
Arithmetic instructions are used to mathematically manipulate data stored in the machine. Before you learn about the different instructions, its important to look at how LLAMA-16 represents numbers. Since LLAMA-16 has an data width of 16 bits and uses Two's Compliment to represent signed numbers, the range of numbers it can handle are between -32768 (0xFFFF) and +32767 (0x7FFF). If a number cannot be represented in 16 bits, an overflow error will occur and the machine will halt.

However, if a number can be represented in 16 bits then LLAMA-16 will operate on it, negative or positive. This means that if the result of an operation is representable in 16 bits *and* is less than -32768 or greater than +32767, the value will underflow or overflow, but still be stored as a valid value. Keep this in mind when writing your programs!

#### Addition - `add`
`add [imm16/reg/mem], [reg, mem]`

The addition instruction is used to sum two values together. The 16-bit signed number stored in the first operand will be added to the 16-bit signed number stored in the second operand and then stored in the location specified by the second operand. If the result is representable in 16-bits and is less than -32768 or greater than +32767, the value will underflow or overflow. If the result is not representable in 16 bits, the machine will halt with an overflow error. Keep this in mind when writing your programs!

#### Subtraction - `sub`
`sub [imm16/reg/mem], [reg, mem]`

The subtraction instruction is used to subtract one value from another. The 16-bit signed number stored in the first operand will subtracted from the 16-bit signed number stored in the second operand. The result will be stored in the location specified by the second operand.
#### Increment - `inc`
`inc [reg/mem]`

The increment instruction is used to add 1 to the value specified in the first and only operand. The result is stored in the same location.
#### Decrement - `dec`
`dec [reg/mem]`

The decrement instruction is used to subtract 1 from the value specified in the first and only operand. The result is stored in the same location. 

### Logical Operators
#### And - `and`
`and [imm16/reg/mem], [reg/mem]`

The and instruction conducts the logical conjunction operation on the bitwise representation of the values stored in the first and second operands. The result of that operation will be stored in the location specified by the second operand.

#### Or - `or`
`or [imm16/reg/mem], [reg/mem]`

The or instruction conducts the logical disjunction operation on the bitwise representation of the values stored in the first and second operands. The result of that operation will be stored in the location specified by the second operand.

#### Not - `not`
`not [imm16/reg/mem], [reg/mem]`

The or instruction conducts the logical negation operation on the bitwise representation of the values stored in the first operand. The result of that operation will be stored in the location specified by the second operand.

### Control Flow Instructions
#### Compare - `cmp`
`cmp [imm16/reg/mem], [reg/mem]`

The compare instruction is used to arithmetically compare two values stored in the machine specified by the operand fields. The values used are only read and not changed however the flags register is updated as a result of the compare. The compare instruction resets and loads bits 7-0 in the flags register. This includes the standard negative, zero, and positive flags but also the three additional greater, equal, and less than flags are also set.

> In the current state of development, no instructions are capable of checking the greater, equal, and less than flags. In the interim the negative, zero, and positive flags are used in the stead of the less than, equal, and greater than flags respectively.

#### Jump if Not Zero - `jnz`
`jnz [LABEL]`

The Jump if Not Zero instruction is used to transfer control to another instruction. If the Zero bit is set in the flags register, then the instruction pointer is loaded with the memory address of the label specified in the operand field. If the Zero bit is not set, then the next instruction following the `jnz` instruction is executed.

#### Call - `call`
`call [LABEL]`

The call instruction operates like a jump instruction causing a transfer of program control. Before jumping to location specific by the label operand, the next instruction's location is pushed to the stack. This allows control to be returned back to the next instruction that would have been executed after the call instruction.
#### Return - `ret`
`ret`

The return instruction pops the value currently stored on top of the stack into the instruction pointer register `ip`. This instruction is generally used to transfers program control back to the instruction following a Call Subroutine instruction.

### Halt Instruction
#### Halt - `hlt`
The halt instruction is used to set the machine into a halted state: that is, not actively interpreting program instructions.
> In the current state of the development, it is not possible for user programs to intentionally raise an error and then halt. A user program using the halt instruction will cause the emulator to exit with an "exited normally" status.

## Variable Directives
Variable directives allow a program to store values in memory before runtime. For example, these directives can be used to store initial values of variables or text prompts to be printed to the user. These directives **must** be labeled when they are declared. This allows programs to directly reference the label pointing to the data instead of the data itself. See rules on the valid labels in the [Syntax](#label-field) section of the ISA.
#### Data - `.data`
`[LABEL]: .data [imm16]`

The data directive is used to declare integer constants. These constants must be representable as a 16 bit signed integer (values ranging from -32768 to +32767). If a negative number is to be declared, it should have a leading minus sign with no spaces. Positive numbers should not have any leading signs.

Examples of valid data declarations include: `ONE: .data 1`, `NEGATIVE: .data -1`, `@VAR: .data 345`

#### String - `.string`
`[LABEL]: .string "[string]"`

The string directive is used to declare constants of character strings. The string must be between double or single quotes. If the string is to consist of double or single quotes, those marks should be escaped with a backslash `\"` or `\'`. A string can contain any number of ASCII characters within the delimited quotation marks. The only constraint if the amount of memory available for the string to be stored. Strings are stored in little endian in sequence. They are terminated with either one or two null characters represented as `0` in ASCII.  

Examples of valid string declarations include: `PROMPT: .string "Enter a number: "`, `OUTPUT: .string 'An escaped \'quote\''`.
