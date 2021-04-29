from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore # , RegExMatch
from arpeggio import OrderedChoice, Sequence, And, Not
from arpeggio import RegExMatch as _

from .boundedre import RegExMatchBounded

from .common import EQ, BAR, ws, wx
from .generic.operand import operand
from .option import option

ALL = ( ' option_list ol_first_option ol_term '
        ' ol_list_comma  ol_comma '
        ' ol_list_bar    ol_bar '
        ' ol_list_space  ol_space '
        ' ol_list_single '
       ).split()

#------------------------------------------------------------------------------

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

def ol_first_option():
    # semantic points:
    #   - disallow short_stacked
    #   - disallow BAR without a prior option-line
    return Sequence ( ( Optional(BAR), wx, option ),
                      rule_name='ol_first_option', skipws=False )

def ol_term():
    return OrderedChoice( [ option, operand ],
                            rule_name='ol_term', skipws=False )

def ol_comma():
    return RegExMatchBounded \
        ( r',', lead=r'\s*', trail=r'\s*',
          rule_name='ol_comma', skipws=False )

def ol_term_comma():
    return Sequence( ( ol_comma, ol_term ),
                     rule_name='ol_term_comma', skipws=False )

def option_list_comma():
    return Sequence( ( ol_first_option, OneOrMore(ol_term_comma) ),
                     rule_name='option_list_comma', skipws=False )

def ol_bar():
    return RegExMatchBounded \
        ( r',', lead=r'\s*', trail=r'\s*',
          rule_name='ol_bar', skipws=False )

def ol_term_bar():
    return Sequence( ( ol_bar, ol_term ),
                     rule_name='ol_term_bar', skipws=False )

def option_list_bar():
    return Sequence( ( ol_first_option, OneOrMore(ol_term_bar) ),
                     rule_name='option_list_bar', skipws=False )

def ol_term_space():
    return Sequence( ( ws, ol_term ),
                     rule_name='ol_term_space', skipws=False )

def option_list_space():
    return Sequence( ( ol_first_option, OneOrMore(ol_term_space) ),
                     rule_name='option_list_space', skipws=False )

def option_list_single():
    return Sequence( ( ol_first_option, And(_(r'\s\s')) ),
                     rule_name='option_list_single', skipws=False )

# handle trailing off
def option_list_single_EOF():
    return Sequence( ( ol_first_option, EOF ),
                     rule_name='option_list_single', skipws=False )

def option_list():
    return OrderedChoice ( [ option_list_comma, option_list_bar,
                             option_list_space, option_list_single,
                             option_list_single_EOF ],
                           rule_name='option_list', skipws=False )

#------------------------------------------------------------------------------
