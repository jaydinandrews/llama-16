import argparse
import sys
from pathlib import Path


class Assembler(object):
    line_number, pass_number, address = 0, 1, 0
    output = b''

    # the tokens per line
    label, mnemonic, op1, op2, comment = '', '', '', '', ''

    symbol_table = {}

    def __init__(self):
        description = f'LLAMA-16 Assembler'
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('filename', default='-', help='input file stdin if \'-\'')
        # one output file
        # one for saving symbol table?
        # one for verbose option?
        args = parser.parse_args()

        in_file = Path(args.filename)
        with open(in_file, 'r') as file:
            lines = file.readlines()

        self.assemble(lines)

    def assemble(self, lines):
        self.pass_number = 1
        try:
            for line_number, line in enumerate(lines):
                self.parse(line)
        except StopIteration:
            # reach end of file
            pass

    def parse(self, line):
        """Parse and tokenize line of source code."""
        # Based on this algorithm from Brian Robert Callahan:
        # https://briancallahan.net/blog/20210410.html
        self.label, self.mnemonic, self.op1, self.op2, self.comment = '', '', '', '', ''

        preprocess = line.lstrip()  # remove leading whitespace
        preprocess = preprocess.translate({9: 32})  # replace tabs with spaces

        # Comments
        comment_left, comment_separator, comment_right = preprocess.rpartition(';')
        if comment_separator:
            self.comment = comment_right.strip()
        else:
            # If no comment, then the third argument is the remainder of the line
            # Strip whitespace as before
            comment_left = comment_right.rstrip()

        # TODO: directives .data and .string

        # Second operand
        op2_left, op2_separator, op2_right = comment_left.rpartition(',')
        if op2_separator:
            self.op2 = op2_right.strip()
        else:
            op2_left = op2_right.rstrip()

        # First operand
        op1_left, op1_separator, op1_right = op2_left.rpartition('\t')
        if op1_separator == '\t':
            self.op1 = op1_right.strip()
        else:
            op1_left, op1_separator, op1_right = op2_left.rpartition(' ')
            if op1_separator == ' ':
                self.op1 = op1_right.strip()
            else:
                op1_left = op1_right.strip()

        # mnemonic from label
        mnemonic_left, mnemonic_separator, mnemonic_right = op1_left.rpartition(':')
        if mnemonic_separator:
            self.mnemonic = mnemonic_right.strip()
            self.label = mnemonic_left.strip()
        else:
            mnemonic_left = mnemonic_right.rstrip()
            self.mnemonic = mnemonic_left.strip()

        # Fix when mnemonic ends up as first operand
        if self.mnemonic == '' and self.op1 != '' and self.op2 == '':
            self.mnemonic = self.op1.strip()
            self.op1 = ''

        self.label = self.label.lower()
        self.mnemonic = self.mnemonic.lower()
        # DEBUG: print(f'Label: {self.label}\nMnemonic: {self.mnemonic}\n'
        #      f'Op1: {self.op1}\nOp2: {self.op2}\nComment: {self.comment}\n')
        return self.label, self.mnemonic, self.op1, self.op2, self.comment

    def process(self):
        if self.mnemonic == self.op1 == self.op2 == '':
            self.pass_action(0, b'')
            return

        if self.mnemonic == 'mv':
            pass
        elif self.mnemonic == 'lea':
            pass
        elif self.mnemonic == 'push':
            pass
        elif self.mnemonic == 'pop':
            pass
        elif self.mnemonic == 'add':
            pass
        elif self.mnemonic == 'sub':
            pass
        elif self.mnemonic == 'inc':
            pass
        elif self.mnemonic == 'dec':
            pass
        elif self.mnemonic == 'and':
            pass
        elif self.mnemonic == 'or':
            pass
        elif self.mnemonic == 'not':
            pass
        elif self.mnemonic == 'cmp':
            pass
        elif self.mnemonic == 'call':
            pass
        elif self.mnemonic == 'jnz':
            pass
        elif self.mnemonic == 'ret':
            pass
        elif self.mnemonic == 'hlt':
            pass
        else:
            self.write_error(f'unrecognized mnemonic "{self.mnemonic}"')

    def write_error(self, message):
        print(f'Assembly error on line {self.line_number + 1}: {message}')
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
            if output_byte != b'':
                self.output += output_byte

    def add_label(self):
        """Add label to symbol table."""
        symbol = self.label.lower()
        if symbol in self.symbol_table:
            self.write_error(f'duplicate label: "{self.label}"')
        self.symbol_table[symbol] = self.address


if __name__ == "__main__":
    assembler = Assembler()
