import sys
import os
import re

from contextlib import redirect_stdout

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal
from arpeggio import Sequence, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _

#------------------------------------------------------------------------------

from prettyprinter import cpprint as pp
from docopt_parser.parsetreenodes import NonTerminal_eq_structural
import p

#------------------------------------------------------------------------------

from grammar.python.common import ws, COMMA, BAR
from grammar.python.generic.operand import *
from grammar.python.optdesc.option import *

#------------------------------------------------------------------------------

# from docopt_parser import DocOptParserPEG
# from docopt_parser import DocOptSimplifyVisitor_Pass1 as Simplify_Pass1
# from docopt_parser import DocOptSimplifyVisitor_Pass2 as Simplify_Pass2

#------------------------------------------------------------------------------

# grammar_elements = [ long_no_arg, short_no_arg, ws ]
grammar_elements = [ ]

def grammar():
    return Sequence( ( OneOrMore ( grammar_elements ), EOF ),
                     rule_name='grammar', skipws=False )

#------------------------------------------------------------------------------
    
class Test_1_option_ws ( unittest.TestCase ) :

    def setUp(self):

        global grammar_elements

        grammar_elements = [ option, ws ]

        self.parser = ParserPython(grammar, reduce_tree=True)

        # quiet, no parse trees displayed
        # self.debug = False

        # show parse tree for pass >= self.debug
        self.debug = 2

        # self.each = True
        self.show = True

        # # tprint._file =
        # self.tty = open("/dev/tty", 'w')

        # self.rstdout = redirect_stdout(self.tty)
        # self.rstdout.__enter__()

        tprint._on = self.show or self.debug is not False

    #--------------------------------------------------------------------------

    def tearDown(self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

    #--------------------------------------------------------------------------

    def single( self, rule, value ):
        parsed = self.parser.parse(' '+value)
        # tprint("\n", parsed.tree_str(), "\n")
        # print('') ; pp(parsed)
        p_ws = Terminal(ws(), 0, ' ')
        p_option = Terminal(rule(), 0, value)
        p_eof = Terminal(EOF(), 0, '')
        expect = NonTerminal(grammar(), [ p_ws, p_option, p_eof ])
        assert NonTerminal_eq_structural(parsed, expect)

    def test_short_single (self) :
        self.single(short_no_arg, "-l")

    def test_long_single (self) :
        self.single(long_no_arg, "--long")

    #--------------------------------------------------------------------------

    def thrice( self, rule, value ):
        n_times = 3
        input = ' ' + ( value + ' ') * n_times
        parsed = self.parser.parse(input)
        # print('') ; pp(parsed)
        p_option = Terminal(rule(), 0, value)
        p_ws = Terminal(ws(), 0, ' ')
        elements = ( p_option, p_ws ) * n_times
        p_eof = Terminal(EOF(), 0, '')
        expect = NonTerminal(grammar(), [ p_ws, *elements, p_eof ])
        assert NonTerminal_eq_structural(parsed, expect)

    def test_short_thrice (self) :
        self.thrice(short_no_arg, "-l")

    def test_long_thrice (self) :
        self.thrice(long_no_arg, "--long")

    #--------------------------------------------------------------------------

    def test_mixed (self) :
        input = ' -a -b --file --form -l --why '
        #
        input = input.strip()
        parsed = self.parser.parse(' '+input)
        #
        inputs = input.split()
        p_ws = Terminal(ws(), 0, ' ')
        elements = [ ]
        for value in inputs :
            rule = short_no_arg if value[1] == '-' else long_no_arg
            elements.append ( Terminal(rule(), 0, value) )
            elements.append ( p_ws )
        if len(elements) > 0:
            del elements[-1]
        p_eof = Terminal(EOF(), 0, '')
        expect = NonTerminal(grammar(), [ p_ws, *elements, p_eof ])
        assert NonTerminal_eq_structural(parsed, expect)


    #--------------------------------------------------------------------------

    def single_w_arg( self, option_rule, operand_rule, input,
                      option_v, operand_v, sep=None ):
        parsed = self.parser.parse(' '+input)
        # tprint("\n", parsed.tree_str(), "\n")
        # print('') ; pp(parsed)
        p_ws = Terminal(ws(), 0, ' ')
        p_option = Terminal(option_rule(), 0, option_v)
        p_operand = Terminal(operand_rule(), 0, operand_v)
        p_eof = Terminal(EOF(), 0, '')
        elements = [ p_ws, p_option, p_operand, p_eof ]
        if sep is not None:
            elements.insert(2, sep)
        expect = NonTerminal(grammar(), elements)
        # print('') ; pp(expect)
        assert NonTerminal_eq_structural(parsed, expect)

    def SKIP_test_short_single_w_arg_ORIG (self) :
        self.single_w_arg(short_no_arg, operand_all_caps, "-lFILE", "-l", "FILE")

    def SKIP_test_short_single_w_arg (self) :
        operands = { operand_all_caps : 'FILE', operand_angled : '<file>' }
        for sep in "= ":
            for operand_rule, arg in operands.items():
                opt='-f'
                self.single_w_arg(short_no_arg, operand_rule,
                                  f"{opt}{sep}{arg}", opt, arg, sep)

    def _test_long_single_w_arg (self) :
        operands = { operand_all_caps : 'FILE', operand_angled : '<file>' }
        for sep in "= ":
            for operand_rule, arg in operands.items():
                opt='--work'
                self.single_w_arg(long_no_arg, operand_rule,
                                  f"{opt}{sep}{arg}", opt, arg, sep)

    #==============================================================================

    def list_options_only ( self, input, optdef, sep=None):
        grammar_elements = [ option_list, ws ]
        parser = ParserPython(grammar, reduce_tree=True)
        pp(parser.parser_model)
        return
        parsed = parser.parse(' '+input)
        # tprint("\n", parsed.tree_str(), "\n")
        print('') ; pp(parsed)
        return
        p_ws = Terminal(ws(), 0, ' ')
        if sep is None:
            sep = p_ws
        elements = [ p_ws ]
        for ( rule, opt ) in optdef :
            elements.append ( Terminal(rule(), 0, opt) )
            elements.append ( sep )
        if len(elements):
            del elements[-1]
        elements.append( Terminal(EOF(), 0, '') )
        expect = NonTerminal(grammar(), elements)
        # print('') ; pp(expect)
        assert NonTerminal_eq_structural(parsed, expect)

    def test_list_short_pair_space(self) :
        r=short_no_arg
        optdef = ( (r, '-f'), (r, '-g') )
        self.list_options_only( '-f -g', optdef )

    def _test_list_short_pair_comma(self) :
        r=short_no_arg
        optdef = ( (r, '-f'), (r, '-g') )
        self.list_options_only( '-f, -g', optdef, COMMA )

    def SKIP_test_list_short_pair_bar(self) :
        self.execute_passes ( 'short', '-f | -g', start='option' )

    #--------------------------------------------------------------------------

    #==============================================================================
    
    # ✓

    def SKIP_test_short_no_arg(self) :        
        self.execute_passes ( 'short', '-l', start='option' )

    def SKIP_test_short_stacked_lowercase(self) :
        self.execute_passes ( 'short', '-cvf', start='option' )

    def SKIP_test_short_stacked_mixedcase(self) :
        self.execute_passes ( 'short', '-fFILEx', start='option' )

    def SKIP_test_short_w_arg_allcaps__no_space(self) :
        self.execute_passes ( 'short', '-fFILE', start='option' )

    def SKIP_test_short_w_arg_angle__no_space(self) :
        self.execute_passes ( 'short', '-f<file>', start='option' )

    def SKIP_test_short_w_arg_allcaps__space(self) :
        self.execute_passes ( 'short', '-f FILE', start='option' )

    def SKIP_test_short_w_arg_angle__space(self) :
        self.execute_passes ( 'short', '-f <file>', start='option' )

    #--------------------------------------------------------------------------

    def SKIP_test_long_no_arg(self) :
        self.execute_passes ( 'long', '--file', start='option' )

    def SKIP_test_long_w_arg_eq_allcaps(self) :
        self.execute_passes ( 'long', '--file=FILE', start='option' )

    def SKIP_test_long_w_arg_eq_angle(self) :
        self.execute_passes ( 'long', '--file=<file>', start='option' )

    # Too ambiguous in usage patterns but not at all ambiguous within
    # the options-section details.

    # Hmm, a usage pattern hack might be that given '--file <file>'
    #   or '--file FILE', since the operand resolves to the same word as
    #   preceeding long option, presume <file> is an option-operand.

    def DEFER__test_long_w_arg_no_eq_allcaps(self) :
        self.execute_passes ( 'long', '--file FILE', start='option' )

    def DEFER_test_long_w_arg_no_eq_angle(self) :
        self.execute_passes ( 'long', '--file <file>', start='option' )

    #--------------------------------------------------------------------------

    def SKIP_test_list_short_pair_comma(self) :
        self.execute_passes ( 'list', '-f, -g')

    def SKIP_test_list_short_pair_bar(self) :
        self.execute_passes ( 'list', '-f | -g')

    def SKIP_test_list_short_pair_space(self) :
        self.execute_passes ( 'list', '-f -g')

    def SKIP_test_list_short_single(self) :
        self.execute_passes ( 'list', '-f' )

    def SKIP_test_list_short_trio_space(self) :
        self.execute_passes ( 'list', '-f -g -h' )
    #
    def SKIP_test_list_short_pair_space(self) :
        self.execute_passes ( 'list', '-f, -g' )

    def SKIP_test_list_short_trio_space(self) :
        self.execute_passes ( 'list', '-f, -g, -h' )
    #
    def SKIP_test_list_short_pair_space(self) :
        self.execute_passes ( 'list', '-f , -g' )

    def SKIP_test_list_short_trio_space(self) :
        self.execute_passes ( 'list', "-f , -g  \t, -h" )

    #--------------------------------------------------------------------------

    def SKIP_test_list_long_single(self) :
        self.execute_passes ( 'list', '--file' )

    def SKIP_test_list_long_pair_comma(self) :
        self.execute_passes ( 'list', '--file, --floor' )

    def SKIP_test_list_long_pair_bar(self) :
        self.execute_passes ( 'list', '--file | --floor' )

    def SKIP_test_list_long_pair_ws(self) :
        self.execute_passes ( 'list', '--file --floor' )

    def SKIP_test_list_long_pair_with_args(self) :
        self.execute_passes ( 'list', '--file=FILE , --floor=<floor>' )

    def SKIP_test_list_long_single(self) :
        self.execute_passes ( 'list', '-f,-g')

    #--------------------------------------------------------------------------

    def execute_passes ( self, name, input, start=None ):

        if start is None:
            start = name

        self.grammar_file = GRAMMAR_PATTERN.replace('{name}', name)

        self.parser = DocOptParserPEG ( grammar_file = self.grammar_file, \
                                        start = start, memoization = True, \
                                        debug = False )

        if self.show or self.debug is not False :
            print(f"\n: input = '{input}'")

        tree = self.perform_pass(0, 'raw', self.parser.parse, self.ws + input + self.ws )
        tree = self.perform_pass(1, 'simplify-1', Simplify_Pass1().visit, tree )
        tree = self.perform_pass(2, 'simplify-2', Simplify_Pass2().visit, tree )

        if False :
            # remove leading and trailing whitespace including newlines
            output = input.strip()
            # reduce each expanse of whitespace to a single space
            output = re.compile('[ \t]+').sub(' ', output)
            # remove spaces before of after a newline
            output = re.compile(' ?\n ?').sub('\n', output)

            expect = Terminal(self.parser.parser.parser_model, 0, value=output)
            assert tree == expect
            # Now this does seem to be using the Terminal's text eq

        return tree

    #--------------------------------------------------------------------------

    def perform_pass(self, _pass, name, fcn, *args, **kwargs):
        if self.debug is not False :
            if _pass >= self.debug :
                print(f": pass {_pass} : {name}")
        out = fcn(*args, **kwargs)
        if self.debug is not False :
            if _pass >= self.debug :
                pp(out)
                print('')
        return out

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    if tprint._on :
        kwargs['file'] = tprint._file
        print(*args, **kwargs)

tprint._file = open("/dev/tty", 'w')

tprint._on = False

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
