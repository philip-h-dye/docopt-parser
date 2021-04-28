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
