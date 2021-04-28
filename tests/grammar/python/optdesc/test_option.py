import unittest

from arpeggio import ParserPython, NonTerminal, Terminal
from arpeggio import Sequence, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _

from prettyprinter import cpprint as pp
import p

#------------------------------------------------------------------------------

from docopt_parser.parsetreenodes import NonTerminal_eq_structural

from grammar.python.common import ws
from grammar.python.operand import *
from grammar.python.option import *

#------------------------------------------------------------------------------

from docopt_parser import DocOptParserPEG
from docopt_parser import DocOptSimplifyVisitor_Pass1 as Simplify_Pass1
from docopt_parser import DocOptSimplifyVisitor_Pass2 as Simplify_Pass2

#------------------------------------------------------------------------------

def grammar():
    return Sequence( OneOrMore ( [ long_no_arg, short_no_arg, ws ] ),
                     EOF, rule_name='grammar', skipws=False )

#------------------------------------------------------------------------------
    
class Test_Import ( unittest.TestCase ) :

    def setUp(self):

        self.parser = ParserPython(grammar, reduce_tree=True)

        # quiet, no parse trees displayed
        # self.debug = False

        # show parse tree for pass >= self.debug
        self.debug = 2

        # self.each = True
        self.show = True

        # # tprint._file =
        # self.tty = open("/dev/tty", 'w')

        # self.rstdout = redirect_stdout(self.tty)
        # self.rstdout.__enter__()

        tprint._on = self.show or self.debug is not False

    #--------------------------------------------------------------------------

    def tearDown(self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

    #--------------------------------------------------------------------------

    def single( self, rule, value ):
        parsed = self.parser.parse(value)
        # tprint("\n", parsed.tree_str(), "\n")
        # print('') ; pp(parsed)
        p_operand = Terminal(rule(), 0, value)
        p_eof = Terminal(EOF(), 0, '')
        expect = NonTerminal(grammar(), [ p_operand, p_eof ])
        assert NonTerminal_eq_structural(parsed, expect)

    def SKIP_test_angled_single (self) :
        self.single(operand_angled, "<angled-operand>")

    def SKIP_test_all_caps_single (self) :
        self.single(operand_all_caps, "FILE")

    #--------------------------------------------------------------------------

    def thrice( self, rule, value ):
        n_times = 3
        input = ( value + ' ') * n_times
        parsed = self.parser.parse(input)
        # print('') ; pp(parsed)
        p_operand = Terminal(rule(), 0, value)
        p_ws = Terminal(ws(), 0, ' ')
        elements = ( p_operand, p_ws ) * n_times
        p_eof = Terminal(EOF(), 0, '')
        expect = NonTerminal(grammar(), [ *elements, p_eof ])
        assert NonTerminal_eq_structural(parsed, expect)

    def SKIP_test_angled_thrice (self) :
        self.thrice(operand_angled, "<angled-operand>")

    def SKIP_test_all_caps_thrice (self) :
        self.thrice(operand_all_caps, "FILE")

    #--------------------------------------------------------------------------

    def SKIP_test_mixed (self) :
        input = ' <a> <b> CC <d> EE '
        #
        input = input.strip()
        parsed = self.parser.parse(input)
        #
        inputs = input.split()
        p_ws = Terminal(ws(), 0, ' ')
        elements = [ ]
        for value in inputs :
            rule = operand_angled if value[0] == '<' else operand_all_caps
            elements.append ( Terminal(rule(), 0, value) )
            elements.append ( p_ws )
        if len(elements) > 0:
            del elements[-1]
        p_eof = Terminal(EOF(), 0, '')
        expect = NonTerminal(grammar(), [ *elements, p_eof ])
        assert NonTerminal_eq_structural(parsed, expect)

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    if tprint._on :
        kwargs['file'] = tprint._file
        print(*args, **kwargs)

tprint._file = open("/dev/tty", 'w')

tprint._on = False

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
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
from docopt_parser import DocOptSimplifyVisitor_Pass2 as Simplify_Pass2

# import p

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    if tprint._on :
        # kwargs['file'] = tprint._file
        print(*args, **kwargs)

# tprint._file = sys.stdout
tprint._on = False

#------------------------------------------------------------------------------

GRAMMAR_GROUP = 'option'

GRAMMAR_BASE = 'grammar'

GRAMMAR_PATTERN = str( Path( GRAMMAR_BASE, GRAMMAR_GROUP, '{name}.peg' ) )

#------------------------------------------------------------------------------

class Test_Import ( unittest.TestCase ) :

    # In the grammar, options expect to be preceeded by whitespace (i.e. '&ws).
    # Certainly, resolving this in the grammar would be trivial using an alternate
    # regular expression with '^'.  But these isolated grammars are intended to
    # in whole up to the next level.  Requiring any changes during that process
    # would defeat our central goal.
    #
    # So, equally trivial, prefix each input with 'ws' prior to parsing.
    ws = ' '

    #--------------------------------------------------------------------------

    def setUp(self):

        # quiet, no parse trees displayed
        # self.debug = False

        # show parse tree for pass >= self.debug
        self.debug = 2

        # self.each = True
        self.show = True

        # tprint._file =
        self.tty = open("/dev/tty", 'w')

        # self.rstdout = redirect_stdout(self.tty)
        # self.rstdout.__enter__()

        tprint._on = self.show or self.debug is not False

    #--------------------------------------------------------------------------

    def tearDown(self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

    #--------------------------------------------------------------------------

    # ✓

    def SKIP_test_short_no_arg(self) :
        self.execute_passes ( 'short', '-l', start='option' )

    def SKIP_test_short_stacked_lowercase(self) :
        self.execute_passes ( 'short', '-cvf', start='option' )

    def SKIP_test_short_stacked_mixedcase(self) :
        self.execute_passes ( 'short', '-fFILEx', start='option' )

    def SKIP_test_short_w_arg_allcaps__no_space(self) :
        self.execute_passes ( 'short', '-fFILE', start='option' )

    def SKIP_test_short_w_arg_angle__no_space(self) :
        self.execute_passes ( 'short', '-f<file>', start='option' )

    def SKIP_test_short_w_arg_allcaps__space(self) :
        self.execute_passes ( 'short', '-f FILE', start='option' )

    def SKIP_test_short_w_arg_angle__space(self) :
        self.execute_passes ( 'short', '-f <file>', start='option' )

    #--------------------------------------------------------------------------

    def test_list_short_pair_space(self) :
        self.execute_passes ( 'short', '-f -g', start='option' )

    def _test_list_short_pair_comma(self) :
        self.execute_passes ( 'short', '-f, -g', start='option' )

    def SKIP_test_list_short_pair_bar(self) :
        self.execute_passes ( 'short', '-f | -g', start='option' )

    #--------------------------------------------------------------------------

    def SKIP_test_long_no_arg(self) :
        self.execute_passes ( 'long', '--file', start='option' )

    def SKIP_test_long_w_arg_eq_allcaps(self) :
        self.execute_passes ( 'long', '--file=FILE', start='option' )

    def SKIP_test_long_w_arg_eq_angle(self) :
        self.execute_passes ( 'long', '--file=<file>', start='option' )

    # Too ambiguous in usage patterns but not at all ambiguous within
    # the options-section details.

    # Hmm, a usage pattern hack might be that given '--file <file>'
    #   or '--file FILE', since the operand resolves to the same word as
    #   preceeding long option, presume <file> is an option-operand.

    def DEFER__test_long_w_arg_no_eq_allcaps(self) :
        self.execute_passes ( 'long', '--file FILE', start='option' )

    def DEFER_test_long_w_arg_no_eq_angle(self) :
        self.execute_passes ( 'long', '--file <file>', start='option' )

    #--------------------------------------------------------------------------

    def SKIP_test_list_short_pair_comma(self) :
        self.execute_passes ( 'list', '-f, -g')

    def SKIP_test_list_short_pair_bar(self) :
        self.execute_passes ( 'list', '-f | -g')

    def SKIP_test_list_short_pair_space(self) :
        self.execute_passes ( 'list', '-f -g')

    def SKIP_test_list_short_single(self) :
        self.execute_passes ( 'list', '-f' )

    def SKIP_test_list_short_trio_space(self) :
        self.execute_passes ( 'list', '-f -g -h' )
    #
    def SKIP_test_list_short_pair_space(self) :
        self.execute_passes ( 'list', '-f, -g' )

    def SKIP_test_list_short_trio_space(self) :
        self.execute_passes ( 'list', '-f, -g, -h' )
    #
    def SKIP_test_list_short_pair_space(self) :
        self.execute_passes ( 'list', '-f , -g' )

    def SKIP_test_list_short_trio_space(self) :
        self.execute_passes ( 'list', "-f , -g  \t, -h" )

    #--------------------------------------------------------------------------

    def SKIP_test_list_long_single(self) :
        self.execute_passes ( 'list', '--file' )

    def SKIP_test_list_long_pair_comma(self) :
        self.execute_passes ( 'list', '--file, --floor' )

    def SKIP_test_list_long_pair_bar(self) :
        self.execute_passes ( 'list', '--file | --floor' )

    def SKIP_test_list_long_pair_ws(self) :
        self.execute_passes ( 'list', '--file --floor' )

    def SKIP_test_list_long_pair_with_args(self) :
        self.execute_passes ( 'list', '--file=FILE , --floor=<floor>' )

    def SKIP_test_list_long_single(self) :
        self.execute_passes ( 'list', '-f,-g')

    #--------------------------------------------------------------------------

    def execute_passes ( self, name, input, start=None ):

        if start is None:
            start = name

        self.grammar_file = GRAMMAR_PATTERN.replace('{name}', name)

        self.parser = DocOptParserPEG ( grammar_file = self.grammar_file, \
                                        start = start, memoization = True, \
                                        debug = False )

        if self.show or self.debug is not False :
            print(f"\n: input = '{input}'")

        tree = self.perform_pass(0, 'raw', self.parser.parse, self.ws + input + self.ws )
        tree = self.perform_pass(1, 'simplify-1', Simplify_Pass1().visit, tree )
        tree = self.perform_pass(2, 'simplify-2', Simplify_Pass2().visit, tree )

        if False :
            # remove leading and trailing whitespace including newlines
            output = input.strip()
            # reduce each expanse of whitespace to a single space
            output = re.compile('[ \t]+').sub(' ', output)
            # remove spaces before of after a newline
            output = re.compile(' ?\n ?').sub('\n', output)

            expect = Terminal(self.parser.parser.parser_model, 0, value=output)
            assert tree == expect
            # Now this does seem to be using the Terminal's text eq

        return tree

    #--------------------------------------------------------------------------

    def perform_pass(self, _pass, name, fcn, *args, **kwargs):
        if self.debug is not False :
            if _pass >= self.debug :
                print(f": pass {_pass} : {name}")
        out = fcn(*args, **kwargs)
        if self.debug is not False :
            if _pass >= self.debug :
                pp(out)
                print('')
        return out

#------------------------------------------------------------------------------

shorts  = [ 'a', 'c', 'f' ]
longs   = [ 'lead', 'file', 'move', 'turn' ]

sep     = [ ' ', ',', '|' ]

#------------------------------------------------------------------------------
