from arpeggio import RegExMatch as _ , ZeroOrMore, Sequence

from .common import wx

from grammar.python.common import newline, whitespace, ws, wx

def string_no_whitespace():
    return _(r'[^\s\n.]+', rule_name="string_no_whitespace", skipws=False )

def word():
    return _(string_no_whitespace().to_match, rule_name="word", skipws=False )

def words():
    return Sequence( ( wx, word, ZeroOrMore ( Sequence ( ws, word ) ) ),
                     rule_name="words", skipws=False )

def line():
    return Sequence( ( words, newline ),
                     rule_name="line", skipws=False )

def paragraph():
    return OneOrMore( line, rule_name="paragraph", skipws=False )
