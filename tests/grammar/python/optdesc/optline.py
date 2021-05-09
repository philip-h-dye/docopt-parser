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

# option_list, ol_first_option, ol_term
from grammar.python.optdesc.list import *
from grammar.python.optdesc.line import *

from docopt_parser import DocOptListViewVisitor

# from test_list import create_terms, method_name
from .optlist import create_terms, method_name

#------------------------------------------------------------------------------

ALL = ( ' document body element grammar_elements '
        ' ogenerate expect create_expect '
        ' tprint '
      )

#------------------------------------------------------------------------------

grammar_elements = [ option_line, ws, newline ]

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

    def create_method ( actual_text, the_terms ) :
        def the_test_method (self) :
            text = actual_text
            terms = the_terms
            parsed = self.parser.parse(text)
            # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
            # tprint("[parsed]") ; pp(parsed)
            # tprint(f"\ntext = '{text}'\n")
            expect ( text, parsed, *terms, sep=sep )

        return the_test_method

    ( initial_text, terms ) = create_terms( optdefs, sep = sep ) # ', '

    name = method_name(initial_text)

    setattr ( cls, name, create_method ( initial_text, terms ) )

    if False :
        setattr ( cls, f"{name}__newline",
                  create_method ( initial_text + '\n', terms ) )
        for n_spaces in range(1) : # range(4):
            setattr ( cls, f"{name}__trailing_{n_spaces}",
                      create_method ( initial_text + ( ' ' * n_spaces ) ) )

    return ( name, initial_text )

#------------------------------------------------------------------------------

# Restricted set for now:
#   - single space
#   - comma ',' : optionally preceeded and/or followed by a space
#   - bar   '|' : optionally preceeded and/or followed by a space

def expect_separator(sep):

    space = NonTerminal( ol_space(), [ Terminal( StrMatch(' ', rule_name=''), 0, ' ') ] )
    comma = NonTerminal( ol_comma(), [ Terminal( StrMatch(',', rule_name=''), 0, ',') ] )
    bar   = NonTerminal( ol_bar(),   [ Terminal( StrMatch('|', rule_name=''), 0, '|') ] )

    if sep is None :
        return NonTerminal( ol_separator(), [ space ] )

    if not isinstance(sep, str):
        raise ValueError(f"Unreconized expect <sep>, type {str(type(sep))}, value '{repr(sep)}'.\n"
                         "Expected None, a string or perhaps a ParseTreeNode.")

    if len(sep) <= 0:
        # Zero isn't possible since things would run into each other and
        # could not then necessarily be parsed.
        return NonTerminal( ol_separator(), [ space ] )

    if len(sep) > 3:
        raise ValueError(f"<sep> too long, at most 3 possible.  Please resolve.")

    saved_sep = sep

    if sep == ' ':
        return NonTerminal( ol_separator(), [ space ] )

    #--------------------------------------------------------------------------

    # Preceeding spaces

    preceeded = 0
    while sep[0] == ' ':
        preceeded += 1
        sep = sep[1:]

    if preceeded > 1:
        if len(sep) > 0:
            raise ValueError(
                f"option-list separator string '{save_sep}' improperly has separating "
                f"character '{sep[0]}' preceeded by two spaces.  "
                f"No two consequtive spaces permitted since such marks the end of "
                f"the option-list and the start of the option help text")
        else :
            raise ValueError(
                f"option-list separator string '{save_sep}' is all spaces.  "
                f"No two consequtive spaces permitted since such marks the end of "
                f"the option-list and the start of the option help text")

    #--------------------------------------------------------------------------

    # Trailing

    followed = 0
    while sep[-1] == ' ':
        followed += 1
        sep = sep[:-1]

    if followed > 1:
        raise ValueError(
            f"option-list separator string '{save_sep}' improperly has separating "
            f"character '{sep[0]}' followed by two spaces.  "
            f"No two consequtive spaces permitted since such marks the end of "
            f"the option-list and the start of the option help text")

    #--------------------------------------------------------------------------

    if sep[0] == ',':
        core = NonTerminal( ol_comma(), [ comma ] )
    elif sep[0] == '|' :
        core = NonTerminal( ol_bar(), [ bar ] )
    else :
        raise ValueError(
            f"'{sep[0]}' is not a valid option-list separator.  Valid "
            f"separators are COMMA ',', BAR '|' and a SPACE ' '.  "
            f"Additionally, COMMA and BAR may be optionally preceeded"
            f"/followed by one space on each side.")

    if preceeded:
        core.insert(0, space)
    if followed:
        core.append(space)

    return NonTerminal( ol_separator(), [ core ] )

#------------------------------------------------------------------------------

def expect ( text, parsed, *terms, sep = ', ' ) :

    # tprint("[parsed]") ; pp(parsed)

    expect = create_expect ( *terms, eof = ( text[-1] != '\n' ), sep=sep )

    assert parsed == expect, ( f"text = '{text}' :\n"
                               f"[expect]\n{pp_str(expect)}\n"
                               f"[parsed]\n{pp_str(parsed)}" )

