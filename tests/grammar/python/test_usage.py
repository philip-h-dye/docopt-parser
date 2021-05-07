parse_debug                     = False
record                          = False
analyzing                       = False
tst_basic                       = True    # 8 tests
tst_expression_individual       = True    # 8 tests
tst_choice_individual           = True    # 3 tests
tst_required_individual         = True    # 1 test
tst_optional_individual         = True    # 1 test
tst_argument_operand            = True    # 2 tests
tst_argument_command            = True    # 3 tests
tst_argument_option_permute     = True    # 6 tests
tst_expression_series_permute   = True    # 100 tests with single word and n 3
tst_usage_pattern               = True    # 4 tests
tst_usage_intro                 = True    # 10 tests
tst_usage                       = True    # 3 tests

#------------------------------------------------------------------------------

import os

import unittest

from contextlib import redirect_stdout

from prettyprinter import cpprint as pp, pprint as pp_plain

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, ZeroOrMore, OneOrMore, EOF
from arpeggio import ParseTreeNode, RegExMatch as _

from docopt_parser.parsetreenodes import nodes_equal

#------------------------------------------------------------------------------

from grammar.python.common import *

from base import Test_Base

from usage import *

define_usage_expression_shortnames(globals())

#------------------------------------------------------------------------------

class Test_Usage ( Test_Base ) :

    def setUp(self):

        # first get defaults, should all be False for boolean flags
        super().setUp()

        global parse_debug, record, analyzing

        self.parse_debug = parse_debug
        self.record = record
        self.analyzing = analyzing

        # quiet, no parse trees displayeda
        # self.debug = False
        
        # show parse tree for pass >= self.debug
        # self.debug = 2

        # Show text being parsed
        # self.show = True

        # and again, to apply behavior per altered settings
        super().setUp()

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

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_choice_individual, "Choice, individual tests not enabled")
    def test_choice_single (self):

        # hierarchy: choice expression repeatable term argument command

        optlst = olst( opt('-f', ) ) # ' ', '<file>') )

        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )

        xchoice = _choice ( ( expr, ) )

        if self.record :
            write_scratch ( choice = xchoice )

        self.single ( choice, *xchoice  )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_choice_individual, "Choice, individual tests not enabled")
    def test_choice_pair (self):

        # hierarchy: choice expression repeatable term argument command

        optlst = olst( opt('-f', ) ) # ' ', '<file>') )

        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )

        xchoice = _choice ( ( expr, expr ) )

        if self.record :
            write_scratch ( choice = xchoice )

        self.single ( choice, *xchoice )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_choice_individual, "Choice, individual tests not enabled")
    def test_choice_trio (self):

        # hierarchy: choice expression repeatable term argument command

        optlst_1 = olst( opt('--file', ' ', '<file>') )
        expr_1 = _expr ( _wrap ( _optlst_expr( optlst_1 ), (_repeatable, _term) ) )

        optlst_2 = olst( opt('--query', '=', '<query>') )
        expr_2 = _expr ( _wrap ( _optlst_expr( optlst_2 ), (_repeatable, _term) ) )

        optlst_3 = olst( opt('-e', '', 'EXTRACT' ) )
        expr_3 = _expr ( _wrap ( _optlst_expr( optlst_3 ), (_repeatable, _term) ) )

        xchoice = _choice ( ( expr_1, expr_2, expr_3 ) )

        if self.record :
            write_scratch ( choice = xchoice )

        self.single ( choice, *xchoice )

    #--------------------------------------------------------------------------

    # required/optional after CHOICE as it is the rule which they each enclose
    #
    # hierarchy: <rule> choice expression repeatable term argument command

    @unittest.skipUnless(tst_required_individual, "Required, individual tests not enabled")
    def test_required__command (self):
        optlst = olst( opt('-f', ) ) # ' ', '<file>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        xchoice = _choice ( ( expr, ) )
        ( text, expect ) = usage_prepare_required ( *xchoice )
        if self.record :
            write_scratch ( required = (text, expect) )
        self.single ( required, text, expect )

    @unittest.skipUnless(tst_optional_individual, "Optional, individual tests not enabled")
    def test_optional__command (self):
        optlst = olst( opt('-f', ) ) # ' ', '<file>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        xchoice = _choice ( ( expr, ) )
        ( text, expect ) = usage_prepare_optional ( *xchoice )
        if self.record :
            write_scratch ( optional = (text, expect) )
        self.single ( optional, text, expect )

    #--------------------------------------------------------------------------

    @unittest.skipUnless(tst_usage_pattern, "Usage Pattern, tests not enabled")
    def test_program (self):
        ( text, expect ) = usage_prepare_program("naval-fate")
        self.single ( program, text, expect )

    #--------------------------------------------------------------------------

    # usage_pattern = OR? program choice?
    # FIXME:  OR implement and test

    @unittest.skipUnless(tst_usage_pattern, "Usage Pattern, tests not enabled")
    def test_usage_pattern__program_only (self):
        program_ = usage_prepare_program("naval-fate")
        pattern = usage_prepare_pattern( program_ )
        self.single ( usage_pattern, *pattern )

    @unittest.skipUnless(tst_usage_pattern, "Usage Pattern, tests not enabled")
    def test_usage_pattern__single_option (self):
        optlst = olst( opt('-f', ) ) # ' ', '<file>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        choice_ = _choice ( ( expr, ) )
        program_ = usage_prepare_program("naval-fate")
        pattern = usage_prepare_pattern( program_, choice_ )
        self.single ( usage_pattern, *pattern )

    @unittest.skipUnless(tst_usage_pattern, "Usage Pattern, tests not enabled")
    def test_usage_pattern__option_gap_operand (self):
        optlst = olst( opt('--file', ' ', '<file>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        choice_ = _choice ( ( expr, ) )
        program_ = usage_prepare_program("naval-fate")
        pattern = usage_prepare_pattern( program_, choice_ )
        self.single ( usage_pattern, *pattern )

    #--------------------------------------------------------------------------

    # usage_line = _ usage_pattern newline / _ usage_pattern EOF

    @unittest.skipUnless(tst_usage_pattern, "Usage Pattern, tests not enabled")
    def test_usage_line (self):
        optlst = olst( opt('-f', ) ) # ' ', '<file>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        choice_ = _choice ( ( expr, ) )
        program_ = usage_prepare_program("naval-fate")
        pattern = usage_prepare_pattern( program_, choice_ )
        line = usage_prepare_line( pattern, t_newline )
        self.single ( usage_line, *line )

    #--------------------------------------------------------------------------

    # usage_intro = _ r'^\s*((?i)usage)\s*:\s*' + '(\s*\n)*'

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__whitespace_none (self):
        self.single ( usage_intro, *usage_prepare_intro("usage:"))

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__whitespace_leading (self):
        self.single ( usage_intro, *usage_prepare_intro("   usage:"))

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__whitespace_trailing (self):
        self.single ( usage_intro, *usage_prepare_intro("usage:   "))

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__whitespace_before_colon (self):
        self.single ( usage_intro, *usage_prepare_intro("usage   :"))

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__whitespace_everywhere (self):
        self.single ( usage_intro, *usage_prepare_intro("  usage  :  "),
                      skipws=False )

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__newline_one (self):
        newlines = ( '\n' )
        self.single ( usage_intro, *usage_prepare_intro("usage :", *newlines ))

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__newline_two (self):
        newlines = ( ' \n', '   \n' )
        self.single ( usage_intro, *usage_prepare_intro("usage :", *newlines ))

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__trailing_and_newlines (self):
        newlines = ( ' \n', '   \n' )
        self.single ( usage_intro, *usage_prepare_intro("usage :  ", *newlines ))

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__implicit_newlines (self):
        newlines = ( ' ', '   ' )
        self.single ( usage_intro, *usage_prepare_intro("usage :  ", *newlines ))

    @unittest.skipUnless(tst_usage_intro, "Usage Intro, tests not enabled")
    def test_usage_intro__embedded_newlines_trailing_and_newlines (self):
        newlines = ( ' \n', '   \n' )
        self.single ( usage_intro, *usage_prepare_intro("usage :  \n  ", *newlines ))

    #--------------------------------------------------------------------------

    # usage = usage_intro newline* usage_line+

    @unittest.skipUnless(tst_usage, "Usage, tests not enabled")
    def test_usage__001_single_line (self):
        optlst = olst( opt('-f', ) ) # ' ', '<file>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        choice_ = _choice ( ( expr, ) )
        program_ = usage_prepare_program("naval-fate")
        pattern = usage_prepare_pattern( program_, choice_ )
        line = usage_prepare_line( pattern, t_newline )

        intro = usage_prepare_intro("Usage :  ")

        text = intro[0] + line[0]
        expect = NonTerminal( usage_section(), [ intro[1], line[1] ] )

        self.single ( usage_section, text, expect )

    @unittest.skipUnless(tst_usage, "Usage, tests not enabled")
    def Xtest_usage__002_two_lines (self):
        optlst = olst( opt('-f', ) ) # ' ', '<file>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        choice_ = _choice ( ( expr, ) )
        program_ = usage_prepare_program("naval-fate")
        pattern = usage_prepare_pattern( program_, choice_ )
        line = usage_prepare_line( pattern, t_newline )

        intro = usage_prepare_intro("Usage :  ")

        text = intro[0] + line[0] + line[0]
        expect = NonTerminal( usage_section(), [ intro[1], line[1] , line[1] ] )

        self.single ( usage_section, text, expect )

    @unittest.skipUnless(tst_usage, "Usage, tests not enabled")
    def test_usage__003_three_lines (self):
        #
        # FIXME: exactly where does the help text get inserted ?
        #
        optlst = olst( opt('-f', ), opt('-q', ), opt('--file', '=', '<file>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        choice_ = _choice ( ( expr, ) )
        program_ = usage_prepare_program("naval-fate")
        pattern = usage_prepare_pattern( program_, choice_ )
        line_1 = usage_prepare_line( pattern, t_newline )

        optlst = olst( opt('-q', ' ', '<query>'), opt('--query', '=', '<query>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        choice_ = _choice ( ( expr, ) )
        program_ = usage_prepare_program("naval-fate")
        pattern = usage_prepare_pattern( program_, choice_ )
        line_2 = usage_prepare_line( pattern, t_newline )

        optlst = olst( opt('-e', '', '<query>'), opt('--extract', '=', '<query>') )
        expr = _expr ( _wrap ( _optlst_expr( optlst ), (_repeatable, _term) ) )
        choice_ = _choice ( ( expr, ) )
        program_ = usage_prepare_program("naval-fate")
        pattern = usage_prepare_pattern( program_, choice_ )
        line_3 = usage_prepare_line( pattern, t_newline )

        intro = usage_prepare_intro("Usage :  ")

        text = intro[0] + line_1[0] + line_2[0] + line_3[0]
        expect = NonTerminal( usage_section(), [ intro[1], line_1[1], line_2[1], line_3[1] ] )

        self.single ( usage_section, text, expect )

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
