from ..common import ws, wx
from ..operand import *

# option = short EOF

# short = short_w_arg / short_stacked / short_no_arg 
# short_w_arg = short_no_arg operand_no_space
# short_stacked = &ws _ r'-[\w][\w]+\b'
# short_no_arg = &ws _ r'-[\w]'

def short_no_arg():	return r'-[\w]'

# Usage   ? : def short_stacked():	return r'-[\w][\w]+\b'
# Context ? : def short_w_arg():	return Sequence( short_no_arg, operand )

# Context ? : def short():		return [ short_w_arg, short_stacked, short_no_arg ]
