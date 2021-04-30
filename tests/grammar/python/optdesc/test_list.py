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
from docopt_parser.parsetreenodes import NonTerminal_eq_structural
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, newline, COMMA, BAR
from grammar.python.operand import *
# # operand, operand_all_caps, operand_angled
from grammar.python.option import *
# # option, ...

from grammar.python.optdesc.list import option_list, ol_first_option, ol_term
from grammar.python.optdesc.list import ol_term_with_separator, ol_separator

from docopt_parser import DocOptListViewVisitor

#------------------------------------------------------------------------------

grammar_elements = [ option_list, ws, newline ]

def element():
    # To work properly, first argumnet of OrderedChoice must be a
    # list.  IF not, it implicitly becomes Sequence !
    return OrderedChoice ( [ *grammar_elements ], rule_name='element' )

def body():
    return OneOrMore ( element, rule_name='body' )

def document():
    return Sequence( body, EOF, rule_name='document' )

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

    def SKIP_test_single_short_no_arg (self):
        input = '-f'
        parsed = self.parser.parse(input)
        tprint("[parsed]") ; pp(parsed)
        expect ( input, parsed,
                 Terminal( short_no_arg(), 0, '-f' ) ,
        )

    #--------------------------------------------------------------------------

    def SKIP_test_single_short_with_one_arg (self):
        input = '-fNORM'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)
        expect ( input, parsed,
            NonTerminal( short_adj_arg(), [
                Terminal( short_adj_arg__option(), 0, '-f' ) ,
                NonTerminal( operand(), [
                    Terminal( operand_all_caps(), 0, 'NORM' ) ,
                ]) ,
            ]) ,
        )

#------------------------------------------------------------------------------

# Assumming well-formed optdefs, with well-formed being :
#   - Every optdef is a tuple or list like object of one to three strings
#   - The first element is a wellformed short or long option with no argument
#   - The second element is the gap character between the option and its
#     operand -- empty string if none.
#     elements with the later two allowed to by None
#   - allowing None in place of empty string
#   -
#

def create_terms ( optdefs, sep = ' ' ):

    print(f"\n: sep = '{sep}'\n")
    print(f"\n[ optdefs ]\n") ; pp(optdefs) ; print('')

    input = [ ]
    terms = [ ]

    for optdef in optdefs :
        ( opt, gap, operand, *extra ) = ( *optdef, None, None )
        if operand is None:
            operand = ''
            gap = ''
        elif gap is None:
            gap = ''

        input.append(opt + gap + operand)

        if re_short.fullmatch(opt):
            if operand:
                if gap == '':
                    terms.append ( term__short_adj_arg(opt, operand) )
                else :
                    terms.append ( term__short_no_arg(opt) )
                    terms.append ( term__operand(operand) )
            else :
                    terms.append ( term__short_no_arg(opt) )

        elif re_long.fullmatch(opt):
            if operand:
                if gap == '=':
                    terms.append ( term__long_eq_arg(opt, operand) )
                else :
                    terms.append ( term__long_no_arg(opt) )
                    terms.append ( term__operand(operand) )
            else :
                    terms.append ( term__long_no_arg(opt) )

        else :
            raise ValueError(
                f"Invalid option '{opt}' in optdef '{optdef}'.\n"
                f"Please provide a short or long without an "
                f"argument.  Place arguments go in the third position.\n"
                f"  ( (<option> <gap> <operand>), ... )\n"
                f"Example:  ( ( '--file', ' ', '<file>' ),\n"
                f"            ( '--long', '=', '<long' ),\n"
                f"            ( '--quit' ), )\n" )

    return ( sep.join(input), terms )

#------------------------------------------------------------------------------

def term__long_no_arg(opt):
    return Terminal( long_no_arg(), 0, opt)

def term__long_eq_arg(opt, op):
    return NonTerminal( long_eq_arg(),
                        [ term__short_no_arg(opt),
                          StrMatch('=', rule='EQ'),	# FIXME: create global
                          term__operand(op) ], )

def term__short_no_arg(opt):
    return Terminal( short_no_arg(), 0, opt)

def term__short_adj_arg(opt, op):
    return NonTerminal( short_adj_arg(),
                        [ Terminal( short_adj_arg__option(), 0, opt ) ,
                          term__operand(op) ], )

def term__operand(op):
    if re_operand_angled.fullmatch(op) :
        operand_type = operand_angled
    elif re_operand_all_caps.fullmatch(op) :
        operand_type = operand_all_caps
    else :
        raise ValueError(
            f"Invalid optdef operand '{op}'.  Expected either an "
            f"angle operand, '<foo>', or all caps, 'FOO'.  Please address.")

    return NonTerminal( operand(), [ Terminal( operand_type(), 0, op ) ] )

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

