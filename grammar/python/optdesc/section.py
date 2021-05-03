# option-description section
#   option-intro-line
#   options-description*
#     option-line*
#       \s*<option-list>\s\s<option-help>
#         option-list
#           ( option [ option operand [=|, ] comand]* )
#               ^^^ the atoms or terms
#
# FIXME:  add support for option-list continuation :
#         - track amount of leading white space per line
#         - continuation lines start with extra indent
#           and may include '|' prior to lead option

#-----------------------------------------------------------------------------

from arpeggio import EOF, Sequence, OrderedChoice, Optional, StrMatch
from arpeggio import RegExMatch as _, OneOrMore

# from docopt_parser.boundedre import RegExMatchBounded

from ..common import wx, newline, blank_line
# from ..operand import operand
# from ..option import option
# from .list import option_list
from .line import option_line

#------------------------------------------------------------------------------

ALL = ( ' option_description_section '
        # ' option_description_intro '
        # ' option_line_start '
       ).split()

#------------------------------------------------------------------------------

def option_line_start():
    return Sequence( ( wx, option ),
                     rule_name='option_line_start', skipws=False )
                     
def option_description_intro():
    return Sequence ( ( Not(option_line_start), wx, text_line ),
                      rule_name='option_description_intro', skipws=False )

def option_description_section():
    return Sequence( ( # Optional(option_description_intro),
                       OneOrMore(option_line),
                       # [ EOF, blank_line ],
                     ),
                     rule_name='option_description_section', skipws=False )

#------------------------------------------------------------------------------
