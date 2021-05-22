parse_debug                     = False
record                          = False
analyzing                       = False

tst_single                      = True
tst_pair                        = True
tst_trio                        = True
tst_create_expect               = True
tst_space_gap                   = True
tst_variations                  = True

# Not Yet Implemented
tst_operand_command             = False

# # FIXME: comment or remove before commit
# from util import tst_disable_all
# tst_disable_all()
# record                          = True

#------------------------------------------------------------------------------

import sys
import os
import re

from contextlib import redirect_stdout

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, OrderedChoice, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _

#------------------------------------------------------------------------------

from prettyprinter import cpprint as pp, pprint as pp_plain
from docopt_parser.parsetreenodes import NonTerminal_eq_structural
from docopt_parser.parsetreenodes import nodes_equal
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, newline, COMMA, BAR
from grammar.python.operand import operand, operand_all_caps, operand_angled
from grammar.python.option import *

from grammar.python.optdesc.list import *
from grammar.python.optdesc.line import *

from docopt_parser import DocOptListViewVisitor

from .optline import tprint, ogenerate, document, body, element, create_expect

from base import Test_Base
from util import tprint, write_scratch

#------------------------------------------------------------------------------

class Test_Option_Line ( Test_Base ) :

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

        self.grammar = document

        self.parser = ParserPython ( language_def = self.grammar,
                                     reduce_tree = False,
                                     debug = self.parse_debug, )

        if self.record :
            write_scratch ( _clean = True )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_single, "Single tests not enabled")    
    def test_single_short_no_arg (self):
        text = '-f'
        expect = create_expect (
            NonTerminal( option(), [ Terminal( short_no_arg(), 0, '-f' ) ] ) ,
            eof = ( text[-1] != '\n' ) ,
        )
        self.parse_and_verify( text, expect )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_single, "Single tests not enabled")    
    def test_single_short_w_arg (self):
        text = '-fNORM'
        expect = create_expect (
            NonTerminal( option(), [ 
                NonTerminal( short_adj_arg(), [
                    Terminal( short_adj_arg__option(), 0, '-f' ) ,
                    NonTerminal( operand(), [
                        Terminal( operand_all_caps(), 0, 'NORM' ) ,
                    ]) ,
                ]) ,
            ]) ,
            eof = ( text[-1] != '\n' ) ,
        )
        self.parse_and_verify( text, expect )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_single, "Single tests not enabled")    
    def test_single (self):
        text = '-f'
        expect = NonTerminal( document(), [
            NonTerminal( body(), [
                NonTerminal( element(), [
                    NonTerminal( option_line(), [
                        NonTerminal( option_list(), [
                            NonTerminal( ol_first_option(), [
                                NonTerminal( option(), [
                                    Terminal( short_no_arg(), 0, '-f' ),
                                ]) ,
                            ]) ,
                        ]) ,
                        Terminal(EOF(), 0, '') ,
                    ]) ,
                ]) ,
            ]) ,
            Terminal(EOF(), 0, '') ,
        ])
        self.parse_and_verify( text, expect )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_pair, "Pair tests not enabled")    
    def test_pair (self):
        text = '-f -x'
        expect = NonTerminal( document(), [
            NonTerminal( body(), [
                NonTerminal( element(), [
                    NonTerminal( option_line(), [
                        NonTerminal( option_list(), [
                            NonTerminal( ol_first_option(), [
                                NonTerminal( option(), [
                                    Terminal( short_no_arg(), 0, '-f' ),
                                ]) ,
                            ]) ,
                            NonTerminal( ol_term_with_separator(), [
                                NonTerminal( ol_separator(), [
                                    NonTerminal( ol_space(), [
                                        Terminal( StrMatch(' '), 0, ' '),
                                    ]) ,
                                ]) ,
                                NonTerminal( ol_term(), [
                                    NonTerminal( option(), [
                                        Terminal( short_no_arg(), 0, '-x' )
                                    ]) ,
                                ]) ,
                            ]) ,
                        ]) ,
                        Terminal(EOF(), 0, '') ,
                    ]) ,
                ]) ,
            ]) ,
            Terminal(EOF(), 0, '') ,
        ])
        self.parse_and_verify( text, expect )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_trio, "Trio tests not enabled")    
    def test_trio (self):

        text = '-f -x -l'

        expect = NonTerminal( document(), [
            NonTerminal( body(), [
                NonTerminal( element(), [
                    NonTerminal( option_line(), [
                        NonTerminal( option_list(), [
                            NonTerminal( ol_first_option(), [
                                NonTerminal( option(), [
                                    Terminal( short_no_arg(), 0, '-f' ),
                                ]) ,
                            ]) ,
                            NonTerminal( ol_term_with_separator(), [
                                NonTerminal( ol_separator(), [
                                    NonTerminal( ol_space(), [
                                        Terminal( StrMatch(' '), 0, ' '),
                                    ]) ,
                                ]) ,
                                NonTerminal( ol_term(), [
                                    NonTerminal( option(), [
                                        Terminal( short_no_arg(), 0, '-x' )
                                    ]) ,
                                ]) ,
                            ]) ,
                            NonTerminal( ol_term_with_separator(), [
                                NonTerminal( ol_separator(), [
                                    NonTerminal( ol_space(), [
                                        Terminal( StrMatch(' '), 0, ' '),
                                    ]) ,
                                ]) ,
                                NonTerminal( ol_term(), [
                                    NonTerminal( option(), [
                                        Terminal( short_no_arg(), 0, '-l' )
                                    ]) ,
                                ]) ,
                            ]) ,
                        ]) ,
                        Terminal(EOF(), 0, '') ,
                    ]) ,
                ]) ,
            ]) ,
            Terminal(EOF(), 0, '') ,
        ])

        self.parse_and_verify( text, expect )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_create_expect, "Create expect tests not enabled")    
    def test_create_expect(self):

        text = '-f -x -l'

        expect = create_expect (
            NonTerminal( option(), [ Terminal( short_no_arg(), 0, '-f' ) ] ) ,
            NonTerminal( option(), [ Terminal( short_no_arg(), 0, '-x' ) ] ) ,
            NonTerminal( option(), [ Terminal( short_no_arg(), 0, '-l' ) ] ) ,
            eof = ( text[-1] != '\n' ) ,
        )

        # print("[ expect ]")
        # pp(expect[0][0][0][0][1])

        parsed = self.parse(text, expect)
        # tprint("[parsed]") ; pp(parsed)

        # print("[ parsed ]")
        # pp(parsed[0][0][0][0][1])

        self.verify( text, expect, parsed )

    #--------------------------------------------------------------------------

    def tearDown (self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

#------------------------------------------------------------------------------

def generate_line ( cls, optdefs, help_, indent='  ', sep=', ', offset=16 ):

    # tprint(f"generate_line :  optdefs = {optdefs}, help_ = '{help_}, sep='{sep}' )")

    ( method_name, optlist_string ) = ogenerate ( cls, optdefs, sep=sep, )

    if indent is None:
        indent = ''
    if help_ is None:
        help_ = ''

    # print(f": {'indent':<16} : '{indent}'")
    # print(f": {'os string':<16} : '{optlist_string}'")
    # print(f": {'help_':<16} : '{help_}'")
    # sys.stdout.flush()

    return f"{indent}{optlist_string:<{offset}}  {help_}\n"

#------------------------------------------------------------------------------

if False :
    #lgen
    olines = [
        ( ( ( '-h', ), ( '--help', ) ), "Show this usage information." ),
        ( ( ( '-v', ), ( '--version', ) ), "Print the version and exit." ),
    ]

    text = ''
    for ol_spec in olines :
        text += generate_line ( Test_Option_Line, *ol_spec )

    print(f"Options:\n{text}")

#------------------------------------------------------------------------------

def _generate ( optdefs, *args, **kwargs ):
    return ogenerate ( Test_Option_Line, optdefs, *args, **kwargs )

#------------------------------------------------------------------------------

if tst_space_gap:

    _generate ( ( ( '--query', ' ', '<query>', ) ,
                ) )

#------------------------------------------------------------------------------

if tst_variations :

    # boundry condition, the first option is handled separately from succeeding terms
    # and it is an ol_first_option, not an ol_term
    # generate( '-f' )
    _generate ( ( ( '-f', ), ) )

    # boundry condition, '-x' is first ol_term of the option_list's ZeroToMany and
    # the first possible position for a option-argument
    # generate( '-f -x' )
    _generate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                ) )

    # one past boundry condition, first term on on a boundry
    # generate('-f -x -l')
    _generate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                  ( '-l', ) ,
                ) )

    # generate("--file")
    # generate("--file --example")
    # generate("--file --example --list")

    _generate ( ( ( '--file', ) ,
                ) )
    _generate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                ) )
    _generate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                  ( '--list', ) ,
                ) )

    # generate("--file=<FILE> -x")
    # generate("--file=<file> --example=<example>")
    # generate("--file=<file> --example=<example> --list=<list>")

    _generate ( ( ( '--file', '=', '<file>', ) ,
                ) )

    _generate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                ) )

    _generate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                  ( '--list', '=', '<list>', ) ,
                ) )

    # generate("--file=<FILE> -x --example=<EXAMPLE> -y --query=<QUERY> -q")
    _generate ( ( ( '--file', '=', '<FILE>', ) ,
                  ( '-x', ) ,
                  ( '--example', '=', '<EXAMPLE>', ) ,
                  ( '-y', ) ,
                  ( '--query', '=', '<QUERY>', ) ,
                  ( '-q', ) ,
                ) )

    # generate("--file=FILE -x")
    _generate ( ( ( '--file', '=', 'FILE', ) ,
                  ( '-x', ) ,
                ) )

    # generate("--file=FOObar -x")    
    if tst_operand_command  :
        # FIXME: not implemened yet -- 'command/example' option-argument
        _generate ( ( ( '--file', '=', 'FOObar', ) ,
                      ( '-x', ) ,
                    ) )

    # generate("--file=a|b|c -x")
    if tst_operand_command  :
        # FIXME: not implemened yet -- 'command/example' option-argument
        _generate ( ( ( '--file', '=', 'a|b|c', ) ,
                      ( '-x', ) ,
                    ) )

    #------------------------------------------------------------------------------

    _generate ( ( ( '--file', '=', 'NORM' ) ,
                  ( '--file', ' ', 'NORM' ) ,
                  ( '--file', ) ,
                ) )

    _generate ( ( ( '-f', '', 'NORM' ) ,
                  ( '-f', ' ', 'NORM' ) ,
                  ( '-f', ) ,
                ) )

#------------------------------------------------------------------------------

# Option Line Variations
# ----------------------
#   indent     :  0 .. 4
#   offset     :  0 .. 30
#   help gap   :  2 .. 4
#       text   :  None / '' / 'a' / 'ab' / 'Help ...'
#   opt-list   :  handled in test_list, no concern here

# Option Line Errors
# ------------------
#   indent     :  negative
#   offset     :  negative
#   help gap   :  less than 2
#        text  :  ...
#   opt-list   :  handled in test_list, no concern here

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
