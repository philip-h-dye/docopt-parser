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

#------------------------------------------------------------------------------

# *** ONLY WHEN NEEDED
# ***
# ***   Don't import here unless troubleshooting here, as it results in
# ***   parse trees 'docopt_parser.p.NonTerminal', etc.  An effect, diametricly
# ***   opposed to the brevity for which p was creatd.
# ***
# *** BREAKS expected results for rule unit tests such as test_text.py.
# ***

if False :
    # registered prettyprinters for Terminal, NonTerminal, Unwrap, ...
    from p import pp

def dprint(s):
    # print(s)
    pass

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

    rule_groups = ' empty as_value as_lines '.split()

    _empty = ( ' _ EOF blankline COMMA LBRACKET RBRACKET LPAREN RPAREN EOF '
               ' newline '
             )

    _as_value = ( ' string_no_whitespace word words line '
                  ' '
                )

    _as_lines = ( ' description '
                  ' '
                )

    #--------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for group in self.rule_groups :
            if not hasattr(self, group):
                raise ValueError(f"INTERNAL ERROR, rule group '{group}' method "
                                 "missing.  Please contact the maintainer.")
            if group not in kwargs:
                rules = getattr(self, f"_{group}").split()
            else:
                rules = kwargs[group]
                rules = rules.split() if isinstance(rules, str) else rules
                if not isinstance(rules, list):
                    raise ValueError(f"Invalid type for rule group argument "
                                     f"'{group}'. Expected string or list, "
                                     f"found {str(type(rules))}")
            for rule_name in rules:
                setattr(self, f"visit_{rule_name}", getattr(self, group))

    #--------------------------------------------------------------------------

    def visit(self, node, depth=0):

        i = ' ' * 3 * depth
        dprint(f"{i} [ p2 : node = {node}")

        if not hasattr(node, 'rule_name'):
            dprint(f"{i}   - not a known container : {str(type(node))}")
            dprint(f"{i}   => itself")
            dprint(f"{i} ]")
            if isinstance(node, list) and len(node) == 1:
                return node[0]
            return node

        #----------------------------------------------------------------------

        children = []
        if isinstance(node, (NonTerminal, SemanticActionResults)):
            dprint(f"{i}   - visiting children of '{node.name}' : len = {len(node)}")
            # each of these object types is a list
            for child in node :
                response = self.visit(child, 1+depth)
                if response:
                    if not isinstance(response, NonTerminal):
                        children.append(response)
                        continue
                    dprint(f": repeatable : {node.name} : response =")
                    # pp(response)
                    if ( response.rule_name == 'repeating' and
                         len(children) > 0 and
                         response[0] == children[-1] ):
                        dprint(f": repeatable : {node.name} : children =")
                        # pp(children)
                        children[-1] = response
                    else :
                        children.append(response)

        dprint(f"{i}   - visited children = {children}")

        #----------------------------------------------------------------------

        # rule name specific visitor ?

        rule_name = str(node.rule_name)
        method = f"visit_{rule_name}"
        dprint(f"{i}   - {method} ?")
        if hasattr(self, method):
            dprint(f"{i}   - method found, applying to {node.name}")
            out = getattr(self, method)(node, children, 1+depth)
            dprint(f"{i}   => {_res(out,i)}")
            dprint(f"{i} ]")
            return out
        else :
            dprint(f"{i}   - no such method")

        #----------------------------------------------------------------------

        if len(children) <= 0:
            out = Terminal(node.rule, 0, node.value)
            dprint(f"{i}   => {_res(out,i)}")
            dprint(f"{i} ]")
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
        dprint(f"{i}   => {_res(out,i)}")
        dprint(f"{i} ]")
        return out

    #------------------------------------------------------------------------------

    def empty(self, node, children, depth=0):
        return None

    #--------------------------------------------------------------------------

    # Gather composition elements into a terminal
    #   (i.e. a line from a sequence of words)
    def as_value(self, node, children, depth=0):
        if len(children) :
            print(f"\n: as_value() : {node.rule_name} : collecting {len(children)} children"
                  f": {repr(children)}")
            value = ' '.join([c.value for c in children])
        else :
            print(f"\n: as_value() : {node.rule_name} : single value '{node.value}'")
            value = node.value
        return Terminal(StrMatch('', node.rule_name), 0, value)

    #--------------------------------------------------------------------------
    
    # Gather composition elements into a terminal with line breaks
    def as_lines(self, node, children, depth=0):
        if len(children) :
            print(f": as_lines() : {node.rule_name} : collecting {len(children)} children"
                  f": {repr(children)}")
            value = '\n'.join([c.value for c in children])
        else :
            print(f": as_lines() : {node.rule_name} : single value '{node.value}'")
            value = node.value
        return Terminal(StrMatch('', node.rule_name), 0, value)

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
