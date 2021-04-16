import sys
import os
import re

import arpeggio
import arpeggio.cleanpeg
# from arpeggio import visit_parse_tree, PTNodeVisitor, SemanticActionResult
from arpeggio import Terminal, NonTerminal

from prettyprinter import cpprint as pp

#------------------------------------------------------------------------------

slurp = lambda fname : [(f.read(), f.close()) for f in [open(fname,'r')]][0][0]

#------------------------------------------------------------------------------

GRAMMAR_FILE_NAME = 'docopt.peg'

class DocOptParserPEG(object):

    def __init__(self, grammar_text=None, grammar_file=None, debug=False):

        self.debug = debug

        if grammar_text :
            self.grammar_text = grammar_text
        else :
            if grammar_file:
                self.grammar_file = grammar_file
            else :
                self.grammar_file = os.path.join(os.path.dirname(__file__),
                                                 GRAMMAR_FILE_NAME)
            self.grammar_text = slurp(self.grammar_file)

            if '#' in self.grammar_text :
                print("*** Wrong comment prefix, found '#' in grammar !")
                sys.exit(1)

        self.parser = arpeggio.cleanpeg.ParserPEG \
            (self.grammar_text, "docopt", reduce_tree=False)

        self.parser.debug = self.debug

        self.parser.ws = '\r\t '

    def parse(self, input_expr, print_raw=False):
        # self.parser.debug = True
        self.raw_parse_tree = self.parser.parse(input_expr)
        if print_raw:
            print(f"raw parse tree : {str(type(self.raw_parse_tree))}\n"
                  f"{self.raw_parse_tree.tree_str()}\n")

        self.parse_tree = DocOptSimplifyVisitor().visit(self.raw_parse_tree)

        apply_to_tree(self.parse_tree, operand_flatten_chain)

        # order is critical: flatten chain, strip fake, remove bars
        apply_to_tree(self.parse_tree, choice_flatten_chain)
        apply_to_tree(self.parse_tree, choice_strip_fake)
        apply_to_tree(self.parse_tree, choice_remove_bars)

        implict_argument_grouping_strip(self.parse_tree)
        
        # Go last or messes up choices: 'Usage: copy -h | --help | --foo'
        # apply_to_tree(self.parse_tree, flatten_unnecessary_lists)

        return self.parse_tree

#------------------------------------------------------------------------------

# NonTerminal inherits from list such that the list of
# of it's children nodes is itself.

