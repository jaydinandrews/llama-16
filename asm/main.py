import sys, re


class Assembler(object):
    _lines = []

    def __init__(self, asm_file):
        for line in open(asm_file, 'r'):
            self._lines.append(line.strip())

    def assemble(self):
        for line in self._lines:
            print(f'DEBUG: Line: {line}')
            if not line.startswith(';'):
                self.generate_symbol_table(line)

    # noinspection PyMethodMayBeStatic
    def generate_symbol_table(self, line):
        tokens = re.split('; |, |\s', line)
        print(tokens)


if __name__ == "__main__":
    assembler = Assembler(sys.argv[1])
    assembler.assemble()
