import os

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, ZeroOrMore, OneOrMore, EOF
from arpeggio import ParseTreeNode, RegExMatch as _

from contextlib import redirect_stdout

from typing import List, Tuple

from prettyprinter import cpprint as pp, pprint as pp_plain

from p import pp_str

from util import tprint, write_scratch

#------------------------------------------------------------------------------

from grammar.python.common import ws, space as r_space, WHITESPACE_CHARS
from grammar.python.usage import *

from optdesc.optlist import create_termx_obj, method_name, term__operand
from optdesc.optlist import create_terms_obj
from optdesc.optlist import optlst_permutations
from optdesc.optlist import re_operand_angled, re_operand_all_caps
from optdesc.optlist import t_space

#------------------------------------------------------------------------------

from optdesc.optlist import OperandDef, OptionDef, OptionListDef
from optdesc.optline import OptionLineDef
from optdesc.optsect import OptionDescDef

opt     = OptionDef
olst    = OptionListDef
ol      = OptionLineDef
od      = OptionDescDef

#------------------------------------------------------------------------------

def CommandDef(str):
    pass

def ProgramDef(str):
    pass

# Sequence( ( wx, OrderedChoice( [ option, operand, command ] ) ),
def ArgumentDef():
    wx          : str
    value       : Union[OptionDef, OperandDef, CommandDef]

class ChoiceDef (list):         # List[Expression]
    pass

class ExpressionDef (list):     # List[RepeatableDef]
    pass

class TermDef (object):
    value       : object        # Union[OptionsShortcutDef,OptionalDef,RequiredDef,ArgumentDef]

RepeatingDef = bool

class RepeatableDef (object):
    value       : TermDef
    repeating   : RepeatingDef

class OptionalDef (object):
    value       : object        # choice

class RequiredDef (object):
    value       : object        # choice

class OptionsShortCut (object):
    pass

#------------------------------------------------------------------------------

t_eof = Terminal(EOF(), 0, '')
t_repeating = Terminal(repeating(), 0, REPEATING)

#------------------------------------------------------------------------------

def t_command(word):

    if re_operand_angled.fullmatch(word) or re_operand_all_caps.fullmatch(word) :
        raise ValueError(f"Command word '{word}' would be parsed as an "
                         f"operand.  Please address.")

    for ch in WHITESPACE_CHARS :
        if ch in word :
            raise ValueError(
                f"Command word '{word}' contains whitespace and would be parsed "
                f"as multiple arguments, not a single command.  Plesae address.")

    return Terminal( command(), 0, word)

#------------------------------------------------------------------------------

def t_options_shortcut(word):
    expr = options_shortcut().to_match
    if not re.fullmatch(expr, word):
        raise ValueError(f"Invalid options shortcut '{word}'.  Does not "
                         f"satisfy regex r'{expr}'.  Please address.")
    return Terminal( options_shortcut(), 0, word)

#------------------------------------------------------------------------------

#wrap
def usage_prepare_children_wrap ( children : List[Tuple[str,ParseTreeNode]],
                                prepares : list, ) :
    """<children> : list of ( text, expect )
       <prepare>  : iterable of prepare functions taking only ( text, expect )
    """

    for _prepare in prepares[::-1] :
        children = [ _prepare ( *t ) for t in children ]

    return children

def usage_prepare_argument_optlst_expr ( optlst : OptionListDef ) :
    ( texts, terms ) = create_termx_obj ( optlst )
    assert len(texts) == len(terms)
    terms = [ NonTerminal( argument(), [ term ] ) for term in terms ]
    return list(zip( texts, terms ))

#------------------------------------------------------------------------------
                               
def usage_prepare_expression ( children : List[Tuple[str,ParseTreeNode]],
                               sep : str = ' ' ) :
    """<children> : list of ( text, expect )
       <sep>      : separator between children to create text [DEFAULT: ' ']
                    single space minimum ensured
    """
    # optlst : OptionListDef

    if sep is None or len(sep) <= 0 :
        sep = ' '

    text = sep.join ( [ x[0] for x in children ] )
    
    expect = NonTerminal( expression(), [ x[1] for x in children ] )
    
    return ( text, expect )

#------------------------------------------------------------------------------

def usage_prepare_repeatable ( text : str, child : ParseTreeNode,
                               repeating=False, gap='' ) :
    """Consider this BRITTLE code since text does not also incorporate an enclosure."""
    elements = [ child ]
    if repeating :
        text += gap + REPEATING
        elements.append( t_repeating )
    return ( text, NonTerminal( repeatable(), elements ) )

def usage_prepare_optional ( text : str, child : ParseTreeNode ) :
    text = '[ ' + text + ' ]'
    return ( text, NonTerminal( optional(), [ child ] ) )

def usage_prepare_required ( text : str, child : ParseTreeNode ) :
    text = '( ' + text + ' )'
    return ( text, NonTerminal( required(), [ child ] ) )

def usage_prepare_term ( text : str, child : ParseTreeNode ):
    # options_shortcut, optional, required, argument
    return ( text, NonTerminal( term(), [ child ] ) )

#------------------------------------------------------------------------------

def usage_prepare_option ( optdef : OptionDef ):
    ( text, terms ) = create_terms_obj ( olst( optdef ) )
    terms = flatten ( [ (t, t_space) for t in terms ] )
    del terms[-1]
    return ( text, terms )

def usage_prepare_argument_optdef ( optdef : OptionDef ):
    ( text, terms ) = create_terms_obj ( olst( optdef ) )
    terms = flatten ( [ (t, t_space) for t in terms ] )
    del terms[-1]
    expect = NonTerminal( argument(), [ *terms ] )
    return ( text, expect )

def usage_prepare_argument_operand ( text : str ) :
    term = term__operand(text)
    expect = NonTerminal( argument(), [ term ] )
    return ( text, expect )

#------------------------------------------------------------------------------

def usage_prepare_argument_command ( text : str ) :
    expect = NonTerminal( argument(), [ t_command(text) ] )
    return ( text, expect )

#------------------------------------------------------------------------------

def usage_prepare_options_shortcut ( text : str ) :
    return ( text, t_options_shortcut(text) )

#------------------------------------------------------------------------------

def define_usage_expression_shortnames(namespace):
    exec ( """
_term           = usage_prepare_term
_repeatable     = usage_prepare_repeatable
_command        = usage_prepare_argument_command
_optshortcut    = usage_prepare_options_shortcut
_optdef         = usage_prepare_argument_optdef
_optlst_expr    = usage_prepare_argument_optlst_expr
_wrap           = usage_prepare_children_wrap
_expr           = usage_prepare_expression
""", namespace )

define_usage_expression_shortnames(globals())

#------------------------------------------------------------------------------
