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
        self.parser = arpeggio.cleanpeg.ParserPEG(self.grammar_text, "docopt", debug=self.debug)

    def parse(self, input_expr):
        self.raw_parse_tree = self.parser.parse(input_expr)
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
        terminal_len = len(listing)
        def pass2_clean(sx):
            if not isinstance(sx, list):
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
        return children

    def visit_expression(self, node, children):
        return children

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

#------------------------------------------------------------------------------

if __name__ == "__main__":
    
    input_expr = "[ --what [ now ] ] ( move | fire | turn ) [ --speed 11 --angle 35 ] <when>"

    print(f"usage pattern = '{input_expr}'")

    parser = DocOptParserPEG()
    
    parse_tree = parser.parse(input_expr)

    pp(parse_tree)

    sys.exit(0)

#------------------------------------------------------------------------------
