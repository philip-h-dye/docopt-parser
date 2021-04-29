import sys
import os
import re

from contextlib import redirect_stdout

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, OrderedChoice, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _

#------------------------------------------------------------------------------

from prettyprinter import cpprint as pp
from docopt_parser.parsetreenodes import NonTerminal_eq_structural
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, COMMA, BAR
# from grammar.python.generic.operand import *
from grammar.python.optdesc.list import option_list
from grammar.python.optdesc.list import ol_first_option, ol_element
from grammar.python.optdesc.list import ol_operand_lead, ol_operand
from grammar.python.optdesc.list import ol_option_lead, ol_long, ol_short
from grammar.python.optdesc.list import _long, _short

#------------------------------------------------------------------------------

# from docopt_parser import DocOptParserPEG
# from docopt_parser import DocOptSimplifyVisitor_Pass1 as Simplify_Pass1
# from docopt_parser import DocOptSimplifyVisitor_Pass2 as Simplify_Pass2

#------------------------------------------------------------------------------

grammar_elements = [ ]

def element():
    # print("\n: grammar : body : element : grammar_elements :")
    # pp(grammar_elements)
    # print('\n')
    # To work properly, first argumnet of OrderedChoice must be a
    # list.  IF not, it implicitly becomes Sequence !
    return OrderedChoice ( grammar_elements, rule_name='element' )

def body():
    return OneOrMore ( element, rule_name='body' )

def document():
    return Sequence( body, EOF, rule_name='document' )

#------------------------------------------------------------------------------
first=ol_first_option
s=_short
l=_long
a=operand_angled
c=operand_all_caps
#------------------------------------------------------------------------------

class Test_Option_List ( unittest.TestCase ) :

    def setUp(self):

        global grammar_elements

        # grammar_elements = [ option_list, ws ]
        # self.parser = ParserPython(grammar, reduce_tree=True)

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

    def list_options_only ( self, first, optdef, lead=' '):
        global grammar_elements
        input = lead.join([ val for (key, val) in optdef ])
        grammar_elements = [ option_list, ws]
        parser = ParserPython(language_def=document ) # , reduce_tree=True)
        # pp(parser.parser_model)
        parsed = parser.parse(' '+input)
        # tprint("\n", parsed.tree_str(), "\n")
        # return
        p_ws = Terminal(ws(), 0, ' ')
        # print(f"\n: optdef = {repr(optdef)}\n")
        #
        ( rule, opt ) = optdef[0]
        p_first = NonTerminal(first(), [ p_ws, Terminal(rule(), 0, opt) ])
        #
        p_ol_option_lead = Terminal(ol_option_lead(), 0, lead)
        olist_ = [ ]
        for ( rule, opt ) in optdef[1:] :
            p_ol_short = NonTerminal \
                (ol_short(), [ p_ol_option_lead, Terminal(rule(), 0, opt) ])
            olist_.append ( NonTerminal(ol_element(), [ p_ol_short ]) )
        p_olist = NonTerminal(option_list(), [ p_first, olist_ ])
        p_element = NonTerminal(element(), [ p_olist ])
        p_body = NonTerminal(body(), [p_element])
        p_eof = Terminal(EOF(), 0, '')
        expect = NonTerminal(document(), [p_body, p_eof])
        assert NonTerminal_eq_structural(parsed, expect), (
            f"input = '{input}' :\n"
            f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    # document body element option_list ol_first_option

    #---------------------------------------------------------------------------

    def test_short_single (self) :
        f=ol_first_option
        r=_short
        optdef = ( (r, '-f'), )
        self.list_options_only( f, optdef )

    #---------------------------------------------------------------------------

    def test_short_pair_space(self) :
        optdef = ( (s, '-f'), (s, '-g') )
        self.list_options_only( first, optdef )

    def test_short_trio_space(self) :
        first=ol_first_option
        r=_short
        optdef = ( (s, '-f'), (s, '-g') , (s, '-i') )
        self.list_options_only( first, optdef )

    #---------------------------------------------------------------------------

    def test_short_pair_comma(self) :
        first=ol_first_option
        r=_short
        optdef = ( (s, '-f'), (s, '-g') )
        self.list_options_only( first, optdef, lead=',' )

    def test_short_trio_comma(self) :
        first=ol_first_option
        r=_short
        optdef = ( (s, '-f'), (s, '-g') , (s, '-i') )
        self.list_options_only( first, optdef, lead=',' )

    #---------------------------------------------------------------------------

    def test_short_pair_bar(self) :
        first=ol_first_option
        r=_short
        optdef = ( (s, '-f'), (s, '-g') )
        self.list_options_only( first, optdef, lead='|' )

    def test_short_trio_bar(self) :
        first=ol_first_option
        r=_short
        optdef = ( (s, '-f'), (s, '-g') , (s, '-i') )
        self.list_options_only( first, optdef, lead='|' )

    #==========================================================================

    def _t(r, opt):
        return Terminal(r(), 0, opt)

    def test_mixed_pair_bar(self) :
        optdef = ( ((l, '--file'),
                    '=', a, '<file>'),
                   (s, '-g') )
        self.list_options_only( first, optdef, load='|',  )

    def _test_mixed_trio_bar(self) :
        first=ol_first_option
        r=_short
        optdef = ( (s, '-f'), (s, '-g') , (s, '-i') )
        self.list_options_only( first, optdef, lead='|' )

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
