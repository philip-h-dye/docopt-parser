#------------------------------------------------------------------------------

from arpeggio import RegExMatch as _

ALL = [ 'command' ]

#------------------------------------------------------------------------------

def command():
    """Something neiher an option nor operand.  In "naval_fate move <n>",
       'move' is a command.  Defined broadly as a non-whitespace string,
       it is catch all and must be the last item in an OrderedChoice.
    """
    return _(r'[\S]+', rule_name="command")

#------------------------------------------------------------------------------
