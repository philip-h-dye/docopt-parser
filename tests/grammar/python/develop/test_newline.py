import sys

import unittest

from itertools import chain

from prettyprinter import cpprint as pp

#------------------------------------------------------------------------------

from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore, Sequence
from arpeggio import And, Not, StrMatch, RegExMatch # as _
from arpeggio import OrderedChoice

from arpeggio import NonTerminal, Terminal, ParseTreeNode, flatten
from arpeggio import ParserPython, PTNodeVisitor, visit_parse_tree

import arpeggio

#------------------------------------------------------------------------------

from grammar.python.common import newline

from p import pp_str

#------------------------------------------------------------------------------

def words():
    return RegExMatch(r'[\S ]+', rule_name='words')

def element():
    # Without an enclosing list for 'words, newline', OrderedChoice
    #   implicitly becomes Sequence !
    return OrderedChoice ( [ words, newline ], rule_name='element' )

def body():
    return OneOrMore ( element, rule_name='body' )

def document():
    return Sequence( body, EOF, rule_name='document' )

#------------------------------------------------------------------------------

# FIXME:  test the error handling with invalid texts

class Test_Import ( unittest.TestCase ) :

    words1 = "now is the time for all good men"
    words2 = "to rise up in defense of freedom,"
    words3 = "liberty and justice for all"

    #--------------------------------------------------------------------------

    def test_newline_elements_only (self) :

        parser = ParserPython( document, skipws=False )

        text = '\n\n\n'
        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        p_newline	= Terminal(newline(), 0, '\n')
        p_element	= NonTerminal(element(), [p_newline])
        p_body		= NonTerminal(body(), [ p_element, p_element, p_element ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_body, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_words_and_newline (self) :
        def document():
            return Sequence( words, newline, EOF, rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        text = self.words1 + '\n'
        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        p_w1_words	= Terminal(words(), 0, self.words1)
        p_newline	= Terminal(newline(), 0, '\n')
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_w1_words, p_newline, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    #builder
    def builder ( self, texts ):

        p_newline = Terminal(newline(), 0, '\n')

        text = ''.join(flatten(texts))

        body_ = [ ]
        for atom in texts :
            if atom == '\n':
                # print(f": atom = <newline>")
                body_.append ( NonTerminal(element(), [ p_newline ] ) )
            else:
                # print(f": atom = '{atom}'")
                body_.append ( NonTerminal(element(), [ Terminal( words(), 0, atom ) ] ) )

        p_body		= NonTerminal(body(), body_)
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_body, p_eof] )

        # print('\n: expect') ; pp(expect)

        return ( text, expect )


    #--------------------------------------------------------------------------

    def apply (self, texts ) :

        ( text, expect ) = self.builder (
            texts,
        )

        # print(f"\n: text :\n{text}")

        parser = ParserPython( document, skipws=False )
        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_builder_000 (self) :
        self.apply ( ( self.words1, '\n', '\n',
                       #
                   ) )

    def test_builder_001 (self) :
        self.apply ( ( self.words1, '\n', '\n',
                       self.words2, '\n', '\n', '\n',
                       self.words3, '\n',
                   ) )    

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    kwargs['file'] = tprint._tty
    print(*args, **kwargs)

tprint._tty = open("/dev/tty", 'w')

#------------------------------------------------------------------------------

def print_parsed(parsed):
    if isinstance(parsed, ParseTreeNode):
        tprint(parsed.tree_str())
    else:
        pp(parsed)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
