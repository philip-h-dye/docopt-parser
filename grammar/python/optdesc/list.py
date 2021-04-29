#------------------------------------------------------------------------------
# option-list <- <option> [<option-argument>] [ [,=] <option-list> ]
#------------------------------------------------------------------------------

from arpeggio import OrderedChoice, Sequence, ZeroOrMore
from arpeggio import RegExMatch as _

from ..common import EQ, ws
from ..generic.operand import operand

ALL = ( ' option_list ol_first_option ol_element '
        ' ol_option_lead ol_long ol_short  '
        ' _long _short '
        ' ol_operand_lead ol_operand'
       ).split()

# *** The 'lead' expressions for options and operands are what led to
# *** the distinct parsing from usage-pattern.  However, it seems that
# *** one could generalize it to serve both with a modest additional
# *** burden upon semantic analysis with the gain of less code to
# *** maintain.
#
#   1. ol-operand-lead would be broken into three individual,
#      existing, tokens and wrapped in an OrderedChoice
#   2. ol-option-lead, again three existing tokens wrapped in an
#      OrderedChoice

def ol_operand_lead():
    return _( r'(=|\s+)', rule_name='ol_operand_lead', skipws=False )
def ol_operand():
    return Sequence( ( ol_operand_lead, operand ),
                     rule_name='ol_operand', skipws=False )

def _short():
    return _( r'-[\w]',            rule_name='_short', skipws=False )
def _long():
    return _( r'--[\w][-_\w]+\b',   rule_name='_long', skipws=False )

def ol_option_lead():
    return _( r'(\s*[,|]\s*|\s+)',
              rule_name='ol_option_lead', skipws=False )
def ol_short():
    return Sequence( ( ol_option_lead, _short ), rule_name='ol_short')
def ol_long():
    return Sequence( ( ol_option_lead, _long ), rule_name='ol_long')

def ol_element():
    return OrderedChoice( [ ol_long, ol_short, ol_operand ],
                          rule_name='ol_element', skipws=False )

def ol_first_option():
    return Sequence ( ( And(ws), OrderedChoice( [ _long, _short ] ) ),
                      rule_name='ol_first_option', skipws=False )
    
def option_list():
    return Sequence( ( ol_first_option, ZeroOrMore(ol_element) ),
                     rule_name='option_list', skipws=False )

#------------------------------------------------------------------------------
