import argparse
import sys
import time
from pathlib import Path


class Assembler(object):
    line_number, pass_number, address = 0, 1, 0
    output = b""
    debug_mode = False
    ORIGIN = 0x4000

    # the tokens per line
    label, mnemonic, op1, op2, comment = "", "", "", "", ""
    op1_type, op2_type, comment = "", "", ""
    symbol_table = {}

    def __init__(self):
        start_time = time.time()
        description = "LLAMA-16 Assembler"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("filename",
                            default="",
                            help="input source file")
        parser.add_argument("-o",
                            "--outfile",
                            help="output file, {programName}.OUT is default if -o not specified")
        parser.add_argument("-s",
                            "--symtab",
                            action="store_true",
                            help="save symbol table to file")
        parser.add_argument("-d",
                            "--debug",
                            action="store_true",
                            help="print extra debugging information")
        args = parser.parse_args()

        if args.debug:
            self.debug_mode = True

        infile = Path(args.filename)
        with open(infile, "r") as file:
            lines = file.readlines()

        if args.outfile:
            outfile = Path(args.outfile).with_suffix(".OUT")
            if args.symtab:
                symfile = Path(args.outfile).with_suffix(".SYM")
        else:  # no outfile
            outfile = Path(args.filename).with_suffix(".OUT")
            if args.symtab:
                symfile = Path(args.filename).with_suffix(".SYM")

        self.assemble(lines)
        bytes_written = self.write_binary_file(outfile, self.output)
        if args.symtab:
            symbol_count = self.write_symbol_file(symfile, self.symbol_table)

        if args.debug:
            print(f"Writing {bytes_written} bytes to {Path(outfile)}")
            if args.symtab:
                print(f"Writing {symbol_count} symbols to {Path(symfile)}")
            print("--- Finished in %.4f seconds ---" % (time.time() - start_time))

    def write_binary_file(self, filename, binary_data):
        with open(filename, "wb") as file:
            if self.debug_mode:
                print(f'DEBUG binary output: {binary_data}')
            file.write(binary_data)
        return len(binary_data)

    def write_symbol_file(self, filename, table):
        symbol_count = len(table)
        if symbol_count == 0:
            return symbol_count

        with open(filename, "w", encoding="utf-8") as file:
            for symbol in table:
                print(f"{table[symbol]:04X} {symbol[:16].upper()}", file=file)

        return symbol_count

    def assemble(self, lines):
        self.pass_number = 1
        try:
            for line_number, line in enumerate(lines):
                if self.debug_mode:
                    print(f"Line number is {self.line_number}")
                self.parse(line)
                self.process()
                self.line_number += 1
        except StopIteration:
            # reach end of file
            pass

        self.pass_number = 2
        self.line_number = 0
        try:
            for line_number, line in enumerate(lines):
                if self.debug_mode:
                    print(f"Line number is {self.line_number}")
                self.parse(line)
                self.process()
                self.line_number += 1
        except StopIteration:
            # reach end of file
            pass

    def parse(self, line):
        """Parse and tokenize line of source code."""
        # Based on this algorithm from Brian Robert Callahan:
        # https://briancallahan.net/blog/20210410.html
        self.label, self.mnemonic, self.comment = "", "", ""
        self.op1, self.op1_type, self.op2, self.op2_type = "", "", "", ""

        preprocess = line.lstrip()  # remove leading whitespace
        preprocess = preprocess.translate({9: 32})  # replace tabs with spaces

        # Comments
        comment_left, comment_separator, comment_right = preprocess.rpartition(";")
        if comment_separator:
            self.comment = comment_right.strip()
        else:
            # If no comment, then the third argument is the remainder of the line
            # Strip whitespace as before
            comment_left = comment_right.rstrip()

        d_label, directive, d_args = self.parse_directive(comment_left)
        if directive != "":
            self.label = d_label.lower()
            self.mnemonic = directive
            self.op1 = d_args
            if directive == ".data":
                self.op1_type = "data"
            if directive == ".string":
                self.op1_type = "string"

            if self.debug_mode:
                print(f'Label: {self.label}\nMnemonic: {self.mnemonic}\nOp1: {self.op1}\nOp1 Type: {self.op1_type}\n'
                      f'Op2: {self.op2}\nOp2 Type: {self.op2_type}\nComment: {self.comment}\n')
            return (
                self.label,
                self.mnemonic,
                self.op1,
                self.op1_type,
                self.op2,
                self.op2_type,
                self.comment,
            )

        # Second operand
        op2_left, op2_separator, op2_right = comment_left.rpartition(",")
        if op2_separator:
            self.op2 = op2_right.strip()
        else:
            op2_left = op2_right.rstrip()

        # First operand
        op1_left, op1_separator, op1_right = op2_left.rpartition("\t")
        if op1_separator == "\t":
            self.op1 = op1_right.strip()
        else:
            op1_left, op1_separator, op1_right = op2_left.rpartition(" ")
            if op1_separator == " ":
                self.op1 = op1_right.strip()
            else:
                op1_left = op1_right.strip()

        # mnemonic from label
        mnemonic_left, mnemonic_separator, mnemonic_right = op1_left.rpartition(":")
        if mnemonic_separator:
            self.mnemonic = mnemonic_right.strip()
            self.label = mnemonic_left.strip()
        else:
            mnemonic_left = mnemonic_right.rstrip()
            self.mnemonic = mnemonic_left.strip()

        # Fix when mnemonic ends up as first operand
        if self.mnemonic == "" and self.op1 != "" and self.op2 == "":
            self.mnemonic = self.op1.strip()
            self.op1 = ""

        if self.op1:
            if self.op1.startswith("["):
                self.op1_type = "mem_adr"
                self.op1 = self.op1.translate({91: None, 93: None})  # Remove brackets
            elif self.op1.startswith("#"):
                self.op1_type = "imm"
                self.op1 = self.op1.translate({35: None})  # Remove number sign
            elif self.op1 in ["a", "A", "b", "B", "c", "C", "d", "D"]:
                self.op1_type = "reg"
                self.op1.lower()
            else:
                self.op1_type = "label"
                self.label = self.label.lower()

        if self.op2:
            if self.op2.startswith("["):
                self.op2_type = "mem_adr"
                self.op2 = self.op2.translate({91: None, 93: None})  # Remove brackets
            elif self.op2.startswith("#"):
                self.op2_type = "imm"
                self.op2 = self.op2.translate({35: None})  # Remove number sign
            elif self.op2 in ["a", "A", "b", "B", "c", "C", "d", "D", "ip", "IP", "sp", "SP", "bp", "BP"]:
                self.op2_type = "reg"
                self.op2.lower()
            else:
                self.op2_type = "label"
                self.label = self.label.lower()

        self.mnemonic = self.mnemonic.lower()
        if self.debug_mode:
            print(f'Label: {self.label}\nMnemonic: {self.mnemonic}\nOp1: {self.op1}\nOp1 Type: {self.op1_type}\n'
                  f'Op2: {self.op2}\nOp2 Type: {self.op2_type}\nComment: {self.comment}\n')

        return (
            self.label,
            self.mnemonic,
            self.op1,
            self.op1_type,
            self.op2,
            self.op2_type,
            self.comment,
        )

    def parse_directive(self, line):
        d_label, directive, d_args = "", "", ""
        left1, sep1, right1 = line.partition(".data")
        d_type = ".data"
        if sep1 == "":
            left1, sep1, right1 = line.partition(".string")
            d_type = ".string"
        if sep1 == "":
            return d_label, directive, d_args

        directive = d_type
        d_args = right1.strip()

        left2, sep2, right2 = left1.partition(":")
        if sep2 == ":":
            left2 = left2.strip()
            if not left2.isalnum() or left2[0].isdigit():
                self.write_error(f'Invalid label "{left2}"')
            d_label = left2
        elif sep2 != ":" and left2.strip() != "":
            self.write_error(f'Invalid label "{left2}"')

        return d_label, directive, d_args

    def process(self):
        if self.mnemonic == self.op1 == self.op2 == "":
            self.pass_action(0, b"")
            return

        if self.mnemonic == "mv":
            self.mv()
        elif self.mnemonic == "io":
            self.io()
        elif self.mnemonic == "push":
            self.push()
        elif self.mnemonic == "pop":
            self.pop()
        elif self.mnemonic == "add":
            self.add()
        elif self.mnemonic == "sub":
            self.sub()
        elif self.mnemonic == "inc":
            self.inc()
        elif self.mnemonic == "dec":
            self.dec()
        elif self.mnemonic == "and":
            self.mnemonic_and()
        elif self.mnemonic == "or":
            self.mnemonic_or()
        elif self.mnemonic == "not":
            self.mnemonic_not()
        elif self.mnemonic == "cmp":
            self.cmp()
        elif self.mnemonic == "call":
            self.call()
        elif self.mnemonic == "jnz":
            self.jnz()
        elif self.mnemonic == "ret":
            self.ret()
        elif self.mnemonic == "hlt":
            self.hlt()
        elif self.mnemonic == ".data":
            self.directive_data()
        elif self.mnemonic == ".string":
            self.directive_string()
        else:
            self.write_error(f'Unrecognized mnemonic "{self.mnemonic}"')

    def mv(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        # 0x00 = 0
        opcode = 0
        opcode = self.encode_operand_types(opcode, 2)

        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()
        self.memory_address()

    def io(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        if self.op1_type == 'imm' and (self.op2 == 'in' or self.op2 == 'IN'):
            self.write_error("Cannot read word into an immediate.")
        # 0x01 = 1
        opcode = 1
        # encode just the data type, IN/OUT will be encoding next
        opcode = self.encode_operand_types(opcode, 1)
        if self.op2 == 'in' or self.op2 == 'IN':
            opcode += 0x1
        elif self.op2 == 'out' or self.op2 == 'OUT':
            opcode += 0x2
        else:
            self.write_error(f"Error parsing io port. {self.op2} is not a valid port, use IN or OUT.")

        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()
        self.memory_address()

    def push(self):
        self.verify_ops(self.op1 != "" and self.op2 == "")
        # 0x02 = 2
        opcode = 2
        opcode = self.encode_operand_types(opcode, 1)

        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()
        self.memory_address()

    def pop(self):
        self.verify_ops(self.op1 != "" and self.op2 == "")
        # 0x03 = 3
        opcode = 3
        opcode = self.encode_operand_types(opcode, 1)

        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.memory_address()

    def add(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        # 0x04 = 4
        opcode = 4
        opcode = self.encode_operand_types(opcode, 2)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()
        self.memory_address()

    def sub(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        # 0x05 = 5
        opcode = 5
        opcode = self.encode_operand_types(opcode, 2)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()
        self.memory_address()

    def inc(self):
        self.verify_ops(self.op1 != "" and self.op2 == "")
        # 0x06 = 6
        opcode = 6
        opcode = self.encode_operand_types(opcode, 1)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))

    def dec(self):
        self.verify_ops(self.op1 != "" and self.op2 == "")
        # 0x07 = 7
        opcode = 7
        opcode = self.encode_operand_types(opcode, 1)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))

    def mnemonic_and(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        # 0x08 = 8
        opcode = 8
        opcode = self.encode_operand_types(opcode, 2)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()
        self.memory_address()

    def mnemonic_or(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        # 0x08 = 9
        opcode = 9
        opcode = self.encode_operand_types(opcode, 2)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()
        self.memory_address()

    def mnemonic_not(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        # 0x0A = 10
        opcode = 10
        opcode = self.encode_operand_types(opcode, 2)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()
        self.memory_address()

    def cmp(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        # 0x0B = 11
        opcode = 11
        opcode = self.encode_operand_types(opcode, 2)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()
        self.memory_address()

    def call(self):
        self.verify_ops(self.op1 != "" and self.op2 == "")
        # 0x0C = 12
        opcode = 12
        opcode = self.encode_operand_types(opcode, 1)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()

    def jnz(self):
        self.verify_ops(self.op1 != "" and self.op2 == "")
        opcode = 13
        opcode = self.encode_operand_types(opcode, 1)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()

    def ret(self):
        self.verify_ops(self.op1 == "" and self.op2 == "")
        # 0x0E = 14
        self.pass_action(2, b"\x00\xE0")

    def hlt(self):
        self.verify_ops(self.op1 == self.op2 == "")
        self.pass_action(2, b"\x00\xF0")

    def directive_data(self):
        if self.label == "":
            self.write_error(".data and .string directives must be labeled")
        self.verify_ops(self.op1 != "" and self.op2 == "")

        try:
            data = int(self.op1)
            self.pass_action(2, data.to_bytes(2, byteorder="little", signed=True))
        except ValueError:
            self.write_error(f"Error reading \"{self.op1}\", not an integer")

    def directive_string(self):
        if self.label == "":
            self.write_error(".data and .string directives must be labeled")
        self.verify_ops(self.op1 != "" and self.op2 == "")

        string = self.op1
        string = string.strip('\"').strip('\'')
        if len(string) % 2 != 0:
            string += '\0'
        else:
            string += '\0\0'
        data = bytes(string, encoding='utf-8')
        self.pass_action(len(data), data)

    def encode_operand_types(self, opcode, num_ops):
        opcode = opcode << 12
        if self.op1_type == "imm":
            opcode += (14 << 4)
        elif self.op1_type == "reg":
            opcode += (self.register_offset(self.op1) << 4)
        elif self.op1_type == "mem_adr" or self.op1_type == "label":
            if self.debug_mode:
                print(f"DEBUG: Symbol table: {self.symbol_table}")
            opcode += (15 << 4)
        elif self.op2_type == "":
            pass
        else:
            self.write_error(f'Invalid operand "{self.op1}"')

        if num_ops == 1:
            return opcode

        if self.op2_type == "reg":
            opcode += (self.register_offset(self.op2))
        elif self.op2_type == "mem_adr" or self.op2_type == "label":
            if self.debug_mode:
                print(f"DEBUG: Symbol table: {self.symbol_table}")
            opcode += 15
        elif self.op2_type == "":
            pass
        else:
            self.write_error(f'Invalid operand "{self.op2}"')
        return opcode

    def immediate_operand(self):
        # This function also handles LABEL operands. Should this be its own function
        # for ease of readablity and debugging?
        if (self.op1_type != "imm" and self.op1_type != "label"):
            return

        operand = self.op1
        self.address += 1

        # Numerical
        if operand[0].isdigit():
            number = int(operand)
        elif operand.startswith('-'):
            number = int(operand)
        # Label
        elif self.pass_number == 2:
            operand = operand.lower()
            if operand not in self.symbol_table:
                self.write_error(f'Undefined label "{operand}"')
            number = int(self.symbol_table[operand])

        if self.pass_number == 2:
            self.pass_action(2, number.to_bytes(2, byteorder="little", signed=True))

    def memory_address(self):
        if self.op1_type == "mem_adr":
            operand = self.op1
            self.address += 1

            if operand[0].isdigit():
                number = int(operand, 16)
            else:
                number = self.symbol_table.get(operand.lower(), -1)
                if self.pass_number == 2 and number < 0:
                    self.write_error(f"Undefined label \"{operand}\"")

            if self.pass_number == 2:
                self.pass_action(2, number.to_bytes(2, byteorder="little"))

        if self.op2_type == "mem_adr":
            operand = self.op2
            self.address += 1

            if operand[0].isdigit():
                number = int(operand, 16)
            else:
                number = self.symbol_table.get(operand.lower(), -1)
                if self.pass_number == 2 and number < 0:
                    self.write_error(f"Undefined label \"{operand}\"")

            if self.pass_number == 2:
                self.pass_action(2, number.to_bytes(2, byteorder="little"))

    def register_offset(self, reg_in):
        reg = reg_in.lower()
        if reg == "a":
            return 0
        elif reg == "b":
            return 1
        elif reg == "c":
            return 2
        elif reg == "d":
            return 3
        elif reg == "ip":
            return 4
        elif reg == 'sp':
            return 5
        elif reg == 'bp':
            return 6
        else:
            self.write_error(f'Invalid register "{reg}"')

    def verify_ops(self, valid):
        if not valid:
            self.write_error(f'Invalid operands for mnemonic "{self.mnemonic}"')

    def write_error(self, message):
        print(f"Assembly error on line {self.line_number + 1}: {message}")
        if self.debug_mode:
            print(f"DEBUG: Current address: {self.address}\nDEBUG: Current symbol table: {self.symbol_table}")
        sys.exit(1)

    def pass_action(self, size, output_byte):
        """On pass 1: build symbol table. On pass 2: generate code.

        Args:
            size: Number of bytes in the instruction
            output_byte: Opcode, empty binary is no output generated
        """
        align = size % 2

        if self.pass_number == 1:
            if self.label:
                self.add_label()
            self.address += int(size/2) + align
        else:
            if output_byte != b"":
                self.output += output_byte

    def add_label(self):
        """Add label to symbol table."""
        symbol = self.label.lower()
        if symbol in self.symbol_table:
            self.write_error(f'Duplicate label: "{self.label}"')
        self.symbol_table[symbol] = self.address + self.ORIGIN


if __name__ == "__main__":
    assembler = Assembler()
