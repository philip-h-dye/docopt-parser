parse_debug                     = False
record                          = False
analyzing                       = False

tst_basic                       = True
tst_mixed                       = True
tst_with_arg_adj                = True
tst_with_arg_gap                = True

#------------------------------------------------------------------------------

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal
from arpeggio import EOF, Sequence, OrderedChoice, ZeroOrMore, OneOrMore
from arpeggio import RegExMatch as _

from prettyprinter import cpprint as pp

#------------------------------------------------------------------------------

from docopt_parser.parsetreenodes import NonTerminal_eq_structural

from grammar.python.option import long_eq_arg, long_no_arg
from grammar.python.option import short_adj_arg, short_stacked, short_no_arg
from grammar.python.option import option
from grammar.python.operand import operand, operand_angled, operand_all_caps

from grammar.python.common import ws, t_eof, t_space, t_equals, p_ws

from base import Test_Base
from util import tprint, write_scratch

#------------------------------------------------------------------------------

def body():
    return Sequence( OneOrMore ( OrderedChoice ( [ option, operand, ws ] ) ),
                     EOF, rule_name='body', skipws=False )

def grammar():
    return Sequence( OneOrMore ( OrderedChoice ( [ option, operand, ws ] ) ),
                     EOF, rule_name='grammar', skipws=False )

#------------------------------------------------------------------------------

class Test_Option ( Test_Base ) :

    def setUp(self):

        # first get defaults, should all be False for boolean flags
        super().setUp()

        global parse_debug, record, analyzing

        self.parse_debug = parse_debug
        self.record = record
        self.analyzing = analyzing

        # quiet, no parse trees displayeda
        # self.debug = False

        # show parse tree for pass >= self.debug
        # self.debug = 2

        # Show text being parsed
        # self.show = True

        # and again, to apply behavior per altered settings
        super().setUp()

        self.parser = ParserPython ( grammar, reduce_tree = False,
                                     debug = self.parse_debug, )

        write_scratch ( _clean = True )

    #--------------------------------------------------------------------------

    def single( self, rule, text ):
        expect = Terminal(rule(), 0, text)
        super().single( rule, text, expect, skipws=False )

    def thrice( self, rule, text ):
        expect = Terminal(rule(), 0, text)
        self.multiple ( rule, text, expect, n = 3 )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_short_single (self) :
        self.single(short_no_arg, "-l")

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_long_single (self) :
        self.single(long_no_arg, "--long")

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_short_thrice (self) :
        self.thrice(short_no_arg, "-l")

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_long_thrice (self) :
        self.thrice(long_no_arg, "--long")

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_mixed, "Basic tests not enabled")
    def test_mixed (self) :
        text = ' -a -b --file --form -l --why '
        #
        text = text.strip()
        #
        texts = text.split()
        p_ws1 = p_ws(' ')
        elements = [ ]
        for value in texts :
            rule = long_no_arg if value[1] == '-' else short_no_arg
            option_ = Terminal(rule(), 0, value)
            option_ = NonTerminal( option(), [ option_ ] )
            elements.append ( option_ )
            elements.append ( p_ws1.expect )
        if len(elements) > 0:
            del elements[-1]
        expect = NonTerminal(body(), [ *elements, t_eof ])
        super().single(body, text, expect)

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_with_arg_adj, "With argument adjacent, tests not enabled")
    def test_long_eq_arg (self) :
        value = '--file=<a-file>'
        option_ = Terminal( long_no_arg(), 0, '--file' )
        operand_ = Terminal( operand_angled(), 0, '<a-file>' )
        operand_ = NonTerminal( operand(), [ operand_ ] )
        expect = NonTerminal( long_eq_arg(), [ option_, t_equals, operand_ ] )
        expect = NonTerminal( option(), [ expect ] )
        expect = NonTerminal( body(), [ expect, t_eof ] )
        super().single(body, value, expect)

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_with_arg_adj, "With argument adjacent, tests not enabled")
    def test_short_adj_arg (self) :
        value = '-fFILE'
        option_ = Terminal( long_no_arg(), 0, '-f' )
        operand_ = Terminal( operand_all_caps(), 0, 'FILE' )
        operand_ = NonTerminal( operand(), [ operand_ ] )
        expect = NonTerminal( short_adj_arg(), [ option_, operand_ ] )
        expect = NonTerminal( option(), [ expect ] )
        expect = NonTerminal( body(), [ expect, t_eof ] )
        super().single(body, value, expect)

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_with_arg_gap, "With argument gap, tests not enabled")
    def test_long_gap_arg (self) :
        value = '--file <a-file>'
        option_ = Terminal( long_no_arg(), 0, '--file' )
        option_ = NonTerminal( option(), [ option_ ] )
        p_ws1 = p_ws(' ')
        operand_ = Terminal( operand_angled(), 0, '<a-file>' )
        operand_ = NonTerminal( operand(), [ operand_ ] )
        expect = NonTerminal( body(), [ option_, p_ws1.expect, operand_, t_eof ] )
        super().single(body, value, expect)

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_with_arg_gap, "With argument gap, tests not enabled")
    def test_short_gap_arg (self) :
        value = '-f FILE'
        option_ = Terminal( short_no_arg(), 0, '-f' )
        option_ = NonTerminal( option(), [ option_ ] )
        p_ws1 = p_ws(' ')
        operand_ = Terminal( operand_all_caps(), 0, 'FILE' )
        operand_ = NonTerminal( operand(), [ operand_ ] )
        expect = NonTerminal( body(), [ option_, p_ws1.expect, operand_, t_eof ] )
        super().single(body, value, expect)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
