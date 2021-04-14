import sys
import os

from arpeggio.cleanpeg import ParserPEG
from arpeggio import visit_parse_tree, PTNodeVisitor, SemanticActionResults

from prettyprinter import cpprint as pp

slurp = lambda fname : [(f.read(), f.close()) for f in [open(fname,'r')]][0][0]

GRAMMAR_FILE_NAME = 'docopt.peg'

def main(debug=False):

    grammar_file = os.path.join(os.path.dirname(__file__), GRAMMAR_FILE_NAME)

    grammar_text = slurp(grammar_file)

    parser = ParserPEG(grammar_text, "docopt", debug=debug)

    # print(parser)

    input_expr = "FILE\n"
    input_expr = " FILE \n"
    input_expr = "FILE FIELD\n"

    input_expr = "[FILE]\n"
    input_expr = " [ FILE ]\n"

    input_expr = "<now-what>"
    input_expr = " [ FILE ] WHAT <now>\n"

    input_expr = "move"
    input_expr = " [ FILE ] move <now>\n"

    input_expr = "-s"
    input_expr = "--speed"

    input_expr = " [ FILE ] move --speed 11 <now>\n"

    input_expr = " ( move | fire | turn ) \n"

    input_expr = " [ FILE ] ( move | fire | turn ) \n"

    input_expr = "[ FILE ]"
    input_expr = "[ FILE | BOOK | MAGAZINE | FLYER ]"
    input_expr = "[ FILE | BOOK | MAGAZINE | FLYER ] [ WORD ]"
    input_expr = "[ FILE | BOOK ]"
    input_expr = "[ FILE | BOOK | FILM ] [ WORD ]"
    
    input_expr = " [ FILE ] ( move | fire | turn ) [ --speed 11 --angle 35 ] <when>\n"
    # '[' before speed parse as 'command' ?

    input_expr = " [ --what ] "		# OK
    input_expr = " [ --what 11 ] "	# '[' parsed as 'command' ?

    print(f"usage pattern = '{input_expr}'")

    # Then parse tree is created out of the input_expr expression.
    # parser.debug = True  => Error: dot: can't open docopt_peg_parser_model.dot
    parse_tree = parser.parse(input_expr)

    result = visit_parse_tree(parse_tree, DocOptListVisitor())

    pp(ListSemanticResults(result))

    sys.exit(0)

#------------------------------------------------------------------------------

class DocOptListVisitor(PTNodeVisitor):

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

# SemanticActionResults . results = { [ name : value ], ... }
def ListSemanticResults(sx):

    def pass1_flatten(sx):
        if not isinstance(sx, SemanticActionResults):
            return flatten(sx)
        if sx.results is None  or  len(sx.results) <= 0:
            return
        out = [ ]
        for name, value in sx.results.items() :
            out.append(pass1_flatten(value))
        return flatten(out)

    listing = 'listing:'
    listing_len = len(listing)
    def pass2_clean(sx):
        if not isinstance(sx, list):
            return sx
        if isinstance(sx[0], str):
            name = sx[0]
            if name.startswith(listing):
                sx[0] = name[listing_len:]
        out = [ ]
        for value in sx :
            out.append( pass2_clean(value) )
        return out

    return pass2_clean ( pass1_flatten(sx) )
    
#------------------------------------------------------------------------------

idelta=4

def flatten_dict(sx, indent=0):

    i = ' ' * indent

    if len(sx) == 1 :
        key, value = list(sx.items())[0]
        if isinstance(value, list) and len(value) == 1:
            if key == value[0]:
                return flatten(value, indent=indent+idelta)
    
    out = {}
    for key, value in sx.items():
        out[key] = flatten(value, indent=indent+idelta)
    return out

#------------------------------------------------------------------------------

#  ['optional', ['terminal:choice', ['operand', 'WORD']]]

def flatten_chooser(chain_name, sx, indent=0):
    i = ' ' * indent
    if sx[1][0] == f"terminal:{chain_name}":
        return [ sx[0], sx[1][1] ]
    return sx

#------------------------------------------------------------------------------

def flatten_list(sx, indent=0):
    
    i = ' ' * indent

    # print(f"{i}: flatten_list : sx = {repr(sx)}")

    if len(sx) <= 0:
        return []

    # print(f"{i}: flatten list")
    if len(sx) == 1 :
        return flatten(sx[0], indent=indent+idelta)

    out = []
    for value in sx:
        out.append(flatten(value, indent=indent+idelta))

    if len(out) > 0 :
        if out[0] == 'choice':
            return flatten_chain('choice', out, indent=indent+idelta)
        if out[0] in ['optional', 'required']:
            return flatten_chooser('choice', out, indent=indent+idelta)

    return out

#------------------------------------------------------------------------------

def flatten(sx, indent=0):
    # i = ' ' * indent
    if isinstance(sx, str):
        return sx
    if isinstance(sx,list):
        return flatten_list(sx, indent=indent+idelta)
    if isinstance(sx, dict):
        return flatten_dict(sx, indent=indent+idelta)
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

def flatten_chain(chain_name, sx, indent=0):

    i = ' ' * indent

    terminal = f"terminal:{chain_name}"
    listing  = f"listing:{chain_name}"

    print(f"{i}: flatten_chain : enter : '{chain_name}' : sx = {repr(sx)}")

    if not is_chain(chain_name, sx):
        # print(f"{i}: flatten_chain : leave : '{chain_name}' : not a chain")
        return sx
    
    # Terminal if [1] is not a list
    if not isinstance(sx[1], list):
        # print(f"{i}: flatten_chain : leave : '{chain_name}' : not a chain")
        return [ terminal, sx[1] ]
    
    # Terminal if [1][1] is not of this chain
    if not is_chain(chain_name, sx[1][1]):
        # print(f"{i}: flatten_chain : leave : '{chain_name}' : terminal")
        name = terminal if sx[0] == chain_name else sx[0]
        return [ name, sx[1] ]

    child = flatten_chain(chain_name, sx[1][1], indent=indent+idelta)
    # print(f"{i}  : child     :  {repr(child)}")
    # print(f"{i}  : child[1]  :  {repr(child[1])}")

    out = [ listing, [ sx[1][0] ] ]
    # print(f"{i}  : out'     =>  {repr(out)}")

    if child[0].startswith('terminal:') :
        # print(f"{i}  - append    :  {repr(child[1])}")
        out[1].append(child[1])
    else :
        # print(f"{i}  - extend    :  {repr(child[1])}")
        out[1].extend(child[1])

    # print(f"{i}  : out      =>  {repr(out)}")
    
    return out

#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#------------------------------------------------------------------------------
