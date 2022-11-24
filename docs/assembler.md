# 🦙🛠️ LLAMA-16 Assembler 🛠️🦙

## `./asm/core.py [-h] [-o OUTFILE] [-s] [-d] filename`

The LLAMA-16 assembler is used to translate user programs written in plain text into a machine readable binary format. The assembler has a few options that may be helpful when debugging or learning more about machine code.

##### `-h` and `--help`
The help flags displays the usage and available options when running the assembler.

##### `-o` or `--outfile`
The outout file flag is used to choose the name and path of the outputted binary file if the assembly translation process was successful. This flag requires a filename or path and filename.

The default extension of the outputted binary is `.OUT`. The default location of the outputted binary is the same as the source filename.

##### `-s` or `--symtab`
The save symbol table flag is used to save a human readable version of the symbol table generated when assembling a source file. A symbol table is a data structure used by the assembler to keep track of labels and their corresponding memory addresses.

If a symbol table was generated and used by the assembler, the saved symbol table will be saved in the same location as the outputted binary file with the `.SYM` extension.

##### `-d` or `--debug`
The debug flag is used to get a sneak peek into the process of the assembler. If the debug flag is used the following information will be printed for each line of the source file:
* A counter of the current line number
* The value of the label field
* The value of the mnemonic opcode field
* The value of the operand field
* The type of operand in the operand field
* The value of the comment field

Finally, at the end of assembling, the bytes written to the file are printed to standard output. Any ASCII values are printed as characters, otherwise the hex representation of the data is printed.

#### filename
The filename is the only required field. This should be a path to the source file to be assembled. If the path is incomplete or the file cannot be found, the assembler will still attempted to parse the file but fail with an "Unrecognized Mnemonic" error.
