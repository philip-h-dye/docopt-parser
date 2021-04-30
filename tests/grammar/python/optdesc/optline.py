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

from test_list import create_terms, method_name

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

    def create_method ( actual_input, the_terms ) :
        def the_test_method (self) :
            input = actual_input
            terms = the_terms
            parsed = self.parser.parse(input)
            # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
            # tprint("[parsed]") ; pp(parsed)
            # tprint(f"\ninput = '{input}'\n")            
            expect ( input, parsed, *terms, sep=sep )

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

# Restricted set for now:
#   - single space
#   - comma ',' : optionally preceeded and/or followed by a space
#   - bar   '|' : optionally preceeded and/or followed by a space

def expect_separator(sep):

    space = Terminal( StrMatch(' ', rule='SPACE'), 0, ' ')
    comma = Terminal( StrMatch(',', rule='COMMA'), 0, ',')
    bar = Terminal( StrMatch('|', rule='BAR'), 0, '|')

    if sep is None :
        return space

    if not isinstance(sep, str):
        raise ValueError(f"Unreconized expect <sep>, type {str(type(sep))}, value '{repr(sep)}'.\n"
                         "Expected None, a string or perhaps a ParseTreeNode.")

    if len(sep) <= 0:
        # Zero isn't possible since things would run into each other and
        # could not then necessarily be parsed.
        return space

    if len(sep) > 3:
        raise ValueError(f"<sep> too long, at most 3 possible.  Please resolve.")

    saved_sep = sep

    if sep == ' ':
        return space

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

    expect = NonTerminal( document(), [
        NonTerminal( body(), [
            NonTerminal( element(), [
                NonTerminal( option_line(), [
                    NonTerminal( option_list(), [
                        NonTerminal( ol_first_option(), [
                            NonTerminal( option(), [
                                terminals[0],
                            ]) ,
                        ]) ,
                        * [
                            NonTerminal( ol_term_with_separator(), [
                                separator,
                                NonTerminal( ol_term(), [
                                    NonTerminal( option(), [
                                        term
                                    ]) ,
                                ]) ,
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
