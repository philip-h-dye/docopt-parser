import sys
import os
import re

from contextlib import redirect_stdout

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, OrderedChoice, ZeroOrMore, OneOrMore, EOF
from arpeggio import And, Not, RegExMatch as _

#------------------------------------------------------------------------------

from prettyprinter import cpprint as pp
from docopt_parser.parsetreenodes import NonTerminal_eq_structural
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, newline, COMMA, BAR
from grammar.python.operand import operand, operand_all_caps, operand_angled
from grammar.python.option import *

# option_list, ol_first_option, ol_term
from grammar.python.optdesc.list import *
from grammar.python.optdesc.line import *
from grammar.python.optdesc.section import *

from docopt_parser import DocOptListViewVisitor

# from test_list import create_terms, method_name
from optlist import create_terms, method_name
from optline import expect_separator

#------------------------------------------------------------------------------

ALL = ( ' document body element grammar_elements '
        ' ogenerate expect create_expect '
        ' expect_ol_line '
        ' tprint '
      )

#------------------------------------------------------------------------------

grammar_elements = [ option_description_section, blank_line, newline, ws ]

def element():
    # To work properly, first argumnet of OrderedChoice must be a
    # list.  IF not, it implicitly becomes Sequence !
    return OrderedChoice ( [ *grammar_elements ], rule_name='element' )

def body():
    return OneOrMore ( element, rule_name='body' )

def document():
    return Sequence( body, EOF, rule_name='document' )

#------------------------------------------------------------------------------

def ogenerate ( cls, optdefs, sep= ', ') :

    def create_method ( actual_input, the_terms ) :
        def the_test_method (self) :
            input = actual_input
            terms = the_terms
            parsed = self.parser.parse(input)
            # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
            # tprint("[parsed]") ; pp(parsed)
            # DEFER
            # ? # expect ( input, parsed, *terms, sep=sep )
            # tprint(f"\ninput = '{input}'\n")
        return the_test_method

    ( initial_input, terms ) = create_terms( optdefs, sep = sep ) # ', '

    name = method_name(initial_input)

    setattr ( cls, name, create_method ( initial_input, terms ) )

    if False :
        setattr ( cls, f"{name}__newline",
                  create_method ( initial_input + '\n', terms ) )
        for n_spaces in range(1) : # range(4):
            setattr ( cls, f"{name}__trailing_{n_spaces}",
                      create_method ( initial_input + ( ' ' * n_spaces ) ) )

    return ( name, initial_input )

#------------------------------------------------------------------------------

def expect ( input, parsed, *terms, sep = ', ' ) :

    # tprint("[parsed]") ; pp(parsed)

    expect = create_expect ( *terms, eof = ( input[-1] != '\n' ), sep=sep )

    assert parsed == expect, ( f"input = '{input}' :\n"
                               f"[expect]\n{pp_str(expect)}\n"
                               f"[parsed]\n{pp_str(parsed)}" )

#------------------------------------------------------------------------------

def create_expect ( *terminals, eof=False, sep = None ) :

    if len(terminals) <= 0 :
        raise ValueError("No terminals provided.  Please provide at least one.")

    separator = expect_separator(sep)
    sep_space = expect_separator(' ') # required for operands

    expect = NonTerminal( document(), [
        NonTerminal( body(), [
            NonTerminal( element(), [
                NonTerminal( option_description_section(), [
                    NonTerminal( option_line(), [
                        NonTerminal( option_list(), [
                            NonTerminal( ol_first_option(), [ terminals[0], ]) ,
                            * [
                                NonTerminal( ol_term_with_separator(), [
                                    (sep_space if term.rule_name == 'operand'
                                     else separator) ,
                                    NonTerminal( ol_term(), [ term ]),
                                ])
                                for term in terminals[1:]
                            ],
                        ]) ,
                        # Terminal(EOF(), 0, '') , # only if specified via 'eof'
                    ]) ,
                ]) ,
            ]) ,
        ]) ,
        Terminal(EOF(), 0, '') ,
    ])

    if eof :
        expect[0][0][0].append(expect[-1])

    return expect

