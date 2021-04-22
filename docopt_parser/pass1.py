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
    def __post_init__(self):
        assert isinstance(self.value, (list, NonTerminal))
        assert len(self.value) > 0
        assert isinstance(self.value[0], ParseTreeNode)

#------------------------------------------------------------------------------

class DocOptSimplifyVisitor_Pass1(object):

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
                    if not isinstance(response, NonTerminal):
                        children.append(response)
                        continue
                    # print(f": repeatable : {node.name} : response =")
                    # pp(response)
                    if ( response.rule_name == 'repeating' and
                         len(children) > 0 and 
                         response[0] == children[-1] ):
                        # print(f": repeatable : {node.name} : children =")
                        # pp(children)
                        children[-1] = response
                    else :
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

        # if len(children) == 1:
        #     children = children[0]  # can break the Parse Tree

        out = NonTerminal(node.rule, children)
        if False :
            try :
                out = NonTerminal(node.rule, children)
            except:
                # automatically unwrap
                children[0] = Unwrap(children[0])
                out = NonTerminal(node.rule, children)
                out[0] = out[0].value
                # FIXME: this breaks the parse tree
        # print(f"{i}   => {_res(out,i)}")
        # print(f"{i} ]")
        return out

    
    #--------------------------------------------------------------------------

    REPEATING = Terminal(StrMatch('...', rule_name='repeating'), 0, '...')

    # make REPEATED directly searchable within expressions
    def visit_repeated(self, node, children, depth=0):
        return self.REPEATED

    #--------------------------------------------------------------------------

    # Repeatable is in Pass1 because in Pass2, the assertions fail due to unwrapping.
    #
    # Collapse and encapsulate repeated terms
    # i.e. expression ( <other> <foo> <foo> '...' )expression ( <other> <foo> <foo> '...' )
    #   => expression ( <other> repeated(<foo>) )
    #
    # Or improve the grammar:  repeatable = term repeating?
    #
    def visit_repeatable(self, node, children, depth=0):

        if False and str(children) in [ "[command 'turn' [0], command 'rise' [0]]",
                              "[command 'move' [0]]" ]:
            print(f": repeatable : {node.name} : {children}")
            pp(NonTerminal(node.rule, children))
            print('')

        n_children = len(children)
        assert n_children in [1,2]

        term = children[0]

        if n_children == 1:
            return term

        assert children[1] == self.REPEATING

        return NonTerminal(StrMatch(':repeating:','repeating'), [term])

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
