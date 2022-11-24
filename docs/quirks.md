# 🦙⚠️ Quirks of LLAMA-16 ⚠️🦙

LLAMA-16 is far from completion. This project is the product of one (1) overworked and underpaid undergraduate. As a result, some features of LLAMA-16 seem counterintuitive. This document was made to address some of the quirks and kinks of this project.

> NOTE: This is not a list of current bugs or issues of this project. It is intended to be used as a reference of some of the tricks that need to be deployed when writing, assembling, and testing programs. If you've found a bug, please check out the sections addressing issues in the main [wiki page](./llama.md).

## Endianness
While LLAMA-16 might look like a big endian system it is actually a *middle-endian* machine. Since memory addresses and registers can each hold a total of 16 bits (2 bytes), when writing a sequence of 8-bit characters (1 byte) each 16-bit word is stored big endian but within each word the bytes are ordered little endian.

For an example, what would the string 'kayak' look like in memory?

```
ascii:  k  a  y  a  k
hex:    6B 61 79 61 6B
```
On a big-endian 16-bit machine this would look like: `0x6B61 0x7961 0x6B00`
However, LLAMA-16 is a *middle-endian* machine. The string is stored with the first character is lower addresses and the last in the higher addresses **but** within each 16-bit word the bytes are stored little endian:
```
increasing addresses →
-------------------------------
.. | 61 6B | 61 79 | 00 6B | ..
-------------------------------
```

## Using the `io` Instruction
When working with user defined data, there are a few things to keep in mind when using the `io` instruction, namely its important to understand how LLAMA-16 interprets ASCII characters. You see, LLAMA-16 is not very smart often cannot differentiate between regular integers and integers representing ASCII codes.

This means that when using the `io` instruction LLAMA-16 treats any data stored in registers as pure integers. This means that even though the instruction `io a, IN` can accept a string of ASCII characters, only *values* of the first two characters will be stored in register `a` **in little endian**.

The inverse is also true: when using the `io` instruction LLAMA-16 treats all values stored in memory as characters. This means that when reading data from memory to be printed, the string of characters starting at the specified address up until a zero null terminator character is read.

To work around this here are some tips:
* When trying to print numbers, move them into a register and then print from the register.
* When trying to print one character, load it into memory with a zero null character terminator first (remember characters are stored little endian).
* When trying to print a string of characters, make sure that there is a zero null character at the end to mark the termination of the string.

## Forgetting a `hlt` instruction
If there is not `hlt` instruction in a program, then the emulator will continue to grab the next word in memory and attempt to execute it. Since `0000` maps to the instruction `mv a, 0`, the emulator will continuously attempt to move zero into register a over and over again in an infinite loop.

### Found something *not* referenced in this document?
Think you stumbled across a bug or unintended behavior of the project? Congrats and welcome to the club! Now get in line... 

Jokes aside, yes there are bugs in this project. If you've found one, please check to see if there is an open issue addressing it. If not, open a new one! Check out the Issues and Contributing sections of the [wiki page](./llama.md).