#------------------------------------------------------------------------------

def create_expect ( *terminals, eof=False, sep = None ) :

    if len(terminals) <= 0 :
        raise ValueError("No terminals provided.  Please provide at least one.")

    separator = expect_separator(sep)
    sep_space = expect_separator(' ') # required for operands
    # print("[sep-space]")
    # pp(sep_space)

    expect = NonTerminal( document(), [
        NonTerminal( body(), [
            NonTerminal( element(), [
                NonTerminal( option_line(), [
                    NonTerminal( option_list(), [
                        NonTerminal( ol_first_option(), [ terminals[0] ]),
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
        Terminal(EOF(), 0, '') ,
    ])

    if eof :
        expect[0][0][0].append(expect[-1])

    return expect

#------------------------------------------------------------------------------

def option_line_generate ( spec, sep=', ', indent='  ', offset=16 ) :
    ( optlist_string, terms ) = create_terms( spec[0], sep = sep )
    help_ = spec[1]
    if help_ is None :
        help_ = ''
    gap = '  ' if len(help_) > 0 else ''
    # text += f"{indent}{optlist_string:<{offset}}  {help_}\n"
    # text += f"{indent}{optlist_string:<{offset}}  {help_}\n"
    text = f"{indent}{optlist_string:<{offset}}{gap}{help_}\n"
    # print(f"opt-list :  '{text_[:-1]}'")
    expect = option_line_expect \
        ( *terms, sep=sep, indent=indent, gap=gap, help_=help_,
          extra=(offset-len(optlist_string)) )

    return ( text, expect )

#------------------------------------------------------------------------------

def option_line_expect ( *terminals, eof=False, sep=None, indent=None,
                           gap=None, help_=None, extra=0 ) :

    if len(terminals) <= 0 :
        raise ValueError("No terminals provided.  Please provide at least one.")

    separator = expect_separator(sep)
    sep_space = expect_separator(' ') # required for operands
    # print("[sep-space]")
    # pp(sep_space)

    members = [
        NonTerminal( option_list(), [
            NonTerminal( ol_first_option(), [ terminals[0], ]) ,
            * [
                NonTerminal( ol_term_with_separator(), [
                    # separator,
                    (sep_space if term.rule_name == 'operand'
                     else separator) ,
                    NonTerminal( ol_term(), [ term ] ),
                ])
                for term in terminals[1:]
            ],
        ]),
        Terminal(newline(), 0, '\n'),
    ]

    if indent and len(indent) > 0:
        members.insert(0, Terminal(StrMatch(' ',rule_name='wx'), 0, indent) )

    if help_ and len(help_) > 0:
        if extra < 0:
            extra = 0
        # print(f": extra = {extra}")
        gap += ' ' * extra
        members.insert( -1, Terminal(StrMatch(gap, rule_name='option_line_gap'), 0, gap))
        members.insert( -1, Terminal(StrMatch('.', rule_name='option_line_help'), 0, help_))

    expect = NonTerminal( option_line(), [ *members ])

    if eof :
        expect.append( Terminal(EOF(), 0, '') )

    return expect

#------------------------------------------------------------------------------

from util import tprint

#------------------------------------------------------------------------------

from dataclasses import dataclass

from .optlist import OptionDef, OptionListDef, create_terms_obj

@dataclass
class OptionLineDef (object):
    options     : OptionListDef
    help_       : str = None
    sep         : str = None
    indent      : str = None
    gap         : int = None	# default gap size, minimum of two spaces
    offset      : int = None    # default width of option-list

# opt   = OptionDef
# olst  = OptionListDef
# ol    = OptionLineDef

#------------------------------------------------------------------------------

from prettyprinter import register_pretty, pretty_call

@register_pretty(OptionLineDef)
def pretty_OptionLineDef(value, ctx):
    return pretty_call(
        ctx,
        OptionLineDef,
        options=value.options,
        help_=value.help_,
)

#------------------------------------------------------------------------------

def option_line_generate_obj ( spec, sep=', ', indent='  ', offset=16 ) :
    ( optlist_string, terms ) = create_terms_obj ( spec.options, sep = sep )
    if spec.help_ is None :
        spec.help_ = ''
    if len(spec.help_) <= 0:
        spec.gap = ''
        offset = 0 # eliminate unexpected gap
    else :
        if spec.gap is None or len(spec.gap) < 2 :
            spec.gap = '  '
    text = f"{indent}{optlist_string:<{offset}}{spec.gap}{spec.help_}\n"
    expect = option_line_expect \
        ( *terms, sep=sep, indent=indent, gap=spec.gap, help_=spec.help_,
          extra=(offset-len(optlist_string)) )
    return ( text, expect )

#------------------------------------------------------------------------------
