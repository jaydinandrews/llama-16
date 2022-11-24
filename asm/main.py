import sys, re


class Assembler(object):
    _lines = []
    labels = {}

    def __init__(self, asm_file):
        for line in open(asm_file, 'r'):
            self._lines.append(line.strip())

    def assemble(self):
        self.pass_one()
        print(self.labels)

    def pass_one(self):
        for line in self._lines:
            # TODO: Replace ' ' strings with ASCII

            # Remove comments
            comment_sub = line.split(';')
            line = comment_sub[0]

            # Replace commas
            line = line.replace(',', ' ')

            # TODO: Directives?

            print(line)


if __name__ == "__main__":
    assembler = Assembler(sys.argv[1])
    assembler.assemble()
