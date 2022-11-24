import argparse
import sys
from pathlib import Path


class Assembler(object):
    line_number, pass_number, address = 0, 1, 0
    output = b""

    # the tokens per line
    label, mnemonic, op1, op2, comment = "", "", "", "", ""
    op1_type, op2_type, comment = "", "", ""
    symbol_table = {}

    def __init__(self):
        description = "LLAMA-16 Assembler"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("filename",
                            default="-",
                            help="input file stdin if '-'")
        # one output file
        parser.add_argument(
            "-o",
            "--outfile",
            help="output file, program.OUT is default if -o not specified",
        )
        # one for saving symbol table?
        parser.add_argument("-s",
                            "--symtab",
                            action="store_true",
                            help="save symbol table to file")
        # one for verbose option?
        parser.add_argument("-v",
                            "--verbose",
                            action="store_true",
                            help="increase output verbosity")
        args = parser.parse_args()

        if args.filename == "-":
            lines = sys.stdin.readLines()
        else:
            infile = Path(args.filename)
            with open(infile, "r") as file:
                lines = file.readlines()

        if args.filename == "-":
            outfile = args.outfile if args.outfile else "program.OUT"
            symfile = Path(args.outfile).stem + ".SYM" if args.outfile else "program.SYM"
        elif args.outfile:
            outfile = Path(args.outfile)
            symfile = Path(args.outfile).stem + ".SYM"
        else:
            outfile = Path(infile.stem + ".OUT")
            symfile = Path(infile.stem + ".SYM")

        self.assemble(lines)
        bytes_written = self.write_binary_file(outfile, self.output)
        if args.symtab:
            symbol_count = self.write_symbol_file(symfile, self.symbol_table)

        if args.verbose:
            print(f"{bytes_written} bytes written")
            if args.symtab:
                print(f"{symbol_count} symbols written")

    def write_binary_file(self, filename, binary_data):
        with open(filename, "wb") as file:
            # print(f'DEBUG OUTPUT: {binary_data}')
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
                self.parse(line)
                self.process()
        except StopIteration:
            # reach end of file
            pass

        self.pass_number = 2
        try:
            for line_number, line in enumerate(lines):
                self.parse(line)
                self.process()
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

            #print(f'Label: {self.label}\nMnemonic: {self.mnemonic}\nOp1: {self.op1}\nOp1 Type: {self.op1_type}\n'
            #      f'Op2: {self.op2}\nOp2 Type: {self.op2_type}\nComment: {self.comment}\n')
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
            elif self.op2 in ["a", "A", "b", "B", "c", "C", "d", "D"]:
                self.op2_type = "reg"
                self.op2.lower()
            else:
                self.op2_type = "label"
                self.label = self.label.lower()

        self.mnemonic = self.mnemonic.lower()
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
        elif self.mnemonic == "lea":
            self.lea()
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
            self.write_error(f'unrecognized mnemonic "{self.mnemonic}"')

    def mv(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        # 0x00 = 0
        opcode = 0
        opcode = self.encode_operand_types(opcode)
        
        print(f'DEBUG OPCODE IS: {opcode}')
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))
        self.immediate_operand()

    def inc(self):
        self.verify_ops(self.op1 != "" and self.op2 == "")
        # 0x06 = 6
        opcode = 6
        opcode = self.encode_operand_types(opcode)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))

    def dec(self):
        self.verify_ops(self.op1 != "" and self.op2 == "")
        # 0x07 = 7
        opcode = 7 + (self.register_offset(self.op1) << 3)
        self.pass_action(2, opcode.to_bytes(2, byteorder="little"))

    def cmp(self):
        self.verify_ops(self.op1 != "" and self.op2 != "")
        # 0x0B = 11
        opcode = 11 + self.register_offset(self.op2)
        self.pass_action(1, opcode.to_bytes(2, byteorder="little"))

    def jnz(self):
        self.verify_ops(self.op1 != "" and self.op2 == "")
        self.pass_action(3, b"\x00\x0d")

    def hlt(self):
        self.verify_ops(self.op1 == self.op2 == "")
        self.pass_action(1, b"\x00\x0F")

    def encode_operand_types(self, opcode):
        if self.op1_type == "imm":
            opcode += (14 << 4)
        elif self.op1_type == "reg":
            opcode += (self.register_offset(self.op1) << 4)
        elif self.op2_type == "mem":
            opcode += (15 << 4)
        elif self.op2_type == "":
            pass
        else:
            self.write_error(f'invalid operand "{self.op1}"')
        
        if self.op2_type == "imm":
            opcode += 14
        if self.op2_type == "reg":
            opcode += (self.register_offset(self.op2))
        elif self.op2_type == "mem":
            opcode += 15
        elif self.op2_type == "":
            pass
        else:
            self.write_error(f'invalid operand "{self.op2}"')
        return opcode

    def immediate_operand(self, operand_type=16):
        if (self.op1_type != "imm" or self.op2_type != "imm"):
            return
        if self.mnemonic != "cmp":
            operand = self.op1
        else: #TODO: check if second op is imm
            pass

        print(f'IMMEDIATE  HEREEEE')
        # Numerical
        if operand[0].isdigit():
            number = int(operand)
        # Label
        elif self.pass_number == 2:
            operand = operand.lower()
            if operand not in self.symbol_table:
                self.write_error(f'undefined label "{operand}"')
            number = self.symbol_table[operand]

        if self.pass_number == 2:
            operand_size = 1 if operand_type == 8 else 2
            self.output += number.to_bytes(operand_size, byteorder="little")

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
        else:
            self.write_error(f'Invalid register "{reg}"')

    def verify_ops(self, valid):
        if not valid:
            self.write_error(f'Invalid operands for mnemonic "{self.mnemonic}"')

    def write_error(self, message):
        print(f"Assembly error on line {self.line_number + 1}: {message}")
        sys.exit(1)

    def pass_action(self, size, output_byte, add_label=True):
        """On pass 1: build symbol table. On pass 2: generate code.

        Args:
            size: Number of bytes in the instruction
            output_byte: Opcode, empty binary is no output generated
            add_label: True if label should be added
        """

        if self.pass_number == 1:
            if self.label and add_label:
                self.add_label()
            self.address += size
        else:
            if output_byte != b"":
                self.output += output_byte

    def add_label(self):
        """Add label to symbol table."""
        symbol = self.label.lower()
        if symbol in self.symbol_table:
            self.write_error(f'duplicate label: "{self.label}"')
        self.symbol_table[symbol] = self.address

    def check_src(self):
        if self.op1_type == "imm":
            return 2048
        elif self.op1_type == "reg":
            return 1024
        elif self.op1_type == "mem":
            return 512
        else:
            self.write_error(f'unknown operand type: "{self.op1_type}"')

    def check_dst(self):
        if self.op1_type == "reg":
            return 128
        elif self.op1_type == "mem":
            return 64
        else:
            self.write_error(f'unknown operand type: "{self.op1_type}"')


if __name__ == "__main__":
    assembler = Assembler()
