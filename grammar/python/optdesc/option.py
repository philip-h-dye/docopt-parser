#
# TODO
#
#   option-list
#
#   option-help
#
#   option-default
#
#------------------------------------------------------------------------------
#
# Option descriptions -- =
#
#   <options-list>  \s{2} [<help-text> [default: <defaut-argument-value>]
#
#   option-list <- <option> [<option-argument>] [ , <option-list> ]

# from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore
# from arpeggio import RegExMatch as _
from arpeggio import OrderedChoice

from ..common import EQ, ws
from ..operand import operand

from ..generic.option import short_no_arg, long_no_arg

ALL = ( ' long long_w_arg long_w_no_arg '
        ' long_w_arg_eq long_w_arg_ws '
        ' short short_w_arg short_w_no_arg ' 
        ' short_w_arg_adj short_w_arg_eq short_w_arg_ws '
       ).split()

#------------------------------------------------------------------------------

# Short option with argument: '-l<arg>', '-l <arg>' or '-l=<arg>' (rare, but why not)
#
# An option-argument may follow a short option directly, separated by whitespace or
# separated by and equals sign.  Unlike in the usage-description, there is no
# ambiguity, with '-l <arg>', <arg> is an <option-argument> for '-l'.

def short_w_arg_adj():
    return OrderedChoice( [ short_no_arg, operand ],
                          rule_name='short_w_arg_adj' )
def short_w_arg_eq():
    return OrderedChoice( [ short_no_arg, EQ, operand ],
                          rule_name='short_w_arg_eq' )
def short_w_arg_ws():
    return OrderedChoice( [ short_no_arg, ws, operand ],
                          rule_name='short_w_arg_ws' )
def short_w_arg():
    return OrderedChoice( [ short_w_arg_adj, short_w_arg_eq, short_w_arg_ws ],
                          rule_name='short_w_arg' )
def short():
    return OrderedChoice( [ short_w_arg, short_no_arg ],
                          rule_name='short' )

def long_w_arg_eq():
    return OrderedChoice( [ long_no_arg, EQ, operand ],
                          rule_name='long_w_arg_eq' )
def long_w_arg_ws():
    return OrderedChoice( [ long_no_arg, ws, operand ],
                          rule_name='long_w_arg_ws' )
def long_w_arg():
    return OrderedChoice( [ long_w_arg_eq, long_w_arg_ws ],
                          rule_name='long_w_arg' )
def long():
    return OrderedChoice( [ long_w_arg, long_no_arg ], rule_name='long' )

def Xoption():
    return OrderedChoice( [ long, short ], rule_name='option' )

def option():
    return OrderedChoice( [ long_no_arg, short_no_arg ], rule_name='option' )

#------------------------------------------------------------------------------

# option-list <- <option> [<option-argument>] [ [,=] <option-list> ]

def option_separator():
    return _(r'(\s*[,|]\s*|\s+)', rule_name='option_separator', skipws=False)

# def arg_prefix():
#     (?<=\s)
#    return _(r'(\s*[,|]\s*|\s+)', rule_name='option_separator', skipws=False)

def Xoption_list():
    return Sequence( [ option, ZeroOrMore((option_separator, option)) ],
                     rule_name='option_list', skipws=False )

#------------------------------------------------------------------------------

def _short():
    return _(r'-[\w]', rule_name='_short')
    
def _long():
    return _(r'--[\w][-_\w]', rule_name='_long')

def ol_lead():
    return OrderedChoice( [ _long, _short ], rule_name='ol_lead')
    
def ol_separator():
    return _(r'(\s*[,|]\s*|\s+)', rule_name='ol_separator', skipws=False)

def ol_short():
    return Sequence( ol_separator, _short, rule_name='ol_short')
def ol_long():
    return Sequence( ol_separator, _long, rule_name='ol_long')

def ol_operand_lead():
    return _(r'(=|\s+)', rule_name='ol_operand_lead', skipws=False)
def ol_operand():
    return Sequence( ol_operand_lead, operand, rule_name='ol_operand' )

def ol_element():
    return OrderedChoice( [ ol_long, ol_short, ol_operand ],
                          rule_name='ol_element', skipws=False )
    
def option_list():
    return Sequence( [ ol_lead, ZeroOrMore(ol_element) ],
                     rule_name='option_list', skipws=False )

#------------------------------------------------------------------------------

# def options_description():
#     return OneOrMore( 

#------------------------------------------------------------------------------
from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore
from arpeggio import RegExMatch as _

# from .common import ws, wx
# from ..operand import *

ALL = ( ' short_no_arg '
        ' long_no_arg '
      ).split()

# Will the lookbehind within the regex work ?
def short_no_arg():	return _(r'(?<=\s)-[\w]')
def long_no_arg():	return _(r'(?<=\s)--[\w][\w]+')

# As these depend upon whether within 'Usage Pattern' or 'Option Detail',
#   they will be implemented as necessary within those contexts.
# Usage   ? : def short_stacked():	return r'-[\w][\w]+\b'
# Context ? : def short_w_arg():	return Sequence( short_no_arg, operand )
# Context ? : def short():		return [ short_w_arg, short_stacked, short_no_arg ]

# def grammar():		return OneOrMore ( [ short_no_arg, long_no_arg, ws ] ), EOF
