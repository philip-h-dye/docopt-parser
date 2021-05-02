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

import grammar.python.common as common

from p import pp_str

#------------------------------------------------------------------------------

newline = common.newline

def words():
    return RegExMatch(r'[\w.]+', rule_name='words')

def text_line():
    return Sequence( ( words ), newline,
                    rule_name='text_line', skipws=False )
def paragraph():
    return OneOrMore( ( text_line ), rule_name='paragraph', skipws=False )

#------------------------------------------------------------------------------

# FIXME: - need test which are negative.
#        - also, positive and negative lookahead with And(), Not()

class Test_Line ( unittest.TestCase ) :

    line1 = "now.is.the.time.for.all.good.men\n"
    line2 = "to.rise.up.in.defense.of.freedom\n"

    def test_00_simply_three_newlines (self) :
        def element():
            return OrderedChoice ( newline, rule_name='element' )
        def body():
            return OneOrMore ( element, rule_name='body' )
        def document():
            return Sequence( body, EOF, rule_name='document' )
        # print('\n: document') ; pp(document())
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
        #
        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_01_text_line_single (self) :
        def document():
            return Sequence( ( text_line, EOF ), rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        text = self.line1
        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        p_newline	= Terminal(newline(), 0, '\n')
        p_l1_words	= Terminal(words(), 0, self.line1[:-1])
        p_l1_text_line	= NonTerminal(text_line(), [ p_l1_words, p_newline ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_l1_text_line, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_02_text_line_pair (self) :
        def body():
            return OneOrMore ( [ text_line ], rule_name='body' )
        def document():
            return Sequence( ( body, EOF ), rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        text = self.line1 + self.line2
        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)
        #
        # print('\n: flatten') ; pp(flatten(parsed))

        p_newline	= Terminal(newline(), 0, '\n')
        p_l1_words	= Terminal(words(), 0, self.line1[:-1])
        p_l1_text_line	= NonTerminal(text_line(), [ p_l1_words, p_newline ])
        p_l2_words	= Terminal(words(), 0, self.line2[:-1])
        p_l2_text_line	= NonTerminal(text_line(), [ p_l2_words, p_newline ])
        p_body		= NonTerminal(body(), [ p_l1_text_line, p_l2_text_line ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_body, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text		= '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #-------------------------------------------------------------------------

    def test_03_text_line_elements (self) :
        def element():
            return OrderedChoice ( [ text_line ], rule_name='element' )
        def body():
            return OneOrMore ( [ element ], rule_name='body' )
        def document():
            return Sequence( ( body, EOF ), rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        text = self.line1 + self.line2
        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        p_newline	= Terminal(newline(), 0, '\n')
        
        p_l1_words	= Terminal(words(), 0, self.line1[:-1])
        p_l1_text_line	= NonTerminal(text_line(), [ p_l1_words, p_newline ])
        p_l1_element	= NonTerminal(element(), [ p_l1_text_line])

        p_l2_words	= Terminal(words(), 0, self.line2[:-1])
        p_l2_text_line	= NonTerminal(text_line(), [ p_l2_words, p_newline ])
        p_l2_element	= NonTerminal(element(), [ p_l2_text_line])

        p_body		= NonTerminal(body(), [ p_l1_element, p_l2_element ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_body, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_04_paragraph_single (self) :
        def body():
            return OneOrMore ( ( paragraph ), rule_name='body' )
        def document():
            return Sequence( ( body, EOF ), rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        text = self.line1 + self.line2
        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        p_newline	= Terminal(newline(), 0, '\n')
        p_l1_words	= Terminal(words(), 0, self.line1[:-1])
        p_l1_text_line	= NonTerminal(text_line(), [ p_l1_words, p_newline ])
        p_l2_words	= Terminal(words(), 0, self.line2[:-1])
        p_l2_text_line	= NonTerminal(text_line(), [ p_l2_words, p_newline ])
        p_paragraph	= NonTerminal(paragraph(), [ p_l1_text_line, p_l2_text_line ])
        p_body 		= NonTerminal(body(), [ p_paragraph ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [ p_body, p_eof ] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"text = '{text}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_05_paragraph_multiple (self) :
        def body():
            return OneOrMore ( OrderedChoice( [ paragraph, newline ] ), rule_name='body' )
        def document():
            return Sequence( ( body, EOF ), rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        text = self.line1 + self.line2 + '\n'
        text = text * 3
        parsed = parser.parse(text)
        # print('\n: parsed') ; pp(parsed)

        p_newline	= Terminal(newline(), 0, '\n')
        p_l1_words	= Terminal(words(), 0, self.line1[:-1])
        p_l1_text_line	= NonTerminal(text_line(), [ p_l1_words, p_newline ])
        p_l2_words	= Terminal(words(), 0, self.line2[:-1])
        p_l2_text_line	= NonTerminal(text_line(), [ p_l2_words, p_newline ])
        p_paragraph	= NonTerminal(paragraph(), [ p_l1_text_line, p_l2_text_line ])
        p_body 		= NonTerminal(body(), [
            p_paragraph, p_newline,
            p_paragraph, p_newline,
            p_paragraph, p_newline,
        ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [ p_body, p_eof ] )
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
    if False : # isinstance(parsed, ParseTreeNode):
        tprint(parsed.tree_str())
    else:
        # 'p' module add pretty printing for ParseTreeNode types
        pp(parsed)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
