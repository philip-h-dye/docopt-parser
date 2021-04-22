import sys
import os
import re

from typing import Sequence, Dict, ClassVar

from dataclasses import dataclass

import arpeggio
import arpeggio.cleanpeg
# from arpeggio import visit_parse_tree, PTNodeVisitor, SemanticActionResults
from arpeggio import Terminal, NonTerminal, ParseTreeNode, SemanticActionResults
from arpeggio import StrMatch, RegExMatch

# prettyprinter, registered printers for Terminal, NonTerminal
from p import pp

#------------------------------------------------------------------------------

@dataclass
class Unwrap(object):
    value : object
    position : int = 0

#------------------------------------------------------------------------------

class DocOptSimplifyVisitor_Pass3(object):

    def visit(self, node, depth=0):

        i = ' ' * 3 * depth
        # print(f"{i} [ p2 : node = {node}")

        if not hasattr(node, 'rule_name'):
            # print(f"{i}   - not a known container : {str(type(node))}")
            # print(f"{i}   => itself")
            # print(f"{i} ]")
            if isinstance(node, list) and len(node) == 1:
                return node[0]
            return node

        #----------------------------------------------------------------------

        children = []
        if isinstance(node, (NonTerminal, SemanticActionResults)):
            # print(f"{i}   - visiting children of '{node.name}' : len = {len(node)}")
            # each of these object types is a list
            for child in node :
                response = self.visit(child, 1+depth)
                if response:
                    children.append(response)
            # print(f"{i}   - visited children = {children}")

        #----------------------------------------------------------------------

        # rule name specific visitor ?

        rule_name = str(node.rule_name)
        method = f"visit_{rule_name}"
        # print(f"{i}   - {method} ?")
        if hasattr(self, method):
            # print(f"{i}   - method found, applying to {node.name}")
            out = getattr(self, method)(node, children, 1+depth)
            # print(f"{i}   => {_res(out,i)}")
            # print(f"{i} ]")
            return out
        # else :
            # print(f"{i}   - no such method")

        #----------------------------------------------------------------------

        if len(children) <= 0:
            out = Terminal(node.rule, 0, node.value)
            # print(f"{i}   => {_res(out,i)}")
            # print(f"{i} ]")
            return out

        if len(children) == 1:
            children = children[0]
        try :
            out = NonTerminal(node.rule, children)
        except:
            out = NonTerminal(node.rule, [Unwrap(children)])
            # automatically unwrap
            out[0] = out[0].value
        # print(f"{i}   => {_res(out,i)}")
        # print(f"{i} ]")
        return out

    #--------------------------------------------------------------------------

    def visit_BAR(self, node, children, depth):
        return None
   
    #--------------------------------------------------------------------------

    # ?
    def X_visit_choice(self, node, children, depth):
        pass
        return NonTerminal( node.rule, children )
                         
    # only the grouping is needed, it is an 'expression' by context
    #
    # ^^^^ this would not be a proper parse tree.  Push to ListView
    #
    def X_visit_expression(self, node, children, depth):
        if len(children) == 1:
            return Unwrap(children[0])
        return NonTerminal( node.rule, children )
                         
#------------------------------------------------------------------------------

def _res(x, indent=''):
    # return ('\n'+x.tree_str()) if hasattr(x, 'tree_str') else x
    if hasattr(x, 'tree_str'):
        try :
            text = x.tree_str()
        except :
            text = str(x)
    else:
        text = str(x)
    if '\n' in text:
        newline = f"\n{indent}"
        text = newline + text.replace('\n', newline)
    return text

#------------------------------------------------------------------------------
