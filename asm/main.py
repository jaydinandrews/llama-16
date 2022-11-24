import argparse
import sys
from pathlib import Path


class Assembler(object):
    line_number, pass_number, address = 0, 1, 0
    output = b''

    # the tokens per line
    label, mnemonic, op1, op1_type, op2, op2_type, comment = '', '', '', '', '', '', ''
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

        self.pass_number = 2
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
        self.label, self.mnemonic, self.comment = '', '', ''
        self.op1, self.op1_type, self.op2, self.op2_type = '', '', '', ''

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

        d_label, directive, d_args = self.parse_directive(comment_left)
        if directive != '':
            self.label = d_label.lower()
            self.mnemonic = directive
            self.op1 = d_args
            if directive == '.data':
                self.op1_type = 'data'
            if directive == '.string':
                self.op1_type = 'string'

            print(f'Label: {self.label}\nMnemonic: {self.mnemonic}\nOp1: {self.op1}\nOp1 Type: {self.op1_type}\n'
                  f'Op2: {self.op2}\nOp2 Type: {self.op2_type}\nComment: {self.comment}\n')
            return self.label, self.mnemonic, self.op1, self.op1_type, self.op2, self.op2_type, self.comment

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

        if self.op1:
            if self.op1.startswith('['):
                self.op1_type = 'mem_adr'
                self.op1 = self.op1.translate({91: None, 93: None})  # Remove brackets
            elif self.op1.startswith('#'):
                self.op1_type = 'imm'
                self.op1 = self.op1.translate({35: None})  # Remove number sign
            elif self.op1 in ['a', 'A', 'b', 'B', 'c', 'C', 'd', 'D']:
                self.op1_type = 'reg'
                self.op1.lower()
            else:
                self.op1_type = 'label'
                self.label = self.label.lower()

        if self.op2:
            if self.op2.startswith('['):
                self.op2_type = 'mem_adr'
                self.op2 = self.op2.translate({91: None, 93: None})  # Remove brackets
            elif self.op2.startswith('#'):
                self.op2_type = 'imm'
                self.op2 = self.op2.translate({35: None})  # Remove number sign
            elif self.op2 in ['a', 'A', 'b', 'B', 'c', 'C', 'd', 'D']:
                self.op2_type = 'reg'
                self.op2.lower()
            else:
                self.op2_type = 'label'
                self.label = self.label.lower()

        self.mnemonic = self.mnemonic.lower()
        print(f'Label: {self.label}\nMnemonic: {self.mnemonic}\nOp1: {self.op1}\nOp1 Type: {self.op1_type}\n'
              f'Op2: {self.op2}\nOp2 Type: {self.op2_type}\nComment: {self.comment}\n')
        return self.label, self.mnemonic, self.op1, self.op1_type, self.op2, self.op2_type, self.comment

    def parse_directive(self, line):
        d_label, directive, d_args = '', '', ''
        left1, sep1, right1 = line.partition('.data')
        d_type = '.data'
        if sep1 == '':
            left1, sep1, right1 = line.partition('.string')
            d_type = '.string'
        if sep1 == '':
            return d_label, directive, d_args

        directive = d_type
        d_args = right1.strip()

        left2, sep2, right2 = left1.partition(':')
        if sep2 == ':':
            left2 = left2.strip()
            if not left2.isalnum() or left2[0].isdigit():
                self.write_error(f'Invalid label "{left2}"')
            d_label = left2
        elif sep2 != ':' and left2.strip() != '':
            self.write_error(f'Invalid label "{left2}"')

        return d_label, directive, d_args

    def process(self):
        if self.mnemonic == self.op1 == self.op2 == '':
            self.pass_action(0, b'')
            return

        if self.mnemonic == 'mv':
            self.mv()
        elif self.mnemonic == 'lea':
            self.lea()
        elif self.mnemonic == 'push':
            self.push()
        elif self.mnemonic == 'pop':
            self.pop()
        elif self.mnemonic == 'add':
            self.add()
        elif self.mnemonic == 'sub':
            self.sub()
        elif self.mnemonic == 'inc':
            self.inc()
        elif self.mnemonic == 'dec':
            self.dec()
        elif self.mnemonic == 'and':
            self.mnemonic_and()
        elif self.mnemonic == 'or':
            self.mnemonic_or()
        elif self.mnemonic == 'not':
            self.mnemonic_not()
        elif self.mnemonic == 'cmp':
            self.cmp()
        elif self.mnemonic == 'call':
            self.call()
        elif self.mnemonic == 'jnz':
            self.jnz()
        elif self.mnemonic == 'ret':
            self.ret()
        elif self.mnemonic == 'hlt':
            self.hlt()
        elif self.mnemonic == '.data':
            self.directive_data()
        elif self.mnemonic == '.string':
            self.directive_string()
        else:
            self.write_error(f'unrecognized mnemonic "{self.mnemonic}"')

    def verify_ops(self, valid):
        if not valid:
            self.write_error(f'Invalid operands for mnemonic "{self.mnemonic}"')

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

    # x00
    # mv [imm16/reg/mem], [reg/mem]
    def mv(self):
        self.verify_ops(self.op1 != '' and self.op2 != '')
        src_type = self.check_src()
        dst_type = self.check_dest()

    def check_src(self):
        if self.op1_type == 'imm':
            return 2048
        elif self.op1_type == 'reg':
            return 1024
        elif self.op1_type == 'mem':
            return 512
        else:
            self.write_error(f'unknown operand type: "{self.op1_type}"')

    def check_dst(self):
        if self.op1_type == 'reg':
            return 128
        elif self.op1_type == 'mem':
            return 64
        else:
            self.write_error(f'unknown operand type: "{self.op1_type}"')


if __name__ == "__main__":
    assembler = Assembler()
