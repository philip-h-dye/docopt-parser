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

#------------------------------------------------------------------------------

@dataclass
class Unwrap(object):
    value : object

#------------------------------------------------------------------------------

# NonTerminal inherits from list such that the list of
# of it's children nodes is itself.

#list #lst
class DocOptListViewVisitor(object):

    def visit(self, node, depth=0):
        i = ' ' * 4 * depth
        _open = '{' ; _close = '}'
        dprint(f"{i}{_open} visit : node = '{node.name}' : type = {str(type(node))}")
        if not isinstance(node, (NonTerminal, Terminal, SemanticActionResults, list)):
            dprint(f"{i}  : type = {str(type(node))} => itself")
            dprint(f"{i}  => {_res(node,i+'    ')}")
            dprint(f"{i}{_close}")
            return node

        children = []
        if isinstance(node, (NonTerminal, SemanticActionResults, list)):
            # these object types are lists
            dprint(f"{i}  - visit children of {node.name}")
            for child in node : # NonTerminal IS the list
                response = self.visit(child, depth=1+depth)
                if response:
                    if not isinstance(response, Unwrap):
                        children.append(response)
                        continue
                    if isinstance(response.value, (list, NonTerminal)):
                        children.extend(response.value)
                    else :
                        children.append(response.value)

        if not hasattr(node, 'rule_name'):
            if not isinstance(node, list):
                raise TypeError("Unrecognized type {str(type(node))}, has no 'rule_name' but is not a list.")
            return children
        # rule_name can be an list, only empty list observed so far and that
        # means you've only got an empty list
        rule_name = str(node.rule_name)
        method = f"visit_{rule_name}"
        if hasattr(self, method):
            dprint(f"{i}  : calling '{method}'")
            out = getattr(self, method)(node, children, 1+depth)
            dprint(f"{i}  => {_res(out,i+'    ')}")
            dprint(f"{i}{_close}")
            return out
        if isinstance(node, Terminal):
            dprint(f"{i}  : terminal : value = '{node.value}'")
            out = [ rule_name.replace('_','-'), node.value ]
            dprint(f"{i}  => {_res(out,i+'    ')}")
            dprint(f"{i}{_close}")
            return out
        dprint(f"{i}  : non-term : children = {children}")
        out = [ rule_name.replace('_','-') ]
        if len(children) == 1:
            out.extend(children)
        else:
            out.append(children)
        dprint(f"{i}  => {_res(out,i+'    ')}")
        dprint(f"{i}{_close}")
        return out

    #--------------------------------------------------------------------------

    # only the grouping is needed, it is an 'expression' by context
    #
    # WAIT -- must sortout restructuring first
    #
    def visit_expression(self, node, children, depth):
        # if len(children) == 1:
        #    return children
        # return [ node.rule_name.replace('_','-') ] + children
        return children
                         
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

def dprint(*args, **kwargs):
    # print(*args, **kwargs)
    pass

#------------------------------------------------------------------------------
