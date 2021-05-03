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

from arpeggio import EOF, Sequence, OrderedChoice, Optional, StrMatch
from arpeggio import And, Not, RegExMatch as _

# from docopt_parser.boundedre import RegExMatchBounded

from ..common import wx, newline, space
# from ..operand import operand
# from ..option import option
from .list import option_list

ALL = ( ' option_line option_line_gap option_help '
       ).split()

#------------------------------------------------------------------------------

def any_until_eol():
    return _(r'.*$', rule_name="any_until_eol")

#------------------------------------------------------------------------------

def option_line_gap():
    """Two or more spaces -- option line gap"""
    return _(r'   *', rule_name='option_line_gap', skipws=False )

#------------------------------------------------------------------------------

def option_help():
    return Sequence ( ( Not(space), any_until_eol, ), rule_name='option_help')

#------------------------------------------------------------------------------

def option_line():

    # It should not be necessary to incorporate EOF so often.
    # arpeggio.NoMatch: Expected comma or bar or space or '  ' or
    #   newline at position (1, 6) => '-f -x*'.

    return Sequence( ( wx, option_list ,
                       Optional ( ( option_line_gap() ,
                                    Optional ( option_help() ) ) ) ,
                     [ EOF, newline ] ) ,
                     rule_name='option_line', skipws=False )

#------------------------------------------------------------------------------
