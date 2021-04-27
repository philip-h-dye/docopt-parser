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

sys.path.insert(0, 'canonical')

import common

from p import pp_str

#------------------------------------------------------------------------------

newline = common.newline

def words():
    return RegExMatch(r'[\w.]+', rule_name='words')

def text_line():
    return Sequence(words, newline,
                    rule_name='text_line', skipws=False )
def paragraph():
    return OneOrMore( text_line, rule_name='paragraph', skipws=False )

# def element():
#     return OrderedChoice ( paragraph, newline, rule_name='element' )

# def elements():
#     return OneOrMore ( element, rule_name='elements' )

#------------------------------------------------------------------------------

# FIXME: - need test which are negative.
#        - also, positive and negative lookahead with And(), Not()

class Test_Import ( unittest.TestCase ) :

    line1 = "now.is.the.time.for.all.good.men\n"
    line2 = "to.rise.up.in.defense.of.freedom\n"

    def texts(self, rule, ch):
        yield Sequence(rule), ch, [Terminal(rule, 0, ch)]
        yield Sequence(rule, self.words), \
            ''.join([ch, 'good.men']), \
            [ Terminal(rule, 0, ch), Terminal(self.words, 0, 'good.men') ]
        yield Sequence(self.words, rule, self.words), \
            ''.join(['rise', ch, 'up']), \
            [ Terminal(self.words, 0, 'rise'), Terminal(rule, 0, ch), Terminal(self.words, 0, 'up') ]
        yield Sequence(rule, self.words), \
            ''.join([ch, 'in.defense.of.freedom']), \
            [ Terminal(rule, 0, ch), Terminal(self.words, 0, 'in.defense.of.freedom') ]

    def single_char_test(self, rule_f, ch):
        """Test for single : by itself and at start, middle and end of text"""
        rule = self.literal(rule_f, ch)
        for grammar, input, expect in self.texts(rule, ch):
            parser = ParserPython( grammar, skipws=False )
            parsed = parser.parse(input)
            # print_parsed(expect)
            # print_parsed(flatten(parsed))
            parsed = flatten(parsed)
            expect = flatten(expect)
            assert parsed == expect, ( f"ch = ascii {ord(ch)} : input = '{input}' :\n"
                                       f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def _test_ws (self) :
        """ws : One or more of space, tab, carriage return"""
        rule_f = common.ws
        with self.assertRaises(arpeggio.NoMatch) :
            parsed = ParserPython( rule_f(), skipws=False ).parse('')
        for ch in " \t\r" :
            self.single_char_test(rule_f, ch)

    #--------------------------------------------------------------------------

    def _test_wx (self) :
        """wx : Zero or more of space, tab, carriage return"""
        rule_f = common.wx
        input = ''
        parsed = ParserPython( rule_f(), skipws=False ).parse(input)
        # When wx is a sequence : ws*
        # # expect = []
        # Now that it is a single regex :
        expect = None
        assert parsed == expect, ( f"empty string : input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )
        for ch in " \t\r" :
            self.single_char_test(rule_f, ch)

    #--------------------------------------------------------------------------

    def SKIP_test_bar (self) :
        self.single_char_test(common.BAR, '|')

    def SKIP_test_comma (self) :
        self.single_char_test(common.COMMA, ',')

    def SKIP_test_l_paren (self) :
        self.single_char_test(common.L_PAREN, '(')
    def SKIP_test_r_paren (self) :
        self.single_char_test(common.R_PAREN, ')')

    def SKIP_test_l_bracket (self) :
        self.single_char_test(common.L_BRACKET, '[')
    def SKIP_test_r_bracket (self) :
        self.single_char_test(common.R_BRACKET, ']')

    def _test_newline (self) :
        self.single_char_test(common.newline, '\n')

    #--------------------------------------------------------------------------

    def _test_newline_elements__only (self) :
        def element():
            return OrderedChoice ( newline, rule_name='element' )
        def body():
            return OneOrMore ( element, rule_name='body' )
        def document():
            return Sequence( body, EOF, rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        input = '\n\n\n'
        parsed = parser.parse(input)
        # print('\n: parsed') ; pp(parsed)

        p_newline	= Terminal(newline(), 0, '\n')
        p_element	= NonTerminal(element(), [p_newline])
        p_body		= NonTerminal(body(), [ p_element, p_element, p_element ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_body, p_eof] )
        # print('\n: expect') ; pp(expect)
        #
        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def _test_text_line_single (self) :
        def document():
            return Sequence( text_line, EOF, rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        input = self.line1
        parsed = parser.parse(input)
        # print('\n: parsed') ; pp(parsed)

        p_newline	= Terminal(newline(), 0, '\n')
        p_l1_words	= Terminal(words(), 0, self.line1[:-1])
        p_l1_text_line	= NonTerminal(text_line(), [ p_l1_words, p_newline ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_l1_text_line, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_text_line_pair (self) :
        # def element():
        #     return OrderedChoice ( newline, rule_name='element' )
        def body():
            return OneOrMore ( text_line, rule_name='body' )
        def document():
            return Sequence( body, EOF, rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        input = self.line1 + self.line2
        parsed = parser.parse(input)
        print('\n: parsed') ; pp(parsed)
        #
        print('\n: flatten') ; pp(flatten(parsed))

        # if True : return

        p_newline	= Terminal(newline(), 0, '\n')
        p_l1_words	= Terminal(words(), 0, self.line1[:-1])
        p_l1_text_line	= NonTerminal(text_line(), [ p_l1_words, p_newline ])
        p_l2_words	= Terminal(words(), 0, self.line2[:-1])
        p_l2_text_line	= NonTerminal(text_line(), [ p_l2_words, p_newline ])
        p_body		= NonTerminal(body(), [ p_l1_text_line, p_l2_text_line ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_body, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"input		= '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #-------------------------------------------------------------------------

    def _test_text_line_elements__only (self) :
        def element():
            return OrderedChoice ( text_line, rule_name='element' )
        def body():
            return OneOrMore ( element, rule_name='body' )
        def document():
            return Sequence( body, EOF, rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        input = self.line1 + self.line2
        parsed = parser.parse(input)
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

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_paragraph_single (self) :
        def body():
            return OneOrMore ( paragraph, rule_name='body' )
        def document():
            return Sequence( body, EOF, rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        input = self.line1 + self.line2
        parsed = parser.parse(input)
        # print('\n: parsed') ; pp(parsed)

        p_newline	= Terminal(newline(), 0, '\n')
        p_l1_words	= Terminal(words(), 0, self.line1[:-1])
        p_l1_text_line	= NonTerminal(text_line(), [ p_l1_words, p_newline ])
        p_l2_words	= Terminal(words(), 0, self.line2[:-1])
        p_l2_text_line	= NonTerminal(text_line(), [ p_l2_words, p_newline ])
        p_paragraph	= NonTerminal(body(), [ p_l1_text_line, p_l2_text_line ])
        p_body 		= NonTerminal(body(), [ p_paragraph ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [ p_body, p_eof ] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def _test_paragraph_multiple (self) :
        def body():
            return OneOrMore ( element, rule_name='body' )
        def document():
            return Sequence( body, EOF, rule_name='document' )
        # print('\n: document') ; pp(document())
        parser = ParserPython( document, skipws=False )

        input = self.line1 + self.line2
        input = input + '\n'
        parsed = parser.parse(input)
        print('\n: parsed') ; pp(parsed)

        return

        p_newline	= Terminal(newline(), 0, '\n')
        p_l1_words	= Terminal(words(), 0, self.line1[:-1])
        p_l1_text_line	= NonTerminal(text_line(), [ p_l1_words, p_newline ])
        p_l2_words	= Terminal(words(), 0, self.line2[:-1])
        p_l2_text_line	= NonTerminal(text_line(), [ p_l2_words, p_newline ])
        p_paragraph	= NonTerminal(body(), [ p_l2_text_line, p_l2_text_line ])
        p_body		= NonTerminal(body(), [ p_paragraph, p_newline, p_paragraph ])
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_body, p_eof] )
        # print('\n: expect') ; pp(expect)

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def literal(self, rule_f, ch):
        rule = rule_f()
        return StrMatch(ch, rule_f.__name__) if isinstance(rule, str) else rule

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
