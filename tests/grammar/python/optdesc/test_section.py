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

from prettyprinter import cpprint as pp, pprint as pp_plain
from docopt_parser.parsetreenodes import nodes_equal
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, newline, COMMA, BAR
from grammar.python.operand import operand, operand_all_caps, operand_angled
from grammar.python.option import *

from grammar.python.optdesc.list import *
from grammar.python.optdesc.line import *
from grammar.python.optdesc.section import *

from docopt_parser import DocOptListViewVisitor

from .optsect import tprint, document, body, element
from .optsect import create_terms
from .optsect import expect_document
from .optsect import section_optdesc

#------------------------------------------------------------------------------

# Refactoring to use *Def object specifications, isolated in *_obj functions :
from .optsect import section_optdesc_obj

# Shortcuts for creating specification objects
from .optlist import OptionDef as opt, OptionListDef as olst
from .optline import OptionLineDef as ol
from .optsect import OptionDescDef as od

#------------------------------------------------------------------------------

class Test_Usage_Section ( unittest.TestCase ) :

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

    def test_minimal(self):

        ol_line_specs = [
            ( ( ( '-h', ), ( '--help', ) ), "Show this usage information." ),
            ( ( ( '-v', ), ( '--version', ) ), "Print the version and exit." ),
        ]

        ( text, opt_desc ) = section_optdesc ( ol_line_specs )

        expect = expect_document ( [ opt_desc ] )
        # tprint("[expect]") ; pp(expect)
        # with open ("expect.txt", 'w') as f :
        #     pp_plain(expect, stream=f)

        self.parse_and_verify ( text, expect )

    #--------------------------------------------------------------------------

    def test_minimal_obj__step_by_step (self):

        olst_1   = olst ( opt( '-h', ), opt( '--help', ) )
        oline_1  = ol   ( olst_1, "Show this usage information." )
        olst_2   = olst ( opt( '-v', ), opt( '--version', ) )
        oline_2  = ol   ( olst_2, "Print the version and exit." )
        optspecs = od   ( oline_1, oline_2, intro="Options :" )

        # print("[optspecs]") ; pp(optspecs)

        ( text, opt_desc ) = section_optdesc_obj ( optspecs )

        # print(f"[test] text :\n{text}\n")
        # print(f"[test] opt_desc :\n{pp_str(opt_desc)}\n")

        expect = expect_document ( [ opt_desc ] )
        # tprint("[expect]") ; pp(expect)
        # with open ("expect.txt", 'w') as f :
        #     pp_plain(expect, stream=f)

        self.parse_and_verify ( text, expect )

    #--------------------------------------------------------------------------

    def test_minimal_obj__single_spec (self):

        optspecs = od (
            ol ( olst ( opt( '-h', ), opt( '--help', ) ) ,
                 "Show this usage information." ) ,
            ol ( olst ( opt( '-v', ), opt( '--version', ) ) ,
                 "Print the version and exit." ) ,
            intro="Options :" )

        # print("[optspecs]") ; pp(optspecs)

        ( text, opt_desc ) = section_optdesc_obj ( optspecs )

        expect = expect_document ( [ opt_desc ] )

        self.parse_and_verify ( text, expect )

    #--------------------------------------------------------------------------

    # Three bugs for the price of one !
    #
    #   In the option-list, operands may be either part of an option or a term.
    #
    #   opt( '--file', '=', '<file>') :
    #      <file> is part of the term long_eq_arg of '--file'.
    #
    #   opt( '--query', ' ', '<query>') :
    #      <query> is a term itself, separate from long_no_arg '--query'.
    #
    # 1. optline was inserting a comma rather than a space gap before
    #    operands.
    # 2. All optline/optlist term except handlers assumed all terms were
    #    options and wrapped them in an option() Nonterminal.  This wrapping
    #    neeed to be pushed down into the term__{long,short}_* functions.
    #
    # 3. Unexpected space gap between option-list and newline when no help
    #    provided.  Due to offset, without help, it must be 0.
    #
    # Inner node focused analysis is left as an example. Smaller parse trees
    # are much easier to digest quickly.
    #
    def test_space_arg (self):

        optspecs = od (
            ol ( olst ( opt( '--query', ' ', '<query>' ) ) ) ,
            # ol ( olst ( opt( '-f', ) ) ) ,
            # ol ( olst ( opt( '-f', ) , opt( '--file', '=', '<file>' ) ) ,
            #      "File to load." ) ,
            # ol ( olst ( opt( '-x', '', 'FILE' ), opt( '--extract', ) ) ,
            #      "Extract file." ) ,
            ol ( olst ( opt( '-x', '', 'FILE' ) ) ) ,
            intro="Options :", offset=18 )

        # print("[optspecs]") ; pp(optspecs)

        ( text, opt_desc ) = section_optdesc_obj ( optspecs )

        expect = expect_document ( [ opt_desc ] )

        parsed = self.parse ( text, expect )

        # improper comma separator for operand bug
        if False :
            expect = expect[0][0][0][0][1][1][0]
            parsed = parsed[0][0][0][0][1][1][0]

        # improper 'option' wrapper for 'operand'
        if False :
            expect = expect[0][0][0][0][1][1][1]
            parsed = parsed[0][0][0][0][1][1][1]

        self.verify ( text, expect, parsed )

    #--------------------------------------------------------------------------

    def test_some_args (self): # '--query <query>', expect includes comma

        optspecs = od (
            ol ( olst ( opt( '-f', ), opt( '--file', '=', '<file>' ) ) ,
                 "File to load." ) ,
            ol ( olst ( opt( '-x', '', 'EXTRACT' ), opt( '--extract', ) ) ,
                 "Extract file." ) ,
            ol ( olst ( opt( '-m', ' ', 'MEMBER' ), opt( '--member', ) ) ,
                 "member ..." ) ,
            ol ( olst ( opt( '-q', ), opt( '--query', ' ', '<query>' ) ) ,
                 "Query ..." ) ,
            ol ( olst ( opt( '-h', ), opt( '--help', ) ) ,
                 "Show this usage information." ) ,
            ol ( olst ( opt( '-v', ), opt( '--version', ) ) ,
                 "Print the version and exit." ) ,
            intro="Options :", offset=18 )

        # print("[optspecs]") ; pp(optspecs)

        ( text, opt_desc ) = section_optdesc_obj ( optspecs )

        expect = expect_document ( [ opt_desc ] )

        self.parse_and_verify(text, expect)

    #--------------------------------------------------------------------------

    def parse_and_verify ( self, text, expect ) :
        self.verify ( text, expect, self.parse ( text, expect ) )

    #--------------------------------------------------------------------------

    def parse ( self, text, expect ) :

        # tprint(f"\nOptions :\n{text}")

        # with open ("scratch/expect.txt", 'w') as f :
        #     pp_plain(expect, stream=f)

        try :
            parsed = self.parser.parse(text)
        except :
            print("\nParse FAILED\n"
                  f"[expect]\n{pp_str(expect)}\n"
                  f"text = '{text}' :\n" )
            assert 1 == 0

        # tprint("[parsed]") ; pp(parsed)

        return parsed

    #--------------------------------------------------------------------------

    def verify ( self, text, expect, parsed ) :

        with open ("scratch/expect.txt", 'w') as f :
                pp_plain(expect, stream=f)
        with open ("scratch/parsed.txt", 'w') as f :
            pp_plain(parsed, stream=f)

        if False :
            nth_option_line = 0
            expect = expect[0][0] # [0][ nth_option_line ] # [0] [0]
            parsed = parsed[0][0] # [0][ nth_option_line ] # [0] [0]

            with open ("scratch/expect.txt", 'w') as f :
                    pp_plain(expect, stream=f)
            with open ("scratch/parsed.txt", 'w') as f :
                pp_plain(parsed, stream=f)

            print('')
            print(f"[expect] rule '{expect.rule_name}' with {len(expect)} children")
            print(f"[parsed] rule '{parsed.rule_name}' with {len(parsed)} children")

            for i in range(len(expect)) :
                if not nodes_equal( parsed[i], expect[i]) :
                    print ( f"text = '{text}' :\n"
                            f"[expect]\n{pp_str(expect[i])}\n"
                            f"[parsed]\n{pp_str(parsed[i])}" )
                    assert 1 == 0

            if len(expect) < len(parsed) :
                start = len(expect) # - 1
                print ( f"text = '{text}' :\n"
                        f"[expect]\n{pp_str(expect[start:])}\n"
                        f"[parsed]\n{pp_str(parsed[start:])}" )
                assert 1 == 0

        # print("[expect]");  pp(expect) ; print("[parsed]"); pp(parsed)
        # return

        assert nodes_equal(parsed, expect), \
            ( f"text = '{text}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def tearDown (self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
