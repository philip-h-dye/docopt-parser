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
