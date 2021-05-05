tst_basic                       = True    # 8 tests
tst_expression_individual       = True    # 8 tests
tst_argument_operand            = True    # 2 tests
tst_argument_command            = True    # 3 tests
tst_argument_option_permute     = True    # 6 tests
tst_expression_series_permute   = True    # 100 tests with single word and n 3

import os

import unittest

from contextlib import redirect_stdout

from prettyprinter import cpprint as pp, pprint as pp_plain

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, ZeroOrMore, OneOrMore, EOF
from arpeggio import ParseTreeNode, RegExMatch as _

from docopt_parser.parsetreenodes import nodes_equal

#------------------------------------------------------------------------------

from usage import *

define_usage_expression_shortnames(globals())

#------------------------------------------------------------------------------

class Test_Usage ( unittest.TestCase ) :

    def setUp(self):

        # quiet, no parse trees displayed
        # self.debug = False

        # show parse tree for pass >= self.debug
        self.debug = 2

        self.show = True

        tprint._on = self.show or self.debug is not False

    #--------------------------------------------------------------------------

    def HANGS_test_required_command (self):
        ( text, expect ) = usage_prepare_argument_command("move")
        ( text, expect ) = usage_prepare_required ( text, expect )
        self.single ( required, text, expect )

    def HANGS_test_optional_command (self):
        ( text, expect ) = usage_prepare_argument_command("fire")
        ( text, expect ) = usage_prepare_optional ( text, expect )
        self.single ( optional, text, expect )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_options_shortcut (self):
        ( text, expect ) = usage_prepare_options_shortcut ( '[options]' )
        self.single ( options_shortcut, text, expect )

    # Argument.value : Union[OptionDef, OperandDef, CommandDef]
    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_argument_option__long_arg_none(self):
        ( text, expect ) = usage_prepare_argument_optdef ( opt('--now', ) )
        self.single ( argument, text, expect )

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_term_command (self):
        ( text, expect ) = usage_prepare_argument_command("fire")
        ( text, expect ) = usage_prepare_term ( text, expect )
        self.single ( term, text, expect )

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_repeating (self):
        self.single ( repeating, REPEATING, t_repeating )

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_repeatable__command_with_repeating_gap_none (self):
        ( text, expect ) = usage_prepare_argument_command("fire")
        ( text, expect ) = usage_prepare_term ( text, expect )
        ( text, expect ) = usage_prepare_repeatable ( text, expect,
                                                      repeating=True, gap='' )
        self.single ( repeatable, text, expect )

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_repeatable__command_with_repeating_gap_space (self):
        ( text, expect ) = usage_prepare_argument_command("fire")
        ( text, expect ) = usage_prepare_term ( text, expect )
        ( text, expect ) = usage_prepare_repeatable ( text, expect,
                                                      repeating=True, gap=' ' )
        self.single ( repeatable, text, expect )

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_repeatable__command_without_repeating_1 (self):
        ( text, expect ) = usage_prepare_argument_command("fire")
        ( text, expect ) = usage_prepare_term ( text, expect )
        ( text, expect ) = usage_prepare_repeatable ( text, expect,
                                                      repeating=False )
        self.single ( repeatable, text, expect )

    @unittest.skipUnless(tst_basic, "Basic tests not enabled")
    def test_repeatable__command_without_repeating_2 (self):
        self.single ( repeatable, *usage_prepare_repeatable (
            *usage_prepare_term (
                *usage_prepare_argument_command("fire") ) ) )

    @unittest.skipUnless(tst_expression_individual, "Expression, individual tests not enabled")
    def test_expression__command_001_one (self):
        children = ( usage_prepare_repeatable (
            *usage_prepare_term (
                *usage_prepare_argument_command("fire") ) ) ,
        )
        self.single ( expression,
                      * usage_prepare_expression ( children ) )

    @unittest.skipUnless(tst_expression_individual, "Expression, individual tests not enabled")
    def test_expression__command_002_two (self):
        children = ( usage_prepare_repeatable (
            *usage_prepare_term (
                *usage_prepare_argument_command("fire") ) ) ,
        )
        children = ( *children, *children )
        self.single ( expression,
                      * usage_prepare_expression ( children ) )

    @unittest.skipUnless(tst_expression_individual, "Expression, individual tests not enabled")
    def test_expression__command_003_three (self):
        children = ( usage_prepare_repeatable (
            *usage_prepare_term (
                *usage_prepare_argument_command("fire") ) ) ,
        )
        children = ( *children, *children , *children )
        self.single ( expression,
                      * usage_prepare_expression ( children ) )

    @unittest.skipUnless(tst_expression_individual, "Expression, individual tests not enabled")
    def test_expression__command_004_three (self):
        self.single ( expression, * _expr ( (
            _repeatable( *_term ( *_optshortcut ( "[options]" ) ) ) ,
            _repeatable( *_term ( *_command     ( "fire" ) ) ) ,
            _repeatable( *_term ( *_optdef      (
                opt('--file', '=', '<file>' ) ) ) ) ,
            _repeatable( *_term ( *_optdef      (
                opt('--now', ) ) ) ) ,
          ) ) )

    @unittest.skipUnless(tst_expression_individual, "Expression, individual tests not enabled")
    def test_expression__command_005 (self):
        optdef = ('-f',)
        self.single ( expression, * _expr ( (
            _repeatable( *_term ( *_optdef (
                opt( *optdef ) ) ) ) ,
          ) ) )

    @unittest.skipUnless(tst_expression_individual, "Expression, individual tests not enabled")
    def test_expression___dash_f_SPACE_file (self):

        # When separated by space, operand must be its own repeatable term
        
        optdef = opt('-f', ' ', '<file>')

        children = usage_prepare_argument_optlst_expr ( olst( optdef ) )
        
        ( texts, terms ) = list(zip(*children))

        self.single ( expression, 
                      * _expr ( (
                          * [ _repeatable( *_term ( texts[idx], terms[idx] ) )
                              for idx in range(len(terms)) ] ,
                      ) ) )

    @unittest.skipUnless(tst_expression_individual, "Expression, individual tests not enabled")
    def test_expression__wrap_1 (self):

        # When separated by space, operand must be its own repeatable term
    
        optlst = olst( opt('-f', ' ', '<file>') )

        children = _optlst_expr ( optlst )

        assert children == usage_prepare_argument_optlst_expr ( optlst )

        children = _wrap ( children, (_term, ) )
        children = _wrap ( children, (_repeatable, ) )
        
        self.single ( expression, *_expr ( children ) )

    @unittest.skipUnless(tst_expression_individual, "Expression, individual tests not enabled")
    def test_expression__wrap_2 (self):

        # When separated by space, operand must be its own repeatable term
    
        optlst = olst( opt('-f', ) ) # ' ', '<file>') )

        self.single ( expression, *_expr (
            _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) ) )

    #==========================================================================

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
            if not nodes_equal(parsed, expect) :
                print("\n!!!")
                print("!!! no match")
                print("!!!")
                return

        assert nodes_equal(parsed, expect), \
            ( f"text = '{text}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

#==============================================================================

def generate_test__argument_option ( cls, optdef, expect_fail=False ) :

    def create_method ( text, expect ) :
        def the_test_method (self) :
            nonlocal text, expect
            self.single ( argument, text, expect )
        return the_test_method

    ( text, expect ) = usage_prepare_argument_optdef ( optdef )

    # Single argument does not support space separation
    if ' ' not in text :
        name = f"test_argument_option_'{text}'"
        method = create_method ( text, expect )
        if expect_fail :
            method = unittest.expectedFailure(method)
        setattr ( cls, name, method )

#------------------------------------------------------------------------------

def generate_test__argument_operand ( cls, operand_, expect_fail=False ) :

    def create_method ( text, expect ) :
        def the_test_method (self) :
            nonlocal text, expect
            self.single ( argument, text, expect )
        return the_test_method

    ( text, expect ) = usage_prepare_argument_operand ( operand_ )

    name = f"test_argument_operand_'{text}'"
    method = create_method ( text, expect )
    if expect_fail :
        method = unittest.expectedFailure(method)
    setattr ( cls, name, method )

#------------------------------------------------------------------------------

def generate_test__argument_command ( cls, command_, expect_fail=False ) :

    def create_method ( text, expect ) :
        def the_test_method (self) :
            nonlocal text, expect
            self.single ( argument, text, expect )
        return the_test_method

    ( text, expect ) = usage_prepare_argument_command ( command_ )

    name = f"test_argument_command_'{text}'"
    method = create_method ( text, expect )
    if expect_fail :
        method = unittest.expectedFailure(method)
    setattr ( cls, name, method )

#------------------------------------------------------------------------------

#gexpr
def generate_test__expression ( cls, optlst, expect_fail=False ) :

    print(f": generate_test__expression : optlst {repr(optlst)}")

    def create_method ( text, expect ) :
        def the_test_method (self) :
            nonlocal text, expect
            self.single ( expression, text, expect )
        return the_test_method

    ( text, expect ) = _expr (
        _wrap ( _optlst_expr ( optlst ), (_repeatable, _term, ) ) )

    #--------------------------------------------------------------------------

    if len(text) > 0 :
        name = f"test_expression__'{text}'"
        method = create_method ( text, expect )
        if expect_fail :
            method = unittest.expectedFailure(method)
        setattr ( cls, name, method )

#------------------------------------------------------------------------------

if tst_argument_operand :

    generate_test__argument_operand(Test_Usage, 'FILE')
    generate_test__argument_operand(Test_Usage, '<file>')

if tst_argument_command :
    generate_test__argument_command(Test_Usage, 'move')
    generate_test__argument_command(Test_Usage, 'fire')
    generate_test__argument_command(Test_Usage, 'FOObar')

#------------------------------------------------------------------------------

variations = "scratch/variations"
os.makedirs ( variations, exist_ok=True)

#------------------------------------------------------------------------------

if tst_argument_option_permute :
    with open(f"{variations}/argument-option", 'w') as f, redirect_stdout(f) :
        # -f, --file, -fFILE, --file=<file>, etc.
        _optdef_seen = set()
        print(f": generating permutation of optlist for 'file', n opt = 2")
        for optlst in optlst_permutations ( 'file', n_opt_max=2 ) :
            print(f": optlst = {optlst}")
            for optdef in optlst :
                if optdef not in _optdef_seen :
                    _optdef_seen.add ( optdef )
                    print(f"  . {optdef}")
                    generate_test__argument_option ( Test_Usage, opt(*optdef) )

#------------------------------------------------------------------------------

if tst_expression_series_permute : # a few hundred permutations w/o CHOICE

    with open(f"{variations}/expression", 'w') as f, redirect_stdout(f) :
        # -f, --file, -fFILE, --file=<file>, etc.
        # words = ( 'file', 'query', ) ; n=3 # 400 permutations
        words = ( 'file', ) ; n=3 # 100 permutations
        print(f": generating permutation of optlist for {repr(words)}, max n opt = {n}")
        for optlst in optlst_permutations ( words, n_opt_max=n ) :
            optlst_obj = olst ( [ opt(*o) for o in optlst ] )
            generate_test__expression ( Test_Usage, optlst_obj )

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
