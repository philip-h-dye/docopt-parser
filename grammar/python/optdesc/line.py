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

ALL = ( ' option_line '
        ' '
       ).split()

#------------------------------------------------------------------------------

def option_line_gap():
    return StrMatch('  ', rule_name='option_line_gap')

def any_until_eol():
    return _(r'.*$', rule_name="any_until_eol")

def option_line():
    # FIXME: implement default value
    return Sequence( ( wx, option_list, option_line_gap(), any_until_eol() ),
                     rule_name='option_line', skipws=False )

#------------------------------------------------------------------------------
