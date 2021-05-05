import sys
import os
import re

from contextlib import redirect_stdout

# import unicodedata

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, OrderedChoice, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _ , StrMatch, ParseTreeNode

#------------------------------------------------------------------------------

from prettyprinter import cpprint as pp
from docopt_parser.parsetreenodes import NonTerminal_eq_structural
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, newline

from grammar.python.operand import *
# # operand, operand_all_caps, operand_angled
from grammar.python.option import *
# # option, ...

from grammar.python.optdesc.list import option_list, ol_first_option, ol_term
from grammar.python.optdesc.list import ol_term_with_separator, ol_separator
from grammar.python.optdesc.list import ol_space, ol_comma, ol_bar

from docopt_parser import DocOptListViewVisitor

#------------------------------------------------------------------------------

from grammar.python.common import space  as r_space
from grammar.python.common import comma  as r_comma
from grammar.python.common import bar    as r_bar
from grammar.python.common import eq     as r_eq

def r_literal(rule_f, s):
    rule = rule_f()
    if isinstance(rule, str):
        return StrMatch(s, rule_name=rule_f.__name__)
    return rule

t_space   = Terminal(r_literal(r_space  , ' '), 0, ' ')
t_comma   = Terminal(r_literal(r_comma  , ','), 0, ',')
t_bar     = Terminal(r_literal(r_bar    , '|'), 0, '|')
t_eq      = Terminal(r_literal(r_eq     , '='), 0, '=')

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

    # print(f"\n: sep = '{sep}'\n")
    # print(f"\n[ optdefs ]\n") ; pp(optdefs) ; print('')

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
    return NonTerminal( option(), [ Terminal( long_no_arg(), 0, opt ) ] )

def term__long_eq_arg(opt, op):
    return NonTerminal( option(), [
        NonTerminal( long_eq_arg(),
                     [ Terminal( long_no_arg(), 0, opt ) ,
                       t_eq,
                       term__operand(op) ], ) ])

def term__short_no_arg(opt):
    return NonTerminal( option(), [ Terminal( short_no_arg(), 0, opt ) ] )

def term__short_adj_arg(opt, op):
    return NonTerminal( option(), [
        NonTerminal( short_adj_arg(),
                     [ Terminal( short_adj_arg__option(), 0, opt ) ,
                       term__operand(op) ], ) ])

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

    sep_ol_space = NonTerminal( ol_separator(),
                                [ NonTerminal( ol_space(), [ t_space ] ) ] )

    if sep is None :
        return sep_ol_space

    if not isinstance(sep, str):
        raise ValueError(f"Unreconized expect <sep>, type {str(type(sep))}, value '{repr(sep)}'.\n"
                         "Expected None, a string or perhaps a ParseTreeNode.")

    if len(sep) <= 0:
        # Zero isn't possible since things would run into each other and
        # could not then necessarily be parsed.
        return sep_ol_space

    if len(sep) > 3:
        raise ValueError(f"<sep> too long, at most 3 possible.  Please resolve.")

    saved_sep = sep

    if sep == ' ':
        return sep_ol_space

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
        core = NonTerminal( ol_comma(), [ t_comma ] )
    elif sep[0] == '|' :
        core = NonTerminal( ol_bar(), [ t_bar ] )
    else :
        raise ValueError(
            f"'{sep[0]}' is not a valid option-list separator.  Valid "
            f"separators are COMMA ',', BAR '|' and a SPACE ' '.  "
            f"Additionally, COMMA and BAR may be optionally preceeded"
            f"/followed by one space on each side.")

    if preceeded:
        core.insert(0, t_space)
    if followed:
        core.append(t_space)

    return NonTerminal( ol_separator(), [ core ] )

#------------------------------------------------------------------------------

