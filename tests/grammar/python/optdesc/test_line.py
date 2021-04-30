parse_debug = False

import sys
import os
import re

from contextlib import redirect_stdout

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, OrderedChoice, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _

#------------------------------------------------------------------------------

from prettyprinter import cpprint as pp
from docopt_parser.parsetreenodes import NonTerminal_eq_structural
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, newline, COMMA, BAR
from grammar.python.operand import operand, operand_all_caps, operand_angled
from grammar.python.option import *
# # option, ...

# option_list, ol_first_option, ol_term
from grammar.python.optdesc.list import *
from grammar.python.optdesc.line import *

from docopt_parser import DocOptListViewVisitor

#------------------------------------------------------------------------------

grammar_elements = [ option_line, ws, newline ]

def element():
    # To work properly, first argumnet of OrderedChoice must be a
    # list.  IF not, it implicitly becomes Sequence !
    return OrderedChoice ( [ *grammar_elements ], rule_name='element' )

def body():
    return OneOrMore ( element, rule_name='body' )

def document():
    return Sequence( body, EOF, rule_name='document' )

#------------------------------------------------------------------------------

def create_expect ( *terminals, eof=False, separator =
                    Terminal( StrMatch(' ', rule='SPACE'), 0, ' ') ) :

    if len(terminals) <= 0 :
        raise ValueError("No terminals provided.  Please provide at least one.")

    expect = NonTerminal( document(), [
        NonTerminal( body(), [
            NonTerminal( element(), [
                NonTerminal( option_line(), [
                    NonTerminal( option_list(), [
                        NonTerminal( ol_first_option(), [
                            NonTerminal( option(), [
                                terminals[0],
                            ]) ,
                        ]) ,
                        * [
                            NonTerminal( ol_term_with_separator(), [
                                NonTerminal( ol_separator(), [
                                    separator,
                                ]) ,
                                NonTerminal( ol_term(), [
                                    NonTerminal( option(), [
                                        term
                                    ]) ,
                                ]) ,
                            ])
                            for term in terminals[1:]
                        ],
                    ]) ,
                    # Terminal(EOF(), 0, '') , # only if specified via 'eof'
                ]) ,
            ]) ,
        ]) ,
        Terminal(EOF(), 0, '') ,
    ])

    if eof :
        expect[0][0][0].append(expect[-1])

    return expect

#------------------------------------------------------------------------------

first=ol_first_option
s=short_no_arg
l=long_no_arg
a=operand_angled
c=operand_all_caps
# ol=ol_operand_lead

def _t(r, opt):
    return Terminal(r(), 0, opt)

#------------------------------------------------------------------------------

def re_compile(f):
    r = f()
    r.compile()
    return r.regex

re_short  = re_compile(short_no_arg)
re_long   = re_compile(long_no_arg)

def verify_option_type_match(rule, value): # rule in s or r , value : option string

    if rule is _short :
        if re_short.fullmatch(value):
            return
        if len(value) < 2:
            raise ValueError("Short option '{value}' is too short.  Please address.")
        if len(value) > 2:
            raise ValueError("Short option '{value}' is too large.  Please address.")
        raise ValueError("Short option '{value}' is invalid.  Probably invalid characters.")

    if rule is _long :
        if re_long.fullmatch(value):
            return
        if len(value) < 4:
            raise ValueError("Long option '{value}' is too short, it must be "
                             "at least two dashes and two letters.  "
                             "Please address.")
        raise ValueError("Long option '{value}' is invalid.  Probably invalid characters.")

    raise ValueError("verify_option_type_match() should be called only with "
                     "either _long or _short.  Please address.")

#------------------------------------------------------------------------------

