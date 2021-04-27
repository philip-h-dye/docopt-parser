from typing import List, Sequence

from copy import deepcopy

from arpeggio import ParseTreeNode, Terminal, NonTerminal, StrMatch

from prettyprinter import cpprint as pp


dot = StrMatch('.', rule_name = 'dot')
t1 = Terminal(dot, 0, 'one')
n1 = NonTerminal(dot, [ t1 ])

assert isinstance(n1, List)
assert isinstance(n1, Sequence)

