import sys
import unittest
from unittest.mock import patch

from .context import asm

class AssemblerTestSuite(unittest.TestCase):
    """Assembler test cases."""

    def test_parse_args(self):
        testargs = ["core", "-o", "test/bin/fff.OUT", "./prog/basicAdd.asm"]

        with unittest.mock.patch('sys.argv', testargs):
            assembler = asm.Assembler()

if __name__ == '__main__':
    assembler = asm.Assembler()
