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

from grammar.python.common import ws, newline, COMMA, BAR
from grammar.python.generic.operand import *
# # operand, operand_all_caps, operand_angled
from grammar.python.option import *
# # option, ...

from grammar.python.optdesclist_1 import option_list, ol_first_option, ol_term

from docopt_parser import DocOptListViewVisitor

#------------------------------------------------------------------------------

grammar_elements = [ option_list, ws, newline ]

def element():
    # print("\n: grammar : body : element : grammar_elements :")
    # pp(grammar_elements)
    # print('\n')
    # To work properly, first argumnet of OrderedChoice must be a
    # list.  IF not, it implicitly becomes Sequence !
    return OrderedChoice ( [ *grammar_elements ], rule_name='element' )

def body():
    return OneOrMore ( element, rule_name='body' )

def document():
    return Sequence( body, EOF, rule_name='document' )

#------------------------------------------------------------------------------

_short=short_no_arg
_long=long_no_arg

first=ol_first_option
s=_short
l=_long
a=operand_angled
c=operand_all_caps
# ol=ol_operand_lead

def _t(r, opt):
    return Terminal(r(), 0, opt)

#------------------------------------------------------------------------------

def re_compile(f):
    r = f()
    r.compile()
    return r.regex

re_short  = re_compile(_short)
re_long   = re_compile(_long)

def verify_option_type_match(rule, value): # rule in s or r , value : option string

    if rule is _short :
        if re_short.fullmatch(value):
            return
        if len(value) < 2:
            raise ValueError("Short option '{value}' is too short.  Please address.")
        if len(value) > 2:
            raise ValueError("Short option '{value}' is too large.  Please address.")
        raise ValueError("Short option '{value}' is invalid.  Probably invalid characters.")

    if rule is _long :
        if re_long.fullmatch(value):
            return
        if len(value) < 4:
            raise ValueError("Long option '{value}' is too short, it must be "
                             "at least two dashes and two letters.  "
                             "Please address.")
        raise ValueError("Long option '{value}' is invalid.  Probably invalid characters.")

    raise ValueError("verify_option_type_match() should be called only with "
                     "either _long or _short.  Please address.")

#------------------------------------------------------------------------------

class Test_Option_List ( unittest.TestCase ) :

    def setUp(self):

        global grammar_elements

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

        # grammar_elements = [ option_list, ws ]
        self.parser = ParserPython( language_def=document ) # , reduce_tree=True)

    #--------------------------------------------------------------------------

    def tearDown (self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

    #==========================================================================

    # boundry, first option handled separately from others, not a TERM
    def test_simple_short_single (self) :
        input = '-f'
        parsed = self.parser.parse(input)
        # tprint("\n", parsed.tree_str(), "\n")
        tprint("[parsed]")
        pp(parsed)

    #--------------------------------------------------------------------------

    # boundry, second option is 1) first TERM() of ol_list
    #                           2) first possible option-argumemt
    def test_simple_short_pair (self) :
        input = '-f -x'
        parsed = self.parser.parse(input)
        # tprint("\n", parsed.tree_str(), "\n")
        tprint("[parsed]")
        # pp(parsed)
        lst = DocOptListViewVisitor().visit(parsed)
        pp(lst)

    #--------------------------------------------------------------------------

    # first term not on boundry
    def _test_simple_short_trio (self) :
        input = '-f -x -q'
        parsed = self.parser.parse(input)
        # tprint("\n", parsed.tree_str(), "\n")
        tprint("[parsed]")
        # pp(parsed)
        lst = DocOptListViewVisitor().visit(parsed)
        pp(lst)

    #==========================================================================

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
