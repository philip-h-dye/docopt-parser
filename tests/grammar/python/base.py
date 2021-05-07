parse_debug                     = False
record                          = False
analyzing                       = False

#------------------------------------------------------------------------------

import unittest

from prettyprinter import cpprint as pp

from arpeggio import ParserPython, flatten, EOF, NonTerminal, Sequence

from docopt_parser.parsetreenodes import nodes_equal

#------------------------------------------------------------------------------

from grammar.python.common import t_eof

from util import tprint, write_scratch

#------------------------------------------------------------------------------

class Test_Base ( unittest.TestCase ) :

    def setUp(self):

        if not hasattr(self, 'parse_debug'):
            self.parse_debug = False
        if not hasattr(self, 'record'):
            self.record = False
        if not hasattr(self, 'analyzing'):
            self.analyzing = False
        if not hasattr(self, 'debug'):
            self.debug = False
        if not hasattr(self, 'show'):
            self.show = False

        tprint._on = self.show or self.debug is not False

        if self.record :
            write_scratch( _clean=True )

    #--------------------------------------------------------------------------

    def single ( self, rule, text, expect, skipws=True, lead=None ):
        """
        <lead> : ( text, expect ) for leading value to prefix the text
                                  and expect.  Required when rule has
                                  lookbehind.  For '(?<=\s)foo', an simple
                                  lead would be ( ' ', t_space ), as
                                  the lead includes whitespace, skipws=False
                                  is also necessary.
        """
        # The model unfortunately will show 'rule' as a function
        # rather that it's expression.  It is tempting to then instantiate
        # it as rule().  The parse model will now show it nicely.
        #
        # Unfortunately, the resulting parse tree drops the node for rule.
        #
        body = [ rule, EOF ]
        if lead is not None :
            ( text_, expect_ ) = lead
            text = text_ + text
            body.insert(0, expect_ )
        def grammar():
            return Sequence( ( *body ), rule_name='grammar', skipws=skipws )
        # print(f"\n: single : text = '{text}'")
        self.verify_grammar ( grammar, text, [ expect ], skipws=skipws )

    #--------------------------------------------------------------------------

    def multiple ( self, rule, text, expect, n=1, sep='\n' ):
        # both rule and text get a single space prefix to assist when
        # the rule has a whitespace lookahead
        def grammar():
            return Sequence (
                ( OneOrMore( OrderedChoice ( [ rule, ws, newline ] ) ), EOF ),
                rule_name='grammar', skipws=True )
        text = sep.join( [text] * n )
        expect_list = [expect] * n
        # print(f"\n: multiple : text = '{text}'")
        # self.verify_grammar ( grammar, ' '+text, expect_list )
        self.verify_grammar ( grammar, text, expect_list )

    #--------------------------------------------------------------------------

    def verify_grammar ( self, grammar, text, expect_list, skipws=True ):
        self.grammar = grammar()
        self.skipws = skipws
        self.text = text
        self.expect = NonTerminal( self.grammar, [ *expect_list, t_eof ] )
        self.parser = ParserPython ( grammar, ws=" \t\r", skipws=self.skipws,
                                     debug=self.parse_debug, reduce_tree=False )
        self.parse_and_verify( self.text, self.expect )

    #--------------------------------------------------------------------------

    def parse_and_verify ( self, text, expect ) :
        parsed = self.parse ( text, expect )
        self.verify ( text, expect, parsed  )

    #--------------------------------------------------------------------------

    def parse ( self, text, expect ) :

        if not hasattr(self, 'text') or self.text != text :
            self.text = text
        if not hasattr(self, 'expect') or not nodes_equal(expect, self.expect) :
            self.expect = expect

        # tprint(f"\nOptions :\n{text}")

        # written here and in verify since they may be called independently
        if self.record :
            write_scratch( grammar=self.grammar, text=self.text,
                           expect=self.expect, expect_f=flatten(self.expect),
                           model=self.parser.parser_model, )
        try :
            # print(f"\n: text = '{text}'")
            self.parsed = self.parser.parse(text)
            # tprint("[parsed]") ; pp(self.parsed)
            if self.record :
                write_scratch( parsed=self.parsed )
        except Exception as e :
            print("\n"
                  f"[expect]\n{pp_str(expect)}\n\n"
                  f"text = '{text}' :\n\n"
                  f"Parse FAILED :\n"
                  f"{str(e)}" )
            raise

        return self.parsed

    #--------------------------------------------------------------------------

    def verify ( self, text, expect, parsed ) :

        if not hasattr(self, 'text') or self.text != text :
            self.text = text
        if not hasattr(self, 'expect') or not nodes_equal(expect, self.expect) :
            self.expect = expect
        if not hasattr(self, 'parsed') or not nodes_equal(parsed, self.parsed) :
            self.parsed = parsed

        if self.record :
            write_scratch( grammar=self.grammar, text=self.text,
                           expect=self.expect, expect_f=flatten(self.expect),
                           model=self.parser.parser_model, )

        if self.analyzing :
            self.analyze()

        assert nodes_equal(parsed, expect), \
            ( f"text = '{text}' :\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

    #--------------------------------------------------------------------------

    def analyze (self):

        # lose 'self.' for legibility
        expect = self.expect
        parsed = self.parsed

        # 'nth_option_line' specific applicable in docopt/test_line, within the
        # outer enclosing context it would obviously be deeper and certainly
        # not a descendent of the first outer node.  Left as an starting point
        # when focused and detailed analysis needed.
        nth_option_line = 0
        expect = expect[0][0] # [0][ nth_option_line ] # [0] [0]
        parsed = parsed[0][0] # [0][ nth_option_line ] # [0] [0]

        print('')

        expect_terminal = isinstance(expect, Terminal)
        parsed_terminal = isinstance(parsed, Terminal)

        if expect_terminal :
            print(f"[expect] rule '{expect.rule_name}', Terminal = {pp_str(expect)}")
        else :
            print(f"[expect] rule '{expect.rule_name}' with {len(expect)} children")
        if parsed_terminal :
            print(f"[parsed] rule '{parsed.rule_name}', Terminal = {pp_str(parsed)}")
        else :
            print(f"[parsed] rule '{parsed.rule_name}' with {len(parsed)} children")

        if expect_terminal or parsed_terminal :
            assert nodes_equal(parsed, expect), \
                ( f"Detail nodes are not equal.\n"
                  f"[text]   '{text}'\n"
                  f"[expect] rule '{expect.rule_name}'\n{pp_str(expect)}\n"
                  f"[parsed] rule '{parsed.rule_name}'\n{pp_str(parsed)}\n" )
            return

        print(f"[expect] rule '{expect.rule_name}' with {len(expect)} children")
        print(f"[parsed] rule '{parsed.rule_name}' with {len(parsed)} children")

        assert parsed.rule_name == expect.rule_name, \
            ( f"Detail node rule names not equal.\n"
              f"[text]   '{text}'\n"
              f"[expect] rule '{expect.rule_name}' with {len(expect)} children\n"
              f"[parsed] rule '{parsed.rule_name}' with {len(parsed)} children\n"
              f"[expect]\n{pp_str(expect)}\n"
              f"[parsed]\n{pp_str(parsed)}" )

        for i in range(min( len(expect), len(parsed) )):
            assert nodes_equal( parsed[i], expect[i]), \
                ( f"Detail node child {i} is not equal.\n"
                  f"[text]   '{text}'\n"
                  f"[expect] rule '{expect.rule_name}' with {len(expect)} children\n"
                  f"[parsed] rule '{parsed.rule_name}' with {len(parsed)} children\n"
                  f"[expect] [{i}]\n{pp_str(expect[i])}\n"
                  f"[parsed] [{i}]\n{pp_str(parsed[i])}" )

        assert not ( len(expect) > len(parsed) ), \
                ( f"Expect has more children than parsed, earlier children equal.\n"
                  f"[text]   '{text}'\n"
                  f"[expect] rule '{expect.rule_name}' with {len(expect)} children\n"
                  f"[parsed] rule '{parsed.rule_name}' with {len(parsed)} children\n"
                  f"[expect] [{i}]\n{pp_str(expect[len(parsed):])}" )

        assert not ( len(expect) < len(parsed) ), '\n' + \
                ( f"Parsed has more children than expect, earlier children equal.\n"
                  f"[text]   '{text}'\n"
                  f"[expect] rule '{expect.rule_name}' with {len(expect)} children\n"
                  f"[parsed] rule '{parsed.rule_name}' with {len(parsed)} children\n"
                  f"[parsed] [{i}]\n{pp_str(parsed[len(expect):])}" )

#------------------------------------------------------------------------------