def create_expect ( *terminals, sep = None ) :

    separator = expect_separator(sep)
    sep_space = expect_separator(' ')

    # FIXME: create global for 'SPACE'

    if len(terminals) <= 0 :
        raise ValueError("No terminals provided.  Please provide at least one.")

    expect = NonTerminal( document(), [
        NonTerminal( body(), [
            NonTerminal( element(), [
                NonTerminal( option_list(), [
                    NonTerminal( ol_first_option(), [ terminals[0], ]) ,
                    * [
                        NonTerminal( ol_term_with_separator(), [
                            # separator,
                            (sep_space if term.rule_name == 'operand'
                             else separator) ,
                            NonTerminal( ol_term(), [ term ]) ,
                        ])
                        for term in terminals[1:]
                    ],
                ]) ,
            ]) ,
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

from dataclasses import dataclass
from typing import List

class OperandDef (str):
    style : object

@dataclass
class OptionDef (object):
    opt : str
    gap	: str		= None
    operand : str	= None

# opt = OptionDef

# OptionListDef = list[OptionDef]  # 3.9

# olst = OptionListDef

#------------------------------------------------------------------------------

class OptionListDef(list):

    def __init__(self, *elements):
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
            assert isinstance(value, OptionDef), \
                ( f"OptionListDef elements must be of type OptionDef, "
                  f"not {str(type(value))}" )
        super().__init__(elements)

    def __setitem__(self, idx, value):
        assert isinstance(value, OptionDef), \
            ( f"OptionListDef elements must be of type OptionDef, "
              f"not {str(type(value))}" )
        super().__setitem__(idx, value)

#------------------------------------------------------------------------------

from prettyprinter import register_pretty, pretty_call

@register_pretty(OptionDef)
def pretty_OptionDef(value, ctx):
    return pretty_call(
        ctx,
        OptionDef,
        opt=value.opt,
        gap=value.gap,
        operand=value.operand,
)

@register_pretty(OptionListDef)
def pretty_OptionListDef(value, ctx):
    return pretty_call(
        ctx,
        OptionListDef,
        contents=list(value),
)

#------------------------------------------------------------------------------

def create_terms_obj ( optlst, sep = ' ' ):

    # print(f"\n: sep = '{sep}'\n")

    ( texts, terms ) = create_termx_obj ( optlst )

    return ( sep.join(texts), terms )

#------------------------------------------------------------------------------

def create_termx_obj ( optlst ):

    # print(f"\n[ optlst ]\n") ; pp(optlst) ; print('')

    texts = [ ]
    terms = [ ]

    for o in optlst :
        # ( opt, gap, operand, *extra ) = ( *optdef, None, None )
        if o.operand is None:
            o.operand = ''
            o.gap = ''
        elif o.gap is None:
            o.gap = ''

        if re_short.fullmatch(o.opt):
            if o.operand:
                if o.gap == '':
                    terms.append ( term__short_adj_arg(o.opt, o.operand) )
                    texts.append ( o.opt + o.gap + o.operand )
                else :
                    terms.append ( term__short_no_arg(o.opt) )
                    terms.append ( term__operand(o.operand) )
                    texts.append ( o.opt )
                    texts.append ( o.operand )
            else :
                    terms.append ( term__short_no_arg(o.opt) )
                    texts.append ( o.opt )

        elif re_long.fullmatch(o.opt):
            if o.operand:
                if o.gap == '=':
                    terms.append ( term__long_eq_arg(o.opt, o.operand) )
                    texts.append ( o.opt + o.gap + o.operand )
                else :
                    terms.append ( term__long_no_arg(o.opt) )
                    terms.append ( term__operand(o.operand) )
                    texts.append ( o.opt )
                    texts.append ( o.operand )
            else :
                    terms.append ( term__long_no_arg(o.opt) )
                    texts.append ( o.opt )

        else :
            raise ValueError(
                f"Invalid option '{o.opt}' in optdef '{o}'.\n"
                f"Please provide a short or long without an "
                f"argument.  Place arguments go in the third position.\n"
                f"  ( (<option> <gap> <operand>), ... )\n"
                f"Example:  ol( opt( '--file', ' ', '<file>' ),\n"
                f"              opt( '--long', '=', '<long' ),\n"
                f"              opt( '--quit' ), )\n" )

    return ( texts, terms )

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

def optlst_permutations ( *words, n_opt_max=3 ):

    words = flatten(words)

    options = [ ]

    for word in words :

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

        for length in range(1, min(n_opt_max,len(options)+1)) :
            for result in itertools.permutations(options, length) :
                yield result

#------------------------------------------------------------------------------

def generate_tests_on_optlst_varying_sep ( cls, _generate, optlst ) :

    # sep default
    _generate ( cls, optlst )

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

    for sep in [ ' ' ] :
        _generate ( cls, optlst, sep=sep )

    for ch in [ ',', '|' ] :
        for before in [ '', ' ' ] :
            for after in [ '', ' ' ] :
                sep = before + ch + after
                _generate ( cls, optlst, sep=sep )

#------------------------------------------------------------------------------

def generate_tests__all_permutations_of_optlst_and_sep ( cls, _generate, words, n_opt_max=3 ) :

    generate_tests_on_optlst_varying_sep ( cls, _generate, ( ( '-h', ), ( '--help', ) ) )

    for optlst in optlst_permutations ( *words, n_opt_max=n_opt_max ) :
        generate_tests_on_optlst_varying_sep ( cls, _generate, optlst )

#------------------------------------------------------------------------------
