parse_debug                     = False
record                          = False
analyzing                       = False

tst_basic                       = True
tst_mixed                       = True

#------------------------------------------------------------------------------

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal
from arpeggio import Sequence, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _

from prettyprinter import cpprint as pp

#------------------------------------------------------------------------------

from docopt_parser.parsetreenodes import NonTerminal_eq_structural

from grammar.python.common import ws, t_eof, t_space, t_equals, p_ws

from grammar.python.operand import *

from base import Test_Base

from util import tprint, write_scratch

import p

#------------------------------------------------------------------------------

def body():
    return Sequence( OneOrMore ( OrderedChoice ( [ operand, ws ] ) ),
                     EOF, rule_name='body', skipws=False )

def grammar():
    return Sequence( OneOrMore ( [ operand, ws ] ),
                     EOF, rule_name='grammar', skipws=False )

#------------------------------------------------------------------------------
    
class Test_Operand ( Test_Base ) :

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

        self.parser = ParserPython(grammar, reduce_tree=False)

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
    def test_angled_single (self) :
        self.single(operand_angled, "<angled-operand>")

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_all_caps_single (self) :
        self.single(operand_all_caps, "FILE")

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_angled_thrice (self) :
        self.thrice(operand_angled, "<angled-operand>")

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_all_caps_thrice (self) :
        self.thrice(operand_all_caps, "FILE")

    #--------------------------------------------------------------------------

    # @unittest.skipUnless(tst_mixed, "Mixed tests not enabled")
    def test_mixed (self) :
        text = ' <a> <b> CC <d> EE FILE NORM '
        text = text.strip()
        texts = text.split()
        p_ws1 = p_ws(' ')
        elements = [ ]
        for value in texts :
            rule = operand_angled if value[0] == '<' else operand_all_caps
            elements.append ( NonTerminal( operand(),
                                           [ Terminal(rule(), 0, value) ] ) )
            elements.append ( p_ws1.expect )
        if len(elements) > 0:
            del elements[-1]
        expect = NonTerminal(body(), [ *elements, t_eof ])
        super().single(body, text, expect)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