def expect ( input, parsed, *terminals, sep = None ) :

    separator = expect_separator(sep)

    # FIXME: create global for 'SPACE'

    if len(terminals) <= 0 :
        raise ValueError("No terminals provided.  Please provide at least one.")

    expect = NonTerminal( document(), [
        NonTerminal( body(), [
            NonTerminal( element(), [
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
            ]) ,
        ]) ,
        Terminal(EOF(), 0, '') ,
    ])

    assert parsed == expect, ( f"[expect]\n{pp_str(expect)}\n"
                               f"[parsed]\n{pp_str(parsed)}"
                               f"input = '{input}' :\n" )

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

def re_compile(f):
    r = f()
    r.compile()
    return r.regex

re_short		= re_compile(short_no_arg)
re_long			= re_compile(long_no_arg)
re_operand_angled	= re_compile(operand_angled)
re_operand_all_caps	= re_compile(operand_all_caps)

#------------------------------------------------------------------------------

def replace_matching ( name, matcher, prefix ):

    if matcher.search(name) :
        name1 = name
        name = ''
        pos = 0
        for m in matcher.finditer(name1):
            name += name1[pos:m.start()] + prefix + m.group(1)
            pos = m.end()
        name += name1[pos:]

    return name

#------------------------------------------------------------------------------

underscores		= re.compile(r'_+')
eq_option_angle		= re.compile(r'=<([^>]+)>')
eq_option_caps		= re.compile(r'=([A-Z][A-Z]+\b)')
			# '\b' so that not accept '=FOO' of '=FOObar'
eq_option_other		= re.compile(r'=([\S]+)')

# FIXME:  floating values for invalid input tests, any non-identifier character

def method_name ( initial_input ):

    # FIXME: Simplify flow here using separate function: method_name(<input>)

    name = initial_input
    # tprint(f"[1] name      =  '{name}'")
    name = name.replace('-','dash_').replace(' ','_space_').replace('space__','space_')
    # tprint(f"[2] name      =  '{name}'")

    # '=<ARG>' => '_eq_angle_ARG'
    name = replace_matching ( name, eq_option_angle, '_eq_angle_')
    # '=ARG' => '_eq_caps_ARG'
    name = replace_matching ( name, eq_option_caps, '_eq_caps_' )
    # '=\S+' => '_eq_other_ARG'
    name = replace_matching ( name, eq_option_other, '_eq_other_' )

    name = name.replace('|', '_BAR_')
    name = name.replace(',', '_comma_')

    name = underscores.sub(name, '_')

    # During ALPHA, trap any unexpected characters by crashing
    #   reenable for BETA and beyond
    if False : # not name.isidentifier() :
        gather = [ ]
        for ch in name :
            if ch.isidentifier() :
                gather.append ( ch )
            else :
                gather.append ( unicodedata.name(ch).replace(' ','_') )
        name = ''.join(gather)

    return 'test_' + name

#------------------------------------------------------------------------------

def ol_generate ( cls, optdefs, sep =', ' ) :

    def create_method ( actual_input, the_terms ) :
        def the_test_method (self) :
            input = actual_input
            terms = the_terms
            parsed = self.parser.parse(input)
            # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
            tprint("[parsed]") ; pp(parsed)
            tprint(f"\ninput = '{input}'\n")
            # expect ( input, parsed, *terms, sep=sep )
        return the_test_method

    ( initial_input, terms ) = create_terms( optdefs, sep = sep )

    name = method_name(initial_input)

    setattr ( cls, name, create_method ( initial_input, terms ) )

    if False :
        setattr ( cls, f"{name}__newline",
                  create_method ( initial_input + '\n', terms ) )
        for n_spaces in range(1) : # range(4):
            setattr ( cls, f"{name}__trailing_{n_spaces}",
                      create_method ( initial_input + ( ' ' * n_spaces ) ) )

    return initial_input

#------------------------------------------------------------------------------

def _generate ( optdef, *args, **kwargs ):
    # ol_generate ( Test_Option_List, optdef, *args, **kwargs )
    pass

#------------------------------------------------------------------------------

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
if False  :
    _generate ( ( ( '--file', '=', 'FOObar', ) ,
                  ( '-x', ) ,
                ) )

# generate("--file=a|b|c -x")
if False  :
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

if False :
    text = ol_generate ( Test_Option_List, ( ( '-h', ), ( '--help', ) ), sep=' ')
    print('')
    print('* * *')
    print(f"===> '{text}'")
    print('* * *')
    print('')

#------------------------------------------------------------------------------

if False :
    text = ol_generate ( Test_Option_List, ( ( '-h', ), ( '--help', ) ), sep=', ')
    print('')
    print('* * *')
    print(f"===> '{text}'")
    print('* * *')
    print('')

#------------------------------------------------------------------------------

if True :
    text = ol_generate ( Test_Option_List, ( ( '-h', ), ( '--help', ) ), sep=' | ')
    print('')
    print('* * *')
    print(f"===> '{text}'")
    print('* * *')
    print('')

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