#------------------------------------------------------------------------------

from optline import option_line_generate
from optline import option_line_generate as expect_ol_line

def section_optdesc ( line_specs, sep=', ', intro=None, indent='  ',
                      offset=16 ) :
    text = ''

    opt_desc = NonTerminal( option_description_section(),
                            [ Terminal(StrMatch('.'), 0, 'place-holder') ] )
    del opt_desc[0]

    for spec in line_specs :
        ( text_, expect_ ) = option_line_generate \
            ( spec, sep=sep, indent=indent, offset=offset )
        text += text_
        opt_desc.append ( expect_ )

    return ( text, opt_desc )

#------------------------------------------------------------------------------

def expect_document ( sections ) :

    if len(sections) <= 0 :
        raise ValueError("No sections provided.  Please provide at least one.")

    expect = NonTerminal( document(), [
        NonTerminal( body(), [
            NonTerminal( element(), sections )
        ]) ,
        Terminal(EOF(), 0, '') ,
    ])

    return expect

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    if tprint._on :
        kwargs['file'] = tprint._file
        print('')
        print(*args, **kwargs)
        tprint._file.flush()

# tprint._file = sys.stdout
tprint._file = open("/dev/tty", 'w')
# tprint._on = False
tprint._on = True

#------------------------------------------------------------------------------

# from typing import List
from dataclasses import dataclass, field

from optlist import OptionDef, OptionListDef
from optline import OptionLineDef

# @dataclass
# class OptionDescDef (list):
#     # lines   : List[OptionLineDef] = field(default_factory=list)
#     sep     : str = ', '
#     indent  : str = '  '
#     int     : int = 2
#     offset  : int = 16
#     intro   : str = None

# opt   = OptionDef
# olst  = OptionListDef
# ol    = OptionLineDef
# od    = OptionDescDef

#------------------------------------------------------------------------------

class OptionDescDef(list):

    def __init__(self, *elements, sep=', ', gap=2, indent='  ',
                 offset=16, intro=None) :
        # print(f": elements = {repr(elements)}")
        if len(elements) == 1:
            try :
                iter(elements[0])
                elements = elements[0]
            except:
                pass
        # print(f": elements = {repr(elements)}")
        for value in elements :
            # print(f": value = {repr(value)}")
            assert isinstance(value, OptionLineDef), \
                ( f"OptionDescDef elements must be of type OptionLineDef, "
                  f"not {str(type(value))}" )
        super().__init__(elements)
        self.sep     = sep
        self.indent  = indent
        self.gap     = gap	# gap size, minimum of 2 spaces
        self.offset  = offset	# default width of option-list
        self.intro   = intro

        if self.gap is None or self.gap < 2 :
            self.gap = 2

    def __setitem__(self, idx, value):
        assert isinstance(value, OptionLineDef), \
            ( f"OptionDescDef elements must be of type OptionLineDef, "
              f"not {str(type(value))}" )
        super().__setitem__(idx, value)

#------------------------------------------------------------------------------

from prettyprinter import register_pretty, pretty_call

@register_pretty(OptionDescDef)
def pretty_OptionDescDef(value, ctx):
    return pretty_call(
        ctx,
        OptionDescDef,
        contents=list(value),
)

#------------------------------------------------------------------------------

from optline import option_line_generate_obj

def section_optdesc_obj ( optspecs ):

    text = ''

    opt_desc = NonTerminal( option_description_section(),
                            [ Terminal(StrMatch('.'), 0, 'place-holder') ] )
    del opt_desc[0]

    os = optspecs
    for spec in optspecs :
        ( text_, expect_ ) = option_line_generate_obj \
            ( spec, sep=os.sep, indent=os.indent, offset=os.offset )
        # print(f"[optsect] text_\n{text_}\n")
        # print(f"[optsect]\n{pp_str(expect_)}\n")
        text += text_
        opt_desc.append ( expect_ )

    return ( text, opt_desc )

#------------------------------------------------------------------------------