class DocOptSimplifyVisitor(object):

    # Do not strip expression, it's prescense is necessary for
    # correct choice chain flattening
    _strip = ( ' docopt usage usage_line usage_entry '
               ' other_sections other '
               ' option short long long_with_eq_arg '
             ' argument ' 
             # ' expression ' 
             )
    # Do not strip BAR, it's prescense is necessary for choice
    _empty = 'blankline newline EOF LPAREN RPAREN LBRACKET RBRACKET'

    def __init__(self):
        self._strip = set(self._strip.split())
        self._empty = set(self._empty.split())

    def visit(self, node):
        responses = []
        if isinstance(node, NonTerminal):
            responses = []
            for child in node : # NonTerminal IS the list
                response = self.visit(child)
                if response:
                    responses.append(response)
        if node.rule_name in self._empty :
            return None
        if node.rule_name in self._strip :
            return self.strip(node, responses)
        method = f"visit_{node.rule_name}"
        if hasattr(self, method):
            return eval(f"self.{method}(node, responses)")
        if isinstance(node, Terminal):
            return [ node.rule_name, node.value ]
        return [ node.rule_name, responses ]

    #--------------------------------------------------------------------------

    def strip(self, node, children):
        if len(children) == 1:
            children = children[0]
        if len(children) == 1:
            children = children[0]
        if len(children) == 1:
            children = children[0]
        return children

    #--------------------------------------------------------------------------

    # make is searchable within the choice list
    def visit_BAR(self, node, children):
        return 'BAR'

    def visit_expression(self, node, children):
        if len(children) == 1:
            children = children[0]
        if len(children) == 1:
            children = children[0]
        if len(children) == 1:
            children = children[0]
        return children

    #--------------------------------------------------------------------------

    def X_visit_docopt(self, node, children):
        out = []
        for child in children:
            if isinstance(child, list) and child[0] == 'other-sections':
                for elt in child[1]:
                    out.append(elt)
                continue
            out.append(child)
        return out

    #--------------------------------------------------------------------------

    def _visit_intro(self, node, children):
        return [ 'intro', ' '.join(children) ]

    #--------------------------------------------------------------------------

    def _visit_usage(self, node, children):
        return [ "usage", children[1:] ]

    def _visit_usage_pattern(self, node, children):
        return children

    def _visit_program(self, node, children):
        return [ 'program' , node.value ]

    def _visit_optional(self, node, children):
        return [ 'optional' , children ]

    def _visit_required(self, node, children):
        return [ 'required' , children ]

    def _visit_choice(self, node, children):
        return [ 'choice' , children ]

    def _visit_argument(self, node, children):
        return children

    def _visit_option(self, node, children):
        return [ 'option' , children ]

    def _visit_operand(self, node, children):
        return [ 'operand' , children ]

    def _visit_command(self, node, children):
        return { 'command' : node.value }

    def _visit_repeated(self, node, children):
        return [ 'repeated' , node.value ]

    #--------------------------------------------------------------------------

    def _visit_other_sections(self, node, children):
        if len(children) <= 0:
            return None
        return [ 'other-sections', children ]

    def _visit_other(self, node, children):
        if len(children) <= 0:
            return None
        return children

    #--------------------------------------------------------------------------

    def _visit_description(self, node, children):
        return [ 'description', '\n'.join(children) ]

    def visit_line(self, node, children):
        return ' '.join(children)

    def visit_word(self, node, children):
        return node.value

    def _visit_trailing (self, node, children):
        return [ 'trailing', '\n'.join(children) ]

    def _visit_trailing_line (self, node, children):
        return ' '.join(children)

    def _visit_fragment(self, node, children):
        return ' '.join(children)

    #--------------------------------------------------------------------------

    def _visit_operand_section(self, node, children):
        return [ 'operand-section', children ]

    def _visit_operand_intro(self, node, children):
        return [ 'operand-intro', children ]

    def _visit_operand_detail(self, node, children):
        return [ 'operand-detail', children ]

    def _visit_operand_help(self, node, children):
        while isinstance(children[-1], list):
            tmp = children[-1]
            children = children[:-1]
            children.extend(tmp)
        return [ 'operand-help', ' '.join(children) ]

    #--------------------------------------------------------------------------

    def _visit_options_section(self, node, children):
        # return [ 'options-section', children ]
        return children

    def _visit_option_detail(self, node, children):
        return [ 'option-detail', children ]

    def _visit_option_list(self, node, children):
        return [ 'option-list', children ]

    def _visit_option_single(self, node, children):
        # return [ 'option-single', children ]
        return children

    def _visit_short_no_arg(self, node, children):
        return [ 'short-no-arg', node.value ]

    def _visit_short_with_arg(self, node, children):
        return [ 'short-with-arg', children ]

    def _visit_long_no_arg(self, node, children):
        return [ 'long-no-arg', node.value ]

    def _visit_long_with_arg(self, node, children):
        return [ 'long-with-arg', children ]

    def _visit_long_with_gap_arg(self, node, children):
        return [ 'long-with-gap-arg', children ]

    def _visit_option_help(self, node, children):
        while isinstance(children[-1], list):
            tmp = children[-1]
            children = children[:-1]
            children.extend(tmp)
        # print(f"[option-help]") ; pp(children) ; print(f"= = = = =")
        return [ 'option-help', ' '.join(children) ]

    #--------------------------------------------------------------------------

    def _visit_string_no_whitespace(self, node, children):
        return node.value

    def _visit_newline(self, node, children):
        return None

    def _visit_comma(self, node, children):
        return None

#------------------------------------------------------------------------------

def search_tree(t, filter):
    if filter(t):
        yield t
    if isinstance(t, list):
        for elt in t :
            for result in search_tree(elt, filter):
                yield result
    if isinstance(t, dict):
        for key, value in t.items():
            for result in search_tree(key, filter):
                yield result
            for result in search_tree(value, filter):
                yield result

#------------------------------------------------------------------------------

def apply_to_tree(tree, action):

    def _apply_to_tree(t):
        if isinstance(t, list):
            for elt in t :
                _apply_to_tree(elt)
                action(elt)
        if isinstance(t, dict):
            for key, value in t.items():
                # _apply_to_tree(key)
                _apply_to_tree(value)
                action(key)
                action(value)
        action(t)

    _apply_to_tree(tree)

    tree