class Test_Option_Line ( unittest.TestCase ) :

    def setUp(self):

        global grammar_elements
        global parse_debug

        # quiet, no parse trees displayed
        # self.debug = False

        # show parse tree for pass >= self.debug
        self.debug = 2

        # from the module global
        self.parse_debug = parse_debug

        # self.each = True
        self.show = True

        # # tprint._file =
        # self.tty = open("/dev/tty", 'w')

        # self.rstdout = redirect_stdout(self.tty)
        # self.rstdout.__enter__()

        tprint._on = self.show or self.debug is not False

        # grammar_elements = [ option_list, ws ]
        self.parser = ParserPython( language_def=document, skipws=False,
                                    debug = parse_debug, )
        # # NEVER # reduce_tree=True -- needed meaning is lost

    #--------------------------------------------------------------------------

    def _test_single_short_no_arg (self):
        input = '-f'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)

        expect = create_expect (
            Terminal( short_no_arg(), 0, '-f' ) ,
            eof = ( input[-1] != '\n' ) ,
        )

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n"
                                   f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_single_short_w_arg (self):
        input = '-fNORM'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)

        expect = create_expect (
            NonTerminal( short_adj_arg(), [
                Terminal( short_adj_arg__option(), 0, '-f' ) ,
                NonTerminal( operand(), [
                    Terminal( operand_all_caps(), 0, 'NORM' ) ,
                ]) ,
            ]) ,            
            eof = ( input[-1] != '\n' ) ,
        )

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n"
                                   f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_single (self):
        input = '-f'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
        # tprint("[parsed]") ; pp(parsed)

        expect = NonTerminal( document(), [
            NonTerminal( body(), [
                NonTerminal( element(), [
                    NonTerminal( option_line(), [
                        NonTerminal( option_list(), [
                            NonTerminal( ol_first_option(), [
                                NonTerminal( option(), [
                                    Terminal( short_no_arg(), 0, '-f' ),
                                ]) ,
                            ]) ,
                        ]) ,
                        Terminal(EOF(), 0, '') ,
                    ]) ,
                ]) ,
            ]) ,
            Terminal(EOF(), 0, '') ,
        ])

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n"
                                   f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_pair (self):
        input = '-f -x'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
        # tprint("[parsed]") ; pp(parsed)

        expect = NonTerminal( document(), [
            NonTerminal( body(), [
                NonTerminal( element(), [
                    NonTerminal( option_line(), [
                        NonTerminal( option_list(), [
                            NonTerminal( ol_first_option(), [
                                NonTerminal( option(), [
                                    Terminal( short_no_arg(), 0, '-f' ),
                                ]) ,
                            ]) ,
                            NonTerminal( ol_term_with_separator(), [
                                NonTerminal( ol_separator(), [
                                    Terminal( StrMatch(' ', rule='SPACE'), 0, ' '),
                                ]) ,
                                NonTerminal( ol_term(), [
                                    NonTerminal( option(), [
                                        Terminal( short_no_arg(), 0, '-x' )
                                    ]) ,
                                ]) ,
                            ]) ,
                        ]) ,
                        Terminal(EOF(), 0, '') ,
                    ]) ,
                ]) ,
            ]) ,
            Terminal(EOF(), 0, '') ,
        ])

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n"
                                   f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_trio (self):
        input = '-f -x -l'
        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
        # tprint("[parsed]") ; pp(parsed)

        expect = NonTerminal( document(), [
            NonTerminal( body(), [
                NonTerminal( element(), [
                    NonTerminal( option_line(), [
                        NonTerminal( option_list(), [
                            NonTerminal( ol_first_option(), [
                                NonTerminal( option(), [
                                    Terminal( short_no_arg(), 0, '-f' ),
                                ]) ,
                            ]) ,
                            NonTerminal( ol_term_with_separator(), [
                                NonTerminal( ol_separator(), [
                                    Terminal( StrMatch(' ', rule='SPACE'), 0, ' '),
                                ]) ,
                                NonTerminal( ol_term(), [
                                    NonTerminal( option(), [
                                        Terminal( short_no_arg(), 0, '-x' )
                                    ]) ,
                                ]) ,
                            ]) ,
                            NonTerminal( ol_term_with_separator(), [
                                NonTerminal( ol_separator(), [
                                    Terminal( StrMatch(' ', rule='SPACE'), 0, ' '),
                                ]) ,
                                NonTerminal( ol_term(), [
                                    NonTerminal( option(), [
                                        Terminal( short_no_arg(), 0, '-l' )
                                    ]) ,
                                ]) ,
                            ]) ,
                        ]) ,
                        Terminal(EOF(), 0, '') ,
                    ]) ,
                ]) ,
            ]) ,
            Terminal(EOF(), 0, '') ,
        ])

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n"
                                   f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_create_expect(self):

        input = '-f -x -l'

        parsed = self.parser.parse(input)
        # tprint("[parsed]") ; pp(parsed)

        expect = create_expect (
            Terminal( short_no_arg(), 0, '-f' ) ,
            Terminal( short_no_arg(), 0, '-x' ) ,
            Terminal( short_no_arg(), 0, '-l' ) ,
            eof = ( input[-1] != '\n' ) ,
        )

        assert parsed == expect, ( f"input = '{input}' :\n"
                                   f"[expect]\n{pp_str(expect)}\n"
                                   f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def tearDown (self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    if tprint._on :
        kwargs['file'] = tprint._file
        print('')
        print(*args, **kwargs)
        tprint._file.flush()

tprint._file = sys.stdout # open("/dev/tty", 'w')
# tprint._on = False
tprint._on = True

#------------------------------------------------------------------------------

def replace_matching ( name, matcher, prefix ):

    if matcher.search(name) :
        name1 = name
        name = ''
        pos = 0
        for m in matcher.finditer(name1):
            name += name1[pos:m.start()] + prefix + m.group(1)
            pos = m.end()
        name += name1[pos:]

    return name

#------------------------------------------------------------------------------

underscores		= re.compile(r'_+')
eq_option_angle		= re.compile(r'=<([^>]+)>')
eq_option_caps		= re.compile(r'=([A-Z][A-Z]+\b)')
			# '\b' so that not accept '=FOO' of '=FOObar'
eq_option_other		= re.compile(r'=([\S]+)')

# FIXME:  floating values for invalid input tests, any non-identifier character

def method_name ( initial_input ):

    # FIXME: Simplify flow here using separate function: method_name(<input>)

    name = initial_input
    # tprint(f"[1] name      =  '{name}'")
    name = name.replace('-','dash_').replace(' ','_space_').replace('space__','space_')
    # tprint(f"[2] name      =  '{name}'")

    # '=<ARG>' => '_eq_angle_ARG'
    name = replace_matching ( name, eq_option_angle, '_eq_angle_')
    # '=ARG' => '_eq_caps_ARG'
    name = replace_matching ( name, eq_option_caps, '_eq_caps_' )
    # '=\S+' => '_eq_other_ARG'
    name = replace_matching ( name, eq_option_other, '_eq_other_' )

    name = name.replace('|', '_BAR_')
    name = name.replace(',', '_comma_')

    name = underscores.sub(name, '_')

    # During ALPHA, trap any unexpected characters by crashing
    #   reenable for BETA and beyond
    if False : # not name.isidentifier() :
        import unicodedata
        gather = [ ]
        for ch in name :
            if ch.isidentifier() :
                gather.append ( ch )
            else :
                gather.append ( unicodedata.name(ch).replace(' ','_') )
        name = ''.join(gather)

    return 'test_' + name

#------------------------------------------------------------------------------

def generate(initial_input):

    def create_method(actual_input):
        def BASIS_test (self) :
            input = actual_input
            parsed = self.parser.parse(input)
            # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
            tprint("[parsed]") ; pp(parsed)
            # tprint(f"\ninput = '{input}'\n")
        return BASIS_test

    name = method_name(initial_input)

    for n_spaces in range(1) : # range(4):
        setattr ( Test_Option_Line, f"{name}__trailing_{n_spaces}",
                  create_method ( initial_input + ( ' ' * n_spaces ) ) )

    if False :
        def method(self):
            tprint(f": {name}")
        setattr(Test_Option_Line, 'test_000', method)

#------------------------------------------------------------------------------

# boundry condition, the first option is handled separately from succeeding terms
# and it is an ol_first_option, not an ol_term
# generate('-f')
# generate('-f\n')

# boundry condition, '-x' is first ol_term of the option_list's ZeroToMany and
# the first possible position for a option-argument
# generate('-f -x')

# one past boundry condition, first term on on a boundry
# generate('-f -x -l')

# generate("--file")
# generate("--file --example")
# generate("--file --example --list")

# generate("--file=<FILE> -x")
# generate("--file=<file> --example=<example>")
# generate("--file=<file> --example=<example> --list=<list>")

# generate("--file=<FILE> -x --example=<EXAMPLE> -y --query=<QUERY> -q")

# generate("--file=FILE -x")
# generate("--file=FOObar -x")
# generate("--file=a|b|c -x")

#------------------------------------------------------------------------------

from test_list import create_terms

def ogenerate ( optdefs, cls=Test_Option_Line ) :

    def create_method ( actual_input, the_terms ) :
        def the_test_method (self) :
            input = actual_input
            terms = the_terms
            parsed = self.parser.parse(input)
            # tprint("[parsed]") ; tprint("\n", parsed.tree_str(), "\n")
            # tprint("[parsed]") ; pp(parsed)
            # tprint(f"\ninput = '{input}'\n")
            expect ( input, parsed, *terms )
        return the_test_method

    ( initial_input, terms ) = create_terms( optdefs, sep = ' ' ) # ', '

    name = method_name(initial_input)

    setattr ( cls, name, create_method ( initial_input, terms ) )

    if False :
        setattr ( cls, f"{name}__newline",
                  create_method ( initial_input + '\n', terms ) )
        for n_spaces in range(1) : # range(4):
            setattr ( cls, f"{name}__trailing_{n_spaces}",
                      create_method ( initial_input + ( ' ' * n_spaces ) ) )

#------------------------------------------------------------------------------

def expect ( input, parsed, *terms ) :

    # tprint("[parsed]") ; pp(parsed)

    expect = create_expect ( *terms, eof = ( input[-1] != '\n' ) )

    assert parsed == expect, ( f"input = '{input}' :\n"
                               f"[expect]\n{pp_str(expect)}\n"
                               f"[parsed]\n{pp_str(parsed)}" )

#------------------------------------------------------------------------------

# boundry condition, the first option is handled separately from succeeding terms
# and it is an ol_first_option, not an ol_term
# generate( '-f' )
ogenerate ( ( ( '-f', ), ) )

#------------------------------------------------------------------------------

if True :

    # boundry condition, '-x' is first ol_term of the option_list's ZeroToMany and
    # the first possible position for a option-argument
    # generate( '-f -x' )
    ogenerate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                ) )

    # one past boundry condition, first term on on a boundry
    # generate('-f -x -l')
    ogenerate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                  ( '-l', ) ,
                ) )

    # generate("--file")
    # generate("--file --example")
    # generate("--file --example --list")

    ogenerate ( ( ( '--file', ) ,
                ) )
    ogenerate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                ) )
    ogenerate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                  ( '--list', ) ,
                ) )

    # generate("--file=<FILE> -x")
    # generate("--file=<file> --example=<example>")
    # generate("--file=<file> --example=<example> --list=<list>")

    ogenerate ( ( ( '--file', '=', '<file>', ) ,
                ) )

    ogenerate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                ) )

    ogenerate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                  ( '--list', '=', '<list>', ) ,
                ) )

    # generate("--file=<FILE> -x --example=<EXAMPLE> -y --query=<QUERY> -q")
    ogenerate ( ( ( '--file', '=', '<FILE>', ) ,
                  ( '-x', ) ,
                  ( '--example', '=', '<EXAMPLE>', ) ,
                  ( '-y', ) ,
                  ( '--query', '=', '<QUERY>', ) ,
                  ( '-q', ) ,
                ) )

    # generate("--file=FILE -x")
    ogenerate ( ( ( '--file', '=', 'FILE', ) ,
                  ( '-x', ) ,
                ) )

    # generate("--file=FOObar -x")
    if False  :
        ogenerate ( ( ( '--file', '=', 'FOObar', ) ,
                      ( '-x', ) ,
                    ) )

    # generate("--file=a|b|c -x")
    if False  :
        ogenerate ( ( ( '--file', '=', 'a|b|c', ) ,
                      ( '-x', ) ,
                    ) )

    #------------------------------------------------------------------------------

    ogenerate ( ( ( '--file', '=', 'NORM' ) ,
                  ( '--file', ' ', 'NORM' ) ,
                  ( '--file', ) ,
                ) )

    ogenerate ( ( ( '-f', '', 'NORM' ) ,
                  ( '-f', ' ', 'NORM' ) ,
                  ( '-f', ) ,
                ) )

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
