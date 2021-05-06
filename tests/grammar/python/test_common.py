tst_debug_first_char				= False
tst_individual_characters			= True
tst_whitespace_chars				= True
tst_class_whitespace_rule_per_characters	= True
tst_class_rule_whitespace			= True
tst_class_or_more				= True

# FIXME: - need more tests which are negative.
#        - test positive and negative lookahead with And(), Not()

import sys
import os
import re
import string
import unicodedata
import curses.ascii as ascii

import unittest

from copy import deepcopy
from glob import glob
from itertools import chain
from prettyprinter import cpprint as pp, pprint as pp_plain

#------------------------------------------------------------------------------

from arpeggio import ParserPython, flatten, Terminal, Sequence, NoMatch
from arpeggio import EOF, StrMatch, RegExMatch, OrderedChoice, OneOrMore

#------------------------------------------------------------------------------

from grammar.python import common

from p import pp_str

from util import write_scratch, remove_punctuation, tprint, print_parsed

#------------------------------------------------------------------------------

FAKE_SPACE = '.' # chr(1) # Control-A
# Uses FAKE_SPACE in place of space for matching scenarios to work.  If the
# chosen character becomes specified in grammar/python/common.py, simply
# chose another.  Using an available punctuation character makes the
# test data is displayed on errors.

# used in the paragraph scenario
WORDS_CHARACTER_REGEX_NO_LF = r'[\w<space><>]'.replace('<space>', FAKE_SPACE)

WORDS_CHARACTER_REGEX_WITH_LF = r'[\w\n<space><>]'.replace('<space>', FAKE_SPACE)
# '<>' used to bracket any additional characters that need to be escaped for
# a given test, such as '<linefeed>'.

INUSE_CHARACTERS="<><space>".replace('<space>', FAKE_SPACE)

#------------------------------------------------------------------------------

def empty_string_is_accepted(name_prefix, rule_f, ch):
    """Add test that empty string is accepted
    """
    def create_method (rule):
        def the_method(self):
            nonlocal rule
            parsed = ParserPython( rule, skipws=False ).parse('')
        return the_method

    rule = rule_f()
    if isinstance(rule, str) :
        rule = StrMatch(ch, rule_f.__name__)

    test_name = "empty_string_is_accepted"
    method_name = f"test_{name_prefix}_rule_{rule.rule_name}_{test_name}"
    method = create_method(rule)
    setattr ( Test_Common, method_name, method )

#------------------------------------------------------------------------------

def empty_string_raises_NoMatch(name_prefix, rule_f, ch):
    """Add test that empty string does not match
    """
    def create_method (rule):
        def the_method(self):
            nonlocal rule
            with self.assertRaises(NoMatch) :
                parsed = ParserPython( rule, skipws=False ).parse('')
        return the_method

    rule = rule_f()
    if isinstance(rule, str) :
        rule = StrMatch(ch, rule_f.__name__)

    test_name = "empty_string_raises_NoMatch"
    method_name = f"test_{name_prefix}_rule_{rule.rule_name}_{test_name}"
    method = create_method(rule)
    setattr ( Test_Common, method_name, method )

#------------------------------------------------------------------------------

