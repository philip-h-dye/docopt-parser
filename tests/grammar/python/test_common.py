import sys
import os
import re
import string
import unittest

from copy import deepcopy
from glob import glob
from itertools import chain
from prettyprinter import cpprint as pp, pprint as pp_plain

#------------------------------------------------------------------------------

# from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore, Sequence
# from arpeggio import OrderedChoice
# from arpeggio import NonTerminal, Terminal, ParseTreeNode, flatten
# from arpeggio import ParserPython, PTNodeVisitor, visit_parse_tree
# from arpeggio import RegExMatch as _
# import arpeggio

from arpeggio import ParserPython, flatten, Terminal, Sequence, NoMatch
from arpeggio import EOF, StrMatch, RegExMatch, OrderedChoice, OneOrMore

#------------------------------------------------------------------------------

from grammar.python import common

from p import pp_str

#------------------------------------------------------------------------------

FAKE_SPACE = '.' # chr(1) # Control-A
# Uses FAKE_SPACE in place of space for matching scenarios to work.  If the
# chosen character becomes specified in grammar/python/common.py, simply
# chose another.  Using an available punctuation character makes the
# test data is displayed on errors.

# used in the paragraph scenario
WORDS_CHARACTER_REGEX_NO_LF = r'[\w<space><>]'.replace('<space>', FAKE_SPACE)

WORDS_CHARACTER_REGEX = r'[\w\n<space><>]'.replace('<space>', FAKE_SPACE)
words_single_character = re.compile(WORDS_CHARACTER_REGEX)

# '<>' used bracket any additional characters that need to be escaped for
# a given test, such as '<lf>' for linefeed.

#------------------------------------------------------------------------------

# FIXME: - need more tests which are negative.
#        - also, positive and negative lookahead with And(), Not()

