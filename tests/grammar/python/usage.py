import os

from dataclasses import dataclass
from contextlib import redirect_stdout

from typing import List, Tuple, Union

from prettyprinter import cpprint as pp, pprint as pp_plain

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, ZeroOrMore, OneOrMore, EOF
from arpeggio import ParseTreeNode, RegExMatch as _

#------------------------------------------------------------------------------

# tests/grammar/python
from util import tprint, write_scratch
from p import pp_str

#------------------------------------------------------------------------------

ALL = ( # ' UsageSectionDef UsageLineDef UsagePatternDef ProgramDef UsageExpression '
        ' ChoiceDef ExpressionDef TermDef RepeatableDef OptionalDef '
        ' RequiredDef OptionsShortCut ArgumentDef CommandDef '
        #
        ' usage_prepare_choice usage_prepare_children_wrap '
        ' usage_prepare_argument_optlst_expr usage_prepare_expression '
        ' usage_prepare_repeatable usage_prepare_optional '
        ' usage_prepare_required usage_prepare_term usage_prepare_option '
        ' usage_prepare_argument_optdef usage_prepare_argument_operand '
        ' usage_prepare_argument_command usage_prepare_options_shortcut '
        #
        ' define_usage_expression_shortnames '
        #
        ' t_command t_options_shortcut t_repeating '
        #
      ).split()

#------------------------------------------------------------------------------

from grammar.python.common import ws, WHITESPACE_CHARS, t_bar, t_space, t_eof
from grammar.python.common import NEWLINE_REGEX

from grammar.python.usage import *

from optdesc.optlist import create_termx_obj, method_name, term__operand
from optdesc.optlist import create_terms_obj
from optdesc.optlist import optlst_permutations
from optdesc.optlist import re_operand_angled, re_operand_all_caps

from optdesc.optlist import OperandDef, OptionDef, OptionListDef
from optdesc.optline import OptionLineDef
from optdesc.optsect import OptionDescDef

#------------------------------------------------------------------------------

# UsageSectionDef

# UsageLineDef
class ProgramDef(str):
    pass

# UsagePatternDef

@dataclass
class ChoiceDef (list):         # List[Expression]n
    bar         : bool          # Are or are not, separated by '|'

class ExpressionDef (list):     # List[RepeatableDef]
    pass

@dataclass
class TermDef (object):
    value       : object        # Union[OptionsShortcutDef,OptionalDef,RequiredDef,ArgumentDef]

RepeatingDef = bool

@dataclass
class RepeatableDef (object):
    value       : TermDef
    repeating   : RepeatingDef

@dataclass
class OptionalDef (object):
    value       : object        # choice

@dataclass
class RequiredDef (object):
    value       : object        # choice

class OptionsShortCutDef (str):
    pass

class CommandDef(str):
    pass

@dataclass
class ArgumentDef(object):
    # Sequence( ( wx, OrderedChoice( [ option, operand, command ] ) ),
    wx          : str
    value       : Union[OptionDef, OperandDef, CommandDef]

#------------------------------------------------------------------------------

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

def usage_prepare_choice ( children : List[Tuple[str,ParseTreeNode]],
                           gap : int = 1 ) :
    """<children> : list of ( text, expect )
       <spaces>   : number of spaces before and after BAR, '|' [DEFAULT: 1]
       Does not need a BAR boolean argument.  With a single expression child,
       such is unneccessary.  Multiple children alway separated by BAR, '|'.
       gap
    """

    if gap < 0 :
        gap = 0

    sep = (' ' * gap) + BAR + (' ' * gap)

    text = sep.join ( [ x[0] for x in children ] )

    expect = NonTerminal( choice(), flatten([ (x[1], t_bar) for x in children ]) )
    del expect[-1]

    return ( text, expect )

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
    """BRITTLE code since text does not also incorporate an enclosure."""
    elements = [ child ]
    if repeating :
        text += gap + REPEATING
        elements.append( t_repeating )
    return ( text, NonTerminal( repeatable(), elements ) )

def usage_prepare_optional ( text : str, child : ParseTreeNode ) :
    text = '[ ' + text + ' ]'
    return ( text, NonTerminal( optional(),
                                [ t_l_bracket, child, t_r_bracket ] ) )

def usage_prepare_required ( text : str, child : ParseTreeNode ) :
    text = '( ' + text + ' )'
    return ( text, NonTerminal( required(),
                                [ t_l_paren, child, t_r_paren ] ) )

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

def usage_prepare_program ( word : str ) :

    for ch in WHITESPACE_CHARS :
        if ch in word :
            raise ValueError(
                f"Command word '{word}' contains whitespace and would be parsed "
                f"as multiple arguments, not a program name.  Please address.")

    expect = Terminal( program(), 0, word )

    return ( word, expect )

