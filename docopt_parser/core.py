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
from .p import pp

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

        return self.raw_parse_tree

        # self.parse_tree = DocOptSimplifyVisitor().visit(self.raw_parse_tree)
        # return self.parse_tree

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
        # if isinstance(t, (NonTerminal, Unwrap, list)):
        if isinstance(t, (NonTerminal, list)):
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