def string_test(name_prefix, rule_f, s, ch_names=None, empty_ok=False):
    """Generate test methods whether <rule_f> matches <s> in these scenarios :
         - by itself, <s> is the entire input string to be parsed.
         - at start of the parsed text, followed by a phrase
         - in the middle between twp phrases
         - at the end of the parsed text, preceeded by a phrase
         - scattered a various points about a paragraph, at least once
           two <s>'s directly next to each other.
         - Test whether or not the specified rule matches an empty string :
           If empty_ok is False (DEFAULT), a NoMatch exception is expected.
           If empty_ok is True, a successful match is expected.

         Each scenario generates an individual test.  The test names
         include the characters being tested against.

         In each scenario, the 'text' is ensured to not include any
         characters present in <s>.

    """
    def create_method (name, rule_f, rule, s, grammar, input, expect):
        def the_method(self):
            nonlocal name, rule_f, rule, s, grammar, input, expect
            parser = ParserPython( grammar, skipws=False )
            write_scratch( call={'fcn' : 'string_test' , 's' : s ,
                                 'rule_f' : rule_f , 'rule' : rule , },
                           name=name, grammar=grammar, input=input,
                           expect=expect, expect_f=flatten(expect),
                           model=parser.parser_model )
            try :
                parsed = parser.parse(input)
                write_scratch ( parsed=parsed )
                write_scratch ( parsed_f=flatten(parsed) )
            except :
                print(f"\nParser FAILED : s = '{s}' :"
                      f"\ninput = '{input}'"
                      f"[grammar]\n{pp_str(grammar)}\n"
                      f"\n[expect]\n{pp_str(expect)}")
                raise
            # print("[ expect ]") ; pp(expect)
            # print("[ parsed ]") ; pp(parsed)
            parsed = flatten(parsed)
            expect = flatten(expect)
            assert parsed == expect, \
                ( f"s = '{s}' : input = '{input}' :\n"
                  f"[grammar]\n{pp_str(grammar)}\n"
                  f"[expect]\n{pp_str(expect)}\n"
                  f"[parsed]\n{pp_str(parsed)}" )

        return the_method

    #--------------------------------------------------------------------------

    assert len(s) > 0, "Zero length 's' invalid for string_test()"

    for ch in s :
        assert ch not in INUSE_CHARACTERS, \
            ( f"argument s '{s}', contains '{ch}' character whuch is a "
              f"member of INUSE_CHARACTERS, test code must be reconfigured "
              f"in order to handle this character." )

    if empty_ok:
        empty_string_is_accepted(name_prefix, rule_f, ch)
    else:
        empty_string_raises_NoMatch(name_prefix, rule_f, ch)

    rule = rule_f()
    if isinstance(rule, str) :
        # print(f"- rule '{rule_f.__name__}' : create StrMatch() rule for "
        #       f"literal '{ch}' : {ord(ch)} : {hex(ord(ch))}")
        rule = StrMatch(ch, rule_f.__name__)

    ( ch_hexes, ch_names ) = character_lookup ( s, ch_names )

    if len(ch_hexes) == 1 :
        ch_hexes = ch_hexes[0]
        ch_names = ch_names[0]

    for test_name, grammar, input, expect in scenarios(rule, ch):
        method_name = f"test_{name_prefix}_rule_{rule.rule_name}__AGAINST_{ch_hexes}_{ch_names}_{test_name}"
        # print(f"Adding {method_name}")
        method = create_method(method_name, rule_f, rule, ch, grammar, input, expect)
        setattr ( Test_Common, method_name, method )

#--------------------------------------------------------------------------

def character_lookup ( s, ch_names=None ) :

    if ch_names is None or len(ch_names) <= 0 :
        ch_names = [ None for ch in s ]
    else :
        assert len(ch_names) >= len(s), \
            f"Not enough 'ch_names' for each member of 's'"
        assert len(ch_names) <= len(s), \
            f"Too many 'ch_names'.  More than the number of members of 's'."
        for idx in range(len(ch_names)) :
            # assert ch_names[idx] is not None, \
            #     f"ch_names[{idx}] is None.  Please provide a name."
            # assert len(ch_names[idx]) > 0,
            #     f"ch_names[{idx}] is an empty string.  Please provide a name"
            if ch_names[idx] is not None and len(ch_names[idx]) <= 0 :
                ch_names[idx] = None

    ch_hexes = [ ]

    for idx in range(len(s)) :
        ch = s[idx]
        ch_hexes.append ( f"x{ord(ch):02x}" )
        if ch_names[idx] is None :
            if ord(ch) < len(ascii.controlnames):
                ch_names[idx] = ascii.controlnames[ord(ch)]
            else :
                try :
                    ch_names[idx] = unicodedata.lookup(ch)
                except :
                    ch_names[idx] = ch_hexes[idx]

    return ( ch_hexes, ch_names )

