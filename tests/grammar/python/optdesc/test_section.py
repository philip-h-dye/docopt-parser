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
from grammar.python.optdesc.section import *

from docopt_parser import DocOptListViewVisitor

from optsect import tprint, document, body, element, create_expect
from optsect import create_expect, create_terms
from optsect import expect_document, expect_ol_line
from optsect import section_optdesc

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

    def _test_show_parse(self):
        input = ( "  -f  F flag\n"
                  "  -x  X flag\n" )
        parsed = self.parser.parse(input)
        tprint("[parsed]") ; pp(parsed)

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

        tprint(f"\nOptions :\n{text}")

        parsed = self.parser.parse(text)
        # tprint("[parsed]") ; pp(parsed)
        # with open ("parsed.txt", 'w') as f :
        #     pp_plain(parsed, stream=f)

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n"
                                   f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def WIP_test_minimal_obj(self):

        from optlist import OptionDef as opt, OptionListDef as olst
        from optline import OptionLineDef as ol

        olst_1   = olst ( opt( '-h', ), opt( '--help', ) )
        oline_1  = ol   ( olst_1, "Show this usage information." )
        olst_2   = olst ( opt( '-v', ), opt( '--version', ) )
        oline_2  = ol   ( olst_2, "Print the version and exit." )
        ol_line_specs = [ oline_1, oline_2 ]

        ( text, opt_desc ) = section_optdesc_obj ( ol_line_specs )

        expect = expect_document ( [ opt_desc ] )
        # tprint("[expect]") ; pp(expect)
        # with open ("expect.txt", 'w') as f :
        #     pp_plain(expect, stream=f)

        tprint(f"\nOptions :\n{text}")

        parsed = self.parser.parse(text)
        # tprint("[parsed]") ; pp(parsed)
        # with open ("parsed.txt", 'w') as f :
        #     pp_plain(parsed, stream=f)

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n"
                                   f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def SKIP_test_create_expect(self):

        input = '-f -x -l'

        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)

        expect = create_expect (
            Terminal( short_no_arg(), 0, '-f' ) ,
            Terminal( short_no_arg(), 0, '-x' ) ,
            Terminal( short_no_arg(), 0, '-l' ) ,
            eof = ( input[-1] != '\n' ) ,
        )

        assert parsed == expect, ( f"input = '{input}' :\n"
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
