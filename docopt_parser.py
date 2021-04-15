import sys
import os

import arpeggio
import arpeggio.cleanpeg
# from arpeggio import visit_parse_tree, PTNodeVisitor, SemanticActionResults

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
        self.annotated_parse_tree = arpeggio.visit_parse_tree \
            (self.raw_parse_tree, DocOptAnnotationVisitor())
        self.parse_tree = self.clean_semantic_results()
        return self.parse_tree

    def clean_semantic_results(self):

        def pass1_flatten(sx):
            if not isinstance(sx, arpeggio.SemanticActionResults):
                return flatten(sx)
            if sx.results is None  or  len(sx.results) <= 0:
                return
            out = [ ]
            for name, value in sx.results.items() :
                out.append(pass1_flatten(value))
            return flatten(out)

        listing = 'listing:'
        listing_len = len(listing)
        terminal = 'terminal:'
        terminal_len = len(terminal)
        def pass2_clean(sx):
            if not isinstance(sx, list) or len(sx) <= 0:
                return sx
            if isinstance(sx[0], str):
                name = sx[0]
                if name.startswith(listing):
                    sx[0] = name[listing_len:]
                if name.startswith(terminal):
                    sx[0] = name[terminal_len:]
            out = [ ]
            for value in sx :
                out.append( pass2_clean(value) )
            return out

        return pass2_clean ( pass1_flatten(self.annotated_parse_tree) )

#------------------------------------------------------------------------------

# SemanticActionResults . results = { [ name : value ], ... }

def flatten(sx):
    # i = ' ' * indent
    if isinstance(sx, str):
        return sx
    if isinstance(sx,list):
        return flatten_list(sx)
    if isinstance(sx, dict):
        return flatten_dict(sx)
    return sx

#------------------------------------------------------------------------------

def flatten_dict(sx):

    if len(sx) == 1 :
        key, value = list(sx.items())[0]
        if isinstance(value, list) and len(value) == 1:
            if key == value[0]:
                return flatten(value)

    out = {}
    for key, value in sx.items():
        out[key] = flatten(value)
    return out

#------------------------------------------------------------------------------

def flatten_list(sx):

    if len(sx) <= 0:
        return []

    if len(sx) == 1 :
        return flatten(sx[0])

    out = []
    for value in sx:
        out.append(flatten(value))

    if len(out) > 0 :
        if out[0] in ['optional', 'required']:
            return flatten_chooser('choice', out)
        if out[0] == 'choice':
            return flatten_chain('choice', out)
        if out[0] == 'option-list':
            return flatten_chain('option-list', out)
        if out[0] == 'option-list':
            return flatten_chain('option-help', out)

    return out

#------------------------------------------------------------------------------

#  ['optional', ['terminal:choice', ['operand', 'WORD']]]

def flatten_chooser(chain_name, sx):
    if isinstance(sx[1], list) and sx[1][0] == f"terminal:{chain_name}":
        return [ sx[0], sx[1][1] ]
    return sx

#------------------------------------------------------------------------------

# Chained:
#   sx = [ 'choice', [{'command': 'move'}, ['choice', {'command': 'fire'}]]]
#   sx = [ sx[0] = 'choice'
#        , sx[1] = [ sx[1][0] = {'command': 'move'}
#                  , sx[1][1] = [ sx[1][1][0] = 'choice'
#                               , sx[1][1][1] = {'command': 'fire'}]]]

# Terminal :
#   sx = ['choice', {'command': 'fire'}]
#   sx = [ sx[0] = 'choice'
#        , sx[1] = {'command': 'fire'} ]

def is_chain(chain_name, sx):
    return ( isinstance(sx, list) and
             sx[0] in [ chain_name,
                        f"terminal:{chain_name}",
                        f"listing:{chain_name}" ] )

def flatten_chain(chain_name, sx):

    terminal = f"terminal:{chain_name}"
    listing  = f"listing:{chain_name}"

    if not is_chain(chain_name, sx):
        return sx

    # Terminal if [1] is not a list
    if not isinstance(sx[1], list):
        return [ terminal, sx[1] ]

    # Terminal if [1][1] is not of this chain
    if not is_chain(chain_name, sx[1][1]):
        name = terminal if sx[0] == chain_name else sx[0]
        return [ name, sx[1] ]

    child = flatten_chain(chain_name, sx[1][1])

    out = [ listing, [ sx[1][0] ] ]

    if child[0].startswith('terminal:') :
        out[1].append(child[1])
    else :
        out[1].extend(child[1])

    return out