#--------------------------------------------------------------------------

def scenarios(rule, s): # -> grammar, input, expect

    assert FAKE_SPACE not in s, "INTERNAL ERROR, chosen 'fake space' in string to be tested !"

    rule = deepcopy(rule)

    catchall = RegExMatch( r'.*', rule_name='catch_all' )
    newline = RegExMatch( r'[\n]', rule_name='newline' )

    # t_newline = Terminal(newline, 0, '\n')
    t_eof = Terminal(EOF(), 0, '')
    t_s = Terminal(rule, 0, s)

    def grammar ( _words ) :
        body = OneOrMore( OrderedChoice ( [ rule, _words, catchall, newline ] ) )
        return Sequence( ( body, EOF ) )

    def itself():
        name = f"by_itself"
        return name, Sequence( (rule, EOF) ), s, ( t_s, t_eof )

    def at_start():
        name = 'at_start_followed_by_phrase'
        phrase = fake_spaces_etc(s, 'now is the time')
        assert s not in phrase
        _words = get_words(s)
        text = ''.join([ s, phrase ])
        expect = ( ( t_s, Terminal(_words(), 0, phrase) ), t_eof )
        return name, grammar(_words), text, expect

    def at_start_twice():
        name = 'at_start_followed_by_phrase_twice'
        # 's' at start followed by a phrase, TWICE
        phrase = fake_spaces_etc(s, 'now is the time')
        assert s not in phrase
        _words = get_words(s)
        text = ''.join([ *( (s, phrase) * 2 ) ])
        t_phrase = Terminal(_words(), 0, phrase)
        expect = ( *( (t_s, t_phrase) * 2 ), t_eof )
        return name, grammar(_words), text, expect

    def at_start_two_lines():
        name = 'at_start_followed_by_phrase_two_lines'
        phrase = fake_spaces_etc(s, 'now is the time' + '\n')
        assert s not in phrase
        _words = get_words(s)
        text = ''.join([ *( (s, phrase) * 2 ) ])
        t_phrase = Terminal(_words(), 0, phrase)
        expect = ( *( (t_s, t_phrase) * 2 ), t_eof )
        return name, grammar(_words), text, expect

    def in_the_middle():
        name = 'in_the_middle_between_two_phrases'
        left_phrase = fake_spaces_etc(s, 'for all good men')
        right_phrase = fake_spaces_etc(s, 'to rise up')
        assert s not in left_phrase
        assert s not in right_phrase
        _words = get_words(s)
        t_left = Terminal(_words(), 0, left_phrase)
        t_right = Terminal(_words(), 0, right_phrase)
        expect = ( t_left, t_s, t_right, t_eof )
        text = ''.join([left_phrase, s, right_phrase])
        return name, grammar(_words), text, expect

    def at_end():
        name = 'at_end_preceeded_by_a_phrase'
        phrase = fake_spaces_etc(s, 'in defense of freedom')
        assert s not in phrase
        _words = get_words(s)
        t_phrase = Terminal(_words(), 0, phrase)
        text = ''.join([s, phrase ])
        expect = ( t_s, t_phrase, t_eof )
        return name, grammar(_words), text, expect

    #--------------------------------------------------------------------------

    def paragraph():
        name = 'several_occurances_in_a_paragraph'
        text = """<s>
<s>The essence of America — that which really unites us —
<s>is not ethnicity, <s>or<s>nationality, or religion.
It is an <s> idea—and what an <s> idea it is :
that you can come <s><s> from humble circumstances
and do great things.<s>
  - Condoleezza Rice
<s>"""
        # zero length phrases at start, end and one more in the middle
        n_empty = 3

        text = text.replace('<s>', chr(7))
        text = fake_spaces_etc(s, text)
        text = text.replace(chr(7), '<s>')
        assert s not in text

        _words = get_words(s)

        phrases = re.split('<s>', text)
        assert len(phrases[0]) == 0
        assert len(phrases[-1]) == 0

        t_s = Terminal(rule, 0, s)
        tw = lambda p : Terminal(_words(), 0, p)
        terms = [ ( ( tw(p) if len(p) > 0 else ()), t_s ) for p in phrases ]
        terms = flatten(terms)
        terms[-1] = t_eof # reuse instead of remove, was "del terms[-1]"
        assert len(terms) == 2 * len(phrases) - n_empty

        # Handle the simplest Zero/One Or Many rules on a character class
        #
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

        return name, grammar(_words), s.join(phrases), tuple(terms)

    #--------------------------------------------------------------------------

    tests = [ at_start ,
              at_start_twice ,
              at_start_two_lines ,
              in_the_middle ,
              at_end ,
              paragraph,
            ]

    for test in tests :
        yield test()

