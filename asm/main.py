import argparse, sys
from pathlib import Path


class Assembler(object):
    line_number, pass_number, address = 0, 1, 0
    output = b''

    # the tokens per line
    label, opcode, op1, op2, comment = '', '', '', '', ''

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
        self.label, self.opcode, self.op1, self.op2, self.comment = '', '', '', '', ''

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

        # Opcode from label
        opcode_left, opcode_separator, opcode_right = op1_left.rpartition(':')
        if opcode_separator:
            self.opcode = opcode_right.strip()
            self.label = opcode_left.strip()
        else:
            opcode_left = opcode_right.rstrip()
            self.opcode = opcode_left.strip()

        # Fix when opcode ends up as first operand
        if self.opcode == '' and self.op1 != '' and self.op2 == '':
            self.opcode = self.op1.strip()
            self.op1 = ''

        self.label = self.label.lower()
        self.opcode = self.opcode.lower()
        print(f'Label: {self.label}\nOpcode: {self.opcode}\nOp1: {self.op1}\nOp2: {self.op2}\nComment: {self.comment}\n')
        return self.label, self.opcode, self.op1, self.op2, self.comment


if __name__ == "__main__":
    assembler = Assembler()
