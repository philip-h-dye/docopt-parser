import unittest

import sys

from copy import deepcopy

from arpeggio import ParseTreeNode, Terminal, NonTerminal, StrMatch

#------------------------------------------------------------------------------

from docopt_parser.parsetreenodes import *

from docopt_parser.wrap import wrap, unwrap, unwrap_extend, unwrap_into

class Test_Case ( unittest.TestCase ):

    def setUp (self):
        NonTerminal_restore_original_eq()
        self.dot = StrMatch('.', rule_name = 'dot')
        self.t1 = Terminal(self.dot, 0, 'one')
        self.n1 = NonTerminal(self.dot, [ self.t1 ])

    def test_001__t1_eq_n1__without_eq (self):
        assert self.t1 == self.n1
        # it is using t1's __eq__ :  text(self) == text(other)

    def test_002__n1_eq_t1__without_eq (self):
        assert self.n1 == self.t1

    def test_003__t1_eq_n1__with_eq (self):
        NonTerminal_enable_structural_eq()
        assert self.t1 == self.n1
        # no change, still using t1's __eq__ :  text(self) == text(other)

    def test_004__n1_eq_t1__with_eq (self):
        if False :
            from prettyprinter import cpprint as pp
            import p
            print(f": test_004__n1_eq_t1__with_eq")
            print(f": n1 :")
            pp(self.n1)
            print(f": t1 :")
            pp(self.t1)
        NonTerminal_enable_structural_eq()
        with self.assertRaises(AssertionError) as context:
            assert self.n1 == self.t1 # now it fails
            self.assertTrue('Internal error, AssertionError not raised !!!')
        assert self.n1 != self.t1
        assert self.n1 == deepcopy(self.n1)

        t2 = Terminal(self.dot, 0, 'one')
        n2 = NonTerminal(self.dot, [ t2 ])
        assert self.n1 == n2

        t2 = Terminal(self.dot, 0, 'one')
        n2 = NonTerminal(self.dot, [ t2 ])
        assert self.n1 == n2

        bang = StrMatch('!', rule_name = 'bang')
        t3 = Terminal(bang, 0, 'one')
        n3 = NonTerminal(bang, [ t3 ])
        assert self.n1 != n3

#------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(sys.argv)

#------------------------------------------------------------------------------