#------------------------------------------------------------------------------

def get_words(s):
    """When 's' contains a linefeed, 'words' rule must not not include
       linefeed as a word character.
    """
    if '\n' in s :
        def words():
            return RegExMatch(WORDS_CHARACTER_REGEX_NO_LF+'+',
                                  rule_name='words')
    else :
        def words():
            return RegExMatch(WORDS_CHARACTER_REGEX_WITH_LF+'+',
                                  rule_name='words')
    return words

#------------------------------------------------------------------------------

def fake_spaces_etc(s, text):
    """Revised the provided text such that it does not include any
       character present in ch.
       - The FAKE_SPACE character is used to space or tab.
       - Removes carriage returns.
       - Punctuation characters are removed with FAKE_SPACE protected
         should it be a punctuation character.
       - members of s are converted hex
    """
    # use FAKE_SPACE instead space and tab
    text = text.replace(' ', FAKE_SPACE)
    text = text.replace('\t', FAKE_SPACE)
    text = text.replace('\r', '')

    # Remove all punctuation but preserve FAKE_SPACE
    non_punctuation_character = chr(3)
    text = text.replace(FAKE_SPACE, non_punctuation_character)
    text = remove_punctuation(text)
    text = text.replace(non_punctuation_character, FAKE_SPACE)
    assert '-' not in s # ASCII dash
    assert '—' not in s # Unicode long dash ?

    # Convert to hex any members of s found in text
    for ch in s :
        if ch in text :
            text = text.replace(ch, f"<x{ord(ch):02x}>")

    return text

#------------------------------------------------------------------------------

