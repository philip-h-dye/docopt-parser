import sys

from contextlib import redirect_stdout

import unittest

from itertools import chain

from prettyprinter import cpprint as pp

from docopt_parser.parsetreenodes import NonTerminal_eq_structural

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

def text():
    return RegExMatch(r'[\S ]+', rule_name='text')

def line():
    return Sequence ( text, newline,
                    rule_name='line', skipws=False )
def paragraph():
    return OneOrMore ( line, rule_name='paragraph', skipws=False )

def element():
    # Without an enclosing list [] for 'words, newline', OrderedChoice
    #   implicitly becomes Sequence !
    return OrderedChoice ( [ paragraph, newline ], rule_name='element' )

def body():
    return OneOrMore ( element, rule_name='body' )

def document():
    return Sequence( body, EOF, rule_name='document' )

#------------------------------------------------------------------------------

texts = [
"""
I am no bird; and no net ensnares me :
I am a free human being with an independent will.
  - Charlotte Bronte
""",
"""
Freedom is not worth having if it does not include the freedom to make mistakes.
  - Mahatma Gandi
""",
"""
From every mountainside, let freedom ring.
  - Martin Luther King, Jr.
""",
"""
The only real prison is fear, and
the only real freedom is freedom from fear.
  - Aung San Suu Kyi
""",
"""
May we think of freedom not as the right to do as we please,
but as the opportunity to do what is right.
  - Peter Marshall
""",
"""
Dreams are the foundation of America.
  - Lupita Nyong'o
""",
"""
In the truest sense, freedom cannot be bestowed; it must be achieved.
  - Franklin D. Roosevelt
""",
"""
We must be free not because we claim freedom, but because we practice it.
  - William Faulkner
""",
"""
Freedom lies in being bold.” - Robert Frost
""",
"""
This, then, is the state of the union:
free and restless, growing and full of hope.
So it was in the beginning.
So it shall always be,
while God is willing,
and we are strong enough to keep the faith.
  - Lyndon B. Johnson
""",
"""
I am an American; free born and free bred,
where I acknowledge no man as my superior,
except for his own worth, or as my inferior,
except for his own demerit.
  - Theodore Roosevelt
""",
"""
For to be free is not merely to cast off one’s chains,
but to live in a way that respects and enhances the freedom of others.
  - Nelson Mandela
""",
"""
The essence of America — that which really unites us —
is not ethnicity, or nationality, or religion.
It is an idea—and what an idea it is :
that you can come from humble circumstances
and do great things.
  - Condoleezza Rice
""",
]


#------------------------------------------------------------------------------

class Test_Import ( unittest.TestCase ) :

    def builder ( self, inputs ):

        p_newline = Terminal(newline(), 0, '\n')

        input = ""

        body_ = [ ]
        for atom in inputs :
            if atom == '\n':
                input += atom
                # print(f": atom = <newline>")
                body_.append ( NonTerminal(element(), [ p_newline ] ) )
            else:
                # Fiddling necessary since 'line' does not support fragments
                # and paragraph does not support leading newlines
                atom = atom.strip()
                input += atom + '\n'
                # print(f": atom = '{atom}'")
                paragraph_ =[]
                for text_ in atom.split('\n'):
                    p_line = NonTerminal(line(), [ Terminal( text(), 0, text_ ), p_newline ])
                    paragraph_.append ( p_line )
                p_paragraph = NonTerminal(paragraph(), paragraph_)
                body_.append ( NonTerminal(element(), [ p_paragraph ]) )

        p_body		= NonTerminal(body(), body_)
        p_eof		= Terminal(EOF(), 0, '')
        expect		= NonTerminal(document(), [p_body, p_eof] )

        return ( input, expect )


    #--------------------------------------------------------------------------

    def apply (self, inputs ) :

        ( input, expect ) = self.builder (
            inputs,
        )

        # print('\n: input = '{input}'")
        # print('\n: expect') ; pp(expect)

        # with open("expect.raw", 'w') as f, redirect_stdout(f) :
        #     pp(expect)

        parser = ParserPython( document, skipws=False )
        parsed = parser.parse(input)

        # print('\n: parsed') ; pp(parsed)
        # with open("parsed.raw", 'w') as f, redirect_stdout(f) :
        #     pp(parsed)

        # assert parsed == expect, \

        assert NonTerminal_eq_structural(parsed, expect), \
            ( f"input = '{input}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_builder_001_fragment (self) :
        self.apply ( ( 'one', '\n',
                   ) )

    def test_builder_001_full (self) :
        self.apply ( ( 'one\n', '\n',
                   ) )

    def test_builder_002_fragment (self) :
        self.apply ( ( 'one\ntwo', '\n',
                   ) )

    def test_builder_002_full (self) :
        self.apply ( ( 'one\ntwo\n', '\n',
                   ) )

    def _test_builder_003 (self) :
        self.apply ( ( 'one', '\n',
                       'two', '\n',
                       'three', '\n',
                   ) )

    def _test_builder_005 (self) :
        self.apply ( ( texts[0], '\n', '\n',
                       # texts[3], '\n', '\n',
                       # texts[7], '\n', '\n',
                   ) )

    def _test_builder_007 (self) :
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
