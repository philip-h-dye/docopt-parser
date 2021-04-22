import sys
import os
import re

from typing import Sequence, Dict, ClassVar

from dataclasses import dataclass

from prettyprinter import cpprint as pp

import arpeggio
import arpeggio.cleanpeg
# from arpeggio import visit_parse_tree, PTNodeVisitor, SemanticActionResults
from arpeggio import ( Terminal, NonTerminal, StrMatch, SemanticActionResults, ParseTreeNode )

#------------------------------------------------------------------------------

from prettyprinter import register_pretty, pretty_call

@register_pretty(SemanticActionResults)
def pretty_SemanticActionResults(value, ctx):
    return pretty_call(
        ctx,
        SemanticActionResults,
        rule_name=value.rule_name,
        contents=list(value),
    )

# @register_pretty(Unwrap)
def _pretty_Unwrap(value, ctx):
    return pretty_call(
        ctx,
        Unwrap,
        value=value.value,
    )

import p

#------------------------------------------------------------------------------

x = Terminal(StrMatch('.', 'x'), 0, 'value:x')

y = Terminal(StrMatch('.', 'y'), 0, 'value:y')

v = NonTerminal(StrMatch('.', 'x_y'), [ x, y ])

t = NonTerminal(StrMatch('.', 'v_v'), [ v, v ])

pp(v)

pp(t, indent=2)

#------------------------------------------------------------------------------