class Test_Common ( unittest.TestCase ) :

    def _test_1_x09_tab (self) :
        self.single_char_test(common.tab, common.TAB)

    def test_1_x0a_lf__linefeed (self) :
        self.single_char_test(common.lf, common.LF)

    def SKIP_test_1_x0d_cr__carriage_return (self) :
        self.single_char_test(common.space, common.CR)

    def SKIP_test_1_x20_space (self) :
        self.single_char_test(common.space, common.SPACE)

    def SKIP_test_1_x2c_comma (self) :
        self.single_char_test(common.comma, common.COMMA)

    def SKIP_test_1_x28_l_paren (self) :
        self.single_char_test(common.l_paren, common.L_PAREN)
    def SKIP_test_1_x29_r_paren (self) :
        self.single_char_test(common.r_paren, common.R_PAREN)

    def SKIP_test_1_x3d_eq__equals_sign (self) :
        self.single_char_test(common.eq, common.EQ)

    def SKIP_test_1_x5b_l_bracket (self) :
        self.single_char_test(common.l_bracket, common.L_BRACKET)
    def SKIP_test_1_x5d_r_bracket (self) :
        self.single_char_test(common.r_bracket, common.R_BRACKET)

    def SKIP_test_1_x7c_bar__vertical_bar (self) :
        self.single_char_test(common.bar, common.BAR)

    #--------------------------------------------------------------------------

    def SKIP_test_2_01_whitespace_chars(self) :
        for ch in common.WHITESPACE_CHARS :
            rule_f = lambda : StrMatch(ch, rule_name=f"single '{ch}'")
            self.single_char_test(rule_f, ch)

    def SKIP_test_2_02_whitespace_rules(self) :
        for rule in common.WHITESPACE_RULES :
            self.single_char_test(rule, rule())

    def SKIP_test_2_03_whitespace (self) :
        """whitespace : One of space, tab, carriage-return"""
        with self.assertRaises(NoMatch) :
            parsed = ParserPython( common.whitespace(), skipws=False ).parse('')
        for ch in common.WHITESPACE_CHARS :
            self.single_char_test(common.whitespace, ch)

    def SKIP_test_2_04_ws (self) :
        """ws : One or more of space, tab, carriage-return"""
        self.one_or_more_of_charset(common.ws, common.WHITESPACE_CHARS)

    def BROKEN_test_2_05_wx (self) :
        """wx : Zero or more of space, tab, carriage return"""
        rule_f = common.wx
        input = ''
        parser = ParserPython( rule_f(), skipws=False )
        # for input in [ '', ' ',
        # for input in [ '', ' ',
        # for input in [ '', ' ',
        parsed = parser.parse('')
        # When wx is a sequence : ws*
        # # expect = []
        # Now that it is a single regex :
        expect = None
        assert parsed == expect, ( f"empty string : input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )
        for ch in common.WHITESPACE_CHARS :
            self.single_char_test(rule_f, ch)

    def SKIP_test_2_06_newline (self) :
        """newline : a newline, optionally preceeded by whitespace"""
        # self.single_char_test(common.blank_line, '\n')
        pass

    def SKIP_test_2_07_blankline (self) :
        """blank_line : a newline, preceeded by a newline, optional whitespace between"""
        # self.single_char_test(common.blank_line, '\n')
        pass

    #--------------------------------------------------------------------------

    def one_or_more_of_charset(self, rule_f, charset):
        """..."""
        with self.assertRaises(NoMatch) :
            parsed = ParserPython( rule_f(), skipws=False ).parse('')
        self.or_more_of_charset(rule_f, charset)

    def zero_or_more_of_charset(self, rule_f, charset):
        """..."""
        parsed = ParserPython( rule_f(), skipws=False ).parse('')
        self.or_more_of_charset(rule_f, charset)

    def or_more_of_charset(self, rule_f, charset):
        """..."""
        for ch in charset :
            print(f": ch = '{ch}'")
            self.single_char_test(rule_f, ch)
        for ch in charset :
            pass # self.single_char_test(rule_f, ch*2)
        for ch in charset :
            pass # self.single_char_test(rule_f, ch*3)
        for ch in charset :
            pass # self.single_char_test(rule_f, ch+charset)
        for ch in charset :
            pass # self.single_char_test(rule_f, charset+ch)

    #--------------------------------------------------------------------------

    def single_char_test(self, rule_f, ch):
        """Test for single : by itself and at start, middle and end of text"""
        assert len(ch) == 1, "single_char_test() only works for single character strings !"
        rule = rule_f()
        if isinstance(rule, str) :
            print(f"- rule '{rule_f.__name__}' : create StrMatch() rule for "
                  f"literal '{ch}' : {ord(ch)} : {hex(ord(ch))}")
            rule = StrMatch(ch, rule_f.__name__)
        for grammar, input, expect in self.scenarios(rule, ch):
            parser = ParserPython( grammar, skipws=False )
            write_scratch( call={'fcn' : 'single_char_test' , 'ch' : ch ,
                                 'rule_f' : rule_f , 'rule' : rule , },
                           grammar=grammar, input=input,
                           expect=expect, expect_f=flatten(expect),
                           model=parser.parser_model, _clean=True, )
            if True : # '\n' in ch :
                print(f"\n: char  = '{ch}' : {ord(ch)} : {hex(ord(ch))}")
                print(f"\n: input = '{input}'")
            try :
                parsed = parser.parse(input)
                write_scratch ( parsed=parsed )
                write_scratch ( parsed_f=flatten(parsed) )
            except :
                print(f"\nParser FAILED : ch = '{ch}' : ascii {ord(ch)}"
                      f"\ninput = '{input}'"
                      f"[grammar]\n{pp_str(grammar)}\n"
                      f"\n[expect]\n{pp_str(expect)}")
                raise
            # print("[ expect ]") ; pp(expect)
            # print("[ parsed ]") ; pp(parsed)
            parsed = flatten(parsed)
            expect = flatten(expect)
            assert parsed == expect, \
                ( f"ch = ascii {ord(ch)} : input = '{input}' :\n"
                  f"[grammar]\n{pp_str(grammar)}\n"
                  f"[expect]\n{pp_str(expect)}\n"
                  f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def scenarios(self, rule, s): # -> grammar, input, expect

        assert FAKE_SPACE not in s, "INTERNAL ERROR, chosen 'fake space' in string to be tested !"

        rule = deepcopy(rule)

        t_eof = Terminal(EOF(), 0, '')
        t_s = Terminal(rule, 0, s)

        if True :
            # 's' by itself
            yield Sequence( (rule, EOF) ), s, ( t_s, t_eof )

        if True :
            # 's' at start followed by a phrase
            phrase = fake_spaces_etc('now is the time')
            ( _words, phrase, _lf ) = self.get_words(s, phrase)
            assert s not in phrase
            text = ''.join([ s, phrase ])
            body = OneOrMore( OrderedChoice ( [ rule, _words ] ) )
            grammar = Sequence( ( body, EOF ) )
            expect = ( ( t_s, Terminal(_words(), 0, phrase) ), t_eof )
            yield grammar, text, expect

        if False :
            # 's' at start followed by a phrase, TWICE
            phrase = fake_spaces_etc('now is the time')
            ( _words, phrase, _lf ) = self.get_words(s, phrase)
            assert s not in phrase
            text = ''.join([ *((s, phrase) * 2) ])
            body = OneOrMore( OrderedChoice ( [ rule, _words ] ) )
            grammar = Sequence( ( body, EOF ) )
            expect = ( (t_s, Terminal(_words(), 0, phrase)) * 2, t_eof )
            yield grammar, text, expect

        if False :
            # 's' at start followed by a phrase, Two Lines
            phrase = fake_spaces_etc('now is the time')
            # ** Won't catch the '\n' since it is added below
            ( _words, phrase, _lf ) = self.get_words(s, phrase)
            assert s not in phrase
            pair = (s, phrase)
            text = ''.join( ( *pair, '\n', *pair ) )
            ( _words, do_not_use, _lf ) = self.get_words(s, text)
            newline = RegExMatch( r'[\n]', rule_name='newline' )
            body = OneOrMore( OrderedChoice ( [ rule, _words, newline ] ) )
            grammar = Sequence( ( body, EOF ) )
            # t_newline = Terminal(newline, 0, '\n')
            t_words_1 = Terminal(_words(), 0, phrase+_lf)
            t_words_2 = Terminal(_words(), 0, phrase)
            expect = ( ( t_s, t_words_1, t_s, t_words_2 ), t_eof )
            yield grammar, text, expect

        # 's' in the middle between two phrases
        left_phrase = fake_spaces_etc('for all good men')
        right_phrase = fake_spaces_etc('to rise up')
        assert s not in left_phrase
        assert s not in right_phrase
        t_left = Terminal(words(), 0, left_phrase)
        t_right = Terminal(words(), 0, right_phrase)
        grammar = Sequence( (words, rule, words, EOF) )
        expect = ( t_left, t_s, t_right, t_eof )
        text = ''.join([left_phrase, s, right_phrase])
        yield grammar, text, expect

        # 's' at end, preceeded by a phrase
        phrase = fake_spaces_etc('in defense of freedom')
        t_phrase = Terminal(words(), 0, phrase)
        assert s not in phrase
        yield Sequence( (rule, words, EOF) ), ''.join([s, phrase ]), \
            ( t_s, t_phrase, t_eof )

        # 's' occuring a few times in the midst of a text
        text = """<s>
<s>The essence of America — that which really unites us —
<s>is not ethnicity, or nationality, or religion.
It is an idea—and what an idea it is :
that you can come <s><s> from humble circumstances
and do great things.<s>
  - Condoleezza Rice
<s>"""
        # zero length phrases at start, end and one more in the middle
        n_empty = 3

        text = text.replace('<s>', chr(7))
        text = fake_spaces_etc(text)
        text = text.replace(chr(7), '<s>')

        ( _words, text ) = self.get_words(s, text)

        assert not ( s in text )

        phrases = re.split('<s>', text)
        assert len(phrases[0]) == 0
        assert len(phrases[-1]) == 0

        catchall = RegExMatch( r'.*', rule_name='catch_all' )
        newline = RegExMatch( r'[\n]', rule_name='newline' )
        body = OneOrMore( OrderedChoice ( [ rule, _words, catchall, newline ] ) )
        grammar = Sequence( ( body, EOF ) )

        t_s = Terminal(rule, 0, s)
        def tw(p) :
            return Terminal(words(), 0, p)
        terms = [ ( ( tw(p) if len(p) > 0 else ()), t_s ) for p in phrases ]
        terms = flatten(terms)
        terms[-1] = t_eof # reuse instead of remove, was "del terms[-1]"
        assert len(terms) == 2 * len(phrases) - n_empty

        # Simplistic handling of Zero/One Or Many rules
        if isinstance(rule, RegExMatch) and rule.to_match[-1] in '*+':
            # collapse any series of 't_s' elements into a single ts element
            limit = len(terms) - 1
            idx = 0
            while idx < limit :
                if ( terms[idx].rule_name == t_s.rule_name and
                     terms[idx+1].rule_name == t_s.rule_name ) :
                    value = terms[idx].value+ terms[idx+1].value
                    terms[idx] = Terminal(rule, 0, value )
                    del terms[idx+1]
                    limit -=1
                else :
                    idx += 1

        yield grammar, s.join(phrases), tuple(terms)

    #--------------------------------------------------------------------------

    def get_words(self, s, text):
        """When both 's' and 'text' contains a linefeed, change the 'words'
           regex to not accept linefeed and replace all occurances of linefeed
           in 'text' with '<linefeed>'.
        """
        _lf = '\n'
        if _lf in s and _lf in text :
            print(": paragraph scenario with 'LF' character")
            _lf = '<linefeed>'
            text = text.replace('\n', _lf)
            def _words():
                return RegExMatch(WORDS_CHARACTER_REGEX_NO_LF+'+',
                                  rule_name='words')
        else :
            _words = words

        return ( _words, text, _lf )

    #--------------------------------------------------------------------------

    def single_char_regex_test(self, rule_f, ch):
        """Test for single ch matched by rule : by itself and at start, middle and end of text"""
        #wip !@#
        for grammar, input, expect in self.scenarios(rule_f(), ch):
            parser = ParserPython( grammar, skipws=False )
            try :
                parsed = parser.parse(input)
            except :
                print(f"\nParser FAILED : ch = '{ch}' : ascii {ord(ch)}"
                      f"input = '{input}'\n"
                      f"[expect]\n{pp_str(expect)}\n"
                      f"[parsed]\n{pp_str(parsed)}" )
                continue
            # print_parsed(expect)
            # print_parsed(flatten(parsed))
            parsed = flatten(parsed)
            expect = flatten(expect)
            assert parsed == expect, \
                ( f"ch = ascii {ord(ch)} : input = '{input}' :\n"
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

# https://stackoverflow.com/questions/11066400/remove-punctuation-from-unicode-formatted-strings
import unicodedata
import sys

unicode_punctuation = \
    dict.fromkeys ( i for i in range(sys.maxunicode)
                    if unicodedata.category(chr(i)).startswith('P') )

def remove_punctuation(text):
    return text.translate(unicode_punctuation)

#------------------------------------------------------------------------------

def fake_spaces_etc(s):
    # replace space, ' ', with FAKE_SPACE
    s = s.replace(' ', FAKE_SPACE)
    # replace tab, '\t', with FAKE_SPACE
    s = s.replace("\t", FAKE_SPACE)
    # strip punctuation
    # NO # s = re.sub(r'[[:punct:]]', '', s)
    # NO # s = s.strip(string.punctuation)
    # punctuation = string.punctuation.replace('['+FAKE_SPACE+']', '')
    # Misses unicode punctuation # s = re.sub('['+punctuation+']', '', s)
    # s = re.sub(ur"\p{P}", '', s) # requires third-party 'regex' as 're'
    if True : # FAKE_SPACE in unicode_punctuation : # always fails
        s = s.replace(FAKE_SPACE, chr(3))
    s = remove_punctuation(s)
    if True : # FAKE_SPACE in unicode_punctuation : # always fails
        s = s.replace(chr(3), FAKE_SPACE)
    assert not ( '-' in s )	# ASCII dash
    assert not ( '—' in s )	# Unicode long dash ?
    return s

# rule for use in matching scenarios
def words():
    expr = WORDS_CHARACTER_REGEX + '+'
    return RegExMatch(expr, rule_name='words')

#------------------------------------------------------------------------------

def write_scratch ( **kwargs ) :
    if '_clean' in kwargs and kwargs['_clean'] is True:
        for file in glob("scratch/*"):
            os.unlink(file)
    for name in kwargs :
        with open ( f"scratch/{name}", 'w' ) as f :
            pp_plain( kwargs[name] , stream=f )

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
