import sys
import os
import re

from contextlib import redirect_stdout

import unicodedata

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, OrderedChoice, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _ , StrMatch, ParseTreeNode

#------------------------------------------------------------------------------

from prettyprinter import cpprint as pp
from docopt_parser.parsetreenodes import nodes_equal
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, newline, COMMA, BAR
from grammar.python.operand import *
from grammar.python.option import *

from grammar.python.optdesc.list import option_list, ol_first_option, ol_term
from grammar.python.optdesc.list import ol_term_with_separator, ol_separator

from docopt_parser import DocOptListViewVisitor

from optlist import document, create_terms, create_expect, method_name

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
        self.parser = ParserPython( language_def=document, skipws=False )
        # # NEVER # reduce_tree=True -- needed meaning is lost

    #--------------------------------------------------------------------------

    def tearDown (self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

    #--------------------------------------------------------------------------

    def test_single_short_no_arg (self):
        input = '-f'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)
        expect = create_expect (
            NonTerminal( option(), [Terminal(short_no_arg(), 0, '-f')] )
        )

        assert nodes_equal(parsed, expect, verbose=True), \
            ( f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}"
              f"text = '{text}' :\n" )

    #--------------------------------------------------------------------------

    def test_single_short_with_one_arg (self):
        input = '-fNORM'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)
        expect = create_expect (
            NonTerminal( option(), [
                NonTerminal( short_adj_arg(), [
                    Terminal( short_adj_arg__option(), 0, '-f' ) ,
                    NonTerminal( operand(), [
                        Terminal( operand_all_caps(), 0, 'NORM' ) ,
                    ]) ,
                ]) ,
            ]) ,
        )

    #--------------------------------------------------------------------------

    def test_single_optdefs (self):

        # optdefs = ( ( '--file', '=', '<file>', ) , )
        # optdefs = ( ( '--file', ) ,  ( '--example', ) , )
        optdefs = ( ( '--file', '=', 'NORM' ) ,
                    ( '--file', ' ', 'NORM' ) ,
                    ( '--file', ) ,
                  )

        sep =', '

        ( text, terms ) = create_terms( optdefs, sep = sep )

        expect = create_expect ( *terms, sep=sep )

        parsed = self.parser.parse(text)

        # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
        # tprint("[parsed]") ; pp(parsed)
        # tprint(f"\ntext = '{text}'\n")

        # Option line 1 :  [0][0][0]
        #  first option             [0]
        if False :
            expect = expect[0][0][0] # [0]  # [0] [0]
            parsed = parsed[0][0][0] # [0]  # [0] [0]

            # if False :
            print('')
            print(f": Expect '{expect.rule_name}' with {len(expect)} children")
            print(f": Parsed '{parsed.rule_name}' with {len(parsed)} children")
            print('')
            for i in range(len(expect)) :
                if not nodes_equal( parsed[i], expect[i], verbose=True) :
                    print(f"Child {i} does not match :\n"
                          f"[expect]\n{pp_str(expect[i])}\n"
                          f"[parsed]\n{pp_str(parsed[i])}"
                          f"text = '{text}' :\n" )
                    return

            assert len(expect) == len(parsed)

        # print("\n[expect]");  pp(expect) ; print("[parsed]"); pp(parsed)
        # return

        assert nodes_equal(parsed, expect, verbose=True), \
            ( f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}"
              f"text = '{text}' :\n" )

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    if tprint._on :
        kwargs['file'] = tprint._file
        print('')
        print(*args, **kwargs)
        tprint._file.flush()

tprint._file = sys.stdout # open("/dev/tty", 'w')
# tprint._on = False
tprint._on = True

#------------------------------------------------------------------------------

def ol_generate ( cls, optdefs, sep =', ', expect_fail=False ) :

    def create_method ( actual_input, the_terms ) :
        def the_test_method (self) :
            input = actual_input
            terms = the_terms
            expect = create_expect ( *terms, sep=sep )
            try :
                parsed = self.parser.parse(input)
            except :
                print("\nParse FAILED\n"
                      f"[expect]\n{pp_str(expect)}\n"
                      f"input = '{input}' :\n" )
                assert 1 == 0

            # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
            # tprint("[parsed]") ; pp(parsed)
            # tprint(f"\ninput = '{input}'\n")
            assert nodes_equal(parsed, expect, verbose=True), \
                ( f"[expect]\n{pp_str(expect)}\n"
                  f"[parsed]\n{pp_str(parsed)}"
                  f"input = '{input}' :\n" )
        return the_test_method

    ( initial_input, terms ) = create_terms( optdefs, sep = sep )

    name = method_name(initial_input)
    method = create_method ( initial_input, terms )
    if expect_fail :
        method = unittest.expectedFailure(method)
    setattr ( cls, name, method )

