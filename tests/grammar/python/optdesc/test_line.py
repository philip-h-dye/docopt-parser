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

from prettyprinter import cpprint as pp, pprint as pp_plain
from docopt_parser.parsetreenodes import NonTerminal_eq_structural
from docopt_parser.parsetreenodes import nodes_equal
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, newline, COMMA, BAR
from grammar.python.operand import operand, operand_all_caps, operand_angled
from grammar.python.option import *

from grammar.python.optdesc.list import *
from grammar.python.optdesc.line import *

from docopt_parser import DocOptListViewVisitor

from .optline import tprint, ogenerate, document, body, element, create_expect

from util import write_scratch

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
        self.grammar = document
        self.parser = ParserPython( language_def=self.grammar, skipws=False,
                                    debug = parse_debug, )
        
        # NEVER # reduce_tree=True -- needed meaning is lost

    #--------------------------------------------------------------------------

    def single ( self, rule, text, expect ):
        # both rule and text get a single space prefix to assist when
        # the rule has a whitespace lookahead
        #
        # The model unfortunately will show 'rule' as a function
        # rather that it's expression.  It is tempting to then instantiate
        # it as rule().  The parse model now show it nicely.
        #
        # Unfortunately, the resulting parse tree drops the node for rule.
        #
        def grammar():
            return Sequence( ( wx, rule, EOF ) ,
                             rule_name='grammar', skipws=True )
        self.verify_grammar ( grammar, ' '+text, expect )

    #--------------------------------------------------------------------------

    def multiple_spaced ( self, rule, text, expect ):
        # both rule and text get a single space prefix to assist when
        # the rule has a whitespace lookahead
        def grammar():
            return Sequence( ( OrderedChoice ( [ rule(), ws, newline ] ), EOF ),
                             rule_name='grammar', skipws=True )
        self.verify_grammar ( grammar, ' '+text, expect )

    #--------------------------------------------------------------------------

    def verify_grammar ( self, grammar, text, expect ):
        self.grammar = grammar()
        expect = NonTerminal( self.grammar, [ expect, t_eof ] )
        self.parser = ParserPython ( grammar, skipws=False, reduce_tree=False )
        self.parse_and_verify( text, expect )

    #--------------------------------------------------------------------------

    def parse_and_verify ( self, text, expect ) :
        self.verify ( text, expect, self.parse ( text, expect ) )

    #--------------------------------------------------------------------------

    def parse ( self, text, expect ) :

        # tprint(f"\nOptions :\n{text}")

        write_scratch( call={'fcn' : 'parse' },
                       grammar=self.grammar, text=text,
                       expect=expect, expect_f=flatten(expect),
                       model=self.parser.parser_model, _clean=True, )
        try :
            # print(f"\n: text = '{text}'")
            parsed = self.parser.parse(text)
            write_scratch( parsed=parsed )
        except Exception as e :
            print("\n"
                  f"[expect]\n{pp_str(expect)}\n\n"
                  f"text = '{text}' :\n\n"
                  f"Parse FAILED :\n"
                  f"{str(e)}" )
            raise

        # tprint("[parsed]") ; pp(parsed)

        with open ("scratch/parsed.txt", 'w') as f :
            pp_plain(expect, stream=f)

        return parsed

    #--------------------------------------------------------------------------

    def verify ( self, text, expect, parsed ) :

        with open ("scratch/expect.txt", 'w') as f :
                pp_plain(expect, stream=f)
        with open ("scratch/parsed.txt", 'w') as f :
            pp_plain(parsed, stream=f)

        if False :
            nth_option_line = 0
            expect = expect[0][0] # [0][ nth_option_line ] # [0] [0]
            parsed = parsed[0][0] # [0][ nth_option_line ] # [0] [0]

            with open ("scratch/expect.txt", 'w') as f :
                    pp_plain(expect, stream=f)
            with open ("scratch/parsed.txt", 'w') as f :
                pp_plain(parsed, stream=f)

            print('')
            print(f"[expect] rule '{expect.rule_name}' with {len(expect)} children")
            print(f"[parsed] rule '{parsed.rule_name}' with {len(parsed)} children")

            for i in range(len(expect)) :
                if not nodes_equal( parsed[i], expect[i]) :
                    print ( f"text = '{text}' :\n"
                            f"[expect]\n{pp_str(expect[i])}\n"
                            f"[parsed]\n{pp_str(parsed[i])}" )
                    assert 1 == 0

            if len(expect) < len(parsed) :
                start = len(expect) # - 1
                print ( f"text = '{text}' :\n"
                        f"[expect]\n{pp_str(expect[start:])}\n"
                        f"[parsed]\n{pp_str(parsed[start:])}" )
                assert 1 == 0

        # print("[expect]");  pp(expect) ; print("[parsed]"); pp(parsed)

        if False :
            # Less flashly output sometime useful when debugging
            if not nodes_equal(parsed, expect) :
                print("\n!!!")
                print("!!! no match")
                print("!!!")
            return

        assert nodes_equal(parsed, expect), \
            ( f"text = '{text}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def test_single_short_no_arg (self):
        input = '-f'
        expect = create_expect (
            NonTerminal( option(), [ Terminal( short_no_arg(), 0, '-f' ) ] ) ,
            eof = ( input[-1] != '\n' ) ,
        )
        self.parse_and_verify( input, expect )

    #--------------------------------------------------------------------------

    def test_single_short_w_arg (self):
        input = '-fNORM'
        expect = create_expect (
            NonTerminal( option(), [ 
                NonTerminal( short_adj_arg(), [
                    Terminal( short_adj_arg__option(), 0, '-f' ) ,
                    NonTerminal( operand(), [
                        Terminal( operand_all_caps(), 0, 'NORM' ) ,
                    ]) ,
                ]) ,
            ]) ,
            eof = ( input[-1] != '\n' ) ,
        )
        self.parse_and_verify( input, expect )

    #--------------------------------------------------------------------------

    def test_single (self):
        input = '-f'
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
        self.parse_and_verify( input, expect )

    #--------------------------------------------------------------------------

    def test_pair (self):
        input = '-f -x'
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
                                    NonTerminal( ol_space(), [
                                        Terminal( StrMatch(' '), 0, ' '),
                                    ]) ,
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
        self.parse_and_verify( input, expect )

    #--------------------------------------------------------------------------

    def test_trio (self):

        input = '-f -x -l'

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
                                    NonTerminal( ol_space(), [
                                        Terminal( StrMatch(' '), 0, ' '),
                                    ]) ,
                                ]) ,
                                NonTerminal( ol_term(), [
                                    NonTerminal( option(), [
                                        Terminal( short_no_arg(), 0, '-x' )
                                    ]) ,
                                ]) ,
                            ]) ,
                            NonTerminal( ol_term_with_separator(), [
                                NonTerminal( ol_separator(), [
                                    NonTerminal( ol_space(), [
                                        Terminal( StrMatch(' '), 0, ' '),
                                    ]) ,
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

        self.parse_and_verify( input, expect )

    #--------------------------------------------------------------------------

    def test_create_expect(self):

        input = '-f -x -l'

        expect = create_expect (
            NonTerminal( option(), [ Terminal( short_no_arg(), 0, '-f' ) ] ) ,
            NonTerminal( option(), [ Terminal( short_no_arg(), 0, '-x' ) ] ) ,
            NonTerminal( option(), [ Terminal( short_no_arg(), 0, '-l' ) ] ) ,
            eof = ( input[-1] != '\n' ) ,
        )

        # print("[ expect ]")
        # pp(expect[0][0][0][0][1])

        parsed = self.parse(input, expect)
        # tprint("[parsed]") ; pp(parsed)

        # print("[ parsed ]")
        # pp(parsed[0][0][0][0][1])

        self.verify( input, expect, parsed )

    #--------------------------------------------------------------------------

    def tearDown (self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

#------------------------------------------------------------------------------

def generate_line ( cls, optdefs, help_, indent='  ', sep=', ', offset=16 ):

    # tprint(f"generate_line :  optdefs = {optdefs}, help_ = '{help_}, sep='{sep}' )")

    ( method_name, optlist_string ) = ogenerate ( cls, optdefs, sep=sep, )

    if indent is None:
        indent = ''
    if help_ is None:
        help_ = ''

    # print(f": {'indent':<16} : '{indent}'")
    # print(f": {'os string':<16} : '{optlist_string}'")
    # print(f": {'help_':<16} : '{help_}'")
    # sys.stdout.flush()

    return f"{indent}{optlist_string:<{offset}}  {help_}\n"

#------------------------------------------------------------------------------

if False :
    #lgen
    olines = [
        ( ( ( '-h', ), ( '--help', ) ), "Show this usage information." ),
        ( ( ( '-v', ), ( '--version', ) ), "Print the version and exit." ),
    ]

    text = ''
    for ol_spec in olines :
        text += generate_line ( Test_Option_Line, *ol_spec )

    print(f"Options:\n{text}")

#------------------------------------------------------------------------------

def _generate ( optdefs, *args, **kwargs ):
    return ogenerate ( Test_Option_Line, optdefs, *args, **kwargs )

#------------------------------------------------------------------------------

# boundry condition, the first option is handled separately from succeeding terms
# and it is an ol_first_option, not an ol_term
# generate( '-f' )
_generate ( ( ( '-f', ), ) )

#------------------------------------------------------------------------------

if False :
    pass

if True :
    pass

    # boundry condition, '-x' is first ol_term of the option_list's ZeroToMany and
    # the first possible position for a option-argument
    # generate( '-f -x' )
    _generate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                ) )

    # one past boundry condition, first term on on a boundry
    # generate('-f -x -l')
    _generate ( ( ( '-f', ) ,
                  ( '-x', ) ,
                  ( '-l', ) ,
                ) )

    # generate("--file")
    # generate("--file --example")
    # generate("--file --example --list")

    _generate ( ( ( '--file', ) ,
                ) )
    _generate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                ) )
    _generate ( ( ( '--file', ) ,
                  ( '--example', ) ,
                  ( '--list', ) ,
                ) )

    # generate("--file=<FILE> -x")
    # generate("--file=<file> --example=<example>")
    # generate("--file=<file> --example=<example> --list=<list>")

    _generate ( ( ( '--file', '=', '<file>', ) ,
                ) )

    _generate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                ) )

    _generate ( ( ( '--file', '=', '<file>', ) ,
                  ( '--example', '=', '<example>', ) ,
                  ( '--list', '=', '<list>', ) ,
                ) )

    # generate("--file=<FILE> -x --example=<EXAMPLE> -y --query=<QUERY> -q")
    _generate ( ( ( '--file', '=', '<FILE>', ) ,
                  ( '-x', ) ,
                  ( '--example', '=', '<EXAMPLE>', ) ,
                  ( '-y', ) ,
                  ( '--query', '=', '<QUERY>', ) ,
                  ( '-q', ) ,
                ) )

    # generate("--file=FILE -x")
    _generate ( ( ( '--file', '=', 'FILE', ) ,
                  ( '-x', ) ,
                ) )

    # generate("--file=FOObar -x")    
    if False  :
        # FIXME: not implemened yet -- 'command/example' option-argument
        _generate ( ( ( '--file', '=', 'FOObar', ) ,
                      ( '-x', ) ,
                    ) )

    # generate("--file=a|b|c -x")
    if False  :
        # FIXME: not implemened yet -- 'command/example' option-argument
        _generate ( ( ( '--file', '=', 'a|b|c', ) ,
                      ( '-x', ) ,
                    ) )

    #------------------------------------------------------------------------------

    _generate ( ( ( '--file', '=', 'NORM' ) ,
                  ( '--file', ' ', 'NORM' ) ,
                  ( '--file', ) ,
                ) )

    _generate ( ( ( '-f', '', 'NORM' ) ,
                  ( '-f', ' ', 'NORM' ) ,
                  ( '-f', ) ,
                ) )

#------------------------------------------------------------------------------

# Option Line Variations
# ----------------------
#   indent     :  0 .. 4
#   offset     :  0 .. 30
#   help gap   :  2 .. 4
#       text   :  None / '' / 'a' / 'ab' / 'Help ...'
#   opt-list   :  handled in test_list, no concern here

# Option Line Errors
# ------------------
#   indent     :  negative
#   offset     :  negative
#   help gap   :  less than 2
#        text  :  ...
#   opt-list   :  handled in test_list, no concern here

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
