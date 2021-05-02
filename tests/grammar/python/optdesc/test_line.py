parse_debug = False

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
from grammar.python.operand import operand, operand_all_caps, operand_angled
from grammar.python.option import *
# # option, ...

# option_list, ol_first_option, ol_term
from grammar.python.optdesc.list import *
from grammar.python.optdesc.line import *

from docopt_parser import DocOptListViewVisitor

from optline import tprint, ogenerate, document, body, element, create_expect

#------------------------------------------------------------------------------

class Test_Option_Line ( unittest.TestCase ) :

    def setUp(self):

        global grammar_elements
        global parse_debug

        # quiet, no parse trees displayed
        # self.debug = False

        # show parse tree for pass >= self.debug
        self.debug = 2

        # from the module global
        self.parse_debug = parse_debug

        # self.each = True
        self.show = True

        # # tprint._file =
        # self.tty = open("/dev/tty", 'w')

        # self.rstdout = redirect_stdout(self.tty)
        # self.rstdout.__enter__()

        tprint._on = self.show or self.debug is not False

        # grammar_elements = [ option_list, ws ]
        self.parser = ParserPython( language_def=document, skipws=False,
                                    debug = parse_debug, )
        # # NEVER # reduce_tree=True -- needed meaning is lost

    #--------------------------------------------------------------------------

    def _test_single_short_no_arg (self):
        input = '-f'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)

        expect = create_expect (
            Terminal( short_no_arg(), 0, '-f' ) ,
            eof = ( input[-1] != '\n' ) ,
        )

        assert NonTerminal_eq_structural(parsed, expect), \
            ( f"input = '{input}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_single_short_w_arg (self):
        input = '-fNORM'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)

        expect = create_expect (
            NonTerminal( short_adj_arg(), [
                Terminal( short_adj_arg__option(), 0, '-f' ) ,
                NonTerminal( operand(), [
                    Terminal( operand_all_caps(), 0, 'NORM' ) ,
                ]) ,
            ]) ,
            eof = ( input[-1] != '\n' ) ,
        )

        assert NonTerminal_eq_structural(parsed, expect), \
            ( f"input = '{input}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_single (self):
        input = '-f'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
        # tprint("[parsed]") ; pp(parsed)

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

        assert NonTerminal_eq_structural(parsed, expect), \
            ( f"input = '{input}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_pair (self):
        input = '-f -x'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
        # tprint("[parsed]") ; pp(parsed)

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

        assert NonTerminal_eq_structural(parsed, expect), \
            ( f"input = '{input}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_trio (self):
        input = '-f -x -l'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
        # tprint("[parsed]") ; pp(parsed)

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

        assert NonTerminal_eq_structural(parsed, expect), \
            ( f"input = '{input}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_create_expect(self):

        input = '-f -x -l'

        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)

        expect = create_expect (
            Terminal( short_no_arg(), 0, '-f' ) ,
            Terminal( short_no_arg(), 0, '-x' ) ,
            Terminal( short_no_arg(), 0, '-l' ) ,
            eof = ( input[-1] != '\n' ) ,
        )

        assert NonTerminal_eq_structural(parsed, expect), \
            ( f"input = '{input}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def tearDown (self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

#------------------------------------------------------------------------------

def lgenerate ( cls, optdefs, help_, indent='  ', sep=', ', offset=16 ):

    # tprint(f"lgenerate :  optdefs = {optdefs}, help_ = '{help_}, sep='{sep}' )")

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

#lgen

olines = [
    ( ( ( '-h', ), ( '--help', ) ), "Show this usage information." ),
    ( ( ( '-v', ), ( '--version', ) ), "Print the version and exit." ),
]

text = ''
for ol_spec in olines :
    text += lgenerate ( Test_Option_Line, *ol_spec )

print(f"Options:\n{text}")

#------------------------------------------------------------------------------

def tgenerate ( optdef, *args, **kwargs ):
    # OLD # ogenerate ( optdef, *args, cls=Test_Option_Line, **kwargs )
    # ogenerate ( Test_Option_Line, optdef, *args, **kwargs )
    pass

#------------------------------------------------------------------------------

# boundry condition, the first option is handled separately from succeeding terms
# and it is an ol_first_option, not an ol_term
# generate( '-f' )
tgenerate ( ( ( '-f', ), ) )

#------------------------------------------------------------------------------

if True  :

    # boundry condition, '-x' is first ol_term of the option_list's ZeroToMany and
    # the first possible position for a option-argument
    # generate( '-f -x' )
    tgenerate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                ) )

    # one past boundry condition, first term on on a boundry
    # generate('-f -x -l')
    tgenerate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                  ( '-l', ) ,
                ) )

    # generate("--file")
    # generate("--file --example")
    # generate("--file --example --list")

    tgenerate ( ( ( '--file', ) ,
                ) )
    tgenerate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                ) )
    tgenerate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                  ( '--list', ) ,
                ) )

    # generate("--file=<FILE> -x")
    # generate("--file=<file> --example=<example>")
    # generate("--file=<file> --example=<example> --list=<list>")

    tgenerate ( ( ( '--file', '=', '<file>', ) ,
                ) )

    tgenerate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                ) )

    tgenerate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                  ( '--list', '=', '<list>', ) ,
                ) )

    # generate("--file=<FILE> -x --example=<EXAMPLE> -y --query=<QUERY> -q")
    tgenerate ( ( ( '--file', '=', '<FILE>', ) ,
                  ( '-x', ) ,
                  ( '--example', '=', '<EXAMPLE>', ) ,
                  ( '-y', ) ,
                  ( '--query', '=', '<QUERY>', ) ,
                  ( '-q', ) ,
                ) )

    # generate("--file=FILE -x")
    tgenerate ( ( ( '--file', '=', 'FILE', ) ,
                  ( '-x', ) ,
                ) )

    # generate("--file=FOObar -x")
    if False  :
        tgenerate ( ( ( '--file', '=', 'FOObar', ) ,
                      ( '-x', ) ,
                    ) )

    # generate("--file=a|b|c -x")
    if False  :
        tgenerate ( ( ( '--file', '=', 'a|b|c', ) ,
                      ( '-x', ) ,
                    ) )

    #------------------------------------------------------------------------------

    tgenerate ( ( ( '--file', '=', 'NORM' ) ,
                  ( '--file', ' ', 'NORM' ) ,
                  ( '--file', ) ,
                ) )

    tgenerate ( ( ( '-f', '', 'NORM' ) ,
                  ( '-f', ' ', 'NORM' ) ,
                  ( '-f', ) ,
                ) )

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
