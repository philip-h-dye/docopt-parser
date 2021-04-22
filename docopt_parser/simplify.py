import sys
import os
import re

from typing import Sequence, Dict, ClassVar

from dataclasses import dataclass

import arpeggio
import arpeggio.cleanpeg
# from arpeggio import visit_parse_tree, PTNodeVisitor, SemanticActionResults
from arpeggio import ( Terminal, NonTerminal, StrMatch, SemanticActionResults, ParseTreeNode )

# prettyprinter, registered printers for Terminal, NonTerminal
from p import pp

from pass1 import *
from pass2 import *

#------------------------------------------------------------------------------

# NonTerminal inherits from list such that the list of
# of it's children nodes is itself.

class DocOptSimplifyVisitor(object):

    def visit(self, node):
        # all Arpeggio style objects
        pass1 = DocOptSimplifyVisitor_Pass1().visit(node)
        # eliminate wrappers
        pass2 = DocOptSimplifyVisitor_Pass2().visit(pass1)
        return pass2

#------------------------------------------------------------------------------