#------------------------------------------------------------------------------

def _generate ( optdef, *args, **kwargs ):
    ol_generate ( Test_Option_List, optdef, *args, **kwargs )

#------------------------------------------------------------------------------

if False :
    pass

if True :
    pass

    # boundry condition, the first option is handled separately from succeeding terms
    # and it is an ol_first_option, not an ol_term
    _generate ( ( ( '-f', ), ) )

    # boundry condition, '-x' is first ol_term of the option_list's ZeroToMany and
    # the first possible position for a option-argument
    _generate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                ) )

    # one past boundry condition, first term on on a boundry
    _generate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                  ( '-l', ) ,
                ) )

    _generate ( ( ( '--file', ) ,
                ) )

    _generate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                ) )
    _generate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                  ( '--list', ) ,
                ) )

    _generate ( ( ( '--file', '=', '<file>', ) ,
                ) )

    _generate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                ) )

    _generate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                  ( '--list', '=', '<list>', ) ,
                ) )

    _generate ( ( ( '--file', '=', '<FILE>', ) ,
                  ( '-x', ) ,
                  ( '--example', '=', '<EXAMPLE>', ) ,
                  ( '-y', ) ,
                  ( '--query', '=', '<QUERY>', ) ,
                  ( '-q', ) ,
                ) )

    _generate ( ( ( '--file', '=', 'FILE', ) ,
                  ( '-x', ) ,
                ) )

    _generate ( ( ( '--file', '=', 'NORM' ) ,
                  ( '--file', ' ', 'NORM' ) ,
                  ( '--file', ) ,
                ) )

    _generate ( ( ( '-f', '', 'NORM' ) ,
                  ( '-f', ' ', 'NORM' ) ,
                  ( '-f', ) ,
                ) )

#------------------------------------------------------------------------------

if False :

    # *** 'command' not yet implemented -- Not Supported during generate

    _generate ( ( ( '--file', '=', 'FOObar', ) ,
                  ( '-x', ) ,
                ) ,
                expect_fail=True )

    _generate ( ( ( '--file', '=', 'a|b|c', ) ,
                  ( '-x', ) ,
                ) ,
                expect_fail=True )

#------------------------------------------------------------------------------

# Option List Variations
# ----------------------
#   term sep   :  None / '' / ' ' / ' ?, ?' / ' ?| ?'  # all variations
#   n options  :  1 .. 4
#   option     :  long        / short
#     arg gap  :  eq | space  / adj | space
#         type :  all-caps    / angled        [ / command ]

# Option List Errors
# ------------------
#   n options  :  0
#   term sep   :  ?
#   option     :
#     arg gap  :  missing ?
#         type :  neither all-caps nor angled [ nor command ]

#------------------------------------------------------------------------------

import itertools

def option_variations ( word ):

    options = [ ]

    short = f"-{word[0]}"
    options.append( (short, ) )
    for arg in ( word.upper(), f"<{word}>" ) :
        for gap in ( '', ' ' ) :
            options.append( (short, gap, arg) )

    long = f"--{word}"
    options.append( (long, ) ) 
    for arg in ( word.upper(), f"<{word}>" ) :
        for gap in '= ':
            options.append( (long, gap, arg) )

    for n in range(1, min(4,len(options)+1)) :
        for result in itertools.permutations(options, n):
            yield result

#------------------------------------------------------------------------------

def generate_sep_variations(optdef):

    # sep default
    ol_generate ( Test_Option_List, optdef )
    #
    # FIXME: Too finicky, change user supplied NONE or '' to DEFAULT
    #
    # sep=None, crashs in optlist, line 121 :
    #   return ( sep.join(input), terms )
    # => AttributeError: 'NoneType' object has no attribute 'join'
    #
    # sep='' :
    # => arpeggio.NoMatch: Expected operand_angled or operand_all_caps or space
    #    or comma or bar or long_no_arg or short_adj_arg__option or short_stacked
    #    or short_no_arg or ws or newline or EOF at position (1, 3) => '-h*--help'.
    #
    for sep in [ ' ' ] :
        ol_generate ( Test_Option_List, optdef, sep=sep)
    for ch in [ ',', '|' ] :
        for before in [ '', ' ' ] :
            for after in [ '', ' ' ] :
                sep = before + ch + after
                ol_generate ( Test_Option_List, optdef, sep=sep)

#------------------------------------------------------------------------------

if True :

    generate_sep_variations( ( ( '-h', ), ( '--help', ) ) )

    for optdef in option_variations( 'file' ) :
        generate_sep_variations(optdef)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
