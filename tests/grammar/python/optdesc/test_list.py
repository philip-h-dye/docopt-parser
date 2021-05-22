parse_debug                     = False
record                          = False
analyzing                       = False

tst_single                      = True
tst_space_gap                   = True
tst_variations                  = True
tst_permutations                = True

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

import unicodedata

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, OrderedChoice, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _ , StrMatch, ParseTreeNode

#------------------------------------------------------------------------------

from prettyprinter import cpprint as pp
from docopt_parser.parsetreenodes import nodes_equal

#------------------------------------------------------------------------------

from grammar.python.common import ws, newline, COMMA, BAR
from grammar.python.operand import *
from grammar.python.option import *

from grammar.python.optdesc.list import option_list, ol_first_option, ol_term
from grammar.python.optdesc.list import ol_term_with_separator, ol_separator

from docopt_parser import DocOptListViewVisitor

from .optlist import document, create_terms, create_expect, method_name
from .optlist import generate_tests__all_permutations_of_optlst_and_sep

# Refactoring for option specification by object instead of tuples
from .optlist import create_terms_obj
from .optlist import define_optlist_shortnames
define_optlist_shortnames()

from base import Test_Base
from util import tprint, write_scratch

from p import pp_str

#------------------------------------------------------------------------------

class Test_Option_List ( Test_Base ) :

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
        parsed = self.parser.parse(text)
        # tprint("[parsed]") ; pp(parsed)
        expect = create_expect (
            NonTerminal( option(), [Terminal(short_no_arg(), 0, '-f')] )
        )

        assert nodes_equal(parsed, expect, verbose=True), \
            ( f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}"
              f"text = '{text}' :\n" )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_single, "Single tests not enabled")
    def test_single_short_with_one_arg (self):
        text = '-fNORM'
        parsed = self.parser.parse(text)
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

    @unittest.skipUnless(tst_single, "Single tests not enabled")
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

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_space_gap, "Space gap tests not enabled")
    def test_space_gap (self):

        optlst = olst (
            opt ( '--query', ' ', '<query>' ),
            # opt ( '--file', ' ', 'NORM' ) ,
            # opt( '--file', '=', 'NORM' ) ,
            # ( '--file', ) ,
        )

        sep =', '

        ( text, terms ) = create_terms_obj( optlst, sep = sep )

        expect = create_expect ( *terms, sep=sep )

        self.parse_and_verify( text, expect )

#------------------------------------------------------------------------------

def ol_generate ( cls, optdefs, sep =', ', expect_fail=False ) :

    def create_method ( actual_text, the_terms ) :
        def the_test_method (self) :
            text = actual_text
            terms = the_terms
            expect = create_expect ( *terms, sep=sep )
            try :
                parsed = self.parser.parse(text)
            except :
                print("\nParse FAILED\n"
                      f"[expect]\n{pp_str(expect)}\n"
                      f"text = '{text}' :\n" )
                assert 1 == 0

            # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
            # tprint("[parsed]") ; pp(parsed)
            # tprint(f"\ntext = '{text}'\n")
            assert nodes_equal(parsed, expect, verbose=True), \
                ( f"[expect]\n{pp_str(expect)}\n"
                  f"[parsed]\n{pp_str(parsed)}"
                  f"text = '{text}' :\n" )
        return the_test_method

    ( initial_text, terms ) = create_terms( optdefs, sep = sep )

    name = method_name(initial_text)
    method = create_method ( initial_text, terms )
    if expect_fail :
        method = unittest.expectedFailure(method)
    setattr ( cls, name, method )

#------------------------------------------------------------------------------

def tol_generate ( optdef, *args, **kwargs ):
    ol_generate ( Test_Option_List, optdef, *args, **kwargs )

#------------------------------------------------------------------------------

if tst_variations :

    # boundry condition, the first option is handled separately from succeeding terms
    # and it is an ol_first_option, not an ol_term
    tol_generate ( ( ( '-f', ), ) )

    # boundry condition, '-x' is first ol_term of the option_list's ZeroToMany and
    # the first possible position for a option-argument
    tol_generate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                ) )

    # one past boundry condition, first term on on a boundry
    tol_generate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                  ( '-l', ) ,
                ) )

    tol_generate ( ( ( '--file', ) ,
                ) )

    tol_generate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                ) )
    tol_generate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                  ( '--list', ) ,
                ) )

    tol_generate ( ( ( '--file', '=', '<file>', ) ,
                ) )

    tol_generate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                ) )

    tol_generate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                  ( '--list', '=', '<list>', ) ,
                ) )

    tol_generate ( ( ( '--file', '=', '<FILE>', ) ,
                  ( '-x', ) ,
                  ( '--example', '=', '<EXAMPLE>', ) ,
                  ( '-y', ) ,
                  ( '--query', '=', '<QUERY>', ) ,
                  ( '-q', ) ,
                ) )

    tol_generate ( ( ( '--file', '=', 'FILE', ) ,
                  ( '-x', ) ,
                ) )

    tol_generate ( ( ( '--file', '=', 'NORM' ) ,
                  ( '--file', ' ', 'NORM' ) ,
                  ( '--file', ) ,
                ) )

    tol_generate ( ( ( '-f', '', 'NORM' ) ,
                  ( '-f', ' ', 'NORM' ) ,
                  ( '-f', ) ,
                ) )

#------------------------------------------------------------------------------

if tst_operand_command :

    # *** 'command' operand not yet implemented -- Not Supported during generate

    tol_generate ( ( ( '--file', '=', 'FOObar', ) ,
                  ( '-x', ) ,
                ) ,
                expect_fail=True )

    tol_generate ( ( ( '--file', '=', 'a|b|c', ) ,
                  ( '-x', ) ,
                ) ,
                expect_fail=True )

#------------------------------------------------------------------------------

if tst_permutations :
    generate_tests__all_permutations_of_optlst_and_sep \
        ( Test_Option_List, ol_generate, words=['file'] )

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
