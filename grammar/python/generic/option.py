#
# Here are only the two fundamental regular expressions for
# long and short options.  Other option aspects are dependent
# upon context :
#
#    usage-pattern         usage/option.py
#
#    option-description    optdesc/option.py

from arpeggio import RegExMatch as _

ALL = ( 'short_no_arg', 'long_no_arg' )


def short_no_arg():
    return _(r'(?<=\s)-[\w]', rule_name='short_no_arg')

def long_no_arg():
    return _(r'(?<=\s)--[\w][\w]+', rule_name='long_no_arg')

# regex lookbehind works quite nicely with Arpeggio.

#------------------------------------------------------------------------------
# from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore
# from .common import ws, wx
# from ..operand import *
# Usage   ? : def short_stacked():	return r'-[\w][\w]+\b'
# Context ? : def short_w_arg():	return Sequence( short_no_arg, operand )
# Context ? : def short():		return [ short_w_arg, short_stacked, short_no_arg ]
# def grammar():
#     return OneOrMore ( [ short_no_arg, long_no_arg, ws ] ), EOF
#------------------------------------------------------------------------------
