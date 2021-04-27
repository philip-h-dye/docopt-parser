import sys
import os
import re

from contextlib import redirect_stdout

import unittest

# from pathlib import Path

from prettyprinter import cpprint as pp

# from arpeggio import NonTerminal, Terminal
from arpeggio import ParserPython

# import p

#------------------------------------------------------------------------------

from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF, \
        ParserPython, PTNodeVisitor, visit_parse_tree
from arpeggio import RegExMatch as _

#------------------------------------------------------------------------------

sys.path.insert(0, 'canonical')

from operand import grammar as operand_grammar

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    kwargs['file'] = tprint._tty
    print(*args, **kwargs)

tprint._tty = open("/dev/tty", 'w')

#------------------------------------------------------------------------------

class Test_Import ( unittest.TestCase ) :

    def setUp(self):
        self.parser = ParserPython(operand_grammar)

    #--------------------------------------------------------------------------

    def tearDown(self):
        pass

    #--------------------------------------------------------------------------

    def test_angled (self) :
        input = "<angled-operand>"
        self.parse_tree = self.parser.parse(input)
        tprint(self.parse_tree.tree_str(), "\n")
        assert True

    def test_all_caps (self) :
        input = "FILE"
        self.parse_tree = self.parser.parse(input)
        tprint(self.parse_tree.tree_str(), "\n")
        assert True

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