#------------------------------------------------------------------------------

def fix_choice_reqopt(node):
    if ( isinstance(node,list) and
         node[0] == 'choice' and
         isinstance(node[1],list) and
         node[1][0] in ['optional','required']
    ) :
        node[0], node[1][0] = node[1][0], node[0]

#------------------------------------------------------------------------------

def flatten_unnecessary_lists(node):
    if ( isinstance(node, list) and
         len(node) == 1 and
         isinstance(node[0], list)
    ) :
        children = node[0]
        del node[0]
        node.extend(children)

#------------------------------------------------------------------------------

# Do not remove bars yet
def choice_flatten_chain(node):
    try :
        if ( node[0] == 'choice' and
             'BAR' in node[1] and
             len(node[1]) == 3 and
             node[1][2][0] == 'choice'
        ) :
            addition = node[1][2][1]
            node[1] = node[1][:-1]
            node[1].extend(addition)
    except :
        pass

#------------------------------------------------------------------------------

def choice_remove_bars(node):
    if ( isinstance(node, list) and
         len(node) > 0 and
         node[0] == 'choice' and
         isinstance(node[1], list) and
         'BAR' in node[1]
    ) :
        node[1].remove('BAR')

#------------------------------------------------------------------------------
#
# [ ['long_no_arg', '--flag'],
#   ['operand', [['operand_angled', '<repeating>']]],
#   [ ['operand', [['operand_angled', '<repeating>']]],
#     ['repeated', '...'] ]
#   ['long_no_arg', '--what'],
# ]
#
# becomes
#
# [ ['long_no_arg', '--flag'],
#   ['operand', [['operand_angled', '<repeating>']]],
#   ['operand', [['operand_angled', '<repeating>']]],
#   ['repeated', '...']
#   ['long_no_arg', '--what'],
# ]
#

def operand_flatten_chain(node):
    if not isinstance(node, list):
        return
    idx = 0
    while idx < len(node):
        child = node[idx]
        found = False
        try :
            found = ( child[0][0] == 'operand' )
        except :
            pass
        if found :
            del node[idx]
            for elt in child[::-1]:
                node.insert(idx, elt)
            idx += len(child) - 1
        idx += 1

#------------------------------------------------------------------------------

# A fake choice does not contain BAR, '|'
#
#   [ 'choice',
#     [ [ ['command', 'a'],
#         ['command', 'b'],
#         ['command', 'c']
#       ] ] ]
#
# becomes:
#
#   [ ['command', 'a'],
#     ['command', 'b'],
#     ['command', 'c']
#   ]

def choice_strip_fake(node):

    try :
        if node[0] != 'choice' :
            return
    except :
        pass

    children = node[1]
    if len(children) == 1:
        children = children[0]
    if 'BAR' in children :
        return
    node.clear()
    node.extend(children)

#------------------------------------------------------------------------------

# : node = [ 'usage_pattern',
#            [ ['program', 'my_program'],
#              [ ['long_no_arg', '--flag'],
#                ['operand', [['operand_angled', '<unexpected>']]],
#                ['operand', [['operand_angled', '<grouping>']]]
#              ] ] ]
#
#    [0]           : 'usage_pattern',
#    [1][0][0]     : 'program'
#    [1][1]        : potentially spurious list
#    [1][1][0]     : rule-name in a non-spurious entry
#
# becomes
#
#   [ 'usage_pattern',
#     [ ['program', 'my_program'],
#       ['long_no_arg', '--flag'],
#       ['operand', [['operand_angled', '<unexpected>']]],
#       ['operand', [['operand_angled', '<grouping>']]]
#     ] ] ]

def implict_argument_grouping_strip(root):

    # implicit group starting with third argument
    if root[0] != 'usage_pattern':
        found = False
        for section in root:
            if section[0] == 'usage_pattern':
                found = True
                root = section
                break
        if not found :
            return

    try :
        if root[0] != 'usage_pattern' :
            return
        if root[1][0][0] != 'program' :
            return
        if isinstance(root[1][1][0], str) :
            return
    except :
        pass

    # [1][1]  : potentially spurious list
    children = root[1][1]
    del root[1][1]
    root[1].extend(children)

#------------------------------------------------------------------------------
