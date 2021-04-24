import unittest

from copy import deepcopy

from arpeggio import ParseTreeNode, Terminal, NonTerminal, StrMatch

from prettyprinter import cpprint as pp

#------------------------------------------------------------------------------

from docopt_parser.wrap import WrappedList, FakeNode, wrap, unwrap, unwrap_into

#------------------------------------------------------------------------------

class Test_Case ( unittest.TestCase ):

    def test_marker ( self ):
        pass

    def setUp ( self ):
        self.dot = StrMatch('.', rule_name = 'self.dot')

        self.s1 = 's1 : string'

        # rule, position, value
        self.t1 = Terminal(self.dot, 0, 'one')
        self.t2 = Terminal(self.dot, 0, 'two')
        self.t3 = Terminal(self.dot, 0, 'three')

        assert not isinstance(self.t1, list)
        assert not isinstance(self.t2, list)
        assert not isinstance(self.t3, list)

        # rule, value : a list where the first element is a node
        # self.n1 = NonTerminal(self.dot, self.t1)   # TypeError: 'Terminal' object is not subscriptable
        self.n2 = NonTerminal(self.dot, [ self.t1 ])
        self.n3 = NonTerminal(self.dot, self.n2 )
        self.n4 = NonTerminal(self.dot, [ self.n2 ])

        assert isinstance(self.n2, list)
        assert isinstance(self.n3, list)
        assert isinstance(self.n4, list)

        self.v0 = self.n2
        self.v1 = [ 'v1 : string 1', 'v1 : string 2' ]
        self.v2 = self.t1
        self.v3 = 'v3 : string'

    def test_wrap_unneccessary(self):

        w = wrap(deepcopy(self.v0))
        assert not hasattr(w, '_please_unwrap')
        assert w == self.v0

    def test_wrap_and_unwrap__case_1 (self):

        # Case 1 : list but [0] is not a ParseTreeNode

        w = wrap(deepcopy(self.v1))
        assert hasattr(w, '_please_unwrap')
        assert w._please_unwrap == 1
        assert w is not self.v1
        # pp(self.v1)
        # pp(unwrap(deepcopy(w)))
        assert unwrap(w) == self.v1

    def test_wrap_and_unwrap__case_2 (self):

        # Case 2 : not a list, value is a ParseTreeNode

        w = wrap(deepcopy(self.v2))
        assert hasattr(w, '_please_unwrap')
        # print(f": w2._please_unwrap == {w._please_unwrap}")
        assert w._please_unwrap == 2
        assert w is not self.v2
        # pp(self.v2)
        # pp(unwrap(deepcopy(w)))
        # pp(w)
        assert unwrap(w) == self.v2

    def test_wrap_and_unwrap__case_3 (self):

        # Case 3 : not a list, value is not a ParseTreeNode

        w = wrap(deepcopy(self.v3))
        assert hasattr(w, '_please_unwrap')
        # print(f": w3._please_unwrap == {w._please_unwrap}")
        assert w._please_unwrap == 3
        assert w is not self.v3
        # pp(self.v3)
        # pp(unwrap(deepcopy(w)))
        assert unwrap(w) == self.v3

    #--------------------------------------------------------------------------

    def test_unwrap_into__case_1 (self):

        # Case 1 : list but [0] is not a ParseTreeNode

        aaa = [ self.t1, self.v1, self.t2 ]
        sav = deepcopy(aaa) ; sav[1] = wrap(deepcopy(sav[1]))
        dst = deepcopy(sav)

        n = unwrap_into(dst,1)

        # print(f": sav") ; pp(sav) ; print('')
        # print(f": dst : n = {n}") ; pp(dst) ; print('')
        # print(f": aaa") ; pp(aaa) ; print('')

        assert dst == aaa

    def test_unwrap_into__case_2 (self):

        # Case 2 : not a list, value is a ParseTreeNode

        aaa = [ self.t1, self.n2, self.t1 ]
        sav = deepcopy(aaa) ; sav[1] = wrap(deepcopy(sav[1]))
        dst = deepcopy(sav)

        n = unwrap_into(dst,1)

        # print(f": sav") ; pp(sav) ; print('')
        # print(f": dst : n = {n}") ; pp(dst) ; print('')
        # print(f": aaa") ; pp(aaa) ; print('')

        assert dst == aaa

    def test_unwrap_into__case_3 (self):

        # Case 3 : not a list, value is not a ParseTreeNode

        aaa = [ self.t1, self.s1 , self.t1 ]
        sav = deepcopy(aaa) ; sav[1] = wrap(deepcopy(sav[1]))
        dst = deepcopy(sav)

        n = unwrap_into(dst,1)

        # print(f": sav") ; pp(sav) ; print('')
        # print(f": dst : n = {n}") ; pp(dst) ; print('')
        # print(f": aaa") ; pp(aaa) ; print('')

        assert dst == aaa

#------------------------------------------------------------------------------
