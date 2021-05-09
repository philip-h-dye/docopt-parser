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

from grammar.python.common import newline, blank_line

from p import pp_str

#------------------------------------------------------------------------------

def words():
    return RegExMatch(r'[\S ]+', rule_name='words')

def element():
    # Without an enclosing list for 'words, newline', OrderedChoice
    #   implicitly becomes Sequence !
    return OrderedChoice ( [ words, blank_line, newline ], rule_name='element' )

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

    def test_alone (self) :

        parser = ParserPython( document, skipws=False )

        text = '\n\n\n'
        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        t_newline     = Terminal(newline(), 0, '\n')
        t_blank_line  = Terminal(blank_line(), 0, '\n')
        e_newline     = NonTerminal(element(), [t_newline])
        e_blank_line  = NonTerminal(element(), [t_blank_line])
        p_body        = NonTerminal(body(), [ e_newline, e_blank_line, e_blank_line ])
        p_eof         = Terminal(EOF(), 0, '')
        expect        = NonTerminal(document(), [p_body, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_with_some_words_1 (self) :

        parser = ParserPython( document, skipws=False )

        text = f"{self.words1}\n\n"

        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        t_words1	  = Terminal(words(), 0, self.words1)
        e_words1	  = NonTerminal(element(), [ t_words1 ])
        t_newline     = Terminal(newline(), 0, '\n')
        e_newline     = NonTerminal(element(), [ t_newline ])
        t_blank_line  = Terminal(blank_line(), 0, '\n')
        e_blank_line  = NonTerminal(element(), [ t_blank_line ])
        p_body        = NonTerminal(body(), [ e_words1, e_newline, e_blank_line ])
        p_eof         = Terminal(EOF(), 0, '')
        expect        = NonTerminal(document(), [p_body, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_with_some_words_2 (self) :

        parser = ParserPython( document, skipws=False )

        text = f"{self.words1}\n\n"

        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        expect = NonTerminal(document(), [
            NonTerminal(body(), [
                NonTerminal(element(), [
                    Terminal(words(), 0, self.words1) ,
                ]) ,
                NonTerminal(element(), [
                    Terminal(newline(), 0, '\n') ,
                ]) ,
                NonTerminal(element(), [
                    Terminal(blank_line(), 0, '\n') ,
                ]) ,
            ]) ,
            Terminal(EOF(), 0, '') ,
        ] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_with_some_paragraphs (self) :

        parser = ParserPython( document, skipws=False )

        paragraph = f"{self.words1}\n{self.words2}\n{self.words3}\n"

        text = paragraph + '\n' + paragraph

        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        x_paragraph = [
                NonTerminal(element(), [
                    Terminal(words(), 0, self.words1) ,
                ]) ,
                NonTerminal(element(), [
                    Terminal(newline(), 0, '\n') ,
                ]) ,
                NonTerminal(element(), [
                    Terminal(words(), 0, self.words2) ,
                ]) ,
                NonTerminal(element(), [
                    Terminal(newline(), 0, '\n') ,
                ]) ,
                NonTerminal(element(), [
                    Terminal(words(), 0, self.words3) ,
                ]) ,
                NonTerminal(element(), [
                    Terminal(newline(), 0, '\n') ,
                ]) ,
        ]

        expect = NonTerminal(document(), [
            NonTerminal(body(), [
                *x_paragraph,
                NonTerminal(element(), [
                    Terminal(blank_line(), 0, '\n') ,
                ]) ,
                *x_paragraph,
            ]) ,
            Terminal(EOF(), 0, '') ,
        ] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

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
