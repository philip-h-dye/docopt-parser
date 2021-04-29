import unittest

from arpeggio import ParserPython, NonTerminal, Terminal
from arpeggio import Sequence, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _

from prettyprinter import cpprint as pp
import p

#------------------------------------------------------------------------------

from docopt_parser.parsetreenodes import NonTerminal_eq_structural

from grammar.python.operand import *
from grammar.python.common import ws

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    kwargs['file'] = tprint._tty
    print(*args, **kwargs)

tprint._tty = open("/dev/tty", 'w')

#------------------------------------------------------------------------------
#
# reduce_tree=False
# ----------------
#
#   grammar=Sequence [0-16]
#     operand=OrderedChoice [0-16]
#       operand_angled=RegExMatch(<[-_:\w]+>) [0-16]: <angled-operand>
#     EOF [16-16]:
#
# reduce_tree=True
# ----------------
#
#   grammar=Sequence [0-16]
#     operand_angled=RegExMatch(<[-_:\w]+>) [0-16]: <angled-operand>
#       EOF [16-16]:
#
#   p.NonTerminal(
#       rule_name='grammar',
#       contents=[
#           p.Terminal(rule_name='operand_angled', value='<angled-operand>'),
#           p.Terminal(rule_name='EOF', value='')
#       ]
#   )

#------------------------------------------------------------------------------

def grammar():
    return Sequence( OneOrMore ( [ operand, ws ] ),
                     EOF, rule_name='grammar', skipws=False )

#------------------------------------------------------------------------------
    
class Test_Import ( unittest.TestCase ) :

    def setUp(self):
        self.parser = ParserPython(grammar, reduce_tree=True)

    #--------------------------------------------------------------------------

    def single( self, rule, value ):
        parsed = self.parser.parse(value)
        # tprint("\n", parsed.tree_str(), "\n")
        # print('') ; pp(parsed)
        p_operand = Terminal(rule(), 0, value)
        p_eof = Terminal(EOF(), 0, '')
        expect = NonTerminal(grammar(), [ p_operand, p_eof ])
        assert NonTerminal_eq_structural(parsed, expect)

    def test_angled_single (self) :
        self.single(operand_angled, "<angled-operand>")

    def test_all_caps_single (self) :
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

    def test_angled_thrice (self) :
        self.thrice(operand_angled, "<angled-operand>")

    def test_all_caps_thrice (self) :
        self.thrice(operand_all_caps, "FILE")

    #--------------------------------------------------------------------------

    def test_mixed (self) :
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

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
