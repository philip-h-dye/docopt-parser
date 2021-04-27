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

def words():
    return RegExMatch(r'[\w.]+', rule_name='words')

#------------------------------------------------------------------------------

# FIXME: - need test which are negative.
#        - also, positive and negative lookahead with And(), Not()

class Test_Import ( unittest.TestCase ) :

    def test_ws (self) :
        """ws : One or more of space, tab, carriage return"""
        rule_f = common.ws
        with self.assertRaises(arpeggio.NoMatch) :
            parsed = ParserPython( rule_f(), skipws=False ).parse('')
        for ch in " \t\r" :
            self.single_char_test(rule_f, ch)

    #--------------------------------------------------------------------------

    def test_wx (self) :
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

    def test_bar (self) :
        self.single_char_test(common.BAR, '|')

    def test_comma (self) :
        self.single_char_test(common.COMMA, ',')

    def test_l_paren (self) :
        self.single_char_test(common.L_PAREN, '(')
    def test_r_paren (self) :
        self.single_char_test(common.R_PAREN, ')')

    def test_l_bracket (self) :
        self.single_char_test(common.L_BRACKET, '[')
    def test_r_bracket (self) :
        self.single_char_test(common.R_BRACKET, ']')

    def test_newline (self) :
        self.single_char_test(common.newline, '\n')

    #--------------------------------------------------------------------------

    def single_char_test(self, rule_f, ch):
        """Test for single : by itself and at start, middle and end of text"""
        rule = self.literal(rule_f, ch)
        for grammar, input, expect in self.scenarios(rule, ch):
            parser = ParserPython( grammar, skipws=False )
            parsed = parser.parse(input)
            # print_parsed(expect)
            # print_parsed(flatten(parsed))
            parsed = flatten(parsed)
            expect = flatten(expect)
            assert parsed == expect, ( f"ch = ascii {ord(ch)} : input = '{input}' :\n"
                                       f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    def scenarios(self, rule, ch):
        yield Sequence(rule), ch, [Terminal(rule, 0, ch)]
        yield Sequence(rule, words), \
            ''.join([ch, 'good.men']), \
            [ Terminal(rule, 0, ch), Terminal(words(), 0, 'good.men') ]
        yield Sequence(words, rule, words), \
            ''.join(['rise', ch, 'up']), \
            [ Terminal(words(), 0, 'rise'), Terminal(rule, 0, ch), Terminal(words(), 0, 'up') ]
        yield Sequence(rule, words), \
            ''.join([ch, 'in.defense.of.freedom']), \
            [ Terminal(rule, 0, ch), Terminal(words(), 0, 'in.defense.of.freedom') ]

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
