# option-description section
#   option-intro-line
#   options-descriptions
#     option-description-line
#       \s*<option-list>\s\s<option-help>
#         option-list
#           ( option [ option operand [=|, ] comand]* )
#               ^^^ the atoms or terms
#
# FIXME:  add support for option-list continuation :
#         - track amount of leading white space per line
#         - continuation lines start with extra indent
#           and may include '|' prior to lead option

#------------------------------------------------------------------------------

from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore # , RegExMatch
from arpeggio import OrderedChoice, Sequence, And, Not
from arpeggio import RegExMatch as _

from docopt_parser.boundedre import RegExMatchBounded

from ..common import COMMA, BAR, SPACE, wx
from ..operand import operand
from ..option import option

ALL = ( ' option_list ol_first_option ol_term '
        ' ol_list_comma  ol_comma '
        ' ol_list_bar    ol_bar '
        ' ol_list_space  ol_space '
        ' ol_list_single '
       ).split()

#------------------------------------------------------------------------------

# ol_* are constituent descendents of option_list

# option-description section determining pattern
# - it can't simply be folded into ol_term since a line starting
#   with an option is the determinant.
# - Optional(BAR) supports option-list continuation
def ol_first_option():
    # semantic analysis :
    #   - disallow short_stacked
    #   - is this a continuation of the prior option-list ?
    #   - disallow BAR without a prior option-line
    return Sequence ( ( Optional(BAR), wx, option ),
                      rule_name='ol_first_option', skipws=False )

# Quite strictly a single space
def ol_space():
    return Sequence ( SPACE, Not(SPACE) )

def ol_separator():
    return OrderedChoice( COMMA, BAR, ol_space() )

def ol_term():
    # semantic analysis :
    #   - ol_separator present to facilite reporting a common typo
    return OrderedChoice( [ option, operand, ol_separator ],
                            rule_name='ol_term', skipws=False )
def ol_term_with_separator():
    return Sequence( ( ol_separator, ol_term ),
                     rule_name='ol_term_w_separator', skipws=False )
                     
def option_list():
    # semantic analysis :
    #   - validate that series of option, operand, BAR, COMMA and ol_space
    #     form a meaninful comma/bar/space option-list
    #   - disallow BAR without a prior option-line
    return Sequence( ( ol_first_option, ZeroOrMore(ol_term_with_separator) ),
                     rule_name='option_list', skipws=False )

#------------------------------------------------------------------------------
