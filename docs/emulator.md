# 🦙🛠️ LLAMA-16 Assembler 🛠️🦙

## `./emu/core.py [-h] [-d] program`

The LLAMA-16 assembler is used to translate user programs written in plain text into a machine readable binary format. The assembler has a few options that may be helpful when debugging or learning more about machine code.

##### `-h` and `--help`
The help flags displays the usage and available options when running the assembler.

##### `-d` or `--debug`
The debug flag is used to get a sneak peek into the process of the emulator. If the debug flag a snapshot of the current CPU state is printed to the screen. That information includes:
* The value of the four general purpose registers
* The address stored in the instruction pointer register
* The addresses stored in the stack and base pointer registers
* The current flags that are set
* The type of operand in the operand field
* The value of the comment field

Finally, at the end of emulation when the halt flag is set, one final ending state snapshot is printed to the screen as well as a memory map of any *non-zero* values stored in memory.

#### program
The program name is the only required field. This should be a path to the program file to be run. If the path is incomplete or the file cannot be found, the emulator will still attempted to run file by loading the binary contents of the file into memory and run the commands. Of course, this will more than likely not run anything sensible and will run forever. If you encounter this infinity loop with a program you compiled, you might be missing a `hlt` instruction.
