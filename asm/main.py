import sys, re


class Assembler(object):
    _lines = []

    def __init__(self, asm_file):
        for line in open(asm_file, 'r'):
            self._lines.append(line.strip())

    def assemble(self):
        for line in self._lines:
            line = self.remove_comments(line)  # Clean input file
            print(line)

    # noinspection PyMethodMayBeStatic
    def remove_comments(self, line):
        comment_sub = line.split(';')
        line = comment_sub[0]
        return line


if __name__ == "__main__":
    assembler = Assembler(sys.argv[1])
    assembler.assemble()
