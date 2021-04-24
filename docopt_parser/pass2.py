import sys
import os
import re

from contextlib import redirect_stdout

from typing import Sequence, Dict, ClassVar

from dataclasses import dataclass

from prettyprinter import cpprint as pp

import arpeggio
import arpeggio.cleanpeg
# from arpeggio import visit_parse_tree, PTNodeVisitor, SemanticActionResults
from arpeggio import ( Terminal, NonTerminal, StrMatch, SemanticActionResults, ParseTreeNode )

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

class DocOptSimplifyVisitor_Pass2(object):

    classes = 'unwrap_single unwrap_list empty text'.split()

    _unwrap = ( ' other_sections other '
                ' required '		# explicit no differnet than explicit
                # ' expression '  	# NO, determinant for sides of implicit choice
                ' term argument '
                ' usage_line '          # NOT: usage or usage_pattern
                ' option short long long_with_eq_all_caps long_with_eq_angle '
                ' option_line option_list option_single '
                ' operand_line ' # operand_section '
                # ' short_no_arg short_stacked '
                # ' long_no_arg long_with_eq_arg '
              )

    _unwrap_list = ( ' other_sections '
                     ' required '
                     ' term '
                     ' option_list '
                   )
        
    _unwrap_single = ( ' other '
                       ' usage_line '          # NOT: usage or usage_pattern
                       ' argument '
                       ' option short long '
                       ' option_line option_single long_with_eq_arg '
                     )
        
    _empty = ( ' intro_line '
               ' usage_entry '
               ' operand_all_caps operand_angle '
               ' LPAREN RPAREN LBRACKET RBRACKET OR COMMA EOF blankline newline '
             )

    _text = ( ' intro '
              ' operand_help option_help '
              # ' operand_intro operand_help  '
              # ' option_intro option_help '
             )

    # TERMINALS: ' short_no_arg short_stacked long_with_eq_all_caps long_with_eq_angle '

    # Used to make BAR directly searchable within the choice list
    BAR = Terminal(StrMatch('|', rule_name='BAR'), 0, '|')

    # '--long= <argument>' => '--long' '=' '<argument>'
    # FIXME: revamp grammar to explicitly handle all whitespace, see issues.txt
    EQ = Terminal(StrMatch('=', rule_name='repeated'), 0, '=')

    #--------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        # 'unwrap' -- does too much, break into clearly defined cases
        for _class in classes :
            for rule_name in getattr(self, f"_{_class}").split() :
                setattr(self, f"visit_{rule_name}", getattr(self, _class))

    #--------------------------------------------------------------------------

    def visit(self, node, depth=0, path=[]):

        if not isinstance(node, (NonTerminal, Terminal, SemanticActionResults)):
            return node

        # print(f": visit : {node.name}")

        children = []
        if isinstance(node, (NonTerminal, SemanticActionResults)):
            # these object types are lists
            for child in node : # NonTerminal IS the list
                response = self.visit(child, depth=1+depth, path=path+[node.name])
                if response:
                    if not isinstance(response, Unwrap):
                        children.append(response)
                        continue
                    if isinstance(response.value, (list, NonTerminal)):
                        children.extend(response.value)
                    else :
                        children.append(response.value)

        # In extreme circumstances, rule_name may be list.  Note, that
        # such probably means unwrapping has gone too far and your node
        # is merely an empty list.
        rule_name = str(node.rule_name)
        # print(f": visit : {rule_name}")
        method = f"visit_{rule_name}"
        if hasattr(self, method):
            out = getattr(self, method)(node, children)
            # print(f": {node.name} : {method} => {_res(out)}\n")
            return out

        if len(children) > 0:
            # return nt(node.rule, children)

            # FIXME -- reenable, didn't bring back usage_pattern
            # if type(children) is list and len(children) == 1 :
            #     if type(children[0]) is list :
            #         # print(f": nt : unwrap embedded list")
            #         children = children[0]
            if ( isinstance(children, (list, NonTerminal)) and len(children) > 0
                 and isinstance(children[0], ParseTreeNode) ):
                return NonTerminal(node.rule, children)

            # The above, represent all encountered configurations for children.  If
            # we encounter something diffent, report it:

            with redirect_stdout(sys.stderr):

                print(f"Internal error, unhandled configuration for children of a NonTerminal")
                print('')
                print(f"  path :  ", end='')
                _path = path + [node.name]
                prefix = ''
                for idx in range(len(_path)):
                    i = ' ' * 3 * idx
                    print(f"{prefix}{i}{_path[idx]}")
                    prefix = ' ' * 10
                print('')
                print(f"  node = {node.name} : depth {depth}")
                seq = isinstance(children, Sequence)
                seq_text = ': is a sequence' if seq else ''
                print(f"  children type     = {str(type(children))} {seq_text}")
                if seq:
                    print(f"  children[0] type  = {str(type(children[0]))}")
                print(": children =")
                pp(children)
                print(f"Please report this scenario to the maintainer.")
                out = NonTerminal(node.rule, children) # failure expected
                print(f"Unexpected success, also please report this scenario to the maintainer")
                return out

        return Terminal(node.rule, 0, node.value)

        # print(f": {node.name} : {which} => \n"
        #       f"{node.indent(out.tree_str())}")
        # return out

    #--------------------------------------------------------------------------

    def empty(self, node, children):
        return None

    def unwrap(self, node, children):
        return Unwrap(children)

    def X_unwrap(self, node, children):

        # children should be a either a ParseTreeNode or a list with one element
        # of type ParseTreeNode

        # OR a list containing one such, [[p.Terminal(rule_name='program', value='copy')]]
        if type(children) is list and len(children) == 1 :
            if type(children[0]) is list :
                print(f": unwrap() : unwrap embedded list")
                # pp(children)
                children = children[0]

        if not isinstance(children, list):
            # pp(node)
            raise TypeError("{node.rule_name} children should be a list with one element, "
                            f"not type '{str(type(children))}'")

        if len(children) != 1:
            # pp(node)
            # raise ValueError("{node.rule_name} children should be a list with one "
            #                  "element, not len {len(children)}")
            return Unwrap(children)

        if not isinstance(children[0], ParseTreeNode):
            # pp(node)
            raise ValueError("{node.rule_name} children[0] should be a ParseTreeNode, "
                            f"not type '{str(type(children))}'")
        return Unwrap(children[0])

    #--------------------------------------------------------------------------

    def unwrap_single ( self, node, children ):
        if not ( len(children) == 1 and isinstance(children[0], ParseTreeNode) ):
                 print(f": unwrap single : {node.name}")
                 print(": children =")
                 pp(children)
        assert len(children) == 1, \
            f"{node.name} has {len(children)} children, not 1 as expected"
        single = children[0]
        assert isinstance(single, ParseTreeNode), \
            f"{node.name}'s child is not a ParseTreeNode"
        return Unwrap([single])

    def unwrap_list ( self, node, children ):
        if not ( len(children) > 0 and isinstance(children[0], ParseTreeNode) ):
                 print(f": unwrap list : {node.name}")
                 print(": children =")
                 pp(children)
        assert len(children) > 0, \
            f"{node.name} has no children"
        assert isinstance(children[0], ParseTreeNode), \
            f"{node.name}'s child is not a ParseTreeNode"
        return Unwrap(children)

    #--------------------------------------------------------------------------

    # operand name is all that is relevant (i.e. FILE or <src>)
    def visit_operand(self, node, children):
        return Terminal(node.rule, 0, node.value)

    #--------------------------------------------------------------------------

    # make BAR directly searchable within the choice list
    def visit_BAR(self, node, children):
        return self.BAR

    def visit_choice(self, node, children):

        # *** Need to maintain valid Parse Tree, up one level ?
        # ***   >>> return sentinel indicating that visit should unwrap as
        # ***       children of choice's parent.

        # Eliminate fake choice, now must look into expressions
        #
        # XXX Test case 12 : 'Usage: copy move\ncopy ( move )'
        # XXX      output : error/name/lost-choice-and-expressions
        # XXX
        # XXX Error manifests without this enabled.
        #
        # This isn't the cause, it simply magnifies the error.
        #
        # Error is caused by the puzzling loss of the 'usage_pattern' enclosure
        # >>> unwrap() was doing too much unwrapping
        #
        if True :
            if ( len(children) == 1 and
                 isinstance(children[0], NonTerminal) and
                 children[0].rule_name == 'expression' and
                 self.BAR not in children[0] ) :
                return Unwrap(children[0])

        # Elimnate unnecessary expression wrapper when it has a single child
        #
        # *** If must be FALSE, document why and which test case
        #
        # >>> 'expression' context needful to discriminate between choice factors
        #
        if True :
            # DO NOT ENABLE THIS for now
            for idx in range(len(children)):
                child = children[idx]
                if  ( isinstance(child, NonTerminal) and
                      child.rule_name == 'expression' and
                      len(child) == 1 ) :
                    children[idx] = child[0]

        # Unchain cascading choices -- only necessary if recursive
        #   i.e. choice = expression ( BAR choice )
        #
        # NO LONGER NEEDED:  choice = expression ( BAR expression )*
        #
        if False and ( isinstance(children, list) and len(children) == 3
             and isinstance(children[-1], list) and children[-1][0] ):
            additional = children[-1]
            del children[-1]
            children.extend(additional)

        return NonTerminal(node.rule, children)

    #--------------------------------------------------------------------------

    #example #EXAMPLE
    def visit_Non_Terminal ( self, node, children ):
        return NonTerminal(node.rule, children)

    #--------------------------------------------------------------------------

    def visit_options_intro(self, node, children):
        # print(f": visit_options_intro : {node.name}")
        # pp(children)
        return Terminal(node.rule, 0, '\n'.join(children))       

    def visit_operand_intro(self, node, children):
        # print(f": visit_operand_intro : {node.name}")
        # pp(children)
        return Terminal(node.rule, 0, '\n'.join(children))       

    def _visit_operand_help(self, node, children):
        while isinstance(children[-1], list):
            tmp = children[-1]
            children = children[:-1]
            children.extend(tmp)
        return Terminal(node.rule, 0, '\n'.join(children))

    def _visit_option_help(self, node, children):
        print(f": visit_option_help : {node.name}")
        pp(children)
        while isinstance(children[-1], list):
            additional = children[-1]
            children = children[:-1]
            children.extend(additional)
        if isinstance(children[-1], Terminal):
            children[-1] = children[-1].value
        return Terminal(node.rule, 0, '\n'.join(children))

    #--------------------------------------------------------------------------

    def text(self, node, children):
        # print(f": text : {node.rule_name} : len = {len(children)}")
        # example: option_help = words ( newline !option_single option_help )*
        if isinstance(children[-1], Terminal):
            children[-1] = children[-1].value
        else:
            # example: intro = newline* !usage_entry line+ newline
            while isinstance(children[-1], list):
                additional = children[-1]
                children = children[:-1]
                children.extend(additional)
        return Terminal(node.rule, 0, '\n'.join(children))

    #--------------------------------------------------------------------------

    def visit_description(self, node, children):
        return Terminal(node.rule, 0, '\n'.join(children))

    def visit_line(self, node, children):
        assert len(children) == 1
        return children[0]

    def visit_words(self, node, children):
        return ' '.join(children)

    def visit_word(self, node, children):
        return node.value

    #--------------------------------------------------------------------------

    visit_trailing = text

    def visit_trailing_line (self, node, children):
        assert len(children) == 1
        return children[0]

    def visit_trailing_strings(self, node, children):
        return ' '.join(children)

    def visit_string_no_whitespace(self, node, children):
        return node.value

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
