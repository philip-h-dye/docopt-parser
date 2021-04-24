import sys
import os
import re

from contextlib import redirect_stdout

import unittest

from pathlib import Path

from prettyprinter import cpprint as pp

from arpeggio import NonTerminal, Terminal

from docopt_parser import DocOptParserPEG
from docopt_parser import DocOptSimplifyVisitor_Pass1 as Simplify_Pass1

# import p

#------------------------------------------------------------------------------

GRAMMAR_GROUP = 'text'

GRAMMAR_BASE = 'grammar'

GRAMMAR_PATTERN = str( Path( GRAMMAR_BASE, GRAMMAR_GROUP, '{name}.peg' ) )

#------------------------------------------------------------------------------

class Test_Import ( unittest.TestCase ) :

    def setUp(self):
        pass

    #--------------------------------------------------------------------------

    def _test_string(self) :
        self.execute_passes ( 'string', 'hello', start = 'string_no_whitespace' )

    def _test_word(self) :
        self.execute_passes ( 'word', 'hello' )

    def _test_words(self) :
        self.execute_passes ( 'words', 'good morning' )

    def _test_line(self) :
        self.execute_passes ( 'line', 'good morning' )

    def test_description(self) :
        self.execute_passes ( "description", " Now  .  good men \n rise up . freedom  \n" )

    #--------------------------------------------------------------------------

    def execute_passes ( self, name, input, start=None ):
        if start is None:
            start = name

        self.grammar_file = GRAMMAR_PATTERN.replace('{name}', name)

        self.parser = DocOptParserPEG( grammar_file = self.grammar_file,
                                       start = start )

        with open("/dev/tty", "w") as tty, redirect_stdout(tty) :
            tree = self.perform_pass(0, 'raw', self.parser.parse, input )
            tree = self.perform_pass(1, 'simplify-1', Simplify_Pass1().visit, tree )

        # remove leading and trailing whitespace including newlines
        output = input.strip()
        # reduce each expanse of whitespace to a single space
        output = re.compile('[ \t]+').sub(' ', output)
        # remove spaces before of after a newline
        output = re.compile(' ?\n ?').sub('\n', output)

        expect = Terminal(self.parser.parser.parser_model, 0, value=output)

        assert tree == expect

        return tree

    def perform_pass(self, _pass, name, fcn, *args, **kwargs):
        print(f": pass {_pass} : {name}")
        out = fcn(*args, **kwargs)
        pp(out)
        print('')
        return out

#------------------------------------------------------------------------------