#------------------------------------------------------------------------------

def usage_prepare_pattern ( program, choice_=None ) :
    assert len(program) == 2
    text = program[0]
    expect = [ program[1] ]
    if isinstance(choice_, tuple):
        assert len(choice_) == 2
        text += ' ' + choice_[0]
        expect += [ choice_[1] ]
    return ( text, NonTerminal( usage_pattern(), expect ) )

#------------------------------------------------------------------------------

# usage_prepare_line( pattern, t_newline )

def usage_prepare_line ( pattern : tuple , end : ParseTreeNode ) :

    if not isinstance(end, Terminal) and end.rule_name in['newline', 'EOF'] :
        raise ValueError(
            f"<end> must be t_newline, t_ws_newline or t_eof from grammar.python.common.  "
            f"Not {str(type(end))}.  Please address.")

    ( text, expect ) = pattern

    if end is t_newline :
        text += '\n'
    return ( text, NonTerminal( usage_line(), [ expect, end ] ) )

#------------------------------------------------------------------------------

def usage_prepare_intro ( text : str, *newlines ) :
    """
    <newlines>
    """

    # BRITTLE: depends on internal implementation of usage_intro and newline

    intro = usage_intro()

    intro_expr = intro.elements[0].to_match
    if not re.match(intro_expr, text):
        raise ValueError(
            f"Usage intro text '{text}' does not match regex '{expr}' such "
            f"that it will not be accepted in the parse.  Please address.")

    trailing = [ [], [] ]
    # peal off any trailing whitespace
    expr = f".*[^{WHITESPACE_RAW_STR}]({WS_REGEX})$"
    match = re.match(expr, text)
    if match:
        trailing_ = match.group(1)
        text = text [ : len(text) - len(trailing_) ]
        trailing[0].append( trailing_ )
        trailing[1].append( Terminal(wx(), 0, trailing_) )

    # peal off all trailing newline (i.e. ws + linefeed) segments
    expr = f".*[^{WHITESPACE_RAW_STR}]({NEWLINE_REGEX})$"
    nl = re.compile(expr)
    while ( match := nl.match(text) ) :
        trailing_ = match.group(1)
        text = text [ : len(text) - len(trailing_) ]
        trailing[0].insert(0, trailing_ )
        trailing[1].insert(0, t_wx_newline(trailing_) )

    expr = f"{intro_expr}({NEWLINE_REGEX})*({WS_REGEX})?"
    if not re.fullmatch(expr, text):
        raise ValueError(
            f"Usage intro text '{text}' does not match regex '{expr}' such "
            f"it will not be accepted in the parse.  Please address.")

    last_idx = len(trailing[0]) - 1

    for text_ in newlines:
        trailing[1].append ( t_wx_newline(text_) )
        trailing[0].append ( trailing[1][-1].value )

    # If text had 'trailing' whitespace AND newlines isn't empty,
    # the text's trailing must be prepended on newlines[0]

    if last_idx >= 0 :
        write_scratch ( n_trailing=[ last_idx,
                                     len(trailing[0]),
                                     trailing[0][last_idx],
                                     trailing[0][last_idx][-1] , ] )

        write_scratch ( trailing=trailing )

        if (last_idx+1) < len(trailing[0]) and trailing[0][last_idx][-1] != '\n' :
            trailing[0][last_idx+1] = trailing[0][last_idx] + trailing[0][last_idx+1]
            trailing[1][last_idx+1] = t_wx_newline(trailing[0][last_idx+1])
            del trailing[0][last_idx]
            del trailing[1][last_idx]

    expect = NonTerminal( usage_intro(), [
        Terminal( StrMatch(''), 0, text ),
        *trailing[1]
    ] )

    write_scratch( nl = expect )

    text += ''.join(trailing[0])

    return ( text , expect )

#------------------------------------------------------------------------------

def define_usage_expression_shortnames(namespace):
    exec ( """

_choice         = usage_prepare_choice
_expr           = usage_prepare_expression
_wrap           = usage_prepare_children_wrap
_repeatable     = usage_prepare_repeatable
_term           = usage_prepare_term
_optlst_expr    = usage_prepare_argument_optlst_expr
_optdef         = usage_prepare_argument_optdef
_command        = usage_prepare_argument_command
_optshortcut    = usage_prepare_options_shortcut

opt             = OptionDef
olst            = OptionListDef
ol              = OptionLineDef
od              = OptionDescDef

""", namespace )

define_usage_expression_shortnames(globals())

#------------------------------------------------------------------------------