class Test_Common ( unittest.TestCase ) :

    def setUp(self):
        write_scratch( _clean=True )

    def test_3_explicit_blank_line(self):

        newline = common.newline
        blank_line = common.blank_line
        words = get_words('\n')

        t_newline = Terminal(newline(), 0, '\n')

        text = ""
        expect = []

        s_blank_line_empty = '\n'
        t_blank_line_empty = Terminal(blank_line(), 0, s_blank_line_empty)

        #--------------------------------------------------------------------------

        text += '\n' + s_blank_line_empty
        expect.extend ( ( t_newline, t_blank_line_empty ) )

        self.check_parse ( 'test_blank_line : 1', blank_line, blank_line(),
                           words, text, expect )

        #--------------------------------------------------------------------------

        phrase = fake_spaces_etc(' ', 'Testing 1, 2, 3')
        t_phrase = Terminal(words(), 0, phrase)

        # t_blank_line_empty = Terminal(blank_line(), 0, s_blank_line_empty)

        text += phrase + '\n' + s_blank_line_empty
        expect.extend ( ( t_phrase, t_newline, t_blank_line_empty ) )

        self.check_parse ( 'test_blank_line : 2', blank_line, blank_line(),
                           words, text, expect )

    #--------------------------------------------------------------------------

    def check_parse ( self, fcn, rule_f, rule, words, text, expect ) :

        t_eof = Terminal(EOF(), 0, '')
        expect = ( ( *expect ), t_eof )

        newline = common.newline()
        catchall = RegExMatch( r'.*', rule_name='catch_all' )
        body = OneOrMore( OrderedChoice ( [ rule, words, catchall, newline ] ) )
        grammar = Sequence( ( body, EOF ) )

        parser = ParserPython(grammar, skipws=False)

        write_scratch( call={'fcn' : '{fcn}' , 'text' : text ,
                             'rule_f' : rule_f , 'rule' : rule , },
                       name=fcn, grammar=grammar, text=text,
                       expect=expect, expect_f=flatten(expect),
                       model=parser.parser_model )
        try :
            parsed = parser.parse(text)
            write_scratch ( parsed=parsed )
            write_scratch ( parsed_f=flatten(parsed) )
        except :
            print(f"\nParser FAILED :"
                  f"\ntext = '{text}'"
                  f"[grammar]\n{pp_str(grammar)}\n"
                  f"\n[expect]\n{pp_str(expect)}")
            raise
        # print("[ expect ]") ; pp(expect)
        # print("[ parsed ]") ; pp(parsed)
        parsed = flatten(parsed)
        expect = flatten(expect)
        assert parsed == expect, \
            ( f"text = '{text}' :\n"
              f"[grammar]\n{pp_str(grammar)}\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )


#------------------------------------------------------------------------------

def or_more_from_charset(rule_f, charset, suffix, levels, empty_ok=False):
    for ch in charset :
        s = ch + suffix
        string_test('2_class', rule_f, s, empty_ok=empty_ok)
        if levels > 1 :
            or_more_from_charset(rule_f, charset, s, levels-1, empty_ok)

#------------------------------------------------------------------------------

if tst_individual_characters :

    for name, ch in common.CHARACTER_NAME_TO_CHAR.items() :
        ( ch_hexes, ch_names ) = character_lookup ( ch )
        rule_f = lambda : StrMatch(ch, rule_name=f"common_character_{ch_hexes[0]}_{ch_names[0]}")
        string_test("1_individual", rule_f, ch )
        if tst_debug_first_char :
            break

if tst_whitespace_chars :

    for ch in common.WHITESPACE_CHARS :
        ( ch_hexes, ch_names ) = character_lookup ( ch )
        rule_f = lambda : StrMatch(ch, rule_name=f"whitespace_character_{ch_hexes[0]}_{ch_names[0]}")
        string_test("1_individual", rule_f, ch, ch_names )
        if tst_debug_first_char :
            break

#------------------------------------------------------------------------------

if tst_class_whitespace_rule_per_characters :

    for idx in range(len(common.WHITESPACE_RULES)):
        # individual whitespace character rules, literal character, not regex
        rule_f = common.WHITESPACE_RULES[idx]
        ch = common.WHITESPACE_CHARS[idx]
        string_test("2_class", rule_f, ch)

if tst_class_rule_whitespace :
    # whitespace regular expression : One of space, tab, carriage-return
    rule_f = common.whitespace
    for ch in common.WHITESPACE_CHARS :
        string_test("2_class", rule_f, ch)

#------------------------------------------------------------------------------

if tst_class_or_more :
    pass

    # ws regex : One or more of space, tab, carriage-return
    or_more_from_charset(common.ws, common.WHITESPACE_CHARS, '', 2)

    # wx regex : Zero or more of space, tab, carriage-return
    or_more_from_charset(common.wx, common.WHITESPACE_CHARS, '', 2, empty_ok=True)

    # newline regex : newline, possibly preceeded by whitespace
    or_more_from_charset(common.newline, common.WHITESPACE_CHARS, '\n', 2)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