#------------------------------------------------------------------------------

class DocOptAnnotationVisitor(arpeggio.PTNodeVisitor):

    def visit_docopt(self, node, children):
        out = []
        for child in children:
            if isinstance(child, list) and child[0] == 'other-sections':
                for elt in child[1]:
                    out.append(elt)
                continue
            out.append(child)
        return out

    #--------------------------------------------------------------------------

    def visit_intro(self, node, children):
        return [ 'intro', ' '.join(children) ]

    #--------------------------------------------------------------------------

    def visit_usage(self, node, children):
        return [ "usage", children[1:] ]

    def visit_usage_pattern(self, node, children):
        return children

    def visit_expression(self, node, children):
        return children

    def visit_program(self, node, children):
        return [ 'program' , node.value ]

    def visit_optional(self, node, children):
        return [ 'optional' , children ]

    def visit_required(self, node, children):
        return [ 'required' , children ]

    def visit_choice(self, node, children):
        return [ 'choice' , children ]

    def visit_argument(self, node, children):
        return children

    def visit_option(self, node, children):
        return [ 'option' , children ]

    def visit_operand(self, node, children):
        return [ 'operand' , children ]

    def visit_command(self, node, children):
        return { 'command' : node.value }

    def visit_repeated(self, node, children):
        return [ 'repeated' , node.value ]

    #--------------------------------------------------------------------------

    def visit_other_sections(self, node, children):
        if len(children) <= 0:
            return None
        return [ 'other-sections', children ]

    def visit_other(self, node, children):
        if len(children) <= 0:
            return None
        return children

    #--------------------------------------------------------------------------

    def visit_description(self, node, children):
        return [ 'description', '\n'.join(children) ]

    def visit_line(self, node, children):
        return ' '.join(children)

    def visit_word(self, node, children):
        return node.value

    def visit_trailing (self, node, children):
        return [ 'trailing', '\n'.join(children) ]

    def visit_trailing_line (self, node, children):
        return ' '.join(children)

    def visit_fragment(self, node, children):
        return ' '.join(children)

    #--------------------------------------------------------------------------

    def visit_operand_section(self, node, children):
        return [ 'operand-section', children ]

    def visit_operand_intro(self, node, children):
        return [ 'operand-intro', children ]

    def visit_operand_detail(self, node, children):
        return [ 'operand-detail', children ]

    def visit_operand_help(self, node, children):
        while isinstance(children[-1], list):
            tmp = children[-1]
            children = children[:-1]
            children.extend(tmp)
        return [ 'operand-help', ' '.join(children) ]

    #--------------------------------------------------------------------------

    def visit_options_section(self, node, children):
        # return [ 'options-section', children ]
        return children

    def visit_option_detail(self, node, children):
        return [ 'option-detail', children ]

    def visit_option_list(self, node, children):
        return [ 'option-list', children ]

    def visit_option_single(self, node, children):
        # return [ 'option-single', children ]
        return children

    def visit_short_no_arg(self, node, children):
        return [ 'short-no-arg', node.value ]

    def visit_short_with_arg(self, node, children):
        return [ 'short-with-arg', children ]

    def visit_long_no_arg(self, node, children):
        return [ 'long-no-arg', node.value ]

    def visit_long_with_arg(self, node, children):
        return [ 'long-with-arg', children ]

    def visit_long_with_gap_arg(self, node, children):
        return [ 'long-with-gap-arg', children ]

    def visit_option_help(self, node, children):
        while isinstance(children[-1], list):
            tmp = children[-1]
            children = children[:-1]
            children.extend(tmp)
        # print(f"[option-help]") ; pp(children) ; print(f"= = = = =")
        return [ 'option-help', ' '.join(children) ]

    #--------------------------------------------------------------------------

    def visit_string_no_whitespace(self, node, children):
        return node.value

    def visit_newline(self, node, children):
        return None

    def visit_comma(self, node, children):
        return None

#------------------------------------------------------------------------------
