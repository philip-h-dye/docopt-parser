parse_debug                     = False
record                          = False
analyzing                       = False

tst_non_object                  = True
tst_minimal                     = True
tst_space                       = True
tst_some_args                   = True

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

from base import Test_Base
from util import tprint, write_scratch

#------------------------------------------------------------------------------

class Test_Usage_Section ( Test_Base ) :

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

    @unittest.skipUnless(tst_non_object, "Non-object tests not enabled")
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

    @unittest.skipUnless(tst_minimal, "Minimal tests not enabled")
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

    @unittest.skipUnless(tst_minimal, "Minimal tests not enabled")
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
    @unittest.skipUnless(tst_space, "Space tests not enabled")
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

        write_scratch ( optdesc = opt_desc )

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

        # ...
        if True :
            expect = expect[0][0][0][1]
            parsed = parsed[0][0][0][1]
            write_scratch ( expect=expect, parsed=parsed )

        self.verify ( text, expect, parsed )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_some_args, "Some args tests not enabled")
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

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
