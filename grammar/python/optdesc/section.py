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
from arpeggio import RegExMatch as _, OneOrMore, Not

# from docopt_parser.boundedre import RegExMatchBounded

from ..common import wx, newline, blank_line
# from ..operand import operand
# from ..option import option
# from .list import option_list
# from ..text import line as text_line
from .line import option_line

#------------------------------------------------------------------------------

ALL = ( ' option_description_section '
        # ' option_description_intro '
        # ' option_line_start '
       ).split()

#------------------------------------------------------------------------------

def option_line_start():
    # return Sequence( ( wx, option ),
    return _( r'\s*[-]' ,
              rule_name='option_line_start', skipws=False )

def any_until_end_of_line_0():
    return Sequence ( ( _( r'.*$' ), newline ) ,
              rule_name='any_until_end_of_line', skipws=False )

def any_until_end_of_line():
    return _( r'.*$\n' ,
              rule_name='any_until_end_of_line', skipws=False )

def option_description_intro():
    # return OneOrMore ( Sequence ( ( Not(option_line_start), wx, text_line ) ),
    return OneOrMore ( Sequence ( ( Not(option_line_start), wx, any_until_end_of_line ) ),
                      rule_name='option_description_intro', skipws=False )

def option_description_section():
    return Sequence( ( Optional(option_description_intro),
                       OneOrMore(option_line),
                       # [ EOF, blank_line ],
                     ),
                     rule_name='option_description_section', skipws=False )

#------------------------------------------------------------------------------
