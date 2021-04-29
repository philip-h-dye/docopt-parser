#------------------------------------------------------------------------------
# TODO
#   option-list
#   option-help
#   option-default
#------------------------------------------------------------------------------
# Simplify option-arguments.  If not directly, adjacent w/o whitespace,
# operands are just plain operands.  Whether a given operand should
# be a option-argument is left to semantic analysis.  Semantic analysis
# has to verify all of the details regardless of what does 'favored'
# approach is chosen in parsing.

# The parsing goal is not to glean every possible detail from a successful
# parse.  But rather to successfully parse valid AND INVALID language in
# order to serve the user best.  In semantic analysis, valid language is
# correlated and resolved to provide the details to program for use.  In
# the invalid case, semantic analysis should provide the user detailed
# information on why the provided language is invalid and, if feasible,
# steps that might be taken to resolve the issue I

# Don't try to sqeeze all aspects out during parse.  A simpler,
# mostly-correct, successful parse is better than any failed parse.

import re

from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore, RegExMatch
from arpeggio import OrderedChoice, Sequence, ZeroOrMore
from arpeggio import RegExMatch as _

from docopt_parser.boundedre import RegExMatchBounded

from .common import EQ, ws # , wx
from .operand import operand

ALL = ( ' long_eq_arg long_no_arg '
        ' short_adj_arg short_stacked short_no_arg '
        ' option '
       ).split()

#------------------------------------------------------------------------------

# Punctuation in long and short args, numerous programs use punctuation
# in short or long args, embeded dash and underscore being the most
# common.  [:graph:] seems to make the most sense.  Though perhaps
# less dividing characters '|', ','.  Certainly not '='.

# Consider supporting customization of the option regexes.  Arpeggio's
# class customization technique might be a good model.

def long_no_arg():
    return RegExMatchBounded \
        ( r'--[\w][\w]+', lead=r'(^|(?<=\s))',
          rule_name='long_no_arg', skipws=False )

# Consider '--foo=a|b' : option literal choice -- without no whitespace
#
# FIXME: There are probably numerous other variations to consider.
#
# Possible drawbacks with PEG is partial match might preclude backtracking ?
# return Sequence ( ( long_no_arg, EQ, operand ),
#                   rule_name='long_eq_arg', skipws=False )
#
# FIXME:  Create composite from to_match attributes of
#         long_no_arg() and operand().

def long_eq_arg():
    """long argument, equal sign and operand without whitespace :
         '--file=foobar.txt'
    """
    # '\b' is required to not improperly match '--file=FOO' of '--file=FOObar'
    #   as an all caps option-argument.  Such must be matched as an
    #   option-value using the regular expression from the command() catch-all.
    return RegExMatchBounded \
        ( r'--(?P<name>[\w][\w]+)' '=' r'(?P<argument>(<([-_:\w]+)>|[A-Z][A-Z_]+\b|[\S]+))',
          lead=r'(^|(?<=\s))', rule_name='long_eq_arg', skipws=False )

#------------------------------------------------------------------------------

def short_no_arg():
    return RegExMatchBounded \
        ( r'-[\w]', lead=r'(^|(?<=\s))', trail=r'\b',
          rule_name='short_no_arg', skipws=False )

def short_adj_arg():
    """short with directly adjacent operand, i.e. -fFILE or -f<file>"""
    return RegExMatchBounded \
        ( ( r'-(?P<name>[\w])' + r'(?P<argument>[A-Z][A-Z]+\b)' ),
          lead=r'(^|(?<=\s))', trail=r'\b',
          rule_name='short_adj_arg', skipws=False )

def short_stacked():
    return RegExMatchBounded \
        ( r'-[\w][\w]+', lead=r'(^|(?<=\s))', trail=r'\b',
          rule_name='short_stacked', skipws=False )

#------------------------------------------------------------------------------

def option():
    return OrderedChoice ( [ long_eq_arg, long_no_arg, short_adj_arg,
                             short_stacked, short_no_arg ],
                           rule_name='option', skipws=False )

#------------------------------------------------------------------------------
